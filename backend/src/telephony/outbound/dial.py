import argparse
import asyncio
import contextlib
import logging
import os
import sys
import uuid

from dotenv import load_dotenv
from livekit import api


# ============================================================
# PATH SETUP
# ============================================================

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
BACKEND_DIR = os.path.dirname(SRC_DIR)

for directory in (SRC_DIR, BACKEND_DIR):
    if directory not in sys.path:
        sys.path.insert(0, directory)


# ============================================================
# DATABASE
# ============================================================

try:
    from src.db import is_opted_out, log_call
except ModuleNotFoundError:
    from db import is_opted_out, log_call


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

logger = logging.getLogger("finsahayak-outbound")


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(os.path.join(BACKEND_DIR, ".env.local"))
load_dotenv(os.path.join(BACKEND_DIR, ".env"))
load_dotenv(".env.local")
load_dotenv(".env")


# ============================================================
# FINSAHAYAK AGENT NAME
# ============================================================

AGENT_NAME = "my-agent"


# ============================================================
# SIP DESTINATION
# ============================================================

def parse_sip_destination(
    to_arg: str,
    default_domain: str = "sip.linphone.org",
) -> tuple[str, str]:
    """
    Convert:

        sonali721

    into:

        sip:sonali721@sip.linphone.org

    Also accepts:

        sip:sonali721@sip.linphone.org
    """

    cleaned = to_arg.strip()

    if cleaned.startswith("sip:"):
        cleaned = cleaned[4:]

    if "@" in cleaned:
        user, domain = cleaned.split("@", 1)
    else:
        user = cleaned
        domain = default_domain

    user = user.strip()
    domain = domain.strip()

    if not user:
        raise ValueError("SIP username cannot be empty.")

    return (
        f"sip:{user}@{domain}",
        user,
    )


# ============================================================
# OUTBOUND CALL
# ============================================================

