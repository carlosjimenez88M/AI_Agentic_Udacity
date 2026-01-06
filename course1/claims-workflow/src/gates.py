"""Gate check functions for validation"""

import json
from typing import Dict
from .state import ClaimInformation, SeverityAssessment, ClaimRouting


def gate1_validate_claims_info(claim_info_json: str) -> ClaimInformation:
    """
    Gate 1: Validate extracted claim information.
    
    Args:
        claim_info_json: JSON string with claim data
        
    Returns:
        Validated ClaimInformation object
        
    Raises:
        ValueError: If validation fails
    """
    try:
        claim_dict = json.loads(claim_info_json)
        return ClaimInformation(**claim_dict)
    except Exception as e:
        raise ValueError(f"Invalid claim information format: {e}") from e


def gate2_cost_range_ok(severity_json: str) -> SeverityAssessment:
    """
    Gate 2: Validate severity assessment and cost range.
    
    Ensures estimated costs align with severity levels:
    - Low: $100-$1,000
    - Medium: $1,000-$5,000
    - High: $5,000-$50,000
    
    Args:
        severity_json: JSON string with severity assessment
        
    Returns:
        Validated SeverityAssessment object
        
    Raises:
        ValueError: If validation fails
    """
    try:
        severity_dict = json.loads(severity_json)
        validated = SeverityAssessment(**severity_dict)
        
        cost = validated.est_cost
        severity = validated.severity
        
        # Validate cost ranges
        cost_ranges = {
            "Low": (100, 1000),
            "Medium": (1000, 5000),
            "High": (5000, 50000)
        }
        
        min_cost, max_cost = cost_ranges[severity]
        
        if severity == "Low":
            if not (min_cost <= cost <= max_cost):
                raise ValueError(
                    f"Cost ${cost} out of range for {severity} severity (${min_cost}-${max_cost})"
                )
        else:
            if not (min_cost < cost <= max_cost):
                raise ValueError(
                    f"Cost ${cost} out of range for {severity} severity (${min_cost}-${max_cost})"
                )
        
        return validated
        
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Invalid severity assessment format: {e}") from e


def gate3_validate_routing(routing_json: str) -> ClaimRouting:
    """
    Gate 3: Validate claim routing decision.
    
    Args:
        routing_json: JSON string with routing decision
        
    Returns:
        Validated ClaimRouting object
        
    Raises:
        ValueError: If validation fails
    """
    try:
        routing_dict = json.loads(routing_json)
        return ClaimRouting(**routing_dict)
    except Exception as e:
        raise ValueError(f"Invalid claim routing format: {e}") from e