from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from ..domain.models import FeeQuote, TransferMethod


SCHEDULE_VERSION = "2026.07"
ANNUAL_DAYS = 365
CENTS = Decimal("0.01")


BPS_BY_METHOD: dict[TransferMethod, int] = {
    TransferMethod.ACH: 25,
    TransferMethod.WIRE: 40,
    TransferMethod.IN_KIND: 0,
}

MINIMUM_FEE = Decimal("0.00")
MAXIMUM_FEE = Decimal("250.00")


def _to_cents(value: Decimal) -> Decimal:
    return value.quantize(CENTS, rounding=ROUND_HALF_UP)


def quote_transfer_fee(
    *,
    gross_amount: Decimal,
    method: TransferMethod,
    days_held: int,
) -> FeeQuote:
    if gross_amount <= 0:
        raise ValueError("gross_amount must be positive")

    clamped_days = max(0, min(days_held, ANNUAL_DAYS))
    bps = BPS_BY_METHOD[method]

    raw_fee = (
        gross_amount
        * Decimal(bps)
        / Decimal(10_000)
        * Decimal(clamped_days)
        / Decimal(ANNUAL_DAYS)
    )

    fee = _to_cents(max(MINIMUM_FEE, min(raw_fee, MAXIMUM_FEE)))

    return FeeQuote(
        gross_amount=_to_cents(gross_amount),
        fee_amount=fee,
        net_amount=_to_cents(gross_amount - fee),
        fee_basis_points=bps,
        prorated_days=clamped_days,
        schedule_version=SCHEDULE_VERSION,
    )

