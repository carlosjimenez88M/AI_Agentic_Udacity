# agentic_workflow.py

# EDUCATIONAL NOTE: This workflow orchestrates multiple specialized AI agents to transform
# product specifications into structured project management artifacts (user stories, features, tasks).
# The agents work in a coordinated pipeline, with each agent contributing its specialized expertise.

# Import the specialized agent classes we implemented in Phase 1
# Each agent serves a specific purpose in the workflow:
# - ActionPlanningAgent: Decomposes high-level goals into workflow steps
# - KnowledgeAugmentedPromptAgent: Generates grounded responses using domain knowledge
# - EvaluationAgent: Validates and refines outputs through iterative feedback
# - RoutingAgent: Semantically routes queries to appropriate specialized teams
import sys
import os
from pathlib import Path

# Add the phase_1 directory to the Python path to enable imports
# This allows us to import the agent classes from the workflow_agents module
phase_1_path = Path(__file__).parent.parent / 'phase_1'
sys.path.insert(0, str(phase_1_path))

from workflow_agents.base_agents import (
    ActionPlanningAgent,
    KnowledgeAugmentedPromptAgent,
    EvaluationAgent,
    RoutingAgent
)

from dotenv import load_dotenv

# SECURE CREDENTIAL MANAGEMENT: Load API key from environment variables
# BEST PRACTICE: Never hard-code API keys in source code. Use .env files for local development
# and proper secrets management in production environments.
# WHY THIS MATTERS: Prevents accidental exposure of credentials in version control systems.
# Load .env from the parent starter directory
dotenv_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=dotenv_path)
openai_api_key = os.getenv("OPENAI_API_KEY")

# Validate that the API key was successfully loaded
if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY not found in environment variables. "
        "Please check that your .env file exists and contains the API key."
    )
print("✓ OpenAI API key loaded successfully")

# DOMAIN KNOWLEDGE INJECTION: Load the product specification document
# This document contains the Email Router product requirements and will be used to
# ground all agent responses, ensuring they are specific to this product rather than generic.
# WHY THIS WORKS: By providing detailed domain knowledge, we enable agents to generate
# contextually accurate and product-specific outputs (user stories, features, tasks).
try:
    with open("Product-Spec-Email-Router.txt", "r", encoding="utf-8") as f:
        product_spec = f.read()
    print(f"✓ Product specification loaded ({len(product_spec)} characters)")
except FileNotFoundError:
    raise FileNotFoundError(
        "Product-Spec-Email-Router.txt not found. "
        "Please ensure the file exists in the current directory."
    )

# Instantiate all the agents

# ═══════════════════════════════════════════════════════════════════════════════
# ACTION PLANNING AGENT
# ═══════════════════════════════════════════════════════════════════════════════
# ROLE: Workflow orchestrator that decomposes high-level goals into sequential steps
# WHY THIS MATTERS: This agent analyzes the user's request and determines which specialized
# teams (Product Manager, Program Manager, Development Engineer) need to be involved and
# in what order. It uses knowledge about the project management hierarchy to plan the workflow.

knowledge_action_planning = """You need to break down product development workflows into clear, sequential steps.

IMPORTANT: When you see a request for a "development plan" or similar comprehensive request, create SIMPLE, DIRECT steps. Don't over-decompose!

For a complete development plan with stories, features, and tasks:
Step 1: Generate user stories from the product specification
Step 2: Organize user stories into product features
Step 3: Create development tasks from the features and stories

That's it - just 3 steps! Each step is handled by a specialized team.

WORKFLOW HIERARCHY:
- Stories: Defined from product spec (persona + action + benefit). Written as "As a [persona], I want [action] so that [benefit]"
- Features: Groups of related user stories that form cohesive product capabilities
- Tasks: Engineering work items derived from features/stories with technical details

Keep it simple - let each specialized team do their comprehensive work."""

# Instantiate the action planning agent with knowledge about the PM workflow hierarchy
action_planning_agent = ActionPlanningAgent(
    openai_api_key=openai_api_key,
    knowledge=knowledge_action_planning
)
print("✓ Action Planning Agent initialized")

# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT MANAGER TEAM
# ═══════════════════════════════════════════════════════════════════════════════
# ROLE: Generates user stories from product specifications
# WHY THIS MATTERS: User stories are the foundation of agile development. They capture
# who needs what functionality and why, written from the end-user's perspective.
# PATTERN: Knowledge Agent (generates) → Evaluation Agent (validates & refines)

