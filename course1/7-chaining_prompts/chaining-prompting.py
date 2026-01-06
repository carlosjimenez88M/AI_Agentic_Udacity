'''
Changing Prompting Practice 
'''


#======================#
# ---- libraries ----- #
#======================#


from openai import OpenAI  
from enum import Enum
import json
from pydantic import BaseModel, Field  
from typing import List, Dict, Optional, Literal
import os
from  dotenv import load_dotenv


#========================================#
# ----- load environment variables ----- #
#========================================#
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


#===========================#
# ----- define models ----- #
#===========================#


class OpenAIModels(str, Enum):
    '''
    OpenAI Models Enum Class
    '''
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_41_MINI = "gpt-4.1-mini"
    GPT_41_NANO = "gpt-4.1-nano"


MODEL = OpenAIModels.GPT_41_NANO


def get_completion(messages: Optional[List[Dict[str, str]]] = None,
                   system_prompt: str = None,
                   user_prompt: str = None) -> str:
    '''
    Get completion from OpenAI API
    '''
    messages_list = list(messages) if messages else []
    if system_prompt:
        messages_list.insert(0, {"role": "system", "content": system_prompt}) 
    if user_prompt:
        messages_list.append({"role": "user", "content": user_prompt})
    if not messages_list:
        raise ValueError("Either messages or system_prompt and user_prompt must be provided.")
    try:
        response = client.chat.completions.create(
            model=MODEL.value,
            messages=messages_list,
            temperature=0.000001,
            max_tokens=500)
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"Error en API call: {e}") from e
    


#=============================#   
# ----- text to analyze ----- #
#=============================#

sample_fnols = [
    """
    Claim ID: C001
    Customer: John Smith
    Vehicle: 2018 Toyota Camry
    Incident: While driving on the highway, a rock hit my windshield and caused a small chip
    about the size of a quarter. No other damage was observed.
    """,
    """
    Claim ID: C002
    Customer: Sarah Johnson
    Vehicle: 2020 Honda Civic
    Incident: I was parked at the grocery store and returned to find someone had hit my car and
    dented the rear bumper and taillight. The taillight is broken and the bumper has a large dent.
    """,
    """
    Claim ID: C003
    Customer: Michael Rodriguez
    Vehicle: 2022 Ford F-150
    Incident: I was involved in a serious collision at an intersection. The front of my truck is
    severely damaged, including the hood, bumper, radiator, and engine compartment. The airbags
    deployed and the vehicle is not drivable.
    """,
    """
    Claim ID: C004
    Customer: Emma Williams
    Vehicle: 2019 Subaru Outback
    Incident: My car was damaged in a hailstorm. There are multiple dents on the hood, roof, and
    trunk. The side mirrors were also damaged and one window has a small crack.
    """,
    """
    Claim ID: C005
    Customer: David Brown
    Vehicle: 2021 Tesla Model 3
    Incident: Someone keyed my car in the parking lot. There are deep scratches along both doors
    on the driver's side.
    """,
]



# Define a system prompt for information extraction according to the provided ClaimInformation class
# TODO: Complete the prompt by replacing the parts marked with **********


class ClaimInformation(BaseModel):
    claim_id: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=2, max_length=100)
    vehicle: str = Field(..., min_length=2, max_length=100)
    loss_desc: str = Field(..., min_length=10, max_length=500)
    damage_area: List[
        Literal[
            "windshield",
            "front",
            "rear",
            "side",
            "roof",
            "hood",
            "door",
            "bumper",
            "fender",
            "quarter panel",
            "trunk",
            "glass",
        ]
    ] = Field(..., min_length=1)


info_extraction_system_prompt = """
You are an auto insurance claim processing assistant. 
Your task is to extract key information from First Notice of Loss (FNOL) reports.

Format your response as a valid JSON object with the following keys:
- claim_id (str): The claim ID
- name (str): The customer's full name
- vehicle (str): The vehicle make, model, and year
- loss_desc (str): A concise description of the incident
- damage_area (list[str]): A list of damaged areas on the vehicle (at least one of:
    - windshield
    - front
    - rear
    - side
    - roof
    - hood
    - door
    - bumper
    - fender
    - quarter panel
    - trunk
    - glass

For damage_area, only use items from the list above.

Only respond with the JSON object, nothing else.
"""

#==============================#
# ----- check functions ------ #
#==============================#


def gate1_validate_claims_info(claim_info:str) -> ClaimInformation:
    '''
    Validate claim information extracted from FNOL
    '''
    try:
        claim_info_dict = json.loads(claim_info)
        claim_information = ClaimInformation(**claim_info_dict)
        return claim_information
    except Exception as e:
        raise ValueError(f"Invalid claim information format: {e}") from e


def extract_claim_information(fnol_report: str) :
    '''
    Extract claim information from FNOL report
    '''
    messages = [
        {"role": "system", "content": info_extraction_system_prompt},
        {"role": "user", "content": fnol_report}
    ]
    response = get_completion(messages=messages)
    try:
        claim_information = gate1_validate_claims_info(response)
        return claim_information
    except ValueError as ve:
        raise ve from e
    except Exception as e:
        raise RuntimeError(f"Error extracting claim information: {e}") from e
    