async def make_outbound_call(destination_arg: str):

    # --------------------------------------------------------
    # Load environment
    # --------------------------------------------------------

    load_dotenv(os.path.join(BACKEND_DIR, ".env.local"))
    load_dotenv(os.path.join(BACKEND_DIR, ".env"))
    load_dotenv(".env.local")
    load_dotenv(".env")

    livekit_url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    trunk_id = os.getenv("LIVEKIT_SIP_OUTBOUND_TRUNK_ID")

    # --------------------------------------------------------
    # Validate environment
    # --------------------------------------------------------

    missing = []

    if not livekit_url:
        missing.append("LIVEKIT_URL")

    if not api_key:
        missing.append("LIVEKIT_API_KEY")

    if not api_secret:
        missing.append("LIVEKIT_API_SECRET")

    if not trunk_id:
        missing.append("LIVEKIT_SIP_OUTBOUND_TRUNK_ID")

    if missing:
        logger.error(
            "Missing environment variables: %s",
            ", ".join(missing),
        )
        sys.exit(1)

    # --------------------------------------------------------
    # Parse SIP destination
    # --------------------------------------------------------

    try:
        sip_destination, sip_user = parse_sip_destination(
            destination_arg
        )
    except ValueError as exc:
        logger.error("Invalid SIP destination: %s", exc)
        sys.exit(1)

    # --------------------------------------------------------
    # Opt-out check
    # --------------------------------------------------------

    try:
        if is_opted_out(sip_destination):
            logger.warning(
                "[OUTBOUND] %s has opted out. "
                "Call will NOT be placed.",
                sip_destination,
            )
            return
    except Exception as exc:
        logger.warning(
            "[OUTBOUND] Could not check opt-out status: %s",
            exc,
        )

    # --------------------------------------------------------
    # Create unique room
    # --------------------------------------------------------

    room_name = (
        f"outbound-finance-alert-"
        f"{uuid.uuid4().hex[:8]}"
    )

    # --------------------------------------------------------
    # Logging
    # --------------------------------------------------------

    logger.info("=" * 60)
    logger.info(
        "[OUTBOUND] Starting FinSahayak outbound call"
    )
    logger.info(
        "[OUTBOUND] Track: Financial Services"
    )
    logger.info(
        "[OUTBOUND] Destination: %s",
        sip_destination,
    )
    logger.info(
        "[OUTBOUND] SIP User: %s",
        sip_user,
    )
    logger.info(
        "[OUTBOUND] Agent: %s",
        AGENT_NAME,
    )
    logger.info(
        "[OUTBOUND] Trunk: %s",
        (
            f"{trunk_id[:6]}..."
            f"{trunk_id[-4:]}"
            if len(trunk_id) > 10
            else trunk_id
        ),
    )
    logger.info(
        "[OUTBOUND] Room: %s",
        room_name,
    )
    logger.info("=" * 60)

    # --------------------------------------------------------
    # Log initiated call
    # --------------------------------------------------------

    try:
        log_call(
            room_name,
            sip_destination,
            "initiated",
            notes="FinSahayak outbound financial reminder",
        )
    except Exception as exc:
        logger.warning(
            "[OUTBOUND] Could not log initiated call: %s",
            exc,
        )

    # ========================================================
    # LIVEKIT API
    # ========================================================

    try:

        async with api.LiveKitAPI(
            url=livekit_url,
            api_key=api_key,
            api_secret=api_secret,
        ) as lkapi:

            # =================================================
            # STEP 1 — DISPATCH FINSAHAYAK
            # =================================================

            logger.info(
                "[OUTBOUND] Dispatching FinSahayak worker..."
            )

            dispatch_request = api.CreateAgentDispatchRequest(
                agent_name=AGENT_NAME,
                room=room_name,
               metadata = (
                  '{"track":"financial_services",'
                  '"call_type":"scheme_deadline_reminder",'
                  '"sip_user":"' + sip_user + '"}'  
                ),
            )

            dispatch = (
                await lkapi.agent_dispatch.create_dispatch(
                    dispatch_request
                )
            )

            logger.info(
                "[OUTBOUND] Agent dispatch created ✓"
            )

            logger.info(
                "[OUTBOUND] Dispatch ID: %s",
                getattr(dispatch, "id", "unknown"),
            )

            logger.info(
                "[OUTBOUND] Agent '%s' assigned to room '%s'",
                AGENT_NAME,
                room_name,
            )

            # =================================================
            # STEP 2 — CREATE SIP PARTICIPANT
            # =================================================

            logger.info(
                "[OUTBOUND] Creating SIP participant..."
            )

            sip_request = api.CreateSIPParticipantRequest(
                sip_trunk_id=trunk_id,
                sip_call_to=sip_user,
                room_name=room_name,
                participant_identity=f"sip-{sip_user}",
                participant_name="FinSahayak Customer",
                wait_until_answered=True,
            )

            participant_info = (
                await lkapi.sip.create_sip_participant(
                    sip_request
                )
            )

            # =================================================
            # STEP 3 — CALL ANSWERED
            # =================================================

            logger.info(
                "[OUTBOUND] Call answered ✓"
            )

            logger.info(
                "[OUTBOUND] SIP Participant ID: %s",
                participant_info.participant_id,
            )

            logger.info(
                "[OUTBOUND] Room: %s",
                room_name,
            )

            logger.info(
                "[OUTBOUND] FinSahayak should now be connected."
            )

            logger.info(
                "[OUTBOUND] Waiting for agent + SIP audio..."
            )

            # -------------------------------------------------
            # Log answered
            # -------------------------------------------------

            try:
                log_call(
                    room_name,
                    sip_destination,
                    "answered",
                    notes=(
                        "SIP participant: "
                        f"{participant_info.participant_id}"
                    ),
                )
            except Exception as exc:
                logger.warning(
                    "[OUTBOUND] Could not log answered call: %s",
                    exc,
                )

            # =================================================
            # KEEP API CONNECTION ALIVE BRIEFLY
            # =================================================

            await asyncio.sleep(5)

            logger.info(
                "[OUTBOUND] Outbound call setup complete."
            )

    except Exception as err:

        error_message = str(err)

        logger.error(
            "[OUTBOUND] Call failed: %s",
            error_message,
        )

        if "busy" in error_message.lower():
            logger.error(
                "[OUTBOUND] Linphone reported BUSY."
            )

        elif (
            "no answer" in error_message.lower()
            or "timeout" in error_message.lower()
        ):
            logger.error(
                "[OUTBOUND] No answer from Linphone."
            )

        elif (
            "not found" in error_message.lower()
            or "404" in error_message
        ):
            logger.error(
                "[OUTBOUND] SIP user not found."
            )

        with contextlib.suppress(Exception):
            log_call(
                room_name,
                sip_destination,
                "failed",
                notes=error_message,
            )

        sys.exit(1)


# ============================================================
# CLI
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "FinSahayak outbound Financial Services "
            "SIP caller."
        )
    )

    parser.add_argument(
        "--to",
        type=str,
        default="sonali721",
        help=(
            "Linphone SIP username or full SIP URI. "
            "Example: sonali721"
        ),
    )

    args = parser.parse_args()

    asyncio.run(
        make_outbound_call(args.to)
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()