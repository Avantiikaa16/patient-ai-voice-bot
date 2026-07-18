# Patient Voice Bot

An automated voice bot that calls a medical office AI agent and simulates realistic patient conversations to find bugs and quality issues.

---

## Architecture

The bot uses **Twilio** to place outbound phone calls and stream real-time audio over a WebSocket (Twilio Media Streams). A **FastAPI** server receives that audio and forwards it to **Deepgram** for live speech-to-text transcription. When the agent finishes a sentence, the transcript is sent to **Groq (Llama 3.3 70B)** which generates a realistic patient response in character. That response is converted back to voice using **Deepgram Aura TTS** (mulaw 8kHz — exactly what Twilio expects) and streamed back to the call in real-time.

Each call is driven by a predefined patient scenario (name, goal, personality) so the bot tests a wide range of real-world situations: appointment scheduling, medication refills, insurance questions, edge cases like weekend scheduling, confused elderly callers, and more. After all calls are done, a separate analyzer script reads the saved transcripts and uses Groq again to identify bugs in the agent's responses, outputting a structured markdown bug report.

**Key design choices:**
- Deepgram was chosen for both STT and TTS because it natively handles mulaw 8kHz — the format Twilio uses — eliminating any audio conversion step and reducing latency.
- Groq was chosen for the patient brain because it is free-tier, extremely fast (important for real-time voice), and Llama 3.3 70B produces natural, varied conversational responses.
- Twilio's built-in call recording is used to capture full MP3 audio of both sides, so no manual audio stitching is needed.
- ngrok is started programmatically so the whole system launches with a single command.

---

## Setup

### 1. Prerequisites

- Python 3.10+
- A [Twilio](https://twilio.com) account with an outbound phone number
- A [Deepgram](https://console.deepgram.com) account (free tier)
- A [Groq](https://console.groq.com) account (free tier)
- A [ngrok](https://ngrok.com) account (free tier)

### 2. Install dependencies

```bash
cd voice-patient-bot
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in all values:

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1XXXXXXXXXX
DEEPGRAM_API_KEY=your_deepgram_key
GROQ_API_KEY=your_groq_key
NGROK_AUTH_TOKEN=your_ngrok_token
TARGET_NUMBER=+1XXXXXXXXXX        ← your own phone for testing
PORT=8000
```

---

## Running

### Run all 12 scenarios

```bash
python main.py
```

### Run only the first N calls

```bash
python main.py --calls 3
```

### Run one specific scenario

```bash
python main.py --scenario routine_checkup
```

### Generate bug report from saved transcripts

```bash
python bug_analyzer.py
```

---

## Output

| Location | Contents |
|---|---|
| `transcripts/*.txt` | Human-readable transcript for each call |
| `transcripts/*.json` | Machine-readable transcript (used by bug analyzer) |
| `recordings/*.mp3` | Full call recording (both sides, downloaded from Twilio) |
| `bug_report.md` | Structured bug report with severity levels |

---

## Scenarios tested

| # | Scenario | Patient | Goal |
|---|---|---|---|
| 1 | routine_checkup | Sarah Johnson | Schedule annual physical |
| 2 | medication_refill | Robert Martinez | Refill lisinopril |
| 3 | reschedule_appointment | Emily Chen | Move Monday appointment |
| 4 | cancel_appointment | Michael Brown | Cancel sick visit |
| 5 | insurance_question | Jennifer Williams | Verify BCBS PPO coverage |
| 6 | office_hours_and_location | David Kim | Hours, address, parking |
| 7 | urgent_symptom | Linda Thompson | Severe 2-day headache |
| 8 | new_patient | James Wilson | Register as new patient |
| 9 | multiple_requests | Patricia Davis | Refill + schedule in one call |
| 10 | weekend_scheduling_edge_case | Thomas Anderson | Book Sunday appointment |
| 11 | confused_elderly_caller | Betty Garcia | Schedule with confusion |
| 12 | cost_and_billing_question | Kevin Patel | Out-of-pocket pricing |
