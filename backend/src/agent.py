import asyncio
import logging
import os

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    room_io,
    tokenize,
)
from livekit.plugins import (
    deepgram,
    google,
    murf,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel


# ============================================================
# DATABASE
# ============================================================

try:
    from db import set_opt_out_status
except ModuleNotFoundError:
    from src.db import set_opt_out_status


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger("finsahayak")
logger.setLevel(logging.INFO)


# ============================================================
# ENVIRONMENT
# ============================================================

HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(HERE)

load_dotenv(os.path.join(BACKEND_DIR, ".env.local"))
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

# Also support running directly from backend/
load_dotenv(".env.local")
load_dotenv(".env")


# ============================================================
# FINSAHAYAK SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are FinSahayak, a friendly and helpful AI financial services
voice assistant.

Your track is Financial Services.

You help customers with:
- financial scheme reminders
- eligibility reminders
- important financial deadlines
- general financial information
- simple financial guidance

You can communicate in:
- English
- Hindi
- Hinglish

VOICE RULES:

1. Always be polite, friendly, concise, and clear.

2. Your responses are spoken aloud.
   Do not use markdown, bullet points, emojis, tables, or special formatting.

3. Keep normal responses short, usually one to three conversational sentences.

4. Automatically adapt to the user's language.
   If the user speaks Hindi, respond naturally in Hindi or Hinglish.
   If the user speaks English, respond in English.

5. You are an AI assistant.
   Never pretend to be a human, bank employee, government employee,
   or official financial advisor.

6. Never ask for sensitive financial information.

Never ask for:
- OTP
- UPI PIN
- ATM PIN
- CVV
- password
- bank login credentials
- full card number

7. If the user asks for sensitive information to be shared,
   clearly explain that you do not need that information.

8. Do not provide personalized investment advice.
   You may provide general financial information.

9. Do not promise financial returns.

10. For outbound calls, clearly explain who you are and why you are calling.

11. If the user asks to stop calls or reminders, immediately call
    the opt_out_alerts tool.

Examples:

"stop calling me"
"don't call me again"
"stop these calls"
"I don't want these reminders"
"remove me"
"mujhe call mat karna"
"calls band karo"
"mujhe ye alerts nahi chahiye"

12. After the opt-out tool is called:
    - acknowledge the request
    - confirm politely
    - say goodbye
    - do not continue the conversation

13. The Day 6 outbound use case is a financial scheme deadline reminder.

14. If information is demo/local data, do not falsely describe it as
    live or officially verified information.

15. Never pressure the customer to take a financial action.

Your name is FinSahayak.
You are a safe, concise Financial Services AI voice assistant.
"""


# ============================================================
# OUTBOUND GREETING
# ============================================================

OUTBOUND_GREETING = (
    "Hello, this is FinSahayak, an AI financial services assistant. "
    "I'm calling because a financial scheme you were previously found "
    "eligible for has an upcoming deadline. "
    "If you don't want these reminder calls, just tell me and I'll stop."
)


# ============================================================
# FINSAHAYAK AGENT
# ============================================================

class FinSahayakAgent(Agent):

    def __init__(self) -> None:
        super().__init__(
            instructions=SYSTEM_PROMPT
        )

    @function_tool
    async def opt_out_alerts(
        self,
        context: RunContext,
        reason: str = "",
    ) -> str:
        """
        Store the customer's request to stop future reminder calls.
        """

        logger.info(
            "[FINSAHAYAK] Opt-out requested. Reason: %s",
            reason,
        )

        try:
            set_opt_out_status(
                "sip:sonali721@sip.linphone.org",
                opted_out=True,
            )

            logger.info(
                "[FINSAHAYAK] Opt-out successfully saved."
            )

        except Exception as exc:
            logger.exception(
                "[FINSAHAYAK] Could not save opt-out status: %s",
                exc,
            )

        return (
            "The opt-out request has been recorded. "
            "Tell the customer politely that future reminder calls "
            "will be stopped, then say goodbye."
        )


# Backward compatibility
Assistant = FinSahayakAgent


# ============================================================
# LIVEKIT SERVER
# ============================================================

server = AgentServer()


# ============================================================
# PREWARM
# ============================================================

def prewarm(proc: JobProcess):
    logger.info("[FINSAHAYAK] Loading Silero VAD...")

    proc.userdata["vad"] = silero.VAD.load()

    logger.info("[FINSAHAYAK] Silero VAD loaded.")


server.setup_fnc = prewarm


# ============================================================
# MAIN AGENT SESSION
# ============================================================

@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):

    ctx.log_context_fields = {
        "room": ctx.room.name,
        "agent": "FinSahayak",
        "track": "Financial Services",
    }

    logger.info(
        "[FINSAHAYAK] Starting session."
    )

    logger.info(
        "[FINSAHAYAK] Room: %s",
        ctx.room.name,
    )

    # ========================================================
    # CONNECT TO LIVEKIT FIRST
    # ========================================================

    logger.info(
        "[FINSAHAYAK] Connecting to LiveKit room..."
    )

    await ctx.connect()

    logger.info(
        "[FINSAHAYAK] Connected to LiveKit room."
    )

    # ========================================================
    # WAIT FOR SIP PARTICIPANT
    # ========================================================

    is_sip_call = False
    sip_participant = None

    # Check existing remote participants
    for participant in ctx.room.remote_participants.values():

        logger.info(
            "[FINSAHAYAK] Remote participant detected: %s | kind=%s",
            participant.identity,
            participant.kind,
        )

        if (
            participant.kind
            == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
        ):
            sip_participant = participant
            is_sip_call = True

            logger.info(
                "[FINSAHAYAK] SIP participant already present: %s",
                participant.identity,
            )

            break

    # If SIP participant isn't there yet, wait for it
    if sip_participant is None:

        logger.info(
            "[FINSAHAYAK] Waiting for SIP participant..."
        )

        try:

            sip_participant = await asyncio.wait_for(
                ctx.wait_for_participant(
                    kind=rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                ),
                timeout=30.0,
            )

            is_sip_call = True

            logger.info(
                "[FINSAHAYAK] SIP participant joined: %s",
                sip_participant.identity,
            )

        except asyncio.TimeoutError:

            logger.info(
                "[FINSAHAYAK] No SIP participant detected."
            )

            is_sip_call = False

        except Exception as exc:

            logger.exception(
                "[FINSAHAYAK] Error waiting for SIP participant: %s",
                exc,
            )

    # ========================================================
    # CREATE VOICE SESSION
    # ========================================================

    logger.info(
        "[FINSAHAYAK] Creating voice pipeline..."
    )

    session = AgentSession(

        # ====================================================
        # STT - DEEPGRAM
        # ====================================================

        stt=deepgram.STT(
            model="nova-3",
            language="multi",
        ),

        # ====================================================
        # LLM - GEMINI
        # ====================================================

        llm=google.LLM(
            model="gemini-3.5-flash-lite",
        ),

        # ====================================================
        # TTS - MURF FALCON
        # ====================================================

        tts=murf.TTS(
            voice="Anisha",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(
                min_sentence_len=2
            ),
            text_pacing=True,
        ),

        # ====================================================
        # TURN DETECTION
        # ====================================================

        turn_detection=MultilingualModel(),

        # ====================================================
        # VAD
        # ====================================================

        vad=ctx.proc.userdata["vad"],

        # ====================================================
        # PREEMPTIVE GENERATION
        # ====================================================

        preemptive_generation=True,
    )

    logger.info(
        "[FINSAHAYAK] Voice pipeline created."
    )

    # ========================================================
    # ERROR HANDLER
    # ========================================================

    @session.on("error")
    def on_session_error(event):
        logger.error(
            "[FINSAHAYAK] SESSION ERROR: %s",
            event.error,
        )

    # ========================================================
    # SESSION START
    # ========================================================

    logger.info(
        "[FINSAHAYAK] Starting AgentSession..."
    )

    await session.start(
        agent=FinSahayakAgent(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(

                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if (
                        params.participant.kind
                        == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    )
                    else noise_cancellation.BVC()
                ),

            ),
        ),
    )

    logger.info(
        "[FINSAHAYAK] AgentSession started successfully."
    )

    # ========================================================
    # OUTBOUND GREETING
    # ========================================================

    if is_sip_call:

        logger.info(
            "[FINSAHAYAK] SIP outbound call detected."
        )

        logger.info(
            "[FINSAHAYAK] Sending greeting through Murf Falcon..."
        )

        try:

            # IMPORTANT:
            # session.say() uses the configured Murf TTS.
            #
            # allow_interruptions=False ensures the greeting
            # is not immediately interrupted by telephony noise.

            await session.say(
                OUTBOUND_GREETING,
                allow_interruptions=False,
            )

            logger.info(
                "[FINSAHAYAK] Outbound greeting completed."
            )

        except Exception as exc:

            logger.exception(
                "[FINSAHAYAK] FAILED TO SPEAK GREETING: %s",
                exc,
            )

    else:

        logger.info(
            "[FINSAHAYAK] Browser/inbound session."
        )

        # Browser users can start the conversation normally.


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    cli.run_app(server)