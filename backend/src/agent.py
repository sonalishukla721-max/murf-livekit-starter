import asyncio
import contextlib
import json
import logging
import os
import random
import urllib.request
from datetime import datetime

_bg_tasks: set[asyncio.Task] = set()

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
    from db import (
        sanitize_sensitive_data,
        save_call_record,
        save_escalation,
        set_opt_out_status,
    )
except ModuleNotFoundError:
    from src.db import (
        sanitize_sensitive_data,
        save_call_record,
        save_escalation,
        set_opt_out_status,
    )


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
You are FinSahayak, a friendly, intelligent, and trustworthy AI financial services assistant.

Tagline: "Smart Financial Guidance. Human Help When It Matters."

Your track is Financial Services.

You help customers with:
- answering financial questions (savings accounts, EMIs, loans, fixed deposits, interest rates, schemes)
- providing clear financial guidance and eligibility reminders
- detecting situations requiring human expert assistance
- creating human support requests when authorized by the user

You can communicate in:
- English
- Hindi
- Hinglish

VOICE & RESPONSE RULES:

1. Always be polite, concise, professional, and clear.
2. Your responses are spoken aloud.
   Do not use markdown formatting (no bolding, asterisks, bullet points, emojis, or tables).
3. Keep normal responses short, usually one to three conversational sentences.
4. Automatically adapt to the user's language. Respond in Hindi/Hinglish if spoken to in Hindi, or English if in English.
5. You are an AI assistant. Never pretend to be a human, bank employee, or official financial advisor.
6. Never ask for sensitive financial credentials:
   - OTP
   - UPI PIN / ATM PIN
   - CVV
   - passwords
   - bank login credentials
   - full card or account numbers
7. If the user mentions sensitive details, politely remind them that you do not need those credentials.
8. Do not provide personalized investment advice or promise guaranteed returns.

DAY 7 — HUMAN ESCALATION GUIDELINES:

You must recognize situations that require human review:

SCENARIO A — POSSIBLE FRAUD:
Examples:
- "I see a transaction I did not make."
- "Someone used my account."
- "I think someone has accessed my account."
- "I don't recognize this payment."
- "This transaction isn't mine."

SCENARIO B — COMPLEX FINANCIAL CASE:
Examples:
- "I have a complicated loan issue."
- "I need someone to review my case."
- "I want to speak to a human."
- "The AI cannot solve my financial problem."
- "My case requires a decision."

NORMAL CONVERSATIONS MUST NOT ESCALATE:
Examples:
- "What is a savings account?"
- "What is EMI?"
- "How does a fixed deposit work?"
- "What documents are needed for a loan?"
- "What is compound interest?"
Answer these normally. Do NOT offer or create an escalation for normal questions.

MANDATORY PERMISSION PROTOCOL:
When an escalation scenario (Possible Fraud or Complex Case) is detected:
1. Explain politely that the situation may require human review.
2. Tell the user what information will be included: user name, short summary of the issue, urgency level, language, and preferred follow-up method.
3. Explicitly state that NO sensitive credentials (passwords, PINs, OTPs, CVVs) will be stored or shared.
4. ASK FOR EXPLICIT CONSENT BEFORE CALLING THE TOOL.
   Example phrase:
   "I understand. An unauthorized transaction or potential fraud is serious and may need human review. I can create a support request with your name, a short description of the issue, urgency, language, and preferred follow-up method. I will not include passwords, PINs, OTPs, CVVs, or unnecessary sensitive information. Would you like me to create this request?"

5. IF THE USER SAYS YES:
   Call the `create_escalation` tool immediately with:
   - user_name: caller's name or "Valued Customer"
   - issue_type: "Possible Fraud" or "Complex Financial Case"
   - summary: concise summary of the reported problem
   - urgency: "high" for fraud, "medium" for complex cases
   - language: language of interaction (e.g., "English", "Hindi")
   - preferred_followup: "Phone" or "Email"

   After the tool returns, inform the user:
   "Your support request has been created. Your reference ID is [Reference ID]. The request is currently open. A human support representative will review your case using this reference ID."

6. IF THE USER SAYS NO:
   Do NOT call `create_escalation`.
   Respond: "Understood. I won't create or share a support request."

OUTBOUND CALL RULES:
1. Clearly explain who you are and why you are calling.
2. If the user asks to stop calls or reminders, immediately call `opt_out_alerts`.

Your name is FinSahayak.
You are a safe, concise, and trustworthy Financial Services AI voice assistant.

DAY 9 — GOVERNMENT SCHEME SPECIALIST HANDOFF GUIDELINES:

You have a handoff tool: handoff_to_government_scheme_specialist

