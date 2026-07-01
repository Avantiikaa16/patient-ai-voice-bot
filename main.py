"""
Entry point — starts the FastAPI server, opens an ngrok tunnel,
then places all test calls one at a time.

Usage:
    python main.py                  # Run all 12 scenarios
    python main.py --calls 3        # Run first 3 scenarios
    python main.py --scenario routine_checkup  # Run one specific scenario
"""

import argparse
import asyncio
import logging
import os
import threading
import time

import uvicorn
from dotenv import load_dotenv
from pyngrok import ngrok
from twilio.rest import Client as TwilioClient

import server as app_server
from scenarios import SCENARIOS

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

TARGET_NUMBER = os.getenv("TARGET_NUMBER", "+18054398008")
DELAY_BETWEEN_CALLS = 15  # seconds to wait between calls


def start_uvicorn(port: int):
    """Run FastAPI in a background daemon thread."""
    uvicorn.run(
        app_server.app,
        host="0.0.0.0",
        port=port,
        log_level="warning",
    )


async def wait_for_call(twilio: TwilioClient, call_sid: str, timeout: int = 300):
    """Poll Twilio until the call finishes or timeout is reached."""
    terminal = {"completed", "failed", "canceled", "busy", "no-answer"}
    elapsed = 0
    while elapsed < timeout:
        call = await asyncio.to_thread(twilio.calls(call_sid).fetch)
        if call.status in terminal:
            return call.status
        await asyncio.sleep(5)
        elapsed += 5
    return "timeout"


async def run_scenario(twilio: TwilioClient, scenario: dict, index: int, base_url: str):
    """Place a single call for one scenario and wait for it to complete."""
    session_id = f"call_{index:02d}_{scenario['name']}"

    # Register scenario BEFORE placing call so the webhook can find it instantly
    app_server.session_store[session_id] = scenario

    print(f"\n{'='*60}")
    print(f"  Call {index + 1} | {scenario['name']}")
    print(f"  Patient : {scenario['persona']}")
    print(f"  Goal    : {scenario['goal']}")
    print(f"{'='*60}")

    call = await asyncio.to_thread(
        twilio.calls.create,
        to=TARGET_NUMBER,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        url=f"{base_url}/voice/{session_id}",
        record=True,
        recording_status_callback=f"{base_url}/recording-complete",
        recording_status_callback_method="POST",
        timeout=60,
    )

    logger.info(f"Call placed | SID={call.sid}")

    status = await wait_for_call(twilio, call.sid)
    print(f"  → Call ended with status: {status}")
    return status


async def main():
    parser = argparse.ArgumentParser(description="Voice Patient Bot")
    parser.add_argument("--calls", type=int, default=None, help="Number of calls to make")
    parser.add_argument("--scenario", type=str, default=None, help="Run one scenario by name")
    args = parser.parse_args()

    # Validate env
    required = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER",
                "DEEPGRAM_API_KEY", "GROQ_API_KEY", "TARGET_NUMBER"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        print("Fill in your .env file and try again.")
        return

    port = int(os.getenv("PORT", "8000"))

    # Start ngrok
    ngrok_token = os.getenv("NGROK_AUTH_TOKEN", "")
    if ngrok_token:
        ngrok.set_auth_token(ngrok_token)
    tunnel = ngrok.connect(port, "http")
    base_url = str(tunnel.public_url)
    if base_url.startswith("http://"):
        base_url = base_url.replace("http://", "https://")
    app_server.BASE_URL = base_url
    print(f"\n[OK] ngrok tunnel: {base_url}")

    # Start FastAPI server in background thread
    thread = threading.Thread(target=start_uvicorn, args=(port,), daemon=True)
    thread.start()
    time.sleep(2)  # Give server time to bind
    print(f"[OK] Server running on port {port}")

    # Build scenario list
    if args.scenario:
        scenarios = [s for s in SCENARIOS if s["name"] == args.scenario]
        if not scenarios:
            print(f"ERROR: Scenario '{args.scenario}' not found.")
            print(f"Available: {[s['name'] for s in SCENARIOS]}")
            return
    else:
        scenarios = SCENARIOS
        if args.calls:
            scenarios = scenarios[: args.calls]

    print(f"\n→ Running {len(scenarios)} call(s) to {TARGET_NUMBER}\n")

    twilio = TwilioClient(
        os.getenv("TWILIO_ACCOUNT_SID"),
        os.getenv("TWILIO_AUTH_TOKEN"),
    )

    results = []
    for i, scenario in enumerate(scenarios):
        status = await run_scenario(twilio, scenario, i, base_url)
        results.append({"scenario": scenario["name"], "status": status})

        if i < len(scenarios) - 1:
            print(f"\n  Waiting {DELAY_BETWEEN_CALLS}s before next call...")
            await asyncio.sleep(DELAY_BETWEEN_CALLS)

    # Summary
    print(f"\n{'='*60}")
    print("  ALL CALLS COMPLETE")
    print(f"{'='*60}")
    for r in results:
        print(f"  {r['scenario']:<35} → {r['status']}")

    print("\n→ Transcripts saved in: transcripts/")
    print("→ Recordings saved in : recordings/  (download may take ~30s after call)")
    print("\nRun bug analysis with:  python bug_analyzer.py")


if __name__ == "__main__":
    asyncio.run(main())
