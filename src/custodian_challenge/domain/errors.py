from __future__ import annotations

from typing import Any, ClassVar


class DomainError(Exception):
    code: ClassVar[str] = "domain_error"
    model_safe: ClassVar[bool] = True
    retryable: ClassVar[bool] = False

    def __init__(
        self,
        message: str,
        *,
        remediation: str | None = None,
        **context: Any,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.remediation = remediation
        self.context = context

    def as_tool_result(self) -> dict[str, Any]:
        if not self.model_safe:
            return {
                "error": self.code,
                "message": "An upstream service failed. Do not retry automatically.",
                "retryable": False,
            }
        payload: dict[str, Any] = {
            "error": self.code,
            "message": self.message,
            "retryable": self.retryable,
        }
        if self.remediation:
            payload["remediation"] = self.remediation
        if self.context:
            payload["context"] = self.context
        return payload

class AccountNotFound(DomainError):
    code = "account_not_found"


class AccountRestricted(DomainError):
    code = "account_restricted"


class CustodianNotSupported(DomainError):
    code = "custodian_not_supported"


class MethodNotSupported(DomainError):
    code = "method_not_supported"


class InssuficientBalance(DomainError):
    code = "insufficient_balance"


class UpstreamFailure(DomainError):
    code = "upstream_failure"
    model_safe = False
    retryable = True
