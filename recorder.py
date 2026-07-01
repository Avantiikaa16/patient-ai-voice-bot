"""
Saves call transcripts to text + JSON files.
Downloads MP3 recordings from Twilio after the call ends.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

RECORDINGS_DIR = Path("recordings")
TRANSCRIPTS_DIR = Path("transcripts")


class CallRecorder:
    def __init__(self, session_id: str, scenario: dict):
        self.session_id = session_id
        self.scenario = scenario
        self.call_sid: Optional[str] = None
        self.turns = []
        self.start_time = datetime.now()

        RECORDINGS_DIR.mkdir(exist_ok=True)
        TRANSCRIPTS_DIR.mkdir(exist_ok=True)

        timestamp = self.start_time.strftime("%Y%m%d_%H%M%S")
        scenario_name = scenario.get("name", "unknown")
        self.base_name = f"{timestamp}_{scenario_name}"

    def set_call_sid(self, call_sid: str):
        self.call_sid = call_sid

    def add_turn(self, speaker: str, text: str):
        """Add one turn to the transcript. speaker = 'agent' or 'patient'."""
        self.turns.append({
            "speaker": speaker,
            "text": text,
            "timestamp": datetime.now().isoformat(),
        })

    def save(self):
        """Save transcript files. Call this when the call ends."""
        self._save_text_transcript()
        self._save_json_transcript()

    def _save_text_transcript(self):
        path = TRANSCRIPTS_DIR / f"{self.base_name}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("CALL TRANSCRIPT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Date      : {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Scenario  : {self.scenario.get('name')}\n")
            f.write(f"Patient   : {self.scenario.get('persona')}\n")
            f.write(f"Goal      : {self.scenario.get('goal')}\n")
            if self.call_sid:
                f.write(f"Call SID  : {self.call_sid}\n")
            f.write("=" * 60 + "\n\n")

            for turn in self.turns:
                label = "AGENT  " if turn["speaker"] == "agent" else "PATIENT"
                f.write(f"[{label}]: {turn['text']}\n\n")

        logger.info(f"Transcript saved: {path}")

    def _save_json_transcript(self):
        path = TRANSCRIPTS_DIR / f"{self.base_name}.json"
        data = {
            "session_id": self.session_id,
            "call_sid": self.call_sid,
            "scenario": self.scenario,
            "start_time": self.start_time.isoformat(),
            "turns": self.turns,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"JSON transcript saved: {path}")


async def download_recording(recording_url: str, recording_sid: str, base_name: str):
    """
    Download the call recording from Twilio and save as MP3.
    Called via the /recording-complete webhook.
    """
    RECORDINGS_DIR.mkdir(exist_ok=True)
    mp3_path = RECORDINGS_DIR / f"{base_name}_{recording_sid}.mp3"

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{recording_url}.mp3",
                auth=(account_sid, auth_token),
                timeout=60.0,
                follow_redirects=True,
            )
            if response.status_code == 200:
                mp3_path.write_bytes(response.content)
                logger.info(f"Recording saved: {mp3_path}")
                return str(mp3_path)
            else:
                logger.error(f"Failed to download recording: {response.status_code}")
    except Exception as e:
        logger.error(f"Error downloading recording: {e}")

    return None
