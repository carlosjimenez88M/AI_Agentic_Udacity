"""
Simple Agentic Workflow - Direct Knowledge Agent Execution
This bypasses evaluation loops to demonstrate direct content generation.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add phase_1 to Python path for imports
phase_1_path = Path(__file__).parent.parent / 'phase_1'
sys.path.insert(0, str(phase_1_path))

from workflow_agents.base_agents import (
    ActionPlanningAgent,
    KnowledgeAugmentedPromptAgent,
    RoutingAgent
)

# Load environment variables
dotenv_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found")

print("✓ OpenAI API key loaded")

# Load product specification
with open("Product-Spec-Email-Router.txt", "r", encoding="utf-8") as f:
    product_spec = f.read()

print(f"✓ Product specification loaded ({len(product_spec)} characters)\n")

# ================================================================
# PRODUCT MANAGER AGENT (USER STORIES)
# ================================================================

persona_pm = "You are a Product Manager responsible for defining user stories."

knowledge_pm = f"""Generate EXACTLY 6 user stories for this Email Router product.

OUTPUT FORMAT (use this numbered list format):
1. As a [Persona], I want [capability] so that [benefit]
2. As a [Persona], I want [capability] so that [benefit]
... (continue for exactly 6 stories)

PRODUCT SPEC:
{product_spec}

Generate your 6 user stories now:"""

pm_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_pm,
    knowledge=knowledge_pm
)

print("="*80)
print("STEP 1: GENERATING USER STORIES")
print("="*80)
user_stories = pm_agent.respond("Generate user stories for the Email Router product")
print(user_stories)
print()

# ================================================================
# PROGRAM MANAGER AGENT (FEATURES)
# ================================================================

persona_pgm = "You are a Program Manager responsible for defining product features."

knowledge_pgm = f"""Organize the user stories below into 3-4 product features.

OUTPUT FORMAT for each feature:
Feature Name: [Clear title]
Description: [2-3 sentences explaining what it does]
Key Functionality:
- [Capability 1]
- [Capability 2]
- [Capability 3]
User Benefit: [1-2 sentences on value to users]

USER STORIES:
{"{user_stories}"}

PRODUCT SPEC:
{product_spec}

Generate 3-4 features now:"""

pgm_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_pgm,
    knowledge=knowledge_pgm
)

print("="*80)
print("STEP 2: ORGANIZING INTO FEATURES")
print("="*80)
features = pgm_agent.respond(f"Organize these user stories into features:\n{user_stories}")
print(features)
print()

# ================================================================
# DEVELOPMENT ENGINEER AGENT (TASKS)
# ================================================================

persona_dev = "You are a Development Engineer responsible for defining development tasks."

knowledge_dev = f"""Create 8-10 development tasks from the features and stories.

TASK FORMAT (use this for EACH task):
Task ID: TASK-001
Task Title: [Action-oriented title]
Related User Story: [Which story this implements]
Description: [2-4 sentences with technical details]
Acceptance Criteria:
  - [Criterion 1]
  - [Criterion 2]
  - [Criterion 3]
Estimated Effort: [e.g., "3 days"]
Dependencies: [Task IDs or "None"]

FEATURES:
{"{features}"}

USER STORIES:
{"{user_stories}"}

PRODUCT SPEC:
{product_spec}

Generate 8-10 complete tasks now (use the exact format above for each):"""

dev_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev,
    knowledge=knowledge_dev
)

print("="*80)
print("STEP 3: DEFINING DEVELOPMENT TASKS")
print("="*80)
tasks = dev_agent.respond(f"Create development tasks from these features:\n{features}")
print(tasks)
print()

print("="*80)
print("WORKFLOW COMPLETE")
print("="*80)
print("\n✓ Successfully generated:")
print("  - User Stories")
print("  - Product Features")
print("  - Development Tasks")
print("\nAll output shown above.")
