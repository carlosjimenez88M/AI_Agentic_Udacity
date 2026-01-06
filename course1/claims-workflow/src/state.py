"""State definitions for claims processing workflow"""

from typing import Optional, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


# Pydantic models for structured data
class ClaimInformation(BaseModel):
    """Structured claim information extracted from FNOL"""
    claim_id: str = Field(..., description="Unique claim identifier")
    policy_number: str = Field(..., description="Insurance policy number")
    claimant_name: str = Field(..., description="Name of claimant")
    incident_date: str = Field(..., description="Date of incident")
    incident_type: str = Field(..., description="Type of incident (e.g., collision, theft, fire)")
    damage_description: str = Field(..., description="Description of damage")
    location: str = Field(..., description="Location where incident occurred")


class SeverityAssessment(BaseModel):
    """Damage severity assessment"""
    severity: Literal["Low", "Medium", "High"] = Field(..., description="Severity level")
    est_cost: float = Field(..., description="Estimated repair cost in USD")
    reasoning: str = Field(..., description="Explanation of severity assessment")


class ClaimRouting(BaseModel):
    """Claim routing decision"""
    queue: Literal["auto", "manual", "specialist"] = Field(..., description="Processing queue")
    priority: Literal["low", "medium", "high"] = Field(..., description="Priority level")
    reasoning: str = Field(..., description="Explanation of routing decision")


# TypedDict for LangGraph state
class ClaimState(TypedDict, total=False):
    """State for claims processing workflow"""
    fnol: str  # First Notice of Loss text
    model: str  # LLM model to use
    claim_info: Optional[ClaimInformation]  # Extracted claim information
    severity: Optional[SeverityAssessment]  # Severity assessment
    routing: Optional[ClaimRouting]  # Routing decision
    errors: list[str]  # List of errors encountered
    status: str  # Current workflow status
