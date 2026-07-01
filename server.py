"""
FastAPI server with two responsibilities:
1. /voice/{session_id}   — Twilio webhook, returns TwiML to open a Media Stream
2. /ws/{session_id}      — WebSocket that handles real-time audio (STT → Groq → TTS)
3. /recording-complete   — Twilio callback to download the MP3 after the call ends
"""

import asyncio
import base64
import logging
import os
from typing import Dict, Optional

import httpx
from deepgram import (
    DeepgramClient,
    LiveTranscriptionEvents,
    LiveOptions,
)
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import Connect, VoiceResponse

from patient_brain import PatientBrain
from recorder import CallRecorder, download_recording

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

# Set by main.py once ngrok is running
BASE_URL: str = ""

# session_id → scenario dict  (written by main.py before placing call)
session_store: Dict[str, dict] = {}

# call_sid → base_name for recording download
recording_map: Dict[str, str] = {}


# ---------------------------------------------------------------------------
# Twilio voice webhook — returns TwiML
# ---------------------------------------------------------------------------

@app.post("/voice/{session_id}")
async def voice_webhook(session_id: str, request: Request):
    ws_url = BASE_URL.replace("https://", "wss://").replace("http://", "ws://")

    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=f"{ws_url}/ws/{session_id}")
    response.append(connect)

    logger.info(f"TwiML returned for session {session_id}")
    return Response(content=str(response), media_type="application/xml")


# ---------------------------------------------------------------------------
# Twilio recording callback — downloads MP3 when ready
# ---------------------------------------------------------------------------

@app.post("/recording-complete")
async def recording_complete(request: Request):
    form = await request.form()
    recording_url = form.get("RecordingUrl", "")
    recording_sid = form.get("RecordingSid", "")
    call_sid = form.get("CallSid", "")

    base_name = recording_map.get(call_sid, call_sid)
    logger.info(f"Recording ready for call {call_sid}: {recording_sid}")

    asyncio.create_task(download_recording(recording_url, recording_sid, base_name))
    return Response(content="OK", status_code=200)


