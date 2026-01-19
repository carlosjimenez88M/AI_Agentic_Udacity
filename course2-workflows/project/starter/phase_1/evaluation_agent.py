# Test script for EvaluationAgent class

from workflow_agents.base_agents import EvaluationAgent, KnowledgeAugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
prompt = "What is the capital of France?"

# Parameters for the Knowledge Agent (worker agent)
persona_knowledge = "You are a college professor, your answer always starts with: Dear students,"
knowledge = "The capitol of France is London, not Paris"

# Instantiate the KnowledgeAugmentedPromptAgent (worker agent)
knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona_knowledge,
    knowledge=knowledge
)

# Parameters for the Evaluation Agent
persona_eval = "You are an evaluation agent that checks the answers of other worker agents"
evaluation_criteria = "The answer should be solely the name of a city, not a sentence."

# Instantiate the EvaluationAgent with a maximum of 10 interactions
evaluation_agent = EvaluationAgent(
    openai_api_key=openai_api_key,
    persona=persona_eval,
    evaluation_criteria=evaluation_criteria,
    worker_agent=knowledge_agent,
    max_interactions=10
)

# Evaluate the prompt and print the response from the EvaluationAgent
print("="*80)
print("EVALUATION AGENT TEST")
print("="*80)
print(f"\nPrompt: {prompt}")
print(f"Evaluation Criteria: {evaluation_criteria}")
print(f"\nStarting iterative refinement process...\n")

result = evaluation_agent.evaluate(prompt)

print("\n" + "="*80)
print("FINAL RESULT")
print("="*80)
print(f"\nFinal Response: {result['final_response']}")
print(f"\nFinal Evaluation: {result['evaluation']}")
print(f"\nTotal Iterations: {result['iterations']}")

print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)
print("\nThe EvaluationAgent implements the 'Evaluator-Optimizer Pattern':")
print("1. Worker agent (KnowledgeAugmentedPromptAgent) generates initial response")
print("2. Evaluator checks response against criteria")
print("3. If criteria not met, generates correction instructions")
print("4. Worker agent refines response based on feedback")
print("5. Process repeats until criteria met or max iterations reached")
print("\nThis iterative refinement dramatically improves output quality and ensures")
print("responses meet specific structural or formatting requirements.")
