from __future__ import annotations

import hashlib
import uuid
from decimal import Decimal

from ..domain.errors import (
    AccountNotFound,
    AccountRestricted,
    CustodianNotSupported,
)

from ..domain.models import (
    Account,
    EscalationReason,
    Transfer,
    TransferMethod,
    TransferStatus,
)

from ..ports import (
    AccountRepository,
    CustodianDirectory,
)
from .fees import quote_transfer_fee

SELF_SERVE_CEILING = Decimal("100000.00")


class InMemoryTransferRepository:
    def __init__(self) -> None:
        self._transfers: dict[str, Transfer] = {}
        self._by_key: dict[str, str] = {}

    async def save(self, transfer: Transfer) -> None:
        self._transfers[transfer.id] = transfer
        self._by_key[transfer.idempotency_key] = transfer.id

    async def get(self, transfer_id: str) -> Transfer | None:
        return self._transfers.get(transfer_id)

    async def find_by_idempotency_key(self, key: str) -> Transfer | None:
        transfer_id = self._by_key.get(key)
        return self._transfers.get(transfer_id) if transfer_id else None


def derive_idempotency_key(
    *, account_id: str, custodian_code: str, method: str, amount: Decimal
    ) -> str:
    raw = f"{account_id}|{custodian_code}|{method}|{amount:.2f}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


class TransferService:
    def __init__(
        self,
        *,
        accounts: AccountRepository,
        custodians: CustodianDirectory,
    ) -> None:
        self._accounts = accounts
        self._custodians = custodians

    async def get_account(self, account_id: str) -> Account:
        account = await self._accounts.get(account_id)
        if account is None:
            raise AccountNotFound(
                f"No account with id {account_id!r}.",
                remediation="Ask the user wich of their accounts they mean.",
            )
        return account

    async def check_custodian(self, name_or_code: str) -> dict[str, object]:
        custodian = await self._resolve_custodian(name_or_code)
        return custodian.model_dump(mode="json")

    async def _resolve_custodian(self, name_or_code: str):
        custodian = await self._custodians.resolve(name_or_code)
        if custodian is None:
            known = [c.name for c in await self._custodians.all()]
            raise CustodianNotSupported(
                f"{name_or_code!r} is not a custodian we transfer from.",
                remediation="Offer the supported list, or escalate if they insist.",
                support=known,
            )
        return custodian
