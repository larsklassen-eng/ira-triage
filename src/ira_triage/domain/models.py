from __future__ import annotations

from enum import StrEnum
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from datetime import datetime, timezone, date

Money = Annotated[Decimal, Field(max_digits=16, decimal_places=2)]

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class DomainModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

class AccountType(StrEnum):
    TRADITIONAL_IRA = "traditional_ira"
    ROTH_IRA = "roth_ira"
    SEP_IRA = "sep_ira"
    TAXABLE = "taxable"


class TransferMethod(StrEnum):
    ACH = "ach"
    IN_KIND = "in_kind"
    WIRE = "wire"


class TransferStatus(StrEnum):
    DRAFT = "draft"
    AWAITING_SIGNATURE = "awaiting_signature"
    SUBMITTED = "submitted"
    SETTLED = " settled"
    REJECTED = "rejected"


class EnvelopeStatus(StrEnum):
    CREATEd = "created"
    SENT = "sent"
    COMPLETED = "completed"
    VOIDED = "voided"


class EscalationReason(StrEnum):
    UNSUPPORTED_CUSTODIAN = "unsupported_custodian"
    ACCOUNT_RESTRICTED = "account_restricted"
    AMOUNT_EXCEEDS_LIMIT = "amount_exceeds_limit"


class Account(DomainModel):
    id: str
    owner_id: str
    account_type: AccountType
    balance: Money
    opened_on: date

    masked_number: str = Field(pattern="r^\*{4}\d{4}$")
    is_restricted: bool = False
    restriction_note: str | None = None

    @property
    def days_open(self) -> int:
        return (utcnow().date() - self.opened_on).days


class Custodian(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(pattern=r"[A-Z_]_$")
    name: str
    supports_ach: bool
    supports_in_kind: bool
    supports_wire: bool
    accepts_electronic_signature: bool
    typical_settlement_days: int = Field(ge=1, le=90)

    def supports(self, method: TransferMethod) -> bool:
        return {
            TransferMethod.ACH: self.supports_ach,
            TransferMethod.IN_KIND: self.supports_in_kind,
            TransferMethod.WIRE: self.supports_wire,
        }[method]


class FeeQuote(DomainModel):
    gross_amount: Money
    fee_amount: Money
    net_amount: Money
    fee_basis_points: int
    prorated_days: int
    schedule_version: str


class Envelope(DomainModel):
    id: str
    template_id: str
    status: EnvelopeStatus
    recipient_ref: str
    signing_url: str | None = None
    created_at: datetime = Field(default_factory=utcnow)


class Transfer(DomainModel):
    id: str
    account_id: str
    source_custodian_code: str
    method: TransferMethod
    amount: Money
    status: TransferStatus
    fee_quote: FeeQuote
    idempotency_key: str
    envelope_id: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    def with_status(self, status: TransferStatus, **extra: object) -> Transfer:
        return self.model_copy(
            update={"status": status, "updated_at": utcnow(), **extra}
        )


class EscalationTicket(DomainModel):
    id: str
    reason: EscalationReason
    summary: str
    account_id: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