# ---------------------------------------------------------------------------
# WebSocket — real-time audio pipeline
# ---------------------------------------------------------------------------

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    scenario = session_store.get(session_id, {
        "name": "unknown",
        "persona": "Patient",
        "goal": "Schedule an appointment",
        "context": "",
        "personality": "Polite",
        "notes": "",
    })

    logger.info(f"WebSocket open | session={session_id} | scenario={scenario.get('name')}")

    patient = PatientBrain(scenario)
    recorder = CallRecorder(session_id, scenario)

    # --- Deepgram STT setup ---
    dg_client = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
    dg_conn = dg_client.listen.asyncwebsocket.v("1")

    stream_sid: Optional[str] = None
    call_sid: Optional[str] = None
    is_bot_speaking = False
    utterance_parts: list[str] = []
    response_queue: asyncio.Queue[Optional[str]] = asyncio.Queue()

    # Deepgram fires this for every transcript chunk
    async def on_transcript(self, result, **kwargs):
        alt = result.channel.alternatives[0]
        text = alt.transcript.strip()
        if text and result.is_final:
            utterance_parts.append(text)
        # speech_final = end of this speech segment
        if result.speech_final and utterance_parts:
            full = " ".join(utterance_parts)
            utterance_parts.clear()
            if not is_bot_speaking:
                await response_queue.put(full)

    dg_conn.on(LiveTranscriptionEvents.Transcript, on_transcript)

    dg_options = LiveOptions(
        model="nova-2-phonecall",
        encoding="mulaw",
        sample_rate=8000,
        channels=1,
        interim_results=True,
        utterance_end_ms="2000",
        vad_events=True,
        smart_format=True,
        endpointing=800,  # wait 800ms of silence before speech_final fires
    )

    started = await dg_conn.start(dg_options)
    if not started:
        logger.error("Deepgram connection failed")
        await websocket.close()
        return

    # --- Deepgram keepalive — prevents timeout while bot is speaking ---
    async def deepgram_keepalive():
        while True:
            await asyncio.sleep(8)
            try:
                await dg_conn.keep_alive()
            except Exception:
                break

    keepalive_task = asyncio.create_task(deepgram_keepalive())

    # --- Response loop: transcript → Groq → TTS → Twilio ---
    async def response_loop():
        nonlocal is_bot_speaking

        while True:
            try:
                agent_text = await asyncio.wait_for(response_queue.get(), timeout=90.0)
            except asyncio.TimeoutError:
                logger.warning("No agent speech for 90s — ending call")
                break

            if agent_text is None:
                break

            print(f"\n  [AGENT  ]: {agent_text}")
            recorder.add_turn("agent", agent_text)

            try:
                patient_text, should_hangup = await patient.respond(agent_text)
                print(f"  [PATIENT]: {patient_text}")
                recorder.add_turn("patient", patient_text)

                audio = await text_to_speech(patient_text)
                if audio and stream_sid:
                    is_bot_speaking = True
                    await send_audio(websocket, stream_sid, audio)
                    is_bot_speaking = False

                if should_hangup:
                    logger.info("Patient ending call")
                    await asyncio.sleep(2)
                    if call_sid:
                        await hang_up(call_sid)
                    break

            except Exception as e:
                logger.error(f"Response loop error: {e}")

    loop_task = asyncio.create_task(response_loop())

    # --- Receive audio from Twilio ---
    try:
        async for raw in websocket.iter_json():
            event = raw.get("event")

            if event == "start":
                stream_sid = raw["start"]["streamSid"]
                call_sid = raw["start"].get("callSid", session_id)
                recorder.set_call_sid(call_sid)
                recording_map[call_sid] = recorder.base_name
                logger.info(f"Stream started | stream={stream_sid} | call={call_sid}")

            elif event == "media":
                if not is_bot_speaking:
                    chunk = base64.b64decode(raw["media"]["payload"])
                    await dg_conn.send(chunk)

            elif event == "stop":
                logger.info("Stream stopped by Twilio")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await response_queue.put(None)
        loop_task.cancel()
        keepalive_task.cancel()
        try:
            await asyncio.gather(loop_task, keepalive_task, return_exceptions=True)
        except Exception:
            pass
        await dg_conn.finish()
        recorder.save()
        logger.info(f"Session {session_id} complete — transcript saved")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def text_to_speech(text: str) -> bytes:
    """Convert text to mulaw 8kHz audio using Deepgram Aura TTS."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.deepgram.com/v1/speak",
                params={
                    "model": "aura-asteria-en",
                    "encoding": "mulaw",
                    "sample_rate": "8000",
                    "container": "none",
                },
                headers={
                    "Authorization": f"Token {os.getenv('DEEPGRAM_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json={"text": text},
                timeout=30.0,
            )
            if resp.status_code == 200:
                return resp.content
            logger.error(f"TTS error {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"TTS exception: {e}")
    return b""


async def send_audio(websocket: WebSocket, stream_sid: str, audio: bytes):
    """Send mulaw audio to Twilio in large chunks.
    Twilio buffers and plays at the correct rate — no sleep needed.
    Large chunks reduce WebSocket overhead and eliminate gap artifacts.
    """
    CHUNK = 3200  # 400ms of audio per message — smooth playback, low overhead
    for i in range(0, len(audio), CHUNK):
        chunk = audio[i : i + CHUNK]
        payload = base64.b64encode(chunk).decode("ascii")
        await websocket.send_json({
            "event": "media",
            "streamSid": stream_sid,
            "media": {"payload": payload},
        })
    # Wait for audio to finish playing before allowing next response
    # Duration = bytes / (8000 bytes/sec for mulaw 8kHz)
    duration = len(audio) / 8000
    await asyncio.sleep(duration)


async def hang_up(call_sid: str):
    """End the call via Twilio REST API."""
    try:
        client = TwilioClient(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN"),
        )
        client.calls(call_sid).update(status="completed")
        logger.info(f"Call {call_sid} ended")
    except Exception as e:
        logger.error(f"Failed to hang up: {e}")
