#!/usr/bin/env python3
"""Direct test of the claims workflow (without API)"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.agents.claims_processor import graph

# Sample FNOL (First Notice of Loss)
SAMPLE_FNOL = """Claim ID: C003
Customer: Michael Rodriguez
Vehicle: 2022 Ford F-150
Incident: I was involved in a serious collision at an intersection. The front of my truck is
severely damaged, including the hood, bumper, radiator, and engine compartment. The airbags
deployed and the vehicle is not drivable."""

def test_direct():
    print("=" * 80)
    print("Direct Test of Claims Processing Workflow")
    print("=" * 80)

    print("\nInput FNOL:")
    print(SAMPLE_FNOL)
    print()

    # Run the graph
    input_data = {
        "fnol": SAMPLE_FNOL,
        "model": "gpt-4o-mini"
    }

    print("Running workflow...")
    result = graph.invoke(input_data)

    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)

    # Display claim info
    if "claim_info" in result:
        claim_info = result["claim_info"]
        print("\n📋 Claim Information:")
        print(f"  Claim ID: {claim_info.claim_id}")
        print(f"  Claimant Name: {claim_info.claimant_name}")
        print(f"  Policy Number: {claim_info.policy_number}")
        print(f"  Incident Date: {claim_info.incident_date}")
        print(f"  Incident Type: {claim_info.incident_type}")
        print(f"  Location: {claim_info.location}")
        print(f"  Damage Description: {claim_info.damage_description[:100]}...")

    # Display severity assessment
    if "severity" in result:
        severity = result["severity"]
        print("\n📊 Severity Assessment:")
        print(f"  Severity: {severity.severity}")
        print(f"  Estimated Cost: ${severity.est_cost:,.2f}")
        print(f"  Reasoning: {severity.reasoning[:150]}...")

    # Display routing
    if "routing" in result:
        routing = result["routing"]
        print("\n🚦 Routing Decision:")
        print(f"  Queue: {routing.queue}")
        print(f"  Priority: {routing.priority}")
        print(f"  Reasoning: {routing.reasoning[:150]}...")

    # Check status
    print(f"\n📌 Final Status: {result.get('status', 'unknown')}")

    # Check for errors
    if "errors" in result and result["errors"]:
        print("\n❌ Errors:")
        for error in result["errors"]:
            print(f"  - {error}")
        return False

    print("\n" + "=" * 80)
    print("✅ WORKFLOW EXECUTED SUCCESSFULLY!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    try:
        success = test_direct()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
