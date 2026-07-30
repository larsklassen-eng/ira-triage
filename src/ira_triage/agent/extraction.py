from __future__ import annotations
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field
from ..domain.models import AccountType, TransferMethod

EXTRACTION_TOOL_NAME = "record_transfer_intent"


class Urgency(StrEnum):
    ROUTINE = "routine"
    TIME_SENSITIVE = "time_sensitive"
    DISTRESSED = "distressed"


class TransferIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_type: AccountType | None = Field(
        default=None,
        description=(
            "The instruction the user names, copied verbatim from their message. "
            "Do not noralize, correct spelling, or expand abbreviation."
        )
    )
    source_custodian_raw: str | None = Field(
            default=None,
        description=(
            "The institution the user names, copied verbatim from their message. "
            "Do not normalize, correct spelling, or expand abbreviations."
        ),
    )
    method: TransferMethod | None = Field(
        default=None, description="Transfer method, only if explicitly indicated."
    )
    amount_raw: str | None = Field(
        default=None,
        description=(
            "The amount as written, e.g. '40k', '$12,500', 'about half'. "
            "Null if the user gives no amount."
        ),
    )
    is_full_transfer: bool = Field(
        default=False, description="True only if the user asks to move everything."
    )
    urgency: Urgency = Field(default=Urgency.ROUTINE)
    contains_policy_question: bool = Field(
        default=False,
        description=(
            "True if the user asks about fees, tax treatment, or timelines. "
            "These require a human answer."
        ),
    )
    unresolved: list[str] = Field(
        default_factory=list,
        description=(
            "Short phrases naming anything ambiguous or missing that a human "
            "would need to clarify. Empty if the request is fully specified."
        ),
    )

