#!/usr/bin/env python3
"""Test the claims workflow through the LangGraph API"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:2024"

# Sample FNOL (First Notice of Loss) - the one the user highlighted
SAMPLE_FNOL = """Claim ID: C003
Customer: Michael Rodriguez
Vehicle: 2022 Ford F-150
Incident: I was involved in a serious collision at an intersection. The front of my truck is
severely damaged, including the hood, bumper, radiator, and engine compartment. The airbags
deployed and the vehicle is not drivable."""

def test_workflow():
    print("=" * 80)
    print("Testing Claims Processing Workflow")
    print("=" * 80)

    # 1. Create a thread
    print("\n[1/3] Creating thread...")
    response = requests.post(f"{BASE_URL}/threads", json={})
    if response.status_code != 200:
        print(f"❌ Failed to create thread: {response.status_code}")
        print(response.text)
        return False

    thread_data = response.json()
    thread_id = thread_data["thread_id"]
    print(f"✅ Thread created: {thread_id}")

    # 2. Run the workflow
    print("\n[2/3] Running workflow with FNOL...")
    print(f"FNOL Input:\n{SAMPLE_FNOL}")
    print()

    payload = {
        "assistant_id": "claims_processor",
        "input": {
            "fnol": SAMPLE_FNOL,
            "model": "gpt-4o-mini"
        }
    }

    response = requests.post(
        f"{BASE_URL}/threads/{thread_id}/runs",
        json=payload,
        stream=True
    )

    if response.status_code != 200:
        print(f"❌ Failed to start run: {response.status_code}")
        print(response.text)
        return False

    # Process streaming response
    print("Processing...")
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])
                    if 'event' in data:
                        event = data['event']
                        if event == 'values':
                            # Print status updates
                            values = data.get('data', {})
                            status = values.get('status', 'unknown')
                            print(f"  Status: {status}")
                except json.JSONDecodeError:
                    pass

    print("✅ Workflow completed")

    # 3. Wait for completion
    print("\n[3/3] Waiting for workflow to complete...")
    max_wait = 30  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait:
        runs_resp = requests.get(f"{BASE_URL}/threads/{thread_id}/runs")
        if runs_resp.status_code == 200:
            runs = runs_resp.json()
            if runs and runs[0]["status"] == "success":
                print("✅ Workflow completed successfully")
                break
            elif runs and runs[0]["status"] in ["error", "failed"]:
                print(f"❌ Workflow failed with status: {runs[0]['status']}")
                return False
        time.sleep(1)
    else:
        print("⚠️  Workflow timed out")

    print("Retrieving final state...")

    # Get the run details which includes the final output
    runs_resp = requests.get(f"{BASE_URL}/threads/{thread_id}/runs")
    if runs_resp.status_code != 200:
        print(f"❌ Failed to get runs: {runs_resp.status_code}")
        return False

    runs = runs_resp.json()
    if not runs:
        print("❌ No runs found")
        return False

    run_id = runs[0]["run_id"]

    # Try to get state from the run
    state_resp = requests.get(f"{BASE_URL}/threads/{thread_id}/state")
    if state_resp.status_code == 200:
        state = state_resp.json()
        values = state.get("values", {})
    else:
        # Fallback: Get values from streaming the completed run
        print("Getting results from run stream...")
        stream_resp = requests.post(
            f"{BASE_URL}/threads/{thread_id}/runs/{run_id}/stream",
            json={}
        )

        values = {}
        for line in stream_resp.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        if data.get('event') == 'values':
                            values = data.get('data', {})
                    except json.JSONDecodeError:
                        pass

    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)

    # Display claim info
    if "claim_info" in values:
        claim_info = values["claim_info"]
        print("\n📋 Claim Information:")
        print(f"  Claim ID: {claim_info.get('claim_id')}")
        print(f"  Customer: {claim_info.get('customer_name')}")
        print(f"  Vehicle: {claim_info.get('vehicle')}")
        print(f"  Location: {claim_info.get('incident_location')}")

    # Display severity assessment
    if "severity" in values:
        severity = values["severity"]
        print("\n📊 Severity Assessment:")
        print(f"  Severity: {severity.get('severity')}")
        print(f"  Estimated Cost: ${severity.get('est_cost'):,.2f}")
        print(f"  Key Damages: {', '.join(severity.get('key_damages', []))}")

    # Display routing
    if "routing" in values:
        routing = values["routing"]
        print("\n🚦 Routing Decision:")
        print(f"  Queue: {routing.get('queue')}")
        print(f"  Priority: {routing.get('priority')}")
        print(f"  Reason: {routing.get('reason')}")

    # Check for errors
    if "errors" in values and values["errors"]:
        print("\n❌ Errors:")
        for error in values["errors"]:
            print(f"  - {error}")
        return False

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    try:
        success = test_workflow()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
