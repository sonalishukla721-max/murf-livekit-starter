import logging
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
backend_dir = os.path.dirname(src_dir)

for d in (src_dir, backend_dir):
    if d not in sys.path:
        sys.path.insert(0, d)

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    room_io,
    tokenize,
)
from livekit.plugins import deepgram, google, murf, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

try:
    from src.agent import Assistant
    from src.db import get_farmer_info, log_call
except ModuleNotFoundError:
    from agent import Assistant
    from db import get_farmer_info, log_call

logger = logging.getLogger("outbound-agent")

load_dotenv(os.path.join(backend_dir, ".env.local"))
load_dotenv(os.path.join(backend_dir, ".env"))

server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name="my-agent")
async def outbound_agent_entry(ctx: JobContext):
    logger.info(f"[OUTBOUND] Agent session started for room: {ctx.room.name}")
    ctx.log_context_fields = {"room": ctx.room.name}

    farmer = get_farmer_info("sip:sonali721@sip.linphone.org")
    crop = farmer.get("crop", "Soybean")
    threshold = int(farmer.get("threshold_price", 5000))
    current = int(farmer.get("current_price", 5200))

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=google.LLM(model="gemini-3.5-flash-lite"),
        tts=murf.TTS(
            voice="Anisha",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),
            ),
        ),
    )

    await ctx.connect()
    logger.info(f"[OUTBOUND] Agent connected to room {ctx.room.name}")

    greeting = (
        f"Namaste! Hi, this is KrishiMitra AI, an automated farming assistant. "
        f"I'm calling because the {crop} market price has crossed your threshold of {threshold} rupees "
        f"and is currently around {current} rupees per quintal. "
        f"If you don't want to receive these price alerts, just tell me and I will stop them."
    )

    logger.info("[OUTBOUND] Delivering Farm & Field price alert greeting...")
    await session.say(greeting)
    log_call(
        ctx.room.name,
        "sip:sonali721@sip.linphone.org",
        "answered",
        notes="Opening alert delivered",
    )


if __name__ == "__main__":
    cli.run_app(server)
