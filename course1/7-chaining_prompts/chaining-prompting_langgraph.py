'''
Claims Processing Workflow with LangGraph
'''

#======================#
# ---- libraries ----- #
#======================#

from openai import OpenAI  
from enum import Enum
import json
from pydantic import BaseModel, Field  
from typing import List, Dict, Optional, Literal, TypedDict, Annotated
import os
from dotenv import load_dotenv
import argparse
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
import logging

#========================================#
# ----- setup logging ----- #
#========================================#

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#========================================#
# ----- load environment variables ----- #
#========================================#
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#===========================#
# ----- define models ----- #
#===========================#

class OpenAIModels(str, Enum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_41_MINI = "gpt-4.1-mini"
    GPT_41_NANO = "gpt-4.1-nano"

# Default model (puede ser sobreescrito por argparse)
MODEL = OpenAIModels.GPT_41_MINI


def get_completion(
    messages: Optional[List[Dict[str, str]]] = None,
    system_prompt: Optional[str] = None,
    user_prompt: Optional[str] = None,
    model: Optional[str] = None
) -> str:
    '''Get completion from OpenAI API'''
    messages_list = list(messages) if messages else []
    
    if system_prompt:
        messages_list.insert(0, {"role": "system", "content": system_prompt})
    if user_prompt:
        messages_list.append({"role": "user", "content": user_prompt})
    
    if not messages_list:
        raise ValueError("Must provide messages or prompts")
    
    try:
        response = client.chat.completions.create(
            model=model or MODEL.value,
            messages=messages_list,
            temperature=0,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"API error: {e}") from e


#=============================#   
# ----- Pydantic Models ----- #
#=============================#

class ClaimInformation(BaseModel):
    claim_id: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=2, max_length=100)
    vehicle: str = Field(..., min_length=2, max_length=100)
    loss_desc: str = Field(..., min_length=10, max_length=500)
    damage_area: List[
        Literal[
            "windshield", "front", "rear", "side", "roof", "hood",
            "door", "bumper", "fender", "quarter panel", "trunk", "glass"
        ]
    ] = Field(..., min_length=1)


class SeverityAssessment(BaseModel):
    severity: Literal["Low", "Medium", "High"]
    est_cost: float = Field(..., gt=0)


class ClaimRouting(BaseModel):
    claim_id: str
    queue: Literal["glass", "fast_track", "material_damage", "total_loss"]


#=============================#   
# ----- LangGraph State ----- #
#=============================#

class ClaimWorkflowState(TypedDict):
    """Estado compartido del workflow"""
    fnol: str
    claim_info: Optional[ClaimInformation]
    severity: Optional[SeverityAssessment]
    routing: Optional[ClaimRouting]
    errors: List[str]
    retry_count: int
    status: str  # "processing", "completed", "failed"
    model: str  # Modelo a usar


#=============================#   
# ----- System Prompts ----- #
#=============================#

INFO_EXTRACTION_PROMPT = """
You are an auto insurance claim processing assistant. 
Your task is to extract key information from First Notice of Loss (FNOL) reports.

Format your response as a valid JSON object with the following keys:
- claim_id (str): The claim ID
- name (str): The customer's full name
- vehicle (str): The vehicle make, model, and year
- loss_desc (str): A concise description of the incident
- damage_area (list[str]): A list of damaged areas

Only respond with the JSON object, nothing else.
"""

SEVERITY_ASSESSMENT_PROMPT = """
You are an auto insurance damage assessor. 
Your task is to evaluate the severity of vehicle damage and estimate repair costs.

Apply these carrier heuristics:
- Low damage: Small dents, scratches, glass chips (cost range: $100-$1,000)
- Medium damage: Single panel damage, bumper replacement, door damage (cost range: $1,000-$5,000)
- High damage: Structural damage, multiple panel replacement, engine/drivetrain issues, total loss candidates (cost range: $5,000-$50,000)

Format your response as a valid JSON object with the following keys:
- severity: One of "Low", "Medium", or "High"
- est_cost: Numeric estimate of repair costs

Only respond with the JSON object, nothing else.
"""

