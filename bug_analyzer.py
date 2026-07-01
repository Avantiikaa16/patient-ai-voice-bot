"""
Post-call bug analyzer.
Reads all JSON transcripts and uses Groq to identify bugs / quality issues
in the medical AI agent's responses.

Usage:
    python bug_analyzer.py
"""

import asyncio
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import AsyncGroq

load_dotenv()

TRANSCRIPTS_DIR = Path("transcripts")
BUGS_FILE = Path("bug_report.md")

ANALYSIS_PROMPT = """You are a QA engineer evaluating a medical office AI phone agent.

Read the following call transcript between an AI medical agent and a patient.
Then identify any bugs, quality issues, or concerning behaviors in the AGENT's responses.

Look for issues such as:
- Scheduling appointments on days the office is likely closed (weekends, holidays)
- Failing to collect required information (name, date of birth, reason for visit)
- Giving incorrect or inconsistent information
- Not understanding the patient's request
- Cutting off the patient mid-sentence or ignoring part of a request
- Excessive holds or awkward silences
- Failing to handle multi-part requests
- Confusing the patient with jargon or unclear language
- Not escalating urgent medical symptoms appropriately
- Confirming something without actually processing it
- Repeating the same phrase multiple times in a row

Transcript:
{transcript}

Respond ONLY in this JSON format (array of bugs, empty array if none found):
[
  {{
    "severity": "high|medium|low",
    "title": "Short title of the bug",
    "timestamp_approx": "Approximate turn number or 'N/A'",
    "what_happened": "What the agent did",
    "what_should_have_happened": "What it should have done instead"
  }}
]

If no bugs found, return: []
"""


def format_transcript(turns: list) -> str:
    lines = []
    for i, turn in enumerate(turns, 1):
        label = "AGENT" if turn["speaker"] == "agent" else "PATIENT"
        lines.append(f"[Turn {i}] {label}: {turn['text']}")
    return "\n".join(lines)


async def analyze_transcript(client: AsyncGroq, json_path: Path) -> list[dict]:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    if not data.get("turns"):
        return []

    transcript_text = format_transcript(data["turns"])
    scenario = data.get("scenario", {})

    prompt = ANALYSIS_PROMPT.format(transcript=transcript_text)

    for attempt in range(3):
        try:
            completion = await client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.2,
            )
            raw = completion.choices[0].message.content.strip()

            start = raw.find("[")
            end = raw.rfind("]") + 1
            if start != -1 and end > start:
                bugs = json.loads(raw[start:end])
                for bug in bugs:
                    bug["call_scenario"] = scenario.get("name", "unknown")
                    bug["transcript_file"] = json_path.name
                return bugs
            return []
        except Exception as e:
            msg = str(e)
            if "rate_limit_exceeded" in msg and "try again in" in msg:
                # Parse wait time from error message
                import re
                m = re.search(r"try again in (\d+)m([\d.]+)s", msg)
                wait = (int(m.group(1)) * 60 + float(m.group(2)) + 5) if m else 60
                print(f"  Rate limit hit — waiting {int(wait)}s before retry...")
                await asyncio.sleep(wait)
            else:
                print(f"  Error analyzing {json_path.name}: {e}")
                return []

    return []


def write_bug_report(all_bugs: list[dict]):
    high = [b for b in all_bugs if b.get("severity") == "high"]
    medium = [b for b in all_bugs if b.get("severity") == "medium"]
    low = [b for b in all_bugs if b.get("severity") == "low"]

    with open(BUGS_FILE, "w", encoding="utf-8") as f:
        f.write("# Bug Report — Pretty Good AI Voice Agent\n\n")
        f.write(f"Total bugs found: **{len(all_bugs)}**  ")
        f.write(f"(High: {len(high)}, Medium: {len(medium)}, Low: {len(low)})\n\n")
        f.write("---\n\n")

        for severity, bugs in [("High", high), ("Medium", medium), ("Low", low)]:
            if not bugs:
                continue
            f.write(f"## {severity} Severity\n\n")
            for i, bug in enumerate(bugs, 1):
                f.write(f"### {severity[0]}{i}: {bug.get('title', 'Untitled')}\n\n")
                f.write(f"- **Severity**: {bug.get('severity', 'unknown')}\n")
                f.write(f"- **Scenario**: {bug.get('call_scenario', 'unknown')}\n")
                f.write(f"- **Transcript**: `{bug.get('transcript_file', 'unknown')}`\n")
                f.write(f"- **Approx turn**: {bug.get('timestamp_approx', 'N/A')}\n\n")
                f.write(f"**What happened:** {bug.get('what_happened', '')}\n\n")
                f.write(f"**What should have happened:** {bug.get('what_should_have_happened', '')}\n\n")
                f.write("---\n\n")

    print(f"\nBug report saved: {BUGS_FILE}")
    print(f"  High: {len(high)} | Medium: {len(medium)} | Low: {len(low)}")


async def main():
    client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    json_files = sorted(TRANSCRIPTS_DIR.glob("*.json"))
    if not json_files:
        print("No transcript JSON files found in transcripts/")
        print("Run main.py first to generate calls.")
        return

    print(f"Analyzing {len(json_files)} transcript(s)...\n")

    all_bugs = []
    for path in json_files:
        print(f"  → {path.name}")
        bugs = await analyze_transcript(client, path)
        all_bugs.extend(bugs)
        if bugs:
            print(f"     Found {len(bugs)} issue(s)")
        else:
            print(f"     No issues found")

    write_bug_report(all_bugs)


if __name__ == "__main__":
    asyncio.run(main())