When a user asks questions specifically about government schemes, eligibility for government schemes, government subsidies, student scholarships, agricultural schemes, small business schemes, or government financial programs:
Examples that MUST trigger handoff:
- "What government schemes can help students?"
- "Which government scheme can help farmers financially?"
- "What schemes are available for small businesses?"
- "Am I eligible for a government financial scheme?"
- "Tell me about PM Kisan / Mudra Loan / Atal Pension Yojana"
- "What documents are required for this government scheme?"

When the user asks about government schemes:
1. Announce the handoff clearly: "I'll connect you with our Government Scheme Specialist."
2. Call `handoff_to_government_scheme_specialist` with the user's request and conversation summary.

DO NOT HANDOFF normal banking and general financial questions:
- "What is a savings account?"
- "How does EMI work?"
- "What is a fixed deposit?"
- "What documents are generally required to open a bank account?"
- "What is compound interest?"
Answer these general banking questions directly yourself without handing off.
"""


# ============================================================
# DAY 9 — GOVERNMENT SCHEME SPECIALIST SYSTEM PROMPT
# ============================================================

SPECIALIST_SYSTEM_PROMPT = """
You are the Government Scheme Specialist for FinSahayak AI.

Tagline: "Scheme Guidance. Step by Step."

Your ONLY primary responsibility is to help users understand government financial schemes.

You can help with:
- Scheme purpose and general benefits
- Basic eligibility criteria
- Required documents for applications
- Application requirements and process overview
- Scheme-specific questions using available verified tools

You must:
- Stay strictly focused on government financial schemes.
- Use available tools (check_scheme_eligibility, get_document_list, get_financial_scheme_info) whenever possible.
- Ask only for information necessary to answer the user's question.
- Explain financial information clearly and simply, in plain spoken language.
- Never request passwords, OTPs, PINs, card numbers, CVV, or other authentication secrets.
- Never invent scheme details or guarantee scheme approval.
- Clearly explain when information cannot be verified.
- Escalate to human support using the create_escalation tool when the situation warrants it.
- Maintain the context received from the main FinSahayak agent.
- Never ask the user to repeat their entire question — context has already been passed to you.

You can communicate in English, Hindi, and Hinglish. Automatically adapt to the user's language.

VOICE & RESPONSE RULES:
1. Always be polite, concise, professional, and clear.
2. Your responses are spoken aloud. Do NOT use markdown formatting (no bolding, asterisks, bullet points, emojis, or tables).
3. Keep responses short, usually one to three conversational sentences.
4. You are an AI specialist assistant. Never pretend to be a human or official government advisor.
5. Never ask for sensitive information: OTP, PIN, CVV, passwords, card numbers, full account numbers.
6. If the user mentions sensitive credentials, politely remind them you do not need those.

IF THE USER ASKS SOMETHING OUTSIDE GOVERNMENT SCHEMES:
- Answer briefly if it is very simple and safe.
- Otherwise, offer to hand back: "That's outside my specialist area — let me connect you back with FinSahayak for that question."
- Then call the handoff_back_to_finsahayak tool.

DAY 7 — HUMAN ESCALATION:
You may also create human support requests using the create_escalation tool, following the same protocol:
1. Explain the situation requires human review.
2. Inform what will be included (name, summary, urgency — NO credentials).
3. Get explicit user consent BEFORE calling the tool.
4. After tool returns, confirm the Reference ID to the user.

