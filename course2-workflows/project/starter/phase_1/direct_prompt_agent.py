# Test script for DirectPromptAgent class

from workflow_agents.base_agents import DirectPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load the OpenAI API key from the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

prompt = "What is the Capital of France?"

# Instantiate the DirectPromptAgent
direct_agent = DirectPromptAgent(openai_api_key=openai_api_key)

# Use direct_agent to send the prompt and store the response
direct_agent_response = direct_agent.respond(prompt)

# Print the response from the agent
print("DirectPromptAgent Response:")
print(direct_agent_response)

# Print an explanatory message describing the knowledge source
print("\nKnowledge Source:")
print("The DirectPromptAgent uses the general pre-trained knowledge embedded in the")
print("gpt-3.5-turbo LLM model. It does not use any external knowledge base or")
print("additional context - only the model's training data up to its knowledge cutoff date.")