QUEUE_ROUTING_PROMPT = """
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


#================================#   
# ----- Gate Check Functions ----- #
#================================#

def gate1_validate_claims_info(claim_info: str) -> ClaimInformation:
    """Validate claim information extracted from FNOL"""
    try:
        claim_info_dict = json.loads(claim_info)
        return ClaimInformation(**claim_info_dict)
    except Exception as e:
        raise ValueError(f"Invalid claim format: {e}") from e


def gate2_cost_range_ok(severity_json: str) -> SeverityAssessment:
    """Validate severity assessment and cost range"""
    try:
        severity_dict = json.loads(severity_json)
        validated_severity = SeverityAssessment(**severity_dict)
        
        cost = validated_severity.est_cost
        severity = validated_severity.severity
        
        if severity == "Low" and not (100 <= cost <= 1000):
            raise ValueError(f"Cost ${cost} not in Low range ($100-$1,000)")
        elif severity == "Medium" and not (1000 < cost <= 5000):
            raise ValueError(f"Cost ${cost} not in Medium range ($1,000-$5,000)")
        elif severity == "High" and not (5000 < cost <= 50000):
            raise ValueError(f"Cost ${cost} not in High range ($5,000-$50,000)")
        
        return validated_severity
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid severity format: {e}") from e


def gate3_validate_routing(routing_json: str) -> ClaimRouting:
    """Validate claim routing"""
    try:
        routing_dict = json.loads(routing_json)
        return ClaimRouting(**routing_dict)
    except Exception as e:
        raise ValueError(f"Invalid routing format: {e}") from e


#================================#   
# ----- LangGraph Nodes ----- #
#================================#

def extract_claim_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Node 1: Extract claim information from FNOL"""
    logger.info(f"🔍 Extracting claim information...")
    
    try:
        messages = [
            {"role": "system", "content": INFO_EXTRACTION_PROMPT},
            {"role": "user", "content": state["fnol"]}
        ]
        response = get_completion(messages=messages, model=state.get("model"))
        claim_info = gate1_validate_claims_info(response)
        
        logger.info(f"✅ Extracted claim: {claim_info.claim_id}")
        
        return {
            **state,
            "claim_info": claim_info,
            "status": "claim_extracted"
        }
    
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")
        state["errors"].append(f"Extraction error: {e}")
        state["retry_count"] += 1
        
        # Retry logic
        if state["retry_count"] < 3:
            logger.warning(f"🔄 Retrying... (attempt {state['retry_count']})")
            return extract_claim_node(state)
        
        return {**state, "status": "failed"}


