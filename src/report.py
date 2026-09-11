"""
Stage 5: Reporting
Combines the outputs of every earlier stage into one structured report
and a plain-language recommendation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from .data_gathering import GatheredData
from .validation import ValidationResult
from .analysis import AnalysisResult
from .sentiment import SentimentResult


@dataclass
class Report:
    ticker: str
    recommendation: str
    rationale: List[str] = field(default_factory=list)
    kpis: Dict[str, Any] = field(default_factory=dict)
    ratios: Dict[str, Any] = field(default_factory=dict)
    benchmark: Dict[str, Any] = field(default_factory=dict)
    trend: Dict[str, Any] = field(default_factory=dict)
    sentiment: str = "neutral"
    risk_flags: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def _decide(analysis: AnalysisResult, sentiment: SentimentResult) -> (str, List[str]):
    score = 0
    rationale = []

    margin_cmp = analysis.benchmark.get("margin_vs_sector")
    if margin_cmp == "better than sector avg":
        score += 1
        rationale.append("Net margin is ahead of the sector average.")
    elif margin_cmp == "weaker than sector avg":
        score -= 1
        rationale.append("Net margin trails the sector average.")

    leverage_cmp = analysis.benchmark.get("leverage_vs_sector")
    if leverage_cmp == "better than sector avg":
        score += 1
        rationale.append("Leverage (debt-to-equity) is healthier than peers.")
    elif leverage_cmp == "weaker than sector avg":
        score -= 1
        rationale.append("Leverage is higher than peers, adding balance-sheet risk.")

    if sentiment.overall_sentiment == "positive":
        score += 1
        rationale.append("Recent news sentiment skews positive.")
    elif sentiment.overall_sentiment == "negative":
        score -= 1
        rationale.append("Recent news sentiment skews negative.")

    if sentiment.risk_flags:
        score -= len(sentiment.risk_flags)
        rationale.extend(sentiment.risk_flags)

    if score >= 2:
        return "Accumulate", rationale
    elif score <= -2:
        return "Underweight", rationale
    return "Hold", rationale


def build_report(
    data: GatheredData,
    validation: ValidationResult,
    analysis: AnalysisResult,
    sentiment: SentimentResult,
) -> Report:
    recommendation, rationale = _decide(analysis, sentiment)

    return Report(
        ticker=data.ticker,
        recommendation=recommendation,
        rationale=rationale,
        kpis=analysis.kpis,
        ratios=analysis.ratios,
        benchmark=analysis.benchmark,
        trend=analysis.trend,
        sentiment=sentiment.overall_sentiment,
        risk_flags=sentiment.risk_flags,
        warnings=validation.warnings,
    )


def format_report(report: Report) -> str:
    lines = [
        f"=== InvestIQ Report: {report.ticker} ===",
        f"Recommendation: {report.recommendation}",
        "",
        "KPIs:",
    ]
    for k, v in report.kpis.items():
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append("Ratios vs. Sector Benchmark:")
    for k, v in report.ratios.items():
        lines.append(f"  - {k}: {v}")
    for k, v in report.benchmark.items():
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append("Price Trend:")
    for k, v in report.trend.items():
        lines.append(f"  - {k}: {v}")
    lines.append("")
    lines.append(f"Sentiment: {report.sentiment}")
    if report.risk_flags:
        lines.append("Risk Flags:")
        for flag in report.risk_flags:
            lines.append(f"  - {flag}")
    lines.append("")
    lines.append("Rationale:")
    for r in report.rationale:
        lines.append(f"  - {r}")
    if report.warnings:
        lines.append("")
        lines.append("Data Warnings:")
        for w in report.warnings:
            lines.append(f"  - {w}")
    return "\n".join(lines)
