"""Claims processing workflow graph"""

import json
import logging
from typing import Dict, Literal

from langgraph.graph import StateGraph, START, END

# ✅ CAMBIAR A IMPORTS ABSOLUTOS (sin ..)
from src.state import ClaimState
from src.prompts import (
    INFO_EXTRACTION_PROMPT,
    SEVERITY_ASSESSMENT_PROMPT,
    QUEUE_ROUTING_PROMPT
)
from src.gates import (
    gate1_validate_claims_info,
    gate2_cost_range_ok,
    gate3_validate_routing
)
from src.utils import get_completion

# Configure logging
logger = logging.getLogger(__name__)


#================================#
# ----- Node Functions ----- #
#================================#

def extract_claim_node(state: ClaimState) -> Dict:
    """
    Node 1: Extract claim information from FNOL.
    
    This node:
    1. Sends FNOL to LLM with extraction prompt
    2. Validates response with gate1
    3. Updates state with ClaimInformation
    """
    logger.info("🔍 Extracting claim information...")
    
    try:
        messages = [
            {"role": "system", "content": INFO_EXTRACTION_PROMPT},
            {"role": "user", "content": state["fnol"]}
        ]
        
        response = get_completion(messages=messages, model=state["model"])
        claim_info = gate1_validate_claims_info(response)
        
        logger.info(f"✅ Successfully extracted claim: {claim_info.claim_id}")
        
        return {
            "claim_info": claim_info,
            "status": "claim_extracted"
        }
    
    except Exception as e:
        logger.error(f"❌ Claim extraction failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"Extraction error: {str(e)}"],
            "status": "failed"
        }


def assess_severity_node(state: ClaimState) -> Dict:
    """
    Node 2: Assess damage severity and estimate cost.
    
    This node:
    1. Takes ClaimInformation as input
    2. Sends to LLM with severity assessment prompt
    3. Validates cost range with gate2
    4. Updates state with SeverityAssessment
    """
    logger.info(f"📊 Assessing severity for claim {state['claim_info'].claim_id}...")
    
    try:
        claim_json = state["claim_info"].model_dump_json()
        
        messages = [
            {"role": "system", "content": SEVERITY_ASSESSMENT_PROMPT},
            {"role": "user", "content": claim_json}
        ]
        
        response = get_completion(messages=messages, model=state["model"])
        severity = gate2_cost_range_ok(response)
        
        logger.info(
            f"✅ Severity assessed: {severity.severity} "
            f"(est. ${severity.est_cost:,.2f})"
        )
        
        return {
            "severity": severity,
            "status": "severity_assessed"
        }
    
    except Exception as e:
        logger.error(f"❌ Severity assessment failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"Severity error: {str(e)}"],
            "status": "failed"
        }


def route_claim_node(state: ClaimState) -> Dict:
    """
    Node 3: Route claim to appropriate processing queue.
    
    This node:
    1. Takes ClaimInformation and SeverityAssessment as input
    2. Determines routing queue based on damage and severity
    3. Validates routing decision with gate3
    4. Updates state with ClaimRouting
    """
    logger.info(f"🚦 Routing claim {state['claim_info'].claim_id}...")
    
    try:
        routing_input = {
            'claim_info': state["claim_info"].model_dump(),
            'severity_assessment': state["severity"].model_dump()
        }
        
        messages = [
            {"role": "system", "content": QUEUE_ROUTING_PROMPT},
            {"role": "user", "content": json.dumps(routing_input, indent=2)}
        ]
        
        response = get_completion(messages=messages, model=state["model"])
        routing = gate3_validate_routing(response)
        
        logger.info(f"✅ Claim routed to: {routing.queue}")
        
        return {
            "routing": routing,
            "status": "completed"
        }
    
    except Exception as e:
        logger.error(f"❌ Claim routing failed: {e}")
        return {
            "errors": state.get("errors", []) + [f"Routing error: {str(e)}"],
            "status": "failed"
        }


#================================#
# ----- Conditional Logic ----- #
#================================#

def should_continue(state: ClaimState) -> Literal["continue", "end"]:
    """
    Conditional edge function.
    
    Determines whether to continue the workflow or end it based on status.
    
    Returns:
        "continue" if status is not "failed"
        "end" if workflow failed
    """
    if state["status"] == "failed":
        logger.warning("⚠️ Workflow failed, terminating")
        return "end"
    
    logger.debug(f"✓ Status: {state['status']}, continuing...")
    return "continue"


#================================#
# ----- Build Graph ----- #
#================================#

def build_graph() -> StateGraph:
    """
    Build the claims processing workflow graph.
    
    Graph structure:
        START → extract_claim → assess_severity → route_claim → END
        
    Conditional edges after each node allow early termination on failure.
    
    Returns:
        Compiled StateGraph ready for execution
    """
    workflow = StateGraph(ClaimState)
    
    # Add nodes
    workflow.add_node("extract_claim", extract_claim_node)
    workflow.add_node("assess_severity", assess_severity_node)
    workflow.add_node("route_claim", route_claim_node)
    
    # Define flow
    workflow.add_edge(START, "extract_claim")
    
    # Conditional edges with failure handling
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


# Create the graph instance for langgraph.json
graph = build_graph().compile()