persona_product_manager = "You are a Product Manager, you are responsible for defining the user stories for a product."

# KNOWLEDGE INJECTION WITH RICH COT PROMPTING
# This combines structural patterns with domain knowledge for human-like, thoughtful generation
knowledge_product_manager = f"""You are a Product Manager. Your task is to generate EXACTLY 5-8 user stories for the Email Router product.

OUTPUT FORMAT - Copy this structure EXACTLY for each story:
1. As a [Persona], I want [capability] so that [benefit]
2. As a [Persona], I want [capability] so that [benefit]
... (continue for 5-8 stories total)

EXAMPLE OUTPUT (DO NOT USE THESE - they are just examples of format):
1. As a Customer Support Manager, I want to automatically categorize incoming emails so that my team can prioritize urgent requests
2. As a Technical Support Agent, I want AI-generated response suggestions so that I can respond faster to common questions
3. As an IT Administrator, I want to monitor system performance metrics so that I can ensure reliable email processing

YOUR TURN - Generate 5-8 stories for Email Router product below. Use the EXACT format above. DO NOT write explanations, feedback, or commentary. ONLY write the numbered list of user stories.

PRODUCT SPECIFICATION:
{product_spec}

Generate your 5-8 user stories now (use the numbered list format shown above):"""

# Instantiate the knowledge-augmented agent for generating user stories
product_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager,
    knowledge=knowledge_product_manager
)
print("✓ Product Manager Knowledge Agent initialized")

# Product Manager - Evaluation Agent
# EVALUATOR-OPTIMIZER PATTERN: This agent validates that generated user stories meet quality standards
# It creates a feedback loop: generate → evaluate → refine → repeat until criteria met
# WHY THIS WORKS: Iterative refinement dramatically improves output quality and consistency

persona_product_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."

evaluation_criteria_pm = """STEP 1: Count how many numbered lines start with "As a" in the response. Write down this number.

STEP 2: Decision tree - follow EXACTLY:
- Is the number 5? → Say "Yes, all criteria met."
- Is the number 6? → Say "Yes, all criteria met."
- Is the number 7? → Say "Yes, all criteria met."
- Is the number 8? → Say "Yes, all criteria met."
- Is the number less than 5? → Say "No - found X stories, need 5-8."
- Is the number more than 8? → Say "No - found X stories, need 5-8."

That's it. Just count and follow the decision tree above."""

# Instantiate the evaluation agent that will validate and refine user stories
product_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_product_manager_eval,
    evaluation_criteria=evaluation_criteria_pm,
    worker_agent=product_manager_knowledge_agent,  # The agent being evaluated
    max_interactions=3  # Allow up to 3 refinement iterations
)
print("✓ Product Manager Evaluation Agent initialized")

# ═══════════════════════════════════════════════════════════════════════════════
# PROGRAM MANAGER TEAM
# ═══════════════════════════════════════════════════════════════════════════════
# ROLE: Organizes user stories into cohesive product features
# WHY THIS MATTERS: Features group related stories into logical capabilities, providing
# a higher-level view of the product that bridges user needs and technical implementation.
# PATTERN: Knowledge Agent (generates) → Evaluation Agent (validates & refines)

persona_program_manager = "You are a Program Manager, you are responsible for defining the features for a product."

