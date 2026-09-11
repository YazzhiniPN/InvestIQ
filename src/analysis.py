"""
Stage 3: Analysis
Extracts core KPIs, computes standard financial ratios, and benchmarks
them against illustrative sector-average figures.

Note: sector benchmarks below are illustrative placeholders. For a real
deployment, replace SECTOR_BENCHMARKS with a live peer-comparison feed
(e.g., an industry-average API or a basket of peer tickers you compute
the same ratios for).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from .data_gathering import GatheredData

# Illustrative sector-average ratios (placeholder — swap for a live feed)
SECTOR_BENCHMARKS: Dict[str, Dict[str, float]] = {
    "Technology": {"pe_ratio": 28.0, "net_margin": 0.18, "debt_to_equity": 0.6},
    "Financial Services": {"pe_ratio": 14.0, "net_margin": 0.22, "debt_to_equity": 1.8},
    "Healthcare": {"pe_ratio": 22.0, "net_margin": 0.15, "debt_to_equity": 0.7},
    "Consumer Cyclical": {"pe_ratio": 20.0, "net_margin": 0.08, "debt_to_equity": 0.9},
    "Energy": {"pe_ratio": 11.0, "net_margin": 0.10, "debt_to_equity": 0.5},
    "Default": {"pe_ratio": 20.0, "net_margin": 0.12, "debt_to_equity": 0.8},
}


@dataclass
class AnalysisResult:
    ticker: str
    kpis: Dict[str, Any] = field(default_factory=dict)
    ratios: Dict[str, Optional[float]] = field(default_factory=dict)
    benchmark: Dict[str, Any] = field(default_factory=dict)
    trend: Dict[str, Any] = field(default_factory=dict)


def _safe_first(df, row_names):
    """Return the first matching row's most recent column value, or None."""
    if df is None or df.empty:
        return None
    for name in row_names:
        if name in df.index:
            series = df.loc[name].dropna()
            if not series.empty:
                return float(series.iloc[0])
    return None


def analyze(data: GatheredData) -> AnalysisResult:
    result = AnalysisResult(ticker=data.ticker)
    info = data.info or {}

    revenue = _safe_first(data.financials, ["Total Revenue", "TotalRevenue"])
    net_income = _safe_first(data.financials, ["Net Income", "NetIncome"])
    total_debt = _safe_first(data.balance_sheet, ["Total Debt", "TotalDebt"])
    total_equity = _safe_first(
        data.balance_sheet, ["Stockholders Equity", "Total Stockholder Equity"]
    )

    result.kpis = {
        "revenue": revenue,
        "net_income": net_income,
        "market_cap": info.get("marketCap"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "sector": info.get("sector", "Default"),
    }

    net_margin = (net_income / revenue) if (revenue and net_income and revenue != 0) else None
    debt_to_equity = (
        (total_debt / total_equity) if (total_debt and total_equity and total_equity != 0) else None
    )
    pe_ratio = info.get("trailingPE")

    result.ratios = {
        "pe_ratio": pe_ratio,
        "net_margin": net_margin,
        "debt_to_equity": debt_to_equity,
    }

    sector = result.kpis["sector"] if result.kpis["sector"] in SECTOR_BENCHMARKS else "Default"
    bench = SECTOR_BENCHMARKS[sector]
    result.benchmark = {
        "sector_used": sector,
        "pe_vs_sector": _compare(pe_ratio, bench["pe_ratio"], lower_is_better=True),
        "margin_vs_sector": _compare(net_margin, bench["net_margin"], lower_is_better=False),
        "leverage_vs_sector": _compare(debt_to_equity, bench["debt_to_equity"], lower_is_better=True),
    }

    if data.price_history is not None and not data.price_history.empty:
        closes = data.price_history["Close"]
        result.trend = {
            "period_return_pct": round(
                (closes.iloc[-1] / closes.iloc[0] - 1) * 100, 2
            ) if closes.iloc[0] else None,
            "volatility_pct": round(closes.pct_change().std() * 100, 2),
            "52w_high": round(float(closes.max()), 2),
            "52w_low": round(float(closes.min()), 2),
        }

    return result


def _compare(value, benchmark_value, lower_is_better: bool) -> str:
    if value is None:
        return "insufficient data"
    better = value < benchmark_value if lower_is_better else value > benchmark_value
    return "better than sector avg" if better else "weaker than sector avg"
