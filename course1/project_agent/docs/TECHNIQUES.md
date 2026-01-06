# AI Techniques Deep Dive

Complete explanation of all advanced techniques implemented in this project.

---

## Table of Contents

1. [Chain-of-Thought Prompting](#chain-of-thought-prompting)
2. [ReAct Pattern](#react-pattern)
3. [Structured Output Generation](#structured-output-generation)
4. [Temperature Control](#temperature-control)
5. [Robust JSON Extraction](#robust-json-extraction)
6. [Loop Detection](#loop-detection)
7. [Evaluation-Driven Development](#evaluation-driven-development)

---

## Chain-of-Thought Prompting

### What It Is

A prompting technique that instructs LLMs to break down complex problems into explicit reasoning steps before providing a final answer.

### Why It Works

**Research Finding** (Wei et al. 2022): CoT improves performance on complex reasoning tasks by 15-60% compared to direct prompting.

**Mechanism**:
- Forces systematic thinking
- Reduces cognitive load per step
- Makes errors easier to spot
- Enables self-correction

### Implementation in Cell 14

```python
ITINERARY_AGENT_SYSTEM_PROMPT = """
## Planning Process (Execute in THIS order)

### Phase 1: Data Analysis (5 minutes)
```
STEP 1.1 - Parse Traveler Interests:
- List each traveler and their interests
- Identify overlapping interests
- Note unique interests

STEP 1.2 - Weather Analysis:
- Date | Condition | Suitable for outdoor?
- Identify risky days (rain/storms)
- Plan indoor-heavy for those days

STEP 1.3 - Activity Inventory:
- Total activities available
- By interest category
- By weather suitability
- Price range: min/max/avg
```

### Phase 2: Budget Allocation
```
STEP 2.1 - Calculate Constraints:
- Total budget: B
- Days: N
- Budget per day: B/N
- Must-have activities with costs
- Remaining budget

STEP 2.2 - Prioritization:
P1: Activities matching BOTH travelers
P2: One traveler + weather-appropriate
P3: Unique experiences
P4: Filler activities
```

### Phase 3: Day-by-Day Planning
```
FOR EACH DAY:
  STEP 3.1 - Filter Available
  STEP 3.2 - Select by Priority
  STEP 3.3 - Document Reasoning
```
"""
```

### Best Practices

1. **Be Explicit**: Don't assume LLM knows the process
2. **Number Steps**: Makes it clear there's a sequence
3. **Show Don't Tell**: Provide examples of reasoning
4. **Validate Checkpoints**: Include validation at each phase

### When to Use

- ✅ Complex planning (>3 steps)
- ✅ Multi-constraint problems
- ✅ When explainability matters
- ✅ Tasks with multiple data sources
- ❌ Simple lookup/classification
- ❌ Creative writing
- ❌ When speed > accuracy

---

## ReAct Pattern

### What It Is

**ReAct** = **Rea**soning + **Act**ing

A pattern where agents alternate between:
1. **THOUGHT**: Reasoning about what to do
2. **ACTION**: Calling a tool/function
3. **OBSERVATION**: Processing the result

### Why It Works

**Research Finding** (Yao et al. 2022): ReAct improves success rate on complex tasks by 25-45% vs reasoning-only or acting-only approaches.

**Mechanism**:
- Gathers information as needed
- Adapts to environment feedback
- Self-corrects when tools fail
- Explicit decision making

### Implementation in Cell 34

```python
ITINERARY_REVISION_AGENT_SYSTEM_PROMPT = """
## ReAct Cycle Format

THOUGHT:
1. Current Status:
   - Phase: [1-5]
   - Iteration: [X/15]
   - Failures: [count]
   - Tools used: [list]

2. Analysis:
   - What did OBSERVATION tell me?
   - What's the next logical step?

3. Decision:
   - Tool to use: [name]
   - Why: [justification]
   - Expected outcome: [what I'll learn]

4. Loop Detection:
   - Called this before? [yes/no]
   - If yes, what's different?

ACTION:
{"tool_name": "calculator_tool", "arguments": {"input_expression": "25 + 30 + 50"}}

[System executes and returns OBSERVATION]

OBSERVATION:
Tool calculator_tool executed successfully.
Result: 105

[Agent receives OBSERVATION, starts new THOUGHT]

THOUGHT:
1. Current Status: Iteration 5/15, Failures: 1
2. Analysis: Total cost is 105, budget is 130. Within budget!
3. Decision: Now check weather compatibility...
...
"""
```

### Tool Selection Strategy

```python
## Tool Selection Decision Tree

IF (weather incompatibility):
    → get_activities_by_date_tool (find indoor)

IF (budget exceeded):
    → calculator_tool (verify math)
    → get_activities_by_date_tool (find cheaper)

IF (interest not matched):
    → get_activities_by_date_tool (filter by interest)

IF (all checks pass):
    → run_evals_tool (validate)

IF (evaluations pass):
    → final_answer_tool (submit)
```

### Best Practices

1. **Structured THOUGHT**: Always include status, analysis, decision
2. **Explicit Tool Choice**: State why choosing this tool
3. **Track History**: Prevent calling same tool repeatedly
4. **Max Iterations**: Set clear limit (e.g., 15)
5. **Success Condition**: Define when to call final_answer_tool

### When to Use

- ✅ Tool use scenarios
- ✅ Debugging workflows
- ✅ Iterative improvement
- ✅ Dynamic environments
- ❌ Single-shot tasks
- ❌ No tools available
- ❌ Real-time requirements (<1s)

---

## Structured Output Generation

### Problem

LLMs naturally generate free-form text. Production systems need structured data (JSON, SQL, etc.).

### Solution: Schema + Examples + Validation

```python
## Step 1: Define Schema (Pydantic)
class TravelPlan(BaseModel):
    city: str
    start_date: datetime.date
    end_date: datetime.date
    total_cost: int
    itinerary_days: List[ItineraryDay]

## Step 2: Include Schema in Prompt
PROMPT = f"""
Generate a travel plan matching this JSON schema:
{json.dumps(TravelPlan.model_json_schema(), indent=2)}

Example:
{{
  "city": "AgentsVille",
  "start_date": "2025-06-10",
  ...
}}
"""

## Step 3: Validate Response
travel_plan = TravelPlan.model_validate_json(llm_response)
```

### Techniques for Better Structured Output

1. **Show Schema**: Include JSON schema in prompt
2. **Provide Examples**: 2-3 concrete examples
3. **Use Temperature 0.1-0.2**: Reduces format variations
4. **Validate Early**: Catch errors before using data
5. **Retry on Failure**: 3 attempts handles ~95% of cases

---

## Temperature Control

### What Temperature Does

Controls randomness in LLM outputs:
- **0.0**: Deterministic (always picks highest probability token)
- **0.5**: Balanced
- **1.0**: Creative (samples from full probability distribution)
- **2.0**: Chaotic

### Our Usage

```python
# ItineraryAgent (Cell 14)
temperature = 0.2  # Mostly deterministic, slight creativity

# ItineraryRevisionAgent (Cell 34)
temperature = 0.1  # Maximum determinism for tool use

# Creative writing (if we had it)
temperature = 0.7  # More variety
```

### Impact Data

| Temperature | Consistency | Use Case |
|-------------|-------------|----------|
| 0.1 | ~95% same | Production APIs, tool use |
| 0.2 | ~85% same | Planning, structured output |
| 0.5 | ~60% same | Balanced generation |
| 0.7 | ~40% same | Creative writing |
| 1.0+ | <20% same | Brainstorming, variety |

### Best Practices

1. **Start Low**: Begin with 0.1-0.2 for structured tasks
2. **Measure**: Track output consistency in logs
3. **Adjust Up**: Only increase if outputs too rigid
4. **Document**: Note temperature choice in code comments

---

## Robust JSON Extraction

### The Problem

LLMs return JSON in various formats:
```
# Format 1: Clean JSON
{"city": "AgentsVille", ...}

# Format 2: Markdown wrapped
```json
{"city": "AgentsVille", ...}
```

# Format 3: With commentary
Here's the plan:
```json
{"city": "AgentsVille", ...}
```

# Format 4: Nested in keys
{
  "ANALYSIS": "I analyzed...",
  "FINAL OUTPUT": {"city": "AgentsVille", ...}
}

# Format 5: Split sections
ANALYSIS:
I considered the weather...

FINAL OUTPUT:
```json
{"city": "AgentsVille", ...}
```
```

### Our Solution (Cell 14)

```python
def extract_json_robust(response: str) -> dict:
    """
    Production-ready JSON extraction.

    Handles:
    - Markdown code blocks
    - Section markers
    - Nested keys
    - Commentary
    """
    json_text = response.strip()

    # Step 1: Extract from sections
    if 'FINAL OUTPUT:' in json_text:
        json_text = json_text.split('FINAL OUTPUT:')[-1].strip()

    # Step 2: Remove markdown code blocks
    if '```json' in json_text:
        json_text = json_text.split('```json')[1].split('```')[0].strip()
    elif '```' in json_text:
        parts = json_text.split('```')
        if len(parts) >= 3:
            json_text = parts[1].strip()

    # Step 3: Handle nested JSON (CRITICAL)
    import json
    try:
        parsed = json.loads(json_text)

        if isinstance(parsed, dict):
            # Check for wrapper keys
            if 'FINAL OUTPUT' in parsed:
                parsed = parsed['FINAL OUTPUT']
                json_text = json.dumps(parsed)
            elif 'ANALYSIS' in parsed:
                parsed.pop('ANALYSIS', None)
                json_text = json.dumps(parsed)
    except json.JSONDecodeError:
        # If parse fails, continue with original
        pass

    # Step 4: Final parse
    return json.loads(json_text)
```

### Key Insight

**Parse first, then extract**: Don't try to extract JSON with regex. Parse the whole response, then navigate the structure.

### Testing Strategy

```python
# Test with various formats
test_cases = [
    '{"city": "A"}',  # Clean
    '```json\n{"city": "A"}\n```',  # Markdown
    'ANALYSIS: ...\n\nFINAL OUTPUT:\n{"city": "A"}',  # Sections
    '{"ANALYSIS": "...", "FINAL OUTPUT": {"city": "A"}}',  # Nested
]

for test in test_cases:
    result = extract_json_robust(test)
    assert result == {"city": "A"}
```

---

## Loop Detection

### The Problem

Agents can get stuck:
```
Iteration 1: Call get_activities("2025-06-10")
Iteration 2: Call get_activities("2025-06-10")  # Same!
Iteration 3: Call get_activities("2025-06-10")  # Loop!
```

### Our Solution (Cell 34)

```python
def run_react_cycle(max_steps=15):
    tool_call_history = []

    for step in range(max_steps):
        # Get THOUGHT and ACTION from agent
        resp = agent.get_response()

        # Extract tool call
        tool_name = extract_tool_name(resp)
        arguments = extract_arguments(resp)

        # Create signature for comparison
        tool_signature = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"

        # Check if called recently
        if tool_signature in tool_call_history[-3:]:
            send_warning("""
            LOOP DETECTED:
            You've called {tool_name} with identical arguments
            in your last 3 iterations.

            Try a DIFFERENT approach:
            - Use a different tool
            - Use different parameters
            - Simplify your solution
            """)
            continue  # Skip this iteration

        # Record and execute
        tool_call_history.append(tool_signature)
        result = execute_tool(tool_name, arguments)
```

### Detection Strategy

1. **Track Signatures**: Tool name + sorted arguments
2. **Window Size**: Check last 3 calls (catches immediate loops)
3. **Warning**: Prompt agent to try different approach
4. **Max Iterations**: Hard limit (15) as fallback

### When Loops Happen

- Agent doesn't understand tool output
- Tool returns same data repeatedly
- Agent forgets it already tried this
- Poorly designed prompts

### Prevention

1. **Clear Tool Descriptions**: Agent knows what each tool does
2. **Explicit OBSERVATION Format**: Make results obvious
3. **Loop Check in Prompt**: Remind agent to check history
4. **Diverse Examples**: Show various problem-solving paths

---

## Evaluation-Driven Development

### Philosophy

"If you can't measure it, you can't improve it."

### Pattern

```python
# 1. Define success criteria
def eval_constraint_X(input, output):
    if not satisfies_constraint(output):
        raise AgentError(f"Constraint X failed: {reason}")

# 2. Run all evaluations
def run_all_evals(output, eval_functions):
    failures = []
    for eval_fn in eval_functions:
        try:
            eval_fn(input, output)
        except AgentError as e:
            failures.append(str(e))

    return {
        "success": len(failures) == 0,
        "failures": failures,
    }

# 3. Use in feedback loop
results = run_all_evals(output, ALL_EVAL_FUNCTIONS)

if not results.success:
    feedback = format_failures(results.failures)
    improved_output = agent.improve(output, feedback)
```

### Types of Evaluations

**1. Programmatic** (fast, exact):
```python
def eval_budget(vacation_info, plan):
    if plan.total_cost > vacation_info.budget:
        raise AgentError(f"Budget: {plan.total_cost} > {vacation_info.budget}")
```

**2. LLM-Based** (slower, handles nuance):
```python
def eval_weather_compatibility(vacation_info, plan):
    for day in plan.itinerary_days:
        prompt = f"""
        Activity: {day.activity.description}
        Weather: {day.weather.condition}

        Is this compatible? Respond: IS_COMPATIBLE or IS_INCOMPATIBLE
        """
        result = llm_call(prompt)

        if "IS_INCOMPATIBLE" in result:
            raise AgentError(f"Weather incompatibility on {day.date}")
```

### Benefits

1. **Objective Quality**: Clear pass/fail criteria
2. **Enables Feedback**: Failures become improvement instructions
3. **Regression Prevention**: Catch when changes break things
4. **Documentation**: Evals document what "good" means

### Our Evaluations (Cells 18-23)

| Evaluation | Type | What It Checks |
|------------|------|----------------|
| `eval_start_end_dates_match` | Programmatic | Dates align with input |
| `eval_total_cost_is_accurate` | Programmatic | Cost calculation correct |
| `eval_total_cost_is_within_budget` | Programmatic | Budget not exceeded |
| `eval_itinerary_events_match_actual` | Programmatic | Activities exist (no hallucinations) |
| `eval_itinerary_satisfies_interests` | Programmatic | Each traveler has interest match |
| `eval_activities_and_weather_compatible` | LLM-based | Weather suitability |
| `eval_traveler_feedback_incorporated` | LLM-based | User feedback followed |

---

## Combining Techniques

### The Power of Integration

These techniques work best together:

```
Chain-of-Thought
    ↓
Generates structured reasoning
    ↓
Structured Output
    ↓
Produces valid JSON
    ↓
Evaluation
    ↓
Detects failures
    ↓
ReAct + Tools
    ↓
Iteratively fixes issues
    ↓
Loop Detection
    ↓
Prevents getting stuck
    ↓
Final Validated Output
```

### Real Example from Project

1. **CoT (Cell 14)**: ItineraryAgent plans systematically
2. **Structured Output**: Returns valid TravelPlan JSON
3. **Evaluation (Cell 18-23)**: Checks all 7 criteria
4. **ReAct (Cell 34)**: RevisionAgent fixes failures
5. **Tools**: get_activities, calculator, run_evals
6. **Loop Detection**: Prevents repetitive tool calls
7. **Success**: All evaluations pass

---

## References

- Wei et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in LLMs"
- Yao et al. (2022). "ReAct: Synergizing Reasoning and Acting in LLMs"
- Schick et al. (2023). "Toolformer: LLMs Can Teach Themselves to Use Tools"
- Anthropic (2023). "Constitutional AI: Harmlessness from AI Feedback"

---

**Next**: See [PATTERNS.md](PATTERNS.md) for reusable code templates
