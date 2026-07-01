"""
Groq-powered patient brain.
Simulates a realistic patient calling a medical office AI agent.
"""

import os
import logging
from groq import AsyncGroq

logger = logging.getLogger(__name__)

MAX_TURNS = 20  # Force hangup after this many turns


class PatientBrain:
    def __init__(self, scenario: dict):
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.scenario = scenario
        self.history = []
        self.turn_count = 0

        self.system_prompt = f"""You are {scenario["persona"]}, a patient calling a medical office AI assistant on the phone.

YOUR GOAL: {scenario["goal"]}
YOUR BACKGROUND: {scenario.get("context", "Regular patient")}
YOUR PERSONALITY: {scenario.get("personality", "Polite and friendly")}
SCENARIO NOTES: {scenario.get("notes", "")}

STRICT RULES — follow these exactly:
1. Respond ONLY as the patient. Never break character.
2. Keep responses SHORT — 1 to 3 sentences max. This is a phone call.
3. Sound like a real person, not a script. Use natural filler words like "um", "actually", "let me think", "oh right".
4. React naturally to what the agent says. If it asks for your name, give it. If it asks to hold, say okay.
5. Stay focused on your goal but behave naturally along the way.
6. Do NOT repeat the same phrase twice. Vary your wording.
7. Only add [HANGUP] when ALL of these are true: (a) your goal is completely done with no unanswered questions, AND (b) you have explicitly said goodbye or "thank you, goodbye" in your message. Do NOT add [HANGUP] just because something sounds promising or you confirmed one detail — wait until the entire task is wrapped up and you are saying goodbye.
8. If the agent says it cannot help you or gives a dead-end answer with no path forward, politely say "Okay, thank you anyway, goodbye" and add [HANGUP].
9. You are speaking on a phone — no visual content, keep everything audio-friendly.
10. Never mention that you are an AI or a bot."""

    async def respond(self, agent_text: str) -> tuple[str, bool]:
        """
        Given what the agent just said, return the patient's response.
        Returns (response_text, should_hangup).
        """
        self.turn_count += 1

        self.history.append({
            "role": "user",
            "content": agent_text,
        })

        try:
            completion = await self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.history,
                ],
                max_tokens=150,
                temperature=0.7,
            )

            raw_response = completion.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Groq error: {e}")
            raw_response = "I'm sorry, could you repeat that?"

        should_hangup = "[HANGUP]" in raw_response
        clean_response = raw_response.replace("[HANGUP]", "").strip()

        # Force hangup if conversation is running too long
        if self.turn_count >= MAX_TURNS:
            should_hangup = True
            if not clean_response:
                clean_response = "Thank you so much for your help. Goodbye!"

        self.history.append({
            "role": "assistant",
            "content": clean_response,
        })

        logger.info(f"Turn {self.turn_count} | hangup={should_hangup}")
        return clean_response, should_hangup
