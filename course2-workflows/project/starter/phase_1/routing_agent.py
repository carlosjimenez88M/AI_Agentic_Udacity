# Test script for RoutingAgent class

from workflow_agents.base_agents import RoutingAgent, KnowledgeAugmentedPromptAgent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# ============================================================================
# CREATE SPECIALIZED AGENTS
# ============================================================================

# Texas Agent - Specializes in Texas-related knowledge
texas_persona = "You are a Texas history expert."
texas_knowledge = "Rome, Texas is a small city in East Texas. It was founded in the 1800s and is known for its rural character and agricultural heritage."

texas_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=texas_persona,
    knowledge=texas_knowledge
)

# Europe Agent - Specializes in European knowledge
europe_persona = "You are a European history expert."
europe_knowledge = "Rome, Italy is the capital city of Italy and has a rich history spanning over 2,500 years. It was the center of the Roman Empire and is famous for landmarks like the Colosseum, Vatican City, and the Trevi Fountain."

europe_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=europe_persona,
    knowledge=europe_knowledge
)

# Math Agent - Specializes in mathematical calculations
math_persona = "You are a mathematics expert who solves problems step-by-step."
math_knowledge = "When solving problems, break them down into clear steps. For multiplication, identify the numbers to multiply and compute the result. Always show your work."

math_agent = KnowledgeAugmentedPromptAgent(
    openai_api_key=openai_api_key,
    persona=math_persona,
    knowledge=math_knowledge
)

# ============================================================================
# DEFINE AGENT FUNCTIONS
# ============================================================================

def texas_function(query):
    """Function to handle Texas-related queries"""
    print(f"[Router] Dispatched to Texas Agent")
    return texas_agent.respond(query)

def europe_function(query):
    """Function to handle Europe-related queries"""
    print(f"[Router] Dispatched to Europe Agent")
    return europe_agent.respond(query)

def math_function(query):
    """Function to handle math-related queries"""
    print(f"[Router] Dispatched to Math Agent")
    return math_agent.respond(query)

# ============================================================================
# CONFIGURE ROUTING AGENT
# ============================================================================

routing_agent = RoutingAgent(
    openai_api_key=openai_api_key,
    agents=[
        {
            "name": "Texas Expert",
            "description": "Expert in Texas history, geography, and culture. Handles questions about Texas cities, landmarks, and history.",
            "func": texas_function
        },
        {
            "name": "Europe Expert",
            "description": "Expert in European history, geography, and culture. Handles questions about European cities, landmarks, and history.",
            "func": europe_function
        },
        {
            "name": "Math Expert",
            "description": "Expert in mathematics, calculations, and problem-solving. Handles mathematical questions, story problems, and arithmetic.",
            "func": math_function
        }
    ]
)

# ============================================================================
# TEST ROUTING WITH DIFFERENT PROMPTS
# ============================================================================

print("="*80)
print("ROUTING AGENT TEST")
print("="*80)

test_prompts = [
    "Tell me about the history of Rome, Texas",
    "Tell me about the history of Rome, Italy",
    "One story takes 2 days, and there are 20 stories"
]

for i, prompt in enumerate(test_prompts, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}/3")
    print(f"{'='*80}")
    print(f"Prompt: {prompt}\n")

    result = routing_agent.route(prompt)

    print(f"\nResponse:")
    print(result)
    print()

print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)
print("\nThe RoutingAgent demonstrates semantic routing:")
print("1. Calculates embedding vectors for the query and all agent descriptions")
print("2. Computes cosine similarity between query and each agent")
print("3. Selects the agent with highest similarity score")
print("4. Executes that agent's function")
print("\nKey Advantages over keyword matching:")
print("- Handles synonyms naturally ('history' matches historical expertise)")
print("- Understands context ('Rome, Texas' vs 'Rome, Italy')")
print("- Recognizes implicit intent ('20 stories' implies math calculation)")
print("\nThis enables intelligent, flexible routing without hard-coded rules.")
