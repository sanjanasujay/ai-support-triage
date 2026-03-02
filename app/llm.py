import os
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from .config import settings
from .schemas import TriageResult

MOCK = os.getenv("MOCK_LLM", "false").lower() == "true"

if not MOCK:
    client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_INSTRUCTIONS = (
    "You are a support triage assistant for a university/enterprise IT helpdesk. "
    "Classify the ticket into EXACTLY ONE of these categories:\n"
    "- Access & Accounts (login, permissions, MFA, 403/401)\n"
    "- Website & CMS (Modern Campus CMS, publishing, PCF/content issues)\n"
    "- Storage & Backup (S3/storage, quota, backup/restore)\n"
    "- Network & VPN (wifi, VPN, connectivity)\n"
    "- Billing & Purchasing (invoices, procurement)\n"
    "- Bug Report (unexpected behavior, errors, crashes)\n"
    "- Feature Request (new capability request)\n"
    "- Other\n\n"
    "Urgency MUST be one of: Low, Medium, High, Critical.\n"
    "Return:\n"
    "- category: one of the list above\n"
    "- urgency\n"
    "- summary: 1–2 sentences\n"
    "- draft_reply: short, helpful, professional\n"
    "- confidence: number between 0 and 1\n"
    "Be concise. Do not include extra keys."
)

def _mock_triage(title: str, message: str) -> TriageResult:
    text = (title + " " + message).lower()
    if "403" in text or "login" in text or "access" in text:
        return TriageResult(
            category="Access",
            urgency="High",
            summary="User reports a 403 error when attempting to log in; issue started today.",
            draft_reply="Thanks for reporting this. Please confirm your username and whether you're on VPN. "
                        "Try clearing cookies or using an incognito window; if it persists, we’ll escalate to IT.",
            confidence=0.72,
        )
    return TriageResult(
        category="Other",
        urgency="Medium",
        summary="User submitted a support request that requires additional details.",
        draft_reply="Thanks for reaching out. Could you share more details (steps to reproduce, screenshots, and time of occurrence)?",
        confidence=0.6,
    )

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
def triage_ticket(title: str, message: str) -> TriageResult:
    if MOCK:
        return _mock_triage(title, message)

    rsp = client.responses.parse(
        model=settings.openai_model,
        input=[
            {"role": "system", "content": SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": f"TITLE: {title}\n\nMESSAGE:\n{message}"},
        ],
        text_format=TriageResult,
    )

    msg = rsp.output[0]
    text = msg.content[0]
    if not getattr(text, "parsed", None):
        raise RuntimeError("Could not parse LLM response into schema.")
    return text.parsed