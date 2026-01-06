# AI Agentic Course - Complete Learning Journey

> Comprehensive repository documenting advanced LLM techniques, prompt engineering patterns, and agentic AI systems.

**Course**: Udacity AI Agentic Systems
**Focus**: Prompt Engineering, Chain-of-Thought, ReAct, Feedback Loops, Production MLOps
**Status**: ✅ Complete with production-ready final project

---

## 📚 Course Structure

This repository follows a progressive learning path from basic prompting to production-ready agentic systems:

| Module | Topic | Key Learnings | Status |
|--------|-------|---------------|--------|
| **1** | [Generic Prompting](#1-generic-prompting) | LLM basics, model selection, prompt fundamentals | ✅ |
| **2** | [Role-Based Prompting](#2-role-based-prompting) | Persona definition, expert system design | ✅ |
| **3** | [Chain-of-Thought & ReAct](#3-chain-of-thought--react) | Structured reasoning, tool use patterns | ✅ |
| **4** | [Prompt Refinement](#4-prompt-instruction-refinement) | Iterative improvement, evaluation | ✅ |
| **5** | [Prompt Chaining](#5-chaining-prompts) | Multi-step workflows, state management | ✅ |
| **6** | [Feedback Loops](#6-feedback-loops) | Self-correction, evaluation-driven development | ✅ |
| **7** | [Advanced Chaining](#7-advanced-chaining-practice) | Real-world applications, LangGraph | ✅ |
| **8** | [Feedback Loop Mastery](#8-feedback-loop-implementation) | Complete feedback system implementation | ✅ |
| **Final** | [**AgentsVille Project**](#final-project-agentsv ille-trip-planner) | **Production system with all techniques** | ✅ |

---

## 🎯 What You'll Learn

### Core Techniques

#### 1. **Chain-of-Thought (CoT) Prompting**
- Force LLMs to show step-by-step reasoning
- Improves accuracy on complex tasks by 15-60%
- **Implemented in**: Modules 3, 8, Final Project

**Example**:
```python
PROMPT = """
## Task: Plan a vacation itinerary

## Process (Execute in order):
STEP 1: Analyze traveler interests
STEP 2: Check weather conditions
STEP 3: Filter available activities
STEP 4: Allocate budget
STEP 5: Generate day-by-day plan
"""
```

#### 2. **ReAct Pattern (Reasoning + Acting)**
- THOUGHT → ACTION → OBSERVATION cycles
- Enables tool use and iterative problem-solving
- **Implemented in**: Modules 3, 5, 7, Final Project

**Example**:
```python
THOUGHT: Budget exceeded by $15. Need cheaper activities.
ACTION: {"tool_name": "get_activities", "args": {"max_price": 20}}
OBSERVATION: Found 3 activities under $20
THOUGHT: Replace expensive activity with cheaper one...
```

#### 3. **Feedback Loops**
- Automatic evaluation and improvement
- Self-correcting systems
- **Implemented in**: Modules 6, 8, Final Project

**Example**:
```python
for iteration in range(max_iterations):
    output = generate()
    results = evaluate(output)
    if results.success:
        break
    output = improve(output, results.failures)
```

### Production Skills

- ✅ **Robust JSON Extraction**: Handle various LLM response formats
- ✅ **Temperature Control**: Determinism for production (0.1-0.2)
- ✅ **Error Handling**: Retry logic, graceful degradation
- ✅ **Loop Detection**: Prevent infinite cycles in agents
- ✅ **Pydantic Validation**: Type-safe data structures
- ✅ **Evaluation-Driven Development**: Automated quality checks

---

## 📁 Module Breakdown

### 1. Generic Prompting
**Location**: `1-generic_prompting/`

**What You Learned**:
- LLM fundamentals (tokens, context windows, sampling)
- Model selection criteria (speed vs quality)
- Basic prompt structure (instruction, context, output format)
- Zero-shot vs few-shot prompting

**Key Files**:
- `introduction-to-prompting-for-llm-reasoning-and-planning.ipynb` - Fundamentals
- `model-selection.ipynb` - Choosing the right model

**Practical Takeaway**: Start with clear instructions, provide context, specify output format.

---

### 2. Role-Based Prompting
**Location**: `2-Role_base-Prompting/`

**What You Learned**:
- Defining expert personas ("You are a travel expert with 10 years experience...")
- Role-specific instructions and constraints
- How persona affects LLM behavior

**Key Files**:
- `lesson-1-role-based-prompting.ipynb`

**Practical Takeaway**: Well-defined roles improve response quality and consistency.

---

### 3. Chain-of-Thought & ReAct
**Location**: `3-cot_and_react/`

**What You Learned**:
- **CoT Part I**: Basic step-by-step reasoning
- **CoT Part II**: Complex multi-phase planning
- **ReAct**: Combining reasoning with tool use
- When to use each pattern

**Key Files**:
- `lesson-2-chain-of-thought-and-react-prompting-part-i.ipynb`
- `lesson-2-chain-of-thought-and-react-prompting-part-ii.ipynb`
- `lesson_2_lib.py` - Helper functions

**Practical Takeaway**: CoT for planning, ReAct for tool use, combine for complex agents.

**Code Example**:
```python
# CoT: Forces structured thinking
## Phase 1: Analyze Data
STEP 1.1 - Parse inputs
STEP 1.2 - Identify constraints

## Phase 2: Generate Solution
STEP 2.1 - Apply constraints
STEP 2.2 - Validate output

# ReAct: Tool use cycle
THOUGHT: Need to verify budget calculation
ACTION: call_calculator("25 + 30 + 50")
OBSERVATION: Result = 105
THOUGHT: Within budget of 130, proceed...
```

---

### 4. Prompt Instruction Refinement
**Location**: `4-prompt-instruction-refinement/`

**What You Learned**:
- Iterative prompt improvement
- A/B testing prompts
- Measuring prompt quality
- Common failure modes and fixes

**Key Files**:
- `lesson-3-prompt-instruction-refinement.ipynb`

**Practical Takeaway**: Prompts are code - version, test, and iterate them.

---

### 5. Chaining Prompts
**Location**: `5-chaining-prompts-for-agentic-reasoning/`

**What You Learned**:
- Multi-step workflows (Prompt 1 → output → Prompt 2 → output...)
- State management between prompts
- When to use chaining vs single complex prompt
- Error propagation handling

**Key Files**:
- `lesson-4-chaining-prompts-for-agentic-reasoning.ipynb`

**Practical Takeaway**: Break complex tasks into specialized prompts for better control and debugging.

**Pattern**:
```python
# Step 1: Extract data
data = llm_call(EXTRACTION_PROMPT, raw_input)

# Step 2: Analyze
analysis = llm_call(ANALYSIS_PROMPT, data)

# Step 3: Generate
output = llm_call(GENERATION_PROMPT, analysis)
```

---

### 6. Feedback Loops
**Location**: `6-implementing-llm-feedback-loops/`

**What You Learned**:
- Evaluation function design
- Automatic feedback generation
- Iterative improvement cycles
- When to stop iterating

**Key Files**:
- `lesson-5-implementing-llm-feedback-loops.ipynb`

**Practical Takeaway**: Evaluation + feedback enables self-correcting systems.

**Pattern**:
```python
def feedback_loop(task, test_cases, max_iterations=3):
    code = generate_initial(task)

    for i in range(max_iterations):
        results = run_tests(code, test_cases)

        if all_passed(results):
            return code  # Success

        feedback = format_failures(results)
        code = improve(code, feedback)

    return code  # Best effort
```

---

### 7. Advanced Chaining Practice
**Location**: `7-chaining_prompts/`

**What You Learned**:
- Real-world chaining applications
- LangGraph framework usage
- State persistence
- Complex workflow orchestration

**Key Files**:
- `lesson-4-chaining-prompts-for-agentic-reasoning.ipynb`
- `chaining-prompting.py` - Basic implementation
- `chaining-prompting_langgraph.py` - LangGraph version
- `practice_with_news.ipynb` - Applied practice
- `readme.md` - Module documentation

**Practical Takeaway**: LangGraph simplifies complex multi-agent workflows.

---

### 8. Feedback Loop Implementation
**Location**: `8-feedback_loop/`

**What You Learned**:
- Complete feedback loop implementation from scratch
- Test-Driven Development with LLMs
- Feedback prompt engineering
- Convergence criteria

**Key Files**:
- `lesson-5-implementing-llm-feedback-loops.ipynb` - ✅ **Completed**
- `README_EXPLICACION.md` - Comprehensive guide
- `INSTRUCCIONES_DE_USO.md` - Usage instructions
- `CAMBIOS_REALIZADOS.md` - Implementation details
- `RESUMEN_VISUAL.txt` - Visual summary

**Implemented**:
- ✅ Task description for `process_data()` function
- ✅ 12 comprehensive test cases
- ✅ Initial generation prompt
- ✅ Feedback-based improvement prompt
- ✅ Complete feedback loop with 3 iterations
- ✅ Success: All tests passing

**Practical Takeaway**: TDD + LLM feedback = reliable code generation.

---

## 🚀 Final Project: AgentsVille Trip Planner
**Location**: `project_agent/`

**🏆 Capstone Project**: Integrates ALL techniques learned in course

### What It Does

Generates personalized 3-day travel itineraries considering:
- 🌤️ Weather (avoid outdoor activities on rainy days)
- 💰 Budget (stay within limits)
- 🎯 Interests (match traveler preferences)
- 📅 Availability (only use real activities)

### Techniques Integrated

| Technique | Implementation | Cell |
|-----------|---------------|------|
| **Role-Based** | "Expert travel planner with 10+ years" | 14, 34 |
| **Chain-of-Thought** | 4-phase planning process | 14 |
| **ReAct** | THOUGHT → ACTION → OBSERVATION | 34 |
| **Structured Output** | Pydantic `TravelPlan` model | 13, 14 |
| **Tool Use** | calculator, get_activities, run_evals | 26-31 |
| **Feedback Loops** | Evaluation → improvement cycle | 18-36 |
| **Temperature Control** | 0.2 for planning, 0.1 for tool use | 14, 34 |
| **JSON Extraction** | Robust parsing of LLM responses | 14 |
| **Loop Detection** | Prevent infinite cycles | 34 |
| **Evaluation** | 7 automated quality checks | 18-23 |

### Architecture

```
User Input (VacationInfo)
    ↓
Data Gathering (Weather + Activities)
    ↓
ItineraryAgent (CoT Generation)
    ↓
Initial Plan
    ↓
Evaluations → Failures?
    ↓ YES         ↓ NO
RevisionAgent   Final Plan
(ReAct + Tools)     ↓
    ↓           Output
Improved Plan
    ↓
[Loop back to Evaluations]
```

### Key Implementation Highlights

**1. Chain-of-Thought Planning (Cell 14)**:
```python
## Phase 1: Data Analysis
STEP 1.1 - Parse Traveler Interests
STEP 1.2 - Weather Analysis
STEP 1.3 - Activity Inventory

## Phase 2: Budget Allocation
STEP 2.1 - Calculate Constraints
STEP 2.2 - Prioritization (P1-P4)

## Phase 3: Day-by-Day Planning
FOR EACH DAY:
  STEP 3.1 - Filter Activities
  STEP 3.2 - Select by Priority
  STEP 3.3 - Document Reasoning
```

**2. ReAct Agent (Cell 34)**:
```python
THOUGHT:
1. Current Status: Phase 2, Iteration 4/15, Failures: 2
2. Analysis: Budget exceeded by $15
3. Decision: Use get_activities_by_date_tool for cheaper options
4. Loop Detection: First call for this date

ACTION:
{"tool_name": "get_activities_by_date_tool",
 "arguments": {"date": "2025-06-11", "city": "AgentsVille"}}

[OBSERVATION: Returns list of activities]

THOUGHT:
1. Status: Iteration 5/15, Failures: 1
2. Analysis: Found 3 activities under $20
3. Decision: Replace expensive activity...
```

**3. Robust JSON Extraction** (Critical fix applied):
```python
# Handles multiple LLM response formats
if 'FINAL OUTPUT:' in response:
    json_text = response.split('FINAL OUTPUT:')[-1]

if '```json' in json_text:
    json_text = json_text.split('```json')[1].split('```')[0]

# Handle nested keys
parsed = json.loads(json_text)
if 'FINAL OUTPUT' in parsed:
    parsed = parsed['FINAL OUTPUT']
```

**4. Evaluation Framework**:
```python
ALL_EVAL_FUNCTIONS = [
    eval_start_end_dates_match,      # Dates valid
    eval_total_cost_is_accurate,     # Math correct
    eval_total_cost_is_within_budget, # Budget respected
    eval_itinerary_events_match_actual, # No hallucinations
    eval_itinerary_satisfies_interests, # Interests covered
    eval_activities_and_weather_compatible, # Weather suitable
    eval_traveler_feedback_incorporated, # Feedback followed
]
```

### Files

```
project_agent/
├── README.md               # Complete guide (updated)
├── project_starter.ipynb   # Main implementation ✅
├── project_lib.py          # Utility library
├── .env                    # API configuration
│
├── docs/                   # Documentation
│   ├── TECHNIQUES.md      # AI techniques explained
│   ├── PATTERNS.md        # Reusable patterns (coming)
│   ├── LEARNINGS.md       # Key insights (coming)
│   └── ARCHITECTURE.md    # System design (coming)
│
└── examples/               # Code templates (coming)
    ├── chain_of_thought.py
    ├── react_agent.py
    ├── json_extraction.py
    └── evaluation_framework.py
```

### Status

- ✅ All modules completed
- ✅ All Spanish comments translated to English
- ✅ All emojis removed (professional format)
- ✅ JSON extraction fix applied
- ✅ Tested and validated
- ✅ Production-ready

### Run It

```bash
cd project_agent
jupyter notebook project_starter.ipynb
# Execute all cells
```

**Expected Output**:
```
[OK] Initial Itinerary: 3 days, 6 activities, $105/$130 budget
[OK] Revised Itinerary: All evaluations passed
```

---

## 🔧 Additional Projects

### Claims Workflow
**Location**: `claims-workflow/`

**Purpose**: Practice agentic workflows with LangGraph

**Files**:
- `test_direct.py` - Direct LLM calls
- `test_workflow.py` - LangGraph implementation

---

## 📖 Documentation Philosophy

Each module includes:
1. **Notebooks**: Interactive learning with explanations
2. **Code**: Production-ready implementations
3. **README**: Module-specific documentation (where applicable)
4. **Examples**: Reusable patterns

---

## 🎓 Key Takeaways

### 1. Prompt Engineering is Software Engineering
- Version control your prompts
- Test prompts like code
- Iterate based on failure analysis
- Document what works and why

### 2. Temperature Matters
- 0.1-0.2 for structured tasks (production)
- 0.5-0.7 for creative tasks
- Always start low, increase if needed

### 3. Evaluation Enables Quality
- Define success criteria upfront
- Automate checks where possible
- Use LLMs for subjective evaluations
- Evaluation functions enable feedback loops

### 4. Break Down Complexity
- CoT for planning
- ReAct for tool use
- Chaining for multi-step workflows
- Combine all for production systems

### 5. Production Requires Robustness
- Retry logic (3+ attempts)
- Error handling (graceful degradation)
- Loop detection (prevent infinite cycles)
- JSON extraction (handle all formats)
- Observability (track metrics)

---

## 🚀 Next Steps

### Immediate

1. **Review Final Project**: See all techniques integrated
2. **Run Examples**: Test each pattern hands-on
3. **Read TECHNIQUES.md**: Deep dive into each technique

### Advanced

1. **Extend Project**: Add real APIs, multi-city support
2. **Build Own Agent**: Apply patterns to your domain
3. **Experiment**: Try different temperatures, prompts, models
4. **Contribute**: Improve patterns, add examples

---

## 📚 Resources

### Papers
- [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) - Wei et al. 2022
- [ReAct: Reasoning and Acting](https://arxiv.org/abs/2210.03629) - Yao et al. 2022
- [Toolformer](https://arxiv.org/abs/2302.04761) - Schick et al. 2023

### Frameworks
- [LangChain](https://python.langchain.com/)
- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [Pydantic](https://docs.pydantic.dev/)

### APIs
- [OpenAI API](https://platform.openai.com/docs)
- [Anthropic Claude](https://docs.anthropic.com/)

---

## 📝 Course Completion Checklist

- [x] Module 1: Generic Prompting
- [x] Module 2: Role-Based Prompting
- [x] Module 3: Chain-of-Thought & ReAct
- [x] Module 4: Prompt Refinement
- [x] Module 5: Prompt Chaining
- [x] Module 6: Feedback Loops (Theory)
- [x] Module 7: Advanced Chaining Practice
- [x] Module 8: Feedback Loop Implementation
- [x] **Final Project: AgentsVille (Production System)**

**Status**: ✅ **COURSE COMPLETE**

---

## 💡 Final Thoughts

This course teaches you to build production-ready AI agents by progressively mastering:

1. **Basic Prompting** → Clear instructions
2. **Role-Based** → Expert personas
3. **CoT** → Structured reasoning
4. **ReAct** → Tool use
5. **Chaining** → Multi-step workflows
6. **Feedback** → Self-correction
7. **Integration** → Production systems

The final project demonstrates that complex, reliable AI agents require combining ALL these techniques.

**Key Insight**: There's no single "best" prompting technique - production systems require the right combination for each component.

---

**Last Updated**: January 2026
**Status**: Production-Ready
**Next**: Apply to your own domain

---

Built with 🤖 OpenAI GPT-4.1, Pydantic, Python 3.10+
