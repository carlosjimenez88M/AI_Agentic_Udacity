# AgentsVille Trip Planner - Professional AI Agent System

> A production-ready AI travel planning system demonstrating advanced LLM reasoning techniques, chain-of-thought prompting, ReAct patterns, and feedback loops with MLOps best practices.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI API](https://img.shields.io/badge/OpenAI-API-green.svg)](https://platform.openai.com/)

---

## Table of Contents

- [Overview](#overview)
- [What You'll Learn](#what-youll-learn)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Core Concepts](#core-concepts)
- [Troubleshooting](#troubleshooting)

---

## Overview

This project implements an intelligent travel planning agent system that:
- Generates personalized day-by-day itineraries
- Considers weather, budget, interests, and activity availability
- Self-evaluates and iteratively improves plans using feedback loops
- Demonstrates production-ready prompt engineering

**Real-World Use**: Same architecture powers trip planning, code generation with tests, SQL optimization, automated debugging.

---

## What You'll Learn

| Technique | Use Case | Implemented In |
|-----------|----------|----------------|
| **Chain-of-Thought** | Complex planning tasks | Cell 14 |
| **ReAct Pattern** | Tool use & iteration | Cell 34 |
| **Structured Output** | Force valid JSON | Cell 14 |
| **Feedback Loops** | Auto-improvement | Cells 18-36 |
| **Temperature Control** | Determinism | 0.1-0.2 throughout |
| **JSON Extraction** | Robust parsing | Cell 14 |
| **Loop Detection** | Prevent infinite cycles | Cell 34 |

---

## Quick Start

### Installation
\`\`\`bash
pip install openai pydantic pandas python-dotenv json-repair numexpr
\`\`\`

### Setup
\`\`\`bash
# 1. Configure API
export OPENAI_API_KEY="your-key"

# 2. Run notebook
jupyter notebook project_starter.ipynb
\`\`\`

### Expected Output
\`\`\`
[OK] Initial Itinerary Generated
  Cost: $105 / $130 budget
  Days: 3 (June 10-12)
  Activities: 6 total (2 per day)

[OK] Revised Itinerary
  All evaluations passed
  Feedback incorporated
\`\`\`

---

## Project Structure

\`\`\`
project_agent/
├── README.md                  # This file
├── project_starter.ipynb      # Main implementation
├── project_lib.py             # Utility library
├── .env                       # API config
│
├── docs/                      # Extended docs
│   ├── TECHNIQUES.md         # AI techniques deep dive
│   ├── PATTERNS.md           # Reusable patterns
│   ├── LEARNINGS.md          # Key insights
│   └── ARCHITECTURE.md       # System design
│
└── examples/                  # Code templates
    ├── chain_of_thought.py   # CoT template
    ├── react_agent.py        # ReAct template
    ├── json_extraction.py    # Parsing utility
    └── evaluation_framework.py
\`\`\`

---

## Core Concepts

### 1. Chain-of-Thought (Cell 14)

**What**: Step-by-step reasoning before answer.

\`\`\`python
## Planning Process

### Phase 1: Data Analysis
STEP 1.1 - Parse Interests
STEP 1.2 - Weather Analysis
STEP 1.3 - Activity Inventory

### Phase 2: Budget Strategy
STEP 2.1 - Calculate Constraints
STEP 2.2 - Prioritization (P1-P4)

### Phase 3: Day-by-Day Planning
FOR EACH DAY:
  STEP 3.1 - Filter Activities
  STEP 3.2 - Select (priority-based)
  STEP 3.3 - Document Reasoning
\`\`\`

**Why**: Reduces hallucinations 40-60%, makes reasoning auditable.

---

### 2. ReAct Pattern (Cell 34)

**What**: THOUGHT → ACTION → OBSERVATION cycle.

\`\`\`python
THOUGHT:
1. Status: Phase 2, Iteration 4/15
2. Analysis: Budget exceeded by $15
3. Decision: Find cheaper activities
4. Loop Check: First call for this date

ACTION:
{"tool_name": "get_activities_by_date_tool", 
 "arguments": {"date": "2025-06-11"}}

[OBSERVATION: Returns activity list]

THOUGHT:
1. Status: Phase 3, Iteration 5/15
2. Analysis: Found 3 activities <$20
3. Decision: Replace expensive activity
...
\`\`\`

**Why**: Agent gathers info iteratively, self-corrects.

---

### 3. Robust JSON Extraction (Cell 14)

**Problem**: LLMs wrap JSON in markdown, commentary, extra keys.

**Solution**:
\`\`\`python
# Step 1: Extract from sections
if 'FINAL OUTPUT:' in response:
    json_text = response.split('FINAL OUTPUT:')[-1]

# Step 2: Remove markdown
if '\`\`\`json' in json_text:
    json_text = json_text.split('\`\`\`json')[1].split('\`\`\`')[0]

# Step 3: Handle wrapped JSON
parsed = json.loads(json_text)
if 'FINAL OUTPUT' in parsed:
    parsed = parsed['FINAL OUTPUT']
elif 'ANALYSIS' in parsed:
    parsed.pop('ANALYSIS')
\`\`\`

**Key**: Parse first, then extract nested data.

---

### 4. Evaluation-Driven Development (Cells 18-23)

**Pattern**: Define success as automated functions.

\`\`\`python
def eval_budget(vacation_info, plan):
    if plan.total_cost > vacation_info.budget:
        raise AgentError(f"Budget exceeded")

def eval_weather(vacation_info, plan):
    for day in plan.itinerary_days:
        if day.weather == "rain":
            for activity in day.activities:
                if "outdoor" in activity.description:
                    raise AgentError(f"Outdoor in rain")

results = run_all_evals(plan, [
    eval_budget,
    eval_weather,
    eval_dates,
    eval_interests,
])
\`\`\`

**Benefits**: Objective measurement, enables feedback loops.

---

## Implementation Guide

| Cell | Component | What It Does |
|------|-----------|--------------|
| 8 | VacationInfo | Input validation with Pydantic |
| 10 | Weather Data | Fetch climate for dates |
| 11 | Activities | Fetch available activities |
| 14 | ItineraryAgent | Generate initial plan (CoT) |
| 22 | Weather Eval | LLM-based compatibility check |
| 27 | Activity Tool | Tool for agent data access |
| 34 | RevisionAgent | Iterative improvement (ReAct) |

### Critical: ItineraryAgent (Cell 14)

\`\`\`python
class ItineraryAgent(ChatAgent):
    def get_itinerary(self, vacation_info):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Generate (low temp for determinism)
                response = self.chat(
                    vacation_info.model_dump_json(),
                    temperature=0.2
                )

                # Extract JSON (robust)
                json_text = extract_json_robust(response)

                # Validate (Pydantic)
                plan = TravelPlan.model_validate_json(json_text)

                return plan
            except:
                if attempt == max_retries - 1:
                    raise
\`\`\`

**Components**:
1. Retry logic (3 attempts)
2. Low temperature (0.2)
3. Robust parsing
4. Schema validation

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| JSON errors | Use robust extraction (Cell 14) |
| Budget violations | Add SMART criteria, use calculator |
| Infinite loops | Implement loop detection (Cell 34) |
| Hallucinations | List available items, lower temp |

---

## Learn More

### Documentation
- [AI Techniques Deep Dive](docs/TECHNIQUES.md)
- [Design Patterns](docs/PATTERNS.md)
- [Key Learnings](docs/LEARNINGS.md)
- [Architecture](docs/ARCHITECTURE.md)

### Examples
- [Chain-of-Thought Template](examples/chain_of_thought.py)
- [ReAct Template](examples/react_agent.py)
- [JSON Extraction](examples/json_extraction.py)
- [Evaluation Framework](examples/evaluation_framework.py)

### Papers
- [Chain-of-Thought](https://arxiv.org/abs/2201.11903) - Wei et al. 2022
- [ReAct](https://arxiv.org/abs/2210.03629) - Yao et al. 2022
- [Toolformer](https://arxiv.org/abs/2302.04761) - Schick et al. 2023

---

**Built with**: OpenAI GPT-4.1, Pydantic, Python 3.10+

**Status**: Production-Ready
