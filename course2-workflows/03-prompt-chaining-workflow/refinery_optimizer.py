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
#         Client Configuration 
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






# ----------------------------------
#         Agent Configuration 
# ----------------------------------

def feedstock_analyst_agent(feedstock_name):
    # Prompt refinado: Pide detalles técnicos específicos (API Gravity, Sulfur)
    system_prompt = """
    You are a Senior Petrochemical Expert. Your goal is to analyze hydrocarbon feedstocks technically.
    
    Structure your response in two clear sections:
    1. CHEMICAL PROFILE: Estimate the likely API gravity, sulfur content (sweet/sour), and viscosity.
    2. REFINING POTENTIAL: Briefly explain which refined products (Gasoline, Diesel, Jet Fuel, Heavy Fuel Oil) are most naturally favored by this crude type based on its chemistry.
    
    Keep the analysis concise and professional.
    """

    user_prompt = f"Analyze this feedstock provided by the procurement team: {feedstock_name}"
    
    print(f"\n[1] Feedstock Analyst working on: {feedstock_name}...")
    return call_api(system_prompt, user_prompt, temp=0.2)
    

# AGENT 2: PLANIFICADOR DE DESTILACIÓN
def distillation_planner_agent(feedstock_analysis):
    system_prompt = """
    You are a Refinery Operations Planner managing the Atmospheric Distillation Unit.
    Based on the technical analysis of the crude oil provided, estimate the percentage yields for the fractional distillation process.
    
    You must provide a realistic yield breakdown summing to approximately 100%.
    Format:
    - Liquefied Petroleum Gases (LPG): X%
    - Gasoline/Naphtha: X%
    - Jet Fuel/Kerosene: X%
    - Diesel/Distillates: X%
    - Heavy Residue/Bitumen: X%
    
    Add a one-sentence operational note about processing difficulty (e.g., "High sulfur content will require extensive hydrotreating").
    """
    
    user_prompt = f"""
    Based on the following feedstock analysis, generate the Distillation Yield Plan:
    
    --- FEEDSTOCK ANALYSIS ---
    {feedstock_analysis}
    --------------------------
    """
    
    print(f"[2] Distillation Planner calculating yields...")
    return call_api(system_prompt, user_prompt, temp=0.2)



def market_analyst_agent(distillation_plan):
    
    system_prompt = """
    You are a Senior Energy Market Trader. Your job is to assess the profitability of refined products based on current (simulated) global trends.
    
    Analyze the products mentioned in the production plan. 
    Classify demand for each major product as 'HIGH', 'MODERATE', or 'LOW'.
    
    Mention factors like:
    - Seasonality (e.g., summer driving season favors gasoline, winter favors heating oil).
    - Industrial demand for diesel.
    - Airline travel recovery for Jet Fuel.
    
    Conclude with a 'Market Sentiment' summary.
    """
    
    user_prompt = f"""
    Review the products available from this distillation plan and analyze their market potential:
    
    --- DISTILLATION PLAN ---
    {distillation_plan}
    -------------------------
    """
    
    print(f"[3] Market Analyst assessing demand and prices...")
    return call_api(system_prompt, user_prompt, temp=0.3) # Un poco más de creatividad (temp 0.3)


# AGENT 4: OPTIMIZADOR DE PRODUCCIÓN
def production_optimizer_agent(distillation_plan, market_data):
    # Prompt refinado: El agente debe sintetizar A (Técnica) + B (Economía) = C (Decisión)
    system_prompt = """
    You are the Refinery Plant Manager and Strategy Director. 
    Your ultimate goal is to MAXIMIZE PROFIT margin while respecting technical constraints.
    
    You have the 'Potential Yields' (Supply) and the 'Market Analysis' (Demand).
    
    Provide a Strategic Directive:
    1. PRIORITY PRODUCT: Which product should we maximize production of (e.g., via secondary conversion units like Cracking)?
    2. RATIONALE: Why? (Combine yield availability with market price/demand).
    3. OPERATIONAL ADJUSTMENT: Recommend a specific shift (e.g., "Run the catalytic cracker at max severity to convert Heavy Residue into more Gasoline").
    
    Be decisive and clear.
    """
    
    user_prompt = f"""
    Synthesize the following data to provide the final production order:
    
    --- TECHNICAL YIELDS (Supply) ---
    {distillation_plan}
    
    --- MARKET CONDITIONS (Demand) ---
    {market_data}
    
    Provide your Optimized Production Recommendation.
    """
    
    print(f"[4] Production Optimizer synthesizing final strategy...")
    return call_api(system_prompt, user_prompt, temp=0.2)


# ----------------------------------
#         Orchestration 
# ----------------------------------

def run_refinery_simulation(crude_type):
    print(f"Starting Refinery Optimization Chain for: '{crude_type}'")
    print("="*60)
    
    # 1. Feedstock Analysis
    analysis_output = feedstock_analyst_agent(crude_type)
    print(f"\n--- STEP 1: FEEDSTOCK ANALYSIS ---\n{analysis_output}\n")
    
    # 2. Distillation Planning
    # Pasa el output del agente 1 como input del agente 2
    distillation_output = distillation_planner_agent(analysis_output)
    print(f"\n--- STEP 2: DISTILLATION PLAN ---\n{distillation_output}\n")
    
    # 3. Market Analysis
    # Pasa el plan de destilación para que el analista vea qué productos tenemos
    market_output = market_analyst_agent(distillation_output)
    print(f"\n--- STEP 3: MARKET ANALYSIS ---\n{market_output}\n")
    
    # 4. Final Optimization
    # Pasa AMBOS contextos anteriores para la decisión final
    final_recommendation = production_optimizer_agent(distillation_output, market_output)
    print(f"\n--- STEP 4: FINAL STRATEGY ---\n{final_recommendation}\n")
    
    return final_recommendation


if __name__ == "__main__":
    current_feedstock = "West Texas Intermediate (WTI) Crude"
    
    # Ejecutar la cadena
    run_refinery_simulation(current_feedstock)