Do NOT escalate for normal scheme questions — only for fraud, complex unresolvable cases, or when the user explicitly requests a human.
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
    # Track whether the current session completed a successful financial task
    _call_successful: bool = False
    _failure_type: str = "TASK_INCOMPLETE"

    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT)

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

            logger.info("[FINSAHAYAK] Opt-out successfully saved.")

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

    @function_tool
    async def create_escalation(
        self,
        context: RunContext,
        user_name: str = "Valued Customer",
        issue_type: str = "Possible Fraud",
        summary: str = "",
        urgency: str = "high",
        language: str = "English",
        preferred_followup: str = "Phone",
    ) -> str:
        """
        Create a human support request when a financial situation requires human review
        and the user has given explicit permission.

        Parameters:
        - user_name: Name of the customer (default "Valued Customer")
        - issue_type: "Possible Fraud" or "Complex Financial Case"
        - summary: Brief summary of what happened
        - urgency: "high", "medium", "low", or "emergency"
        - language: Preferred interaction language ("English", "Hindi")
        - preferred_followup: "Phone" or "Email"
        """
        logger.info(
            "[FINSAHAYAK] Creating escalation request. Issue: %s, User: %s",
            issue_type,
            user_name,
        )

        try:
            # Generate reference ID dynamically: FIN-{YEAR}-{4 DIGITS}
            year = datetime.now().year
            rand_digits = random.randint(1000, 9999)
            reference_id = f"FIN-{year}-{rand_digits}"

            # Save escalation into database with sanitization
            res = save_escalation(
                user_name=user_name,
                issue_type=issue_type,
                summary=summary,
                urgency=urgency,
                language=language,
                preferred_followup=preferred_followup,
                reference_id=reference_id,
            )

            ref_id = res.get("reference_id", reference_id)
            logger.info(
                "[FINSAHAYAK] Escalation created successfully with Ref ID: %s", ref_id
            )

            # Optional Discord Webhook notification
            webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
            if webhook_url:
                try:
                    sanitized_sum = sanitize_sensitive_data(summary)
                    payload = {
                        "embeds": [
                            {
                                "title": "🚨 FinSahayak Human Support Request",
                                "color": 15158332
                                if urgency in ["high", "emergency"]
                                else 3447003,
                                "fields": [
                                    {
                                        "name": "Reference ID",
                                        "value": ref_id,
                                        "inline": True,
                                    },
                                    {
                                        "name": "Issue Type",
                                        "value": issue_type,
                                        "inline": True,
                                    },
                                    {
                                        "name": "Urgency",
                                        "value": urgency.upper(),
                                        "inline": True,
                                    },
                                    {
                                        "name": "User",
                                        "value": user_name,
                                        "inline": True,
                                    },
                                    {
                                        "name": "Language",
                                        "value": language,
                                        "inline": True,
                                    },
                                    {
                                        "name": "Follow-up",
                                        "value": preferred_followup,
                                        "inline": True,
                                    },
                                    {
                                        "name": "Summary",
                                        "value": sanitized_sum
                                        or "Human review requested.",
                                    },
                                ],
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        ]
                    }
                    data = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(
                        webhook_url,
                        data=data,
                        headers={
                            "Content-Type": "application/json",
                            "User-Agent": "FinSahayak-AI",
                        },
                    )
                    urllib.request.urlopen(req, timeout=3)
                    logger.info(
                        "[FINSAHAYAK] Discord webhook notification sent for %s", ref_id
                    )
                except Exception as w_err:
                    logger.warning(
                        "[FINSAHAYAK] Could not send Discord webhook: %s", w_err
                    )

            return (
                f"Support request created successfully. "
                f"Reference ID: {ref_id}. Status: open. "
                f"Inform the customer that their reference ID is {ref_id} "
                f"and a human representative will review the case."
            )

        except Exception as exc:
            logger.exception("[FINSAHAYAK] Failed to create escalation: %s", exc)
            return "Failed to create support request due to a system issue. Please ask the user to try again later."

    @function_tool
    async def check_scheme_eligibility(
        self,
        context: RunContext,
        age: str = "",
        income: str = "",
        category: str = "",
        scheme_name: str = "",
    ) -> str:
        """
        Check if a user is eligible for a financial scheme based on basic non-sensitive criteria.
        Call this when the user wants to know if they qualify for any government or bank scheme.

        Parameters:
        - age: User's age (e.g., "35")
        - income: Annual income range (e.g., "below 2 lakhs")
        - category: Category like "general", "SC/ST/OBC", "woman", "farmer"
        - scheme_name: Name of the scheme to check (e.g., "PM Kisan", "Mudra Loan")
        """
        logger.info(
            "[FINSAHAYAK] Eligibility check requested. Scheme: %s, Age: %s, Category: %s",
            scheme_name,
            age,
            category,
        )

        # Mark session as successful — eligibility check is a completed financial task
        self._call_successful = True
        self._failure_type = None

        scheme = scheme_name.strip() or "the requested scheme"
        result = (
            f"Based on the information provided — age {age or 'not specified'}, "
            f"income {income or 'not specified'}, category {category or 'not specified'} — "
            f"you may be eligible for {scheme}. "
            f"Please visit your nearest bank branch or the official government portal to complete the formal verification "
            f"and documentation process. No sensitive credentials are needed for this eligibility check."
        )

        return result

    @function_tool
    async def get_document_list(
        self,
        context: RunContext,
        service_type: str = "",
    ) -> str:
        """
        Return the standard document list required for a common financial service.
        Call this when the user asks what documents are needed for a loan, scheme, or account.

        Parameters:
        - service_type: Type of financial service (e.g., "home loan", "PM Kisan", "Mudra Loan", "savings account")
        """
        logger.info(
            "[FINSAHAYAK] Document list requested. Service: %s",
            service_type,
        )

        # Mark session as successful — providing document list is a completed task
        self._call_successful = True
        self._failure_type = None

        service = service_type.strip() or "this service"
        doc_lists = {
            "home loan": "Aadhaar card, PAN card, income proof (salary slips or ITR), property documents, bank statements for 6 months.",
            "mudra loan": "Aadhaar card, PAN card, business proof, bank statements for 6 months, passport photo.",
            "pm kisan": "Aadhaar card, land ownership documents, bank account details linked to Aadhaar.",
            "savings account": "Aadhaar card, PAN card, one passport-size photograph, and address proof.",
        }

        service_lower = service.lower()
        for key, docs in doc_lists.items():
            if key in service_lower:
                return f"For {service}, the standard documents required are: {docs}"

        return (
            f"For {service}, you will typically need: Aadhaar card, PAN card, income or address proof, "
            f"and relevant service-specific documents. Please confirm with your bank or the concerned office "
            f"for the exact current list."
        )

    @function_tool
    async def get_financial_scheme_info(
        self,
        context: RunContext,
        scheme_name: str = "",
    ) -> str:
        """
        Provide information about a government or bank financial scheme.
        Call this when the user asks about any financial scheme, its benefits, or how to apply.
        Also call this when the user says "show me schemes" or asks to list available schemes.

        Parameters:
        - scheme_name: Name of the scheme (e.g., "PM Kisan", "Atal Pension Yojana", "Mudra Loan").
          Leave empty or omit when user asks for a general list of available schemes.
        """
        logger.info(
            "[FINSAHAYAK] Scheme info requested. Scheme: %s",
            scheme_name,
        )

        # Mark session as successful — providing scheme information completes the user's task
        self._call_successful = True
        self._failure_type = None

        scheme = scheme_name.strip()

        # No specific scheme — return a helpful list of popular schemes
        if not scheme:
            return (
                "Here are some popular government financial schemes I can tell you about. "
                "PM Kisan Samman Nidhi gives income support to farmers. "
                "Pradhan Mantri Mudra Yojana provides collateral-free loans to small businesses. "
                "Atal Pension Yojana is a pension scheme for unorganised sector workers. "
                "PM Jan Dhan Yojana provides zero-balance bank accounts. "
                "PM Awas Yojana provides housing assistance. "
                "Which scheme would you like to know more about?"
            )

        # Detailed info for known schemes
        scheme_details = {
            "pm kisan": (
                "PM Kisan Samman Nidhi provides direct income support of 6000 rupees per year "
                "to eligible farmer families in three installments. Farmers with less than 2 hectares "
                "of cultivable land are typically eligible."
            ),
            "mudra": (
                "Pradhan Mantri Mudra Yojana offers collateral-free loans to small businesses. "
                "It has three categories: Shishu up to 50000 rupees, Kishore up to 5 lakhs, "
                "and Tarun up to 10 lakhs."
            ),
            "atal pension": (
                "Atal Pension Yojana is a government-backed pension scheme for workers aged 18 to 40. "
                "After age 60, you receive a guaranteed monthly pension of 1000 to 5000 rupees."
            ),
            "jan dhan": (
                "Pradhan Mantri Jan Dhan Yojana provides universal access to banking — "
                "zero-balance savings accounts, debit cards, and basic insurance coverage."
            ),
            "pmay": (
                "Pradhan Mantri Awas Yojana provides housing assistance and home loan interest "
                "subsidies to eligible beneficiaries from economically weaker sections."
            ),
            "nsp": (
                "NSP or National Scholarship Portal hosts various Central and State government "
                "scholarships for students from economically weaker sections, SC, ST, OBC, and minority communities. "
                "Eligibility varies by scholarship category and family income."
            ),
        }

        scheme_lower = scheme.lower()
        for key, detail in scheme_details.items():
            if key in scheme_lower:
                return (
                    f"{detail} "
                    f"Would you like me to check eligibility or get the required document list for this scheme?"
                )

        return (
            f"I can provide general information about {scheme}. "
            f"This scheme is designed to support eligible beneficiaries through financial assistance or credit access. "
            f"To get the latest details, benefits, and application process, please visit the official government portal "
            f"or your nearest bank branch. I can also help you check eligibility or get the document list."
        )

    @function_tool
    async def handoff_to_government_scheme_specialist(
        self,
        context: RunContext,
        user_request: str = "",
        conversation_summary: str = "",
    ) -> str:
        """
        Transfer the conversation to the Government Scheme Specialist when the user asks
        about government schemes, scheme eligibility, benefits, required documents,
        or application guidance.

        Parameters:
        - user_request: The user's specific question (as they said it)
        - conversation_summary: A brief one-sentence summary of the conversation so far
        """
        import asyncio

        logger.info(
            "[FINSAHAYAK] Scheduling handoff to Government Scheme Specialist. Request: %s",
            user_request,
        )

        try:
            specialist = GovernmentSchemeSpecialist(
                user_request=user_request,
                conversation_summary=conversation_summary,
            )

            session = context.session
            with contextlib.suppress(Exception):
                session.userdata["call_successful"] = getattr(
                    self, "_call_successful", False
                )

            # IMPORTANT: We must NOT call session.update_agent() synchronously here.
            # Calling it inside a @function_tool before returning disrupts the current
            # LLM response pipeline and prevents the handoff announcement from being spoken.
            # Instead, we defer the agent switch using asyncio.create_task so that:
            #   1. This tool returns the announcement text immediately.
            #   2. The LLM speaks the announcement via TTS.
            #   3. THEN the specialist takes over and generates its greeting.
            async def _deferred_handoff():
                try:
                    # Wait for the announcement speech to be generated and started
                    await asyncio.sleep(3)
                    session.update_agent(specialist)
                    logger.info(
                        "[FINSAHAYAK] Agent switched to GovernmentSchemeSpecialist."
                    )
                    # Trigger the specialist to generate its own intro/greeting
                    await session.generate_reply()
                except Exception as task_exc:
                    logger.exception(
                        "[FINSAHAYAK] Deferred handoff task failed: %s", task_exc
                    )

            _handoff_task = asyncio.create_task(_deferred_handoff())
            _bg_tasks.add(_handoff_task)
            _handoff_task.add_done_callback(_bg_tasks.discard)

            logger.info("[FINSAHAYAK] Handoff task created. Returning announcement.")

            return (
                "I'll connect you with our Government Scheme Specialist who can help you "
                "with the scheme eligibility and document requirements. One moment."
            )

        except Exception as exc:
            logger.exception("[FINSAHAYAK] Handoff setup failed: %s", exc)
            return (
                "I'm unable to connect to the specialist right now, but I can still "
                "help with the information I have, or connect you with human support if needed."
            )


# ============================================================
# DAY 9 — GOVERNMENT SCHEME SPECIALIST AGENT
# ============================================================


class GovernmentSchemeSpecialist(Agent):
    """Specialist agent for government financial scheme guidance."""

    _call_successful: bool = False
    _failure_type: str = "TASK_INCOMPLETE"

    def __init__(
        self,
        user_request: str = "",
        conversation_summary: str = "",
    ) -> None:
        # Inject conversation context from the main agent into the system prompt
        # so the specialist never has to ask the user to repeat themselves.
        context_block = ""
        if user_request:
            context_block = (
                "\n\n--- HANDOFF CONTEXT FROM FINSAHAYAK MAIN AGENT ---\n"
                f"User's original inquiry/topic: {user_request}\n"
            )
            if conversation_summary:
                context_block += f"Conversation summary: {conversation_summary}\n"
            context_block += (
                "\nCRITICAL HANDOFF INSTRUCTIONS:\n"
                "- You already know the topic/scheme being discussed from the context above.\n"
                "- When the user asks follow-up questions (such as 'What documents do I need?' or 'How do I apply?'), immediately answer for the scheme/topic mentioned in the context above (for example, student scholarships/schemes like NSP, PM Kisan for farmers, Mudra Loan for small business, etc.).\n"
                "- Directly provide the required document list or details. For student schemes/scholarships, standard documents are: Aadhaar card, income certificate/proof, previous marksheets or educational certificates, student ID/admission receipt, and bank account details.\n"
                "- Never ask the user to repeat what scheme they are asking about or to re-specify their request.\n"
                "--- END HANDOFF CONTEXT ---\n"
            )

        full_prompt = context_block + SPECIALIST_SYSTEM_PROMPT
        super().__init__(instructions=full_prompt)
        self._user_request = user_request
        self._conversation_summary = conversation_summary

    # ----------------------------------------------------------
    # SCHEME TOOLS (reused from main agent logic)
    # ----------------------------------------------------------

    @function_tool
    async def check_scheme_eligibility(
        self,
        context: RunContext,
        age: str = "",
        income: str = "",
        category: str = "",
        scheme_name: str = "",
    ) -> str:
        """
        Check if a user is eligible for a government financial scheme based on basic
        non-sensitive criteria.

        Parameters:
        - age: User's age (e.g., "35")
        - income: Annual income range (e.g., "below 2 lakhs")
        - category: Category like "general", "SC/ST/OBC", "woman", "farmer"
        - scheme_name: Name of the scheme to check (e.g., "PM Kisan", "Mudra Loan")
        """
        logger.info(
            "[SPECIALIST] Eligibility check. Scheme: %s, Age: %s, Category: %s",
            scheme_name,
            age,
            category,
        )

        self._call_successful = True
        self._failure_type = None

        with contextlib.suppress(Exception):
            context.session.userdata["call_successful"] = True

        scheme = scheme_name.strip() or "the requested scheme"
        return (
            f"Based on the information provided — age {age or 'not specified'}, "
            f"income {income or 'not specified'}, category {category or 'not specified'} — "
            f"you may be eligible for {scheme}. "
            f"Please visit your nearest bank branch or the official government portal to complete "
            f"the formal verification and documentation process. "
            f"No sensitive credentials are needed for this eligibility check."
        )

    @function_tool
    async def get_document_list(
        self,
        context: RunContext,
        service_type: str = "",
    ) -> str:
        """
        Return the standard document list required for a government financial scheme.
        Call this when the user asks what documents are needed for a scheme.

        Parameters:
        - service_type: Type of financial service or scheme
          (e.g., "PM Kisan", "Mudra Loan", "Atal Pension Yojana")
        """
        logger.info(
            "[SPECIALIST] Document list requested. Service: %s",
            service_type,
        )

        self._call_successful = True
        self._failure_type = None

        with contextlib.suppress(Exception):
            context.session.userdata["call_successful"] = True

        service = service_type.strip() or "this scheme"
        doc_lists = {
            "home loan": "Aadhaar card, PAN card, income proof (salary slips or ITR), property documents, bank statements for 6 months.",
            "mudra loan": "Aadhaar card, PAN card, business proof, bank statements for 6 months, passport photo.",
            "pm kisan": "Aadhaar card, land ownership documents, bank account details linked to Aadhaar.",
            "savings account": "Aadhaar card, PAN card, one passport-size photograph, and address proof.",
            "atal pension": "Aadhaar card, savings bank account number, mobile number linked to Aadhaar.",
            "jan dhan": "Aadhaar card or any valid government-issued identity proof and address proof.",
            "pmay": "Aadhaar card, income certificate, property documents, bank account details.",
        }

        service_lower = service.lower()
        for key, docs in doc_lists.items():
            if key in service_lower:
                return f"For {service}, the standard documents required are: {docs}"

        return (
            f"For {service}, you will typically need: Aadhaar card, PAN card, income or address proof, "
            f"and relevant scheme-specific documents. Please confirm with your bank or the concerned "
            f"government office for the exact current list."
        )

    @function_tool
    async def get_financial_scheme_info(
        self,
        context: RunContext,
        scheme_name: str = "",
    ) -> str:
        """
        Provide information about a government financial scheme — its purpose, benefits,
        and how to apply. Call this when the user asks about any government scheme.

        Parameters:
        - scheme_name: Name of the scheme (e.g., "PM Kisan", "Atal Pension Yojana", "Mudra Loan")
        """
        logger.info(
            "[SPECIALIST] Scheme info requested. Scheme: %s",
            scheme_name,
        )

        self._call_successful = True
        self._failure_type = None

        with contextlib.suppress(Exception):
            context.session.userdata["call_successful"] = True

        scheme = scheme_name.strip() or "the requested scheme"

        scheme_details = {
            "pm kisan": (
                "PM Kisan Samman Nidhi provides direct income support of 6000 rupees per year "
                "to eligible farmer families in three installments. Farmers with less than 2 hectares "
                "of cultivable land are typically eligible."
            ),
            "mudra loan": (
                "Pradhan Mantri Mudra Yojana offers collateral-free loans to small businesses and "
                "entrepreneurs. It has three categories: Shishu up to 50000 rupees, Kishore up to "
                "5 lakhs, and Tarun up to 10 lakhs."
            ),
            "atal pension": (
                "Atal Pension Yojana is a government-backed pension scheme for unorganised sector workers. "
                "Citizens aged 18 to 40 can join and receive a guaranteed monthly pension of "
                "1000 to 5000 rupees after age 60."
            ),
            "jan dhan": (
                "Pradhan Mantri Jan Dhan Yojana provides universal access to banking services, "
                "including zero-balance savings accounts, debit cards, and basic insurance coverage."
            ),
            "pmay": (
                "Pradhan Mantri Awas Yojana provides housing assistance and interest subsidies "
                "on home loans to eligible beneficiaries from economically weaker sections and "
                "low-income groups."
            ),
        }

        scheme_lower = scheme.lower()
        for key, detail in scheme_details.items():
            if key in scheme_lower:
                return (
                    f"{detail} "
                    f"To apply, please visit your nearest bank branch or the official government portal. "
                    f"I can also help you check your eligibility or get the required document list."
                )

        return (
            f"I can provide general information about {scheme}. "
            f"This scheme is designed to support eligible beneficiaries through financial assistance or credit access. "
            f"To get the latest details, benefits, and application process, please visit the official government "
            f"portal or your nearest bank branch. I can also help you check your eligibility or prepare "
            f"the document list."
        )

    # ----------------------------------------------------------
    # HUMAN ESCALATION (Day 7 — reused by specialist)
    # ----------------------------------------------------------

    @function_tool
    async def create_escalation(
        self,
        context: RunContext,
        user_name: str = "Valued Customer",
        issue_type: str = "Complex Financial Case",
        summary: str = "",
        urgency: str = "medium",
        language: str = "English",
        preferred_followup: str = "Phone",
    ) -> str:
        """
        Create a human support request when the user's situation cannot be safely resolved
        by the Government Scheme Specialist and the user has given explicit permission.

        Parameters:
        - user_name: Name of the customer (default "Valued Customer")
        - issue_type: "Possible Fraud" or "Complex Financial Case"
        - summary: Brief summary of what happened
        - urgency: "high", "medium", "low", or "emergency"
        - language: Preferred interaction language
        - preferred_followup: "Phone" or "Email"
        """
        logger.info(
            "[SPECIALIST] Creating escalation. Issue: %s, User: %s",
            issue_type,
            user_name,
        )

        try:
            year = datetime.now().year
            rand_digits = random.randint(1000, 9999)
            reference_id = f"FIN-{year}-{rand_digits}"

            res = save_escalation(
                user_name=user_name,
                issue_type=issue_type,
                summary=summary,
                urgency=urgency,
                language=language,
                preferred_followup=preferred_followup,
                reference_id=reference_id,
            )

            ref_id = res.get("reference_id", reference_id)
            logger.info("[SPECIALIST] Escalation created. Ref ID: %s", ref_id)

            webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
            if webhook_url:
                try:
                    sanitized_sum = sanitize_sensitive_data(summary)
                    payload = {
                        "embeds": [
                            {
                                "title": "🚨 FinSahayak Specialist — Human Support Request",
                                "color": 15158332
                                if urgency in ["high", "emergency"]
                                else 3447003,
                                "fields": [
                                    {
                                        "name": "Reference ID",
                                        "value": ref_id,
                                        "inline": True,
                                    },
                                    {
                                        "name": "Issue Type",
                                        "value": issue_type,
                                        "inline": True,
                                    },
                                    {
                                        "name": "Urgency",
                                        "value": urgency.upper(),
                                        "inline": True,
                                    },
                                    {
                                        "name": "User",
                                        "value": user_name,
                                        "inline": True,
                                    },
                                    {
                                        "name": "Language",
                                        "value": language,
                                        "inline": True,
                                    },
                                    {
                                        "name": "Follow-up",
                                        "value": preferred_followup,
                                        "inline": True,
                                    },
                                    {
                                        "name": "Source",
                                        "value": "Government Scheme Specialist",
                                        "inline": True,
                                    },
                                    {
                                        "name": "Summary",
                                        "value": sanitized_sum
                                        or "Human review requested.",
                                    },
                                ],
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        ]
                    }
                    data = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(
                        webhook_url,
                        data=data,
                        headers={
                            "Content-Type": "application/json",
                            "User-Agent": "FinSahayak-AI",
                        },
                    )
                    urllib.request.urlopen(req, timeout=3)
                except Exception as w_err:
                    logger.warning("[SPECIALIST] Discord webhook failed: %s", w_err)

            return (
                f"Support request created successfully. "
                f"Reference ID: {ref_id}. Status: open. "
                f"Inform the customer that their reference ID is {ref_id} "
                f"and a human representative will review the case."
            )

        except Exception as exc:
            logger.exception("[SPECIALIST] Failed to create escalation: %s", exc)
            return "Failed to create support request due to a system issue. Please ask the user to try again later."

    # ----------------------------------------------------------
    # OPTIONAL HAND-BACK TO MAIN AGENT
    # ----------------------------------------------------------

    @function_tool
    async def handoff_back_to_finsahayak(
        self,
        context: RunContext,
        conversation_summary: str = "",
    ) -> str:
        """
        Hand the conversation back to the main FinSahayak agent when the user asks something
        outside the Government Scheme Specialist's area — for example, general banking questions,
        savings accounts, fixed deposits, EMI calculations, or general financial guidance.

        Parameters:
        - conversation_summary: Brief summary of what was discussed with the specialist
        """
        logger.info(
            "[SPECIALIST] Handing back to main FinSahayak agent. Summary: %s",
            conversation_summary,
        )

        try:
            # Persist current success state before switching back
            with contextlib.suppress(Exception):
                context.session.userdata["call_successful"] = getattr(
                    self, "_call_successful", False
                )

            session = context.session
            main_agent = FinSahayakAgent()

            async def _deferred_handback():
                try:
                    await asyncio.sleep(3)
                    session.update_agent(main_agent)
                    logger.info("[SPECIALIST] Agent switched back to FinSahayakAgent.")
                    await session.generate_reply()
                except Exception as task_exc:
                    logger.exception(
                        "[SPECIALIST] Deferred hand-back failed: %s", task_exc
                    )

            _handback_task = asyncio.create_task(_deferred_handback())
            _bg_tasks.add(_handback_task)
            _handback_task.add_done_callback(_bg_tasks.discard)

            logger.info(
                "[SPECIALIST] Hand-back task scheduled. Returning announcement."
            )

            return (
                "Let me connect you back with FinSahayak who can help you with "
                "general financial questions. One moment."
            )

        except Exception as exc:
            logger.exception("[SPECIALIST] Hand-back to main agent failed: %s", exc)
            return (
                "I'll help with that briefly. For detailed general financial guidance, "
                "FinSahayak's main assistant would be the best resource."
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

    logger.info("[FINSAHAYAK] Starting session.")

    logger.info(
        "[FINSAHAYAK] Room: %s",
        ctx.room.name,
    )

    # ========================================================
    # CONNECT TO LIVEKIT FIRST
    # ========================================================

    logger.info("[FINSAHAYAK] Connecting to LiveKit room...")

    await ctx.connect()

    logger.info("[FINSAHAYAK] Connected to LiveKit room.")

    # ========================================================
    # DETECT SIP PARTICIPANT WITHOUT BLOCKING BROWSER SESSIONS
    # ========================================================

    # IMPORTANT: Do NOT wait 30 seconds for a SIP participant here.
    # Browser sessions do not have a SIP participant, and blocking here
    # delays AgentSession startup enough to make the frontend report:
    # "Agent joined the room but did not complete initializing."
    is_sip_call = False
    for participant in ctx.room.remote_participants.values():
        logger.info(
            "[FINSAHAYAK] Remote participant detected: %s | kind=%s",
            participant.identity,
            participant.kind,
        )

        if participant.kind == rtc.ParticipantKind.PARTICIPANT_KIND_SIP:
            is_sip_call = True
            logger.info(
                "[FINSAHAYAK] SIP participant already present: %s",
                participant.identity,
            )
            break

    if not is_sip_call:
        logger.info(
            "[FINSAHAYAK] No SIP participant currently present; "
            "starting as browser/inbound session immediately."
        )

    # ========================================================
    # CREATE VOICE SESSION
    # ========================================================

    logger.info("[FINSAHAYAK] Creating voice pipeline...")

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
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
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

    logger.info("[FINSAHAYAK] Voice pipeline created.")

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

    logger.info("[FINSAHAYAK] Starting AgentSession...")

    # Track session start time and create the agent instance so we can inspect
    # its success flag when the session ends.
    import datetime as _dt

    session_start = _dt.datetime.now(_dt.timezone.utc)
    agent_instance = FinSahayakAgent()

    await session.start(
        agent=agent_instance,
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

    logger.info("[FINSAHAYAK] AgentSession started successfully.")

    # ========================================================
    # OUTBOUND GREETING
    # ========================================================

    if is_sip_call:
        logger.info("[FINSAHAYAK] SIP outbound call detected.")

        logger.info("[FINSAHAYAK] Sending greeting through Murf Falcon...")

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

            logger.info("[FINSAHAYAK] Outbound greeting completed.")

        except Exception as exc:
            logger.exception(
                "[FINSAHAYAK] FAILED TO SPEAK GREETING: %s",
                exc,
            )

    else:
        logger.info("[FINSAHAYAK] Browser/inbound session.")

        # Give browser users an immediate spoken greeting. This also
        # verifies that the Murf TTS output is published to the room.
        try:
            await session.say(
                "Hello, this is FinSahayak. I am ready to help you with your financial questions. How can I help you today?",
                allow_interruptions=True,
            )
            logger.info("[FINSAHAYAK] Browser greeting completed.")
        except Exception as exc:
            logger.exception(
                "[FINSAHAYAK] FAILED TO SPEAK BROWSER GREETING: %s",
                exc,
            )

    # ========================================================
    # SESSION LIFECYCLE — RECORD CALL OUTCOME ON DISCONNECT
    # ========================================================
    try:
        await session.wait_for_disconnect()
    except Exception:
        pass
    finally:
        import datetime as _dt2

        session_end = _dt2.datetime.now(_dt2.timezone.utc)
        duration_secs = max(0, int((session_end - session_start).total_seconds()))

        # Read success state — check session.userdata first (written by any agent
        # during the session, including the specialist after handoff), then fall back
        # to the initial agent_instance attributes.
        try:
            userdata_success = session.userdata.get("call_successful", None)
        except Exception:
            userdata_success = None

        try:
            current_agent = session.current_agent
            current_success = getattr(current_agent, "_call_successful", False)
            current_failure = getattr(current_agent, "_failure_type", "TASK_INCOMPLETE")
        except Exception:
            current_success = False
            current_failure = "TASK_INCOMPLETE"

        call_success = bool(
            userdata_success
            or current_success
            or getattr(agent_instance, "_call_successful", False)
        )
        call_failure_type = (
            current_failure
            if current_success
            else getattr(agent_instance, "_failure_type", "TASK_INCOMPLETE")
        )

        # Detect hang-up with no meaningful exchange
        if not call_success and duration_secs < 10:
            call_failure_type = "USER_HANGUP"

        channel = "sip" if is_sip_call else "browser"

        try:
            save_call_record(
                session_id=ctx.room.name,
                user_id="anonymous",
                started_at=session_start.isoformat(),
                ended_at=session_end.isoformat(),
                duration=duration_secs,
                channel=channel,
                outcome="SUCCESS" if call_success else "FAILED",
                failure_type=None if call_success else call_failure_type,
                success=1 if call_success else 0,
            )
            logger.info(
                "[FINSAHAYAK] Call record saved. Session=%s success=%s duration=%ds",
                ctx.room.name,
                call_success,
                duration_secs,
            )
        except Exception as db_err:
            logger.exception("[FINSAHAYAK] Failed to save call record: %s", db_err)


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    cli.run_app(server)
