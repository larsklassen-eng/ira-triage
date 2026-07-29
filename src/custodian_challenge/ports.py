from __future__ import annotations

from typing import Protocol, runtime_checkable

from .domain.models import (
    Account,
    Custodian,
    Envelope,
    EscalationReason,
    EscalationTicket,
    Transfer,
)


@runtime_checkable
class AccountRepository(Protocol):
    async def get(self, account_id: str) -> Account | None: ...


@runtime_checkable
class CustodianDirectory(Protocol):
    async def resolve(self, nae_or_code: str) -> Custodian | None:
        ...

    async def all(self) -> list[Custodian]: ...