knowledge_program_manager = """You're working as a Program Manager, taking user stories and organizing them into cohesive product features. Let's think through this systematically.

WHAT ARE PRODUCT FEATURES?
Features are the major capabilities or functionalities of a product. They're bigger than individual user stories but more specific than the product itself. Think of features as the "building blocks" that users interact with.

YOUR THINKING PROCESS (Chain of Thought):
1. ANALYZE THE STORIES: Read through all the user stories you receive. What patterns do you see? Which stories are related to each other?
2. IDENTIFY THEMES: Group similar stories together. For example, stories about email handling might form one feature, while stories about reporting might form another.
3. NAME THE FEATURE: Give each group a clear, memorable name that describes what it does (e.g., "Email Classification Engine" or "Performance Dashboard")
4. DESCRIBE THE PURPOSE: Explain what this feature accomplishes and why it exists. What problem does it solve?
5. LIST KEY FUNCTIONALITY: Break down the specific things this feature can do. Be concrete - what actions can users take?
6. ARTICULATE USER BENEFIT: Explain the real-world value. How does this feature make users' lives better or easier?

STRUCTURE FOR EACH FEATURE:
Feature Name: [Clear, descriptive title that sounds professional]
Description: [2-3 sentences explaining what this feature is and its purpose]
Key Functionality: [Bullet list of 3-5 specific capabilities this feature provides]
User Benefit: [1-2 sentences explaining the tangible value users get]

IMPORTANT REMINDERS:
- A feature should combine 2-4 related user stories (not just one, not too many)
- Think about what naturally belongs together from a user's perspective
- Features should feel like distinct areas of functionality
- Aim for 3-5 well-defined features total

Now, carefully analyze the user stories below and organize them into cohesive product features:"""

# Instantiate the knowledge-augmented agent for generating product features
program_manager_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager,
    knowledge=knowledge_program_manager
)
print("✓ Program Manager Knowledge Agent initialized")

# Program Manager - Evaluation Agent
# QUALITY ASSURANCE: Validates that features have proper structure and completeness
persona_program_manager_eval = "You are an evaluation agent that checks the answers of other worker agents."

evaluation_criteria_pgm = """Check if the response contains 3-5 properly structured product features.

REQUIRED: Each feature MUST have ALL 4 components:
1. Feature Name (clear, professional title)
2. Description (2-3 sentences explaining purpose)
3. Key Functionality (3-5 specific capabilities)
4. User Benefit (tangible value to users)

Quick check:
✓ Are there 3-5 features? (count them)
✓ Does each feature have all 4 components with clear labels?
✓ Are features specific to the Email Router product?

RESPONSE FORMAT:
- If you find 3-5 properly formatted features with all 4 components, respond: "Yes, all criteria met."
- If there are too few/many features, respond: "No - found X features, need 3-5."
- If features are missing components, respond: "No - features are missing required components (specify which)."

Be concise."""

# Instantiate the evaluation agent that will validate and refine product features
program_manager_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_program_manager_eval,
    evaluation_criteria=evaluation_criteria_pgm,
    worker_agent=program_manager_knowledge_agent,  # The agent being evaluated
    max_interactions=3  # Allow up to 3 refinement iterations
)
print("✓ Program Manager Evaluation Agent initialized")

# ═══════════════════════════════════════════════════════════════════════════════
# DEVELOPMENT ENGINEER TEAM
# ═══════════════════════════════════════════════════════════════════════════════
# ROLE: Breaks down features into sprint-ready, implementable engineering tasks
# WHY THIS MATTERS: Tasks are the atomic units of work in agile development. They must be
# specific, measurable, and actionable for developers to estimate and implement.
# PATTERN: Knowledge Agent (generates) → Evaluation Agent (validates & refines)

persona_dev_engineer = "You are a Development Engineer, you are responsible for defining the development tasks for a product."