def assess_severity_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Node 2: Assess damage severity"""
    logger.info(f"📊 Assessing severity for {state['claim_info'].claim_id}...")
    
    try:
        claim_json = state["claim_info"].model_dump_json()
        messages = [
            {"role": "system", "content": SEVERITY_ASSESSMENT_PROMPT},
            {"role": "user", "content": claim_json}
        ]
        response = get_completion(messages=messages, model=state.get("model"))
        severity = gate2_cost_range_ok(response)
        
        logger.info(f"✅ Severity: {severity.severity} (${severity.est_cost})")
        
        return {
            **state,
            "severity": severity,
            "status": "severity_assessed"
        }
    
    except Exception as e:
        logger.error(f"❌ Severity assessment failed: {e}")
        state["errors"].append(f"Severity error: {e}")
        return {**state, "status": "failed"}


def route_claim_node(state: ClaimWorkflowState) -> ClaimWorkflowState:
    """Node 3: Route claim to appropriate queue"""
    logger.info(f"🚦 Routing claim {state['claim_info'].claim_id}...")
    
    try:
        routing_input = {
            'claim_info': state["claim_info"].model_dump(),
            'severity_assessment': state["severity"].model_dump()
        }
        messages = [
            {"role": "system", "content": QUEUE_ROUTING_PROMPT},
            {"role": "user", "content": json.dumps(routing_input)}
        ]
        response = get_completion(messages=messages, model=state.get("model"))
        routing = gate3_validate_routing(response)
        
        logger.info(f"✅ Routed to: {routing.queue}")
        
        return {
            **state,
            "routing": routing,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"❌ Routing failed: {e}")
        state["errors"].append(f"Routing error: {e}")
        return {**state, "status": "failed"}


def should_continue(state: ClaimWorkflowState) -> str:
    """Conditional edge: determina si continuar o terminar"""
    if state["status"] == "failed":
        return "end"
    return "continue"


#================================#   
# ----- Build LangGraph ----- #
#================================#

def build_workflow() -> StateGraph:
    """Construye el workflow de LangGraph"""
    
    # Crear grafo
    workflow = StateGraph(ClaimWorkflowState)
    
    # Agregar nodos
    workflow.add_node("extract_claim", extract_claim_node)
    workflow.add_node("assess_severity", assess_severity_node)
    workflow.add_node("route_claim", route_claim_node)
    
    # Definir edges (flujo)
    workflow.set_entry_point("extract_claim")
    
    # Flujo secuencial con validación
    workflow.add_conditional_edges(
        "extract_claim",
        should_continue,
        {
            "continue": "assess_severity",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "assess_severity",
        should_continue,
        {
            "continue": "route_claim",
            "end": END
        }
    )
    
    workflow.add_edge("route_claim", END)
    
    return workflow


#================================#   
# ----- Process Claims ----- #
#================================#

def process_claim(fnol: str, model: str = None) -> Dict:
    """Procesa un solo claim a través del workflow"""
    
    # Construir workflow
    workflow = build_workflow()
    
    # Compilar con memoria para checkpoint
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    # Estado inicial
    initial_state: ClaimWorkflowState = {
        "fnol": fnol,
        "claim_info": None,
        "severity": None,
        "routing": None,
        "errors": [],
        "retry_count": 0,
        "status": "processing",
        "model": model or MODEL.value
    }
    
    # Ejecutar workflow
    config = {"configurable": {"thread_id": "claim_processing"}}
    final_state = app.invoke(initial_state, config)
    
    return final_state


def process_batch(fnols: List[str], model: str = None) -> List[Dict]:
    """Procesa múltiples claims"""
    results = []
    
    for i, fnol in enumerate(fnols, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing claim {i}/{len(fnols)}")
        logger.info(f"{'='*60}")
        
        result = process_claim(fnol, model)
        results.append(result)
    
    return results


#================================#   
# ----- CLI with argparse ----- #
#================================#

def main():
    parser = argparse.ArgumentParser(
        description="Claims Processing Workflow with LangGraph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process single claim
  python workflow.py --fnol "Claim ID: C001..."
  
  # Process batch from file
  python workflow.py --batch claims.json
  
  # Use different model
  python workflow.py --batch claims.json --model gpt-4o-mini
  
  # Debug mode
  python workflow.py --batch claims.json --debug
        """
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--fnol",
        type=str,
        help="Single FNOL report text"
    )
    input_group.add_argument(
        "--batch",
        type=str,
        help="JSON file with array of FNOL reports"
    )
    
    # Model options
    parser.add_argument(
        "--model",
        type=str,
        choices=["gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1-nano"],
        default="gpt-4.1-nano",
        help="OpenAI model to use (default: gpt-4.1-nano)"
    )
    
    # Output options
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file for results"
    )
    
    # Logging options
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress output (only errors)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.ERROR)
    
    # Process claims
    try:
        if args.fnol:
            # Single claim
            result = process_claim(args.fnol, args.model)
            results = [result]
        else:
            # Batch processing
            with open(args.batch, 'r') as f:
                fnols = json.load(f)
            results = process_batch(fnols, args.model)
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"\n✅ Results saved to {args.output}")
        else:
            # Print to console
            print("\n" + "="*60)
            print("RESULTS")
            print("="*60)
            for result in results:
                if result.get("claim_info"):
                    print(f"\nClaim: {result['claim_info'].claim_id}")
                    print(f"Severity: {result['severity'].severity if result.get('severity') else 'N/A'}")
                    print(f"Queue: {result['routing'].queue if result.get('routing') else 'N/A'}")
                    print(f"Status: {result['status']}")
                    if result['errors']:
                        print(f"Errors: {result['errors']}")
    
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())