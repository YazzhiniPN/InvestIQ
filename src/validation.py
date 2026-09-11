"""
Stage 2: Validation
Checks that gathered data is complete and recent enough to analyze.
Downstream stages should not run on data that fails this check without
the caller being aware.
"""

from dataclasses import dataclass, field
from typing import List
from .data_gathering import GatheredData

STALE_PRICE_ROWS_MIN = 5  # need at least a few trading days of history


@dataclass
class ValidationResult:
    ticker: str
    is_valid: bool
    warnings: List[str] = field(default_factory=list)
    blocking_issues: List[str] = field(default_factory=list)


def validate(data: GatheredData) -> ValidationResult:
    result = ValidationResult(ticker=data.ticker, is_valid=True)

    if data.errors:
        result.warnings.extend(data.errors)

    if data.price_history is None or len(data.price_history) < STALE_PRICE_ROWS_MIN:
        result.blocking_issues.append(
            "Insufficient price history to compute trend/volatility."
        )

    if not data.info or "sector" not in data.info:
        result.warnings.append("Sector/company profile info missing or incomplete.")

    if data.financials is None or data.financials.empty:
        result.blocking_issues.append("No income-statement data available.")

    if not data.news:
        result.warnings.append(
            "No recent news found — sentiment stage will fall back to neutral."
        )

    if result.blocking_issues:
        result.is_valid = False

    return result