knowledge_dev_engineer = """You're a Development Engineer breaking down product features into concrete, actionable development tasks. This is where we turn vision into implementable work. Let's think through this carefully and systematically.

WHAT ARE DEVELOPMENT TASKS?
Development tasks are the actual pieces of work that engineers will implement. They're specific, technical, and actionable. Each task should be something a developer can pick up, understand immediately, and complete within a reasonable timeframe (typically a few days).

YOUR THINKING PROCESS (Chain of Thought):
1. UNDERSTAND THE FEATURES: Read through the product features carefully. What needs to be built? What technical components are required?

2. BREAK DOWN THE WORK: For each feature, think about the technical layers:
   - Backend work (APIs, databases, business logic)
   - Frontend work (user interfaces, interactions)
   - Integration work (connecting components, third-party services)
   - Infrastructure work (deployment, monitoring, security)

3. IDENTIFY DEPENDENCIES: What needs to be built first? For example, you can't build the UI before the API exists.

4. DEFINE ACCEPTANCE CRITERIA: How will we know this task is truly "done"? Be specific and testable.

5. ESTIMATE EFFORT: Based on complexity, how long will this realistically take? Be honest.

STRUCTURE FOR EACH TASK (THIS IS MANDATORY):

Task ID: [Use format TASK-001, TASK-002, etc.]
Task Title: [Clear, action-oriented title like "Implement Email Ingestion API" or "Build User Dashboard UI"]
Related User Story: [Which user story(ies) does this support? Reference them specifically]
Description: [2-4 sentences explaining the technical work required. What exactly needs to be built? What technologies or approaches should be used?]
Acceptance Criteria:
  - [Specific, testable criterion 1]
  - [Specific, testable criterion 2]
  - [Specific, testable criterion 3]
  [Include 3-5 clear criteria that define "done"]
Estimated Effort: [Be realistic: e.g., "2-3 days", "1 week", or "Medium complexity - 3 days"]
Dependencies: [List task IDs that must be completed first, or write "None" if this can start immediately]

EXAMPLE OF A WELL-WRITTEN TASK:

Task ID: TASK-001
Task Title: Implement Email SMTP Integration Service
Related User Story: As a support representative, I want incoming emails automatically captured so that I don't miss any customer inquiries
Description: Build a backend service that connects to the organization's SMTP server and retrieves incoming emails in real-time. The service should poll for new messages every 30 seconds, extract email metadata (sender, recipient, subject, timestamp), and store the full email content in the database. Use Python with the imaplib library for SMTP connection.
Acceptance Criteria:
  - Service successfully connects to SMTP server using configurable credentials
  - New emails are detected and retrieved within 30 seconds of arrival
  - Email metadata is extracted correctly and stored in database
  - Service includes error handling for connection failures and reconnects automatically
  - Unit tests cover main functionality with >80% code coverage
Estimated Effort: 3-4 days
Dependencies: None (foundational task)

IMPORTANT GUIDELINES:
- Generate 8-12 comprehensive tasks that cover the full implementation
- Include a mix of backend, frontend, and infrastructure tasks
- Make sure tasks are specific and actionable, not vague (bad: "Build system", good: "Implement email parsing module")
- Each task should take no more than 3-5 days (if bigger, break it down further)
- Think about the logical order - what needs to happen first?
- Consider non-functional requirements like security, performance, and monitoring

Now, analyze the features below and create detailed, implementable development tasks:"""

# Instantiate the knowledge-augmented agent for generating development tasks
development_engineer_knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer,
    knowledge=knowledge_dev_engineer
)
print("✓ Development Engineer Knowledge Agent initialized")

# Development Engineer - Evaluation Agent
# COMPREHENSIVE VALIDATION: Ensures tasks have all required fields for sprint planning
persona_dev_engineer_eval = "You are an evaluation agent that checks the answers of other worker agents."

evaluation_criteria_dev = """Check if the response contains 8-12 properly structured development tasks.

REQUIRED: Each task MUST have ALL 7 components:
1. Task ID (TASK-001, TASK-002, etc.)
2. Task Title (action-oriented)
3. Related User Story (which story it implements)
4. Description (2-4 sentences, technical details)
5. Acceptance Criteria (3-5 specific, testable items)
6. Estimated Effort (realistic time like "3 days")
7. Dependencies (Task IDs or "None")

Quick check:
✓ Are there 8-12 tasks? (count them)
✓ Does each task have all 7 components with clear labels?
✓ Are Task IDs formatted as TASK-001, TASK-002, etc.?
✓ Are tasks specific to the Email Router product (not generic)?

RESPONSE FORMAT:
- If you find 8-12 properly formatted tasks with all 7 components, respond: "Yes, all criteria met."
- If there are fewer than 8 tasks, respond: "No - only X tasks provided, need 8-12."
- If tasks are missing components, respond: "No - tasks are missing required components (specify which)."

Be concise and specific."""

# Instantiate the evaluation agent that will validate and refine development tasks
development_engineer_evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_dev_engineer_eval,
    evaluation_criteria=evaluation_criteria_dev,
    worker_agent=development_engineer_knowledge_agent,  # The agent being evaluated
    max_interactions=3  # Allow up to 3 refinement iterations
)
print("✓ Development Engineer Evaluation Agent initialized")


# ═══════════════════════════════════════════════════════════════════════════════
# TEAM SUPPORT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════
# These functions implement the "generate-and-refine" pattern for each specialized team.
# PATTERN: Each function chains together:
#   1. Knowledge Agent → generates initial response
#   2. Evaluation Agent → validates and iteratively refines
#   3. Return final validated output
# WHY THIS MATTERS: This decouples routing logic from evaluation logic, creating clean
# separation of concerns and making the system more maintainable and testable.