#==============================================#
# ------ run extraction on sample fnols -----  #
#==============================================#



extracted_claims_info = [
    extract_claim_information(fnol) for fnol in sample_fnols
]

for claim_info in extracted_claims_info:
    print(claim_info.model_dump_json(indent=4))


#==============================================#
# -------     Severity Assessment      ------- #
#==============================================#


class SeverityAssessment(BaseModel):
    severity: Literal["Low", "Medium", "High"]
    est_cost: float = Field(..., gt=0)



severity_assessment_system_prompt = """
You are an auto insurance damage assessor. 
Your task is to evaluate the severity of vehicle damage and estimate repair costs.

Apply these carrier heuristics:
- Low damage: Small dents, scratches, glass chips (cost range: $100-$1,000)
- Medium damage: Single panel damage, bumper replacement, door damage (cost range: $1,000-$5,000)
- High damage: Structural damage, multiple panel replacement, engine/drivetrain issues, total loss candidates (cost range: $5,000-$50,000)

Based on the claim information provided, determine:
1. Severity level (Low, Medium, or High)
2. Estimated repair cost (in USD)

Format your response as a valid JSON object with the following keys:
- severity: One of "Low", "Medium", or "High"
- est_cost: Numeric estimate of repair costs (e.g., 750.00)

Only respond with the JSON object, nothing else.
"""


def gate2_cost_range_ok(severity_json: str) -> SeverityAssessment:
    try:
        severity_dict = json.loads(severity_json)
        # validate pydantic model
        validated_severity = SeverityAssessment(**severity_dict)
        

        if validated_severity.severity == "Low" and not (100 <= validated_severity.est_cost <= 1000):
            raise ValueError("Estimated cost not in range for Low severity")
        elif validated_severity.severity == "Medium" and not (1000 < validated_severity.est_cost <= 5000):
            raise ValueError("Estimated cost not in range for Medium severity")
        elif validated_severity.severity == "High" and not (5000 < validated_severity.est_cost <= 50000):
            raise ValueError("Estimated cost not in range for High severity")
        return validated_severity
    except ValueError as ve:
        raise ve from e
    except Exception as e:
        raise ValueError(f"Invalid severity assessment format: {e}") from e


def assess_severity(claim_info: ClaimInformation) -> SeverityAssessment:
    claim_info_json = claim_info.model_dump_json()
    messages = [
        {"role": "system", "content": severity_assessment_system_prompt},
        {"role": "user", "content": claim_info_json}
    ]

    response = get_completion(messages=messages)
    try:
        severity_assessment = gate2_cost_range_ok(response)
        return severity_assessment
    except ValueError as e:
        raise 
    except Exception as e:
        raise RuntimeError(f"Error assessing severity: {e}") from e
    



severity_assessment_items = [
    assess_severity(claim_info) for claim_info in extracted_claims_info
]


for severity in severity_assessment_items:
    print(severity.model_dump_json(indent=4))


#===========================#
# ----- Queue Routing ----- #
#===========================#


class ClaimRouting(BaseModel):
    claim_id: str
    queue: Literal["glass", "fast_track", "material_damage", "total_loss"]


queue_routing_system_prompt = """
You are an auto insurance claim routing specialist. Your task is to determine the appropriate processing queue for each claim.

Use these routing rules:
- 'glass' queue: For Minor damage involving ONLY glass (windshield, windows)
- 'fast_track' queue: For other Minor damage
- 'material_damage' queue: For all Moderate damage
- 'total_loss' queue: For all Major damage

Format your response as a valid JSON object with the following keys:
- claim_id: Use the provided claim ID
- queue: One of "glass", "fast_track", "material_damage", or "total_loss"

Only respond with the JSON object, nothing else.
"""


def gate3_validate_routing(routing_json: str) -> ClaimRouting:
    try:
        routing_dict = json.loads(routing_json)
        claim_routing = ClaimRouting(**routing_dict)
        return claim_routing
    except Exception as e:
        raise ValueError(f"Invalid claim routing format: {e}") from e


def route_claim(claim_info: ClaimInformation, 
                severity_assessment: Optional[SeverityAssessment]) -> ClaimRouting:
    routing_input = {
        'claim_info': claim_info.model_dump(),
        'severity_assessment': severity_assessment.model_dump() if severity_assessment else None
    }
    messages = [
        {"role": "system", "content": queue_routing_system_prompt},
        {"role": "user", "content": json.dumps(routing_input)}
    ]
    response = get_completion(messages=messages)
    try:
        claim_routing = gate3_validate_routing(response)
        return claim_routing
    except ValueError as ve:
        raise ve from e
    except Exception as e:
        raise RuntimeError(f"Error routing claim: {e}") from e
    
claim_routing_items = [
    route_claim(claim_info, severity_assessment) 
    for claim_info, severity_assessment in zip(extracted_claims_info, severity_assessment_items)
]

for claim_routing in claim_routing_items:
    print(claim_routing.model_dump_json(indent=4))