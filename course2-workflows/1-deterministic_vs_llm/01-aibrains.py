"""
Program Management Knowledge Agent - Starter Code

This program demonstrates two approaches to answering program management questions:
1. Using hardcoded knowledge
2. Using an LLM API

Complete the TODOs to build your knowledge agent.
"""
from enum import Enum
from typing import List, Dict, Any
from openai import OpenAI
import os
from dotenv import load_dotenv


from enum import Enum

class OpenAIModel(str, Enum):
    GPT_41 = "gpt-4.1"  # Strong default choice for development tasks, particularly those requiring speed, responsiveness, and general-purpose reasoning. 
    GPT_41_MINI = "gpt-4.1-mini"  # Fast and affordable, good for brainstorming, drafting, and tasks that don't require the full power of GPT-4.1.
    GPT_41_NANO = "gpt-4.1-nano"  # The fastest and cheapest model, suitable for lightweight tasks, high-frequency usage, and edge computing.

MODEL = OpenAIModel.GPT_41_MINI 

# 0090470664
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# TODO: Initialize the OpenAI client if API key is available
# Hint: Use os.getenv() to get the API key from environment variables

def get_hardcoded_answer(question):
    """
    Return answers to program management questions using hardcoded knowledge.
    
    Args:
        question (str): The question about program management
        
    Returns:
        str: The answer to the question
    """
    question_lower = question.lower()
    knowledge_base = {
        "gantt": "A Gantt chart is a visual project management tool that displays tasks over time. It represents activities as horizontal bars on a timeline, allowing you to visualize dependencies, duration, and project progress.",
        
        "agile": "Agile is an iterative project management methodology that emphasizes flexibility, collaboration, and incremental delivery. It's based on short cycles (sprints), continuous feedback, and adaptation to change, rather than following a rigid plan.",
        
        "sprint": "A sprint is a fixed time period (usually 1-4 weeks) in Agile methodologies where the team works to complete a specific set of tasks. At the end of each sprint, a functional product increment is delivered.",
        
        "critical path": "The critical path is the sequence of dependent tasks that determines the minimum project duration. Any delay in critical path tasks will delay the entire project. It's identified using the CPM (Critical Path Method).",
        
        "milestone": "A milestone is a significant point in the project that marks the completion of an important phase or delivery of a key result. Milestones have no duration and serve as checkpoints to measure progress.",
        
        "stakeholder": "Stakeholders are individuals, groups, or organizations that have an interest in or are affected by the project. They include sponsors, clients, end users, project team, and other interested parties. Managing them is crucial for project success.",
        
        "risk": "Risk management involves identifying, analyzing, and responding to uncertainty factors that could impact the project. It includes creating mitigation plans for negative risks and exploitation plans for opportunities.",
    }
    
    # Search for matching keywords in the question
    for keyword, answer in knowledge_base.items():
        if keyword in question_lower:
            return answer
    
    # Default response for questions not in knowledge base
    return "Sorry, I don't have specific information about that question in my knowledge base. Try asking about: Gantt charts, Agile, sprints, critical path, milestones, stakeholders, or risk management."


def get_llm_answer(question):
    """
    Get answers to program management questions using an LLM API.
    
    Args:
        question (str): The question about program management
        
    Returns:
        str: The answer from the LLM
    """

    if client is None:
        raise ValueError("LLM client is not initialized. Please set up your API key.")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a program management expert."},
                {"role": "user", "content": question}
            ],
            temperature=0.001,
            max_tokens=100,
        ) 
        return response.choices[0].message.content
    except Exception as e:
        raise ValueError(f"Error getting answer from LLM: {str(e)}")
    


# Demo function to compare both approaches
def compare_answers(question):
    """Compare answers from both approaches for a given question."""
    print(f"\nQuestion: {question}")
    print("-" * 50)
    hardcoded_answer = get_hardcoded_answer(question)
    print(f"\n Hardcoded Answer:\n{hardcoded_answer}")

    llm_answer = get_llm_answer(question)   
    print(f"\n LLM Answer:\n{llm_answer}")
    print("=" * 50)


# Demo with sample questions
if __name__ == "__main__":
    print("PROGRAM MANAGEMENT KNOWLEDGE AGENT DEMO")
    print("=" * 50)
    
    sample_questions = [
        "What is a Gantt chart?",
        "How does the Agile methodology work?",
        "Explain what a sprint is",
        "What is the critical path in project management?",
        "What are milestones?",
        "How do you manage stakeholders?",
    ]
    
    
    for question in sample_questions:
        compare_answers(question)