def product_manager_support_function(query):
    """
    Product Manager team support function.
    Generates and validates user stories from product specifications.

    WORKFLOW:
    1. Evaluation agent receives the enriched query
    2. It calls the knowledge agent to generate user stories
    3. It validates the stories against format criteria
    4. It iteratively refines until quality standards are met
    5. Returns final validated user stories

    Parameters:
    query (str): The request for user stories

    Returns:
    str: Validated, properly formatted user stories
    """
    print("\n" + "="*80)
    print("PRODUCT MANAGER TEAM ACTIVATED")
    print("="*80)
    print(f"Query: {query}\n")

    print("[Step 1/2] Generating user stories from product specification...")

    # Pass query directly - the knowledge base already has comprehensive instructions
    result = product_manager_evaluation_agent.evaluate(query)

    print(f"[Step 2/2] Validation complete after {result['iterations']} iteration(s)")
    print("="*80 + "\n")

    return result['final_response']


def program_manager_support_function(query):
    """
    Program Manager team support function.
    Organizes user stories into cohesive product features.

    WORKFLOW:
    1. Evaluation agent receives the enriched query
    2. It calls the knowledge agent to organize stories into features
    3. It validates features against structural criteria
    4. It iteratively refines until quality standards are met
    5. Returns final validated features

    Parameters:
    query (str): The request for features (typically includes user stories as context)

    Returns:
    str: Validated, properly structured product features
    """
    print("\n" + "="*80)
    print("PROGRAM MANAGER TEAM ACTIVATED")
    print("="*80)
    print(f"Query: {query}\n")

    print("[Step 1/2] Organizing user stories into product features...")

    # Pass query directly - the knowledge base already has comprehensive instructions
    result = program_manager_evaluation_agent.evaluate(query)

    print(f"[Step 2/2] Validation complete after {result['iterations']} iteration(s)")
    print("="*80 + "\n")

    return result['final_response']


def development_engineer_support_function(query):
    """
    Development Engineer team support function.
    Breaks down features into sprint-ready development tasks.

    WORKFLOW:
    1. Evaluation agent receives the enriched query
    2. It calls the knowledge agent to create development tasks
    3. It validates tasks against comprehensive criteria (7 required fields)
    4. It iteratively refines until quality standards are met
    5. Returns final validated tasks

    Parameters:
    query (str): The request for tasks (typically includes features/stories as context)

    Returns:
    str: Validated, comprehensive development tasks ready for sprint planning
    """
    print("\n" + "="*80)
    print("DEVELOPMENT ENGINEER TEAM ACTIVATED")
    print("="*80)
    print(f"Query: {query}\n")

    print("[Step 1/2] Breaking down features into development tasks...")

    # Pass query directly - the knowledge base already has comprehensive instructions
    result = development_engineer_evaluation_agent.evaluate(query)

    print(f"[Step 2/2] Validation complete after {result['iterations']} iteration(s)")
    print("="*80 + "\n")

    return result['final_response']


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTING AGENT
# ═══════════════════════════════════════════════════════════════════════════════
# ROLE: Semantic dispatcher that routes queries to appropriate specialized teams
# WHY THIS WORKS: Uses embedding-based semantic similarity to understand query meaning
# and match it to the team best equipped to handle it.
# SUPERIORITY OVER KEYWORDS: Handles synonyms, paraphrasing, and context naturally.
# For example, "define user requirements" would route to Product Manager despite not
# containing the exact words "user stories."

# Configure the routing agent with descriptions of each specialized team
# IMPORTANT: Descriptions should be semantically rich and accurately describe each team's
# expertise and responsibilities. The routing agent will use these descriptions to
# calculate similarity scores with incoming queries.
routing_agent = RoutingAgent(
    openai_api_key=openai_api_key,
    agents=[
        {
            "name": "Product Manager",
            "description": (
                "Responsible for defining product personas and user stories only. "
                "Does not define features or tasks. Does not group stories. "
                "Specializes in user-centric requirements and writing stories in the format: "
                "'As a [persona], I want [action] so that [benefit]'."
            ),
            "func": lambda x: product_manager_support_function(x)
        },
        {
            "name": "Program Manager",
            "description": (
                "Responsible for defining product features by organizing similar user stories "
                "into cohesive groups. Does not create tasks. Specializes in feature definition, "
                "feature documentation, and grouping related stories into features."
            ),
            "func": lambda x: program_manager_support_function(x)
        },
        {
            "name": "Development Engineer",
            "description": (
                "Responsible for defining development tasks from features and user stories. "
                "Specializes in technical implementation planning, writing acceptance criteria, "
                "estimating effort, and identifying task dependencies."
            ),
            "func": lambda x: development_engineer_support_function(x)
        }
    ]
)
print("✓ Routing Agent initialized with 3 specialized teams")


