
# -----------------------
#    libraries 
# -----------------------


import os 
from  dotenv import load_dotenv
from openai import OpenAI



#========================================#
# ----- load environment variables ----- #
#========================================#
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



# ----------------------------------
#         Agent Configuration 
# ----------------------------------


def call_api(system_prompt, 
             user_prompt, 
             temp , 
             model="gpt-4.1-mini"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temp,
    )
    return response.choices[0].message.content

    
def research_agent(topic):
    system_prompt = """You are a research specialist who provides structured information.
    Always format your response with these exact headings:
    # OVERVIEW
    # KEY POINTS
    # DETAILS
    """
    user_prompt = f"Research this topic thoroughly: {topic}"
    print(f"Researcher agent working on: {topic}")
    return call_api(system_prompt, 
                    user_prompt, 
                    temp = 0.2)


def writer_agent(topic, research_results):
    """Writer agent that creates content based on research"""
    system_prompt = """You are a content writer who creates engaging material from research.
    Create a well-structured article with a clear introduction, body, and conclusion.
    """
    
    user_prompt = f"""Write an engaging article about {topic} using this research:
    
    {research_results}
    """
    
    print(f"Writer agent creating content for: {topic}")
    return call_api(system_prompt, 
                    user_prompt, 
                    temp = 0.3)

def run_simple_chain(topic):
    """Run a minimal agent chain: Researcher → Writer"""
    print(f"\nStarting simple agent chain for: '{topic}'")
    
    # Step 1: Get research from researcher agent
    research = research_agent(topic)
    print("\nResearch complete!")
    
    # Step 2: Pass research to writer agent
    content = writer_agent(topic, research)
    print("\nContent creation complete!")
    
    # Print results
    print("\n===== RESEARCH OUTPUT =====")
    print(research)
    
    print("\n===== FINAL CONTENT =====")
    print(content)
    
    return {"research": research, "content": content}





if __name__ == "__main__":
    topic = "What are the latest breakthroughts in implementing AI in big corporations? in spanish please "
    results = run_simple_chain(topic)






