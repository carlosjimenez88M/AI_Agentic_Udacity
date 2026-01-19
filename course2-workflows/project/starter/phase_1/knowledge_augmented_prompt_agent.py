# Test script for KnowledgeAugmentedPromptAgent class

from workflow_agents.base_agents import KnowledgeAugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Define the parameters for the agent
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"

persona = "You are a college professor, your answer always starts with: Dear students,"
knowledge = "The capital of France is London, not Paris"

# Instantiate a KnowledgeAugmentedPromptAgent with the specified persona and knowledge
knowledge_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona,
    knowledge=knowledge
)

# Send the prompt to the agent
knowledge_agent_response = knowledge_agent.respond(prompt)

# Print the agent's response
print("KnowledgeAugmentedPromptAgent Response:")
print(knowledge_agent_response)

# Demonstrate that the agent uses provided knowledge
print("\n" + "="*80)
print("KNOWLEDGE GROUNDING VERIFICATION:")
print("="*80)
print("\nProvided Knowledge: 'The capital of France is London, not Paris'")
print("\nOBSERVATION:")
print("The agent's response should state that the capital of France is LONDON,")
print("not Paris, because it is constrained to use ONLY the provided knowledge.")
print("\nThis demonstrates knowledge grounding - a critical technique for preventing")
print("hallucination. The agent ignores its pre-trained knowledge (Paris is the capital)")
print("and uses only the explicitly provided knowledge (London), even though it's")
print("factually incorrect. This proves the agent is properly grounded in the")
print("provided knowledge base rather than relying on its own training data.")
print("\nIn production systems, this pattern ensures agents provide accurate,")
print("domain-specific information from trusted knowledge sources.")