# ═══════════════════════════════════════════════════════════════════════════════
# WORKFLOW EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════
# Run the workflow

print("\n*** Workflow execution started ***\n")
# Workflow Prompt
# ****
# IMPORTANT: This prompt should trigger the workflow to generate Stories → Features → Tasks
workflow_prompt = "Create a complete development plan for this product, including user stories, product features, and development tasks."
# ****
print(f"Task to complete in this workflow, workflow prompt = {workflow_prompt}")

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1: WORKFLOW PLANNING
# ═══════════════════════════════════════════════════════════════════════════════
# The Action Planning Agent analyzes the high-level workflow prompt and decomposes it
# into sequential executable steps using its knowledge of the project management hierarchy.
# WHY THIS MATTERS: Automated workflow decomposition allows the system to handle complex
# multi-step requests without manual intervention or hard-coded workflows.

print("\n" + "="*80)
print("PHASE 1: WORKFLOW PLANNING")
print("="*80)
print(f"\n[Action Planning Agent] Analyzing workflow prompt...")
print(f"Prompt: '{workflow_prompt}'")

# Extract workflow steps using the action planning agent
workflow_steps = action_planning_agent.extract_steps_from_prompt(workflow_prompt)

print(f"\n✓ Workflow decomposed into {len(workflow_steps)} steps:")
for i, step in enumerate(workflow_steps, 1):
    print(f"   {i}. {step}")

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 & 3: STEP EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════
# For each step identified by the planner:
#   1. Routing Agent analyzes the step using semantic similarity
#   2. Dispatches to the best-matched specialized team
#   3. Team's knowledge agent generates initial response
#   4. Team's evaluation agent validates and refines iteratively
#   5. Final validated result is stored
# WHY THIS ARCHITECTURE WORKS: Separation of concerns (planning, routing, generation,
# validation) creates a modular, maintainable system where each component has a single
# clear responsibility.

print("\n\n" + "="*80)
print("PHASE 2 & 3: WORKFLOW EXECUTION")
print("="*80)

# Initialize storage for completed step results
completed_steps = []

# Execute each workflow step sequentially
for step_num, step in enumerate(workflow_steps, 1):
    print(f"\n{'='*80}")
    print(f"EXECUTING STEP {step_num}/{len(workflow_steps)}")
    print(f"{'='*80}")
    print(f"Step: {step}\n")

    # The Routing Agent uses semantic similarity to dispatch to the appropriate team
    # Each team's support function handles generation and validation internally
    print(f"[Routing Agent] Calculating semantic similarities...")
    result = routing_agent.route(step)

    # Store the completed step with metadata
    completed_steps.append({
        "step_number": step_num,
        "step_description": step,
        "result": result
    })

    print(f"\n✓ Step {step_num} completed successfully")

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4: RESULT AGGREGATION AND DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════
# The workflow prompt asked for "development tasks", which is the final output
# in the project management hierarchy (Stories → Features → Tasks).
# We display all completed steps for transparency, then highlight the final output.

print("\n\n" + "="*80)
print("WORKFLOW EXECUTION COMPLETE")
print("="*80)

print(f"\n✓ All {len(completed_steps)} steps executed successfully")
print(f"✓ Workflow objective achieved: {workflow_prompt}\n")

# The final step's result contains the ultimate deliverable (development tasks)
print("\n" + "="*80)
print("FINAL OUTPUT: DEVELOPMENT TASKS FOR EMAIL ROUTER PRODUCT")
print("="*80 + "\n")

final_output = completed_steps[-1]["result"]
print(final_output)

print("\n" + "="*80)
print("END OF WORKFLOW")
print("="*80)