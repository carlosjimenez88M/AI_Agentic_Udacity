# Test script for AugmentedPromptAgent class

from workflow_agents.base_agents import AugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the capital of France?"
persona = "You are a college professor; your answers always start with: 'Dear students,'"

# Instantiate an object of AugmentedPromptAgent with the required parameters
augmented_agent = AugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=persona
)

# Send the 'prompt' to the agent and store the response
augmented_agent_response = augmented_agent.respond(prompt)

# Print the agent's response
print("AugmentedPromptAgent Response:")
print(augmented_agent_response)

# Comments explaining knowledge source and persona effect:
print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)
print("\nKnowledge Source:")
print("The agent uses the same pre-trained knowledge from the gpt-3.5-turbo LLM model")
print("as the DirectPromptAgent. The factual knowledge about Paris being the capital")
print("of France comes from the model's training data.")
print("\nPersona Effect:")
print("The persona specification ('You are a college professor...') significantly")
print("affects HOW the information is presented. Notice that the response:")
print("1. Starts with 'Dear students,' as instructed")
print("2. Uses a more formal, educational tone")
print("3. May include additional context or teaching elements")
print("4. Adopts the communication style of a college professor")
print("\nThis demonstrates how system prompts shape agent behavior without changing")
print("the underlying knowledge base.")
