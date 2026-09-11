"""
Stage 4: Sentiment & Insight
Scores recent news headlines with a lightweight keyword lexicon and
surfaces trend/risk flags from the analysis stage.

This is intentionally dependency-free so the pipeline runs anywhere.
In the Langflow version, swap `score_headlines` for a call to the LLM
component (ask it to rate each headline -1..1) for higher-quality
sentiment — the rest of the pipeline is unchanged either way.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from .data_gathering import GatheredData
from .analysis import AnalysisResult

POSITIVE_WORDS = {
    "beat", "beats", "surge", "growth", "upgrade", "profit", "record",
    "strong", "outperform", "rally", "gain", "bullish", "expansion",
}
NEGATIVE_WORDS = {
    "miss", "misses", "downgrade", "loss", "decline", "weak", "lawsuit",
    "recall", "investigation", "bearish", "layoff", "layoffs", "cut", "plunge",
}


@dataclass
class SentimentResult:
    ticker: str
    headline_scores: List[Dict[str, Any]] = field(default_factory=list)
    overall_sentiment: str = "neutral"
    risk_flags: List[str] = field(default_factory=list)


def score_headlines(news: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    scored = []
    for item in news[:10]:
        title = (item.get("title") or "").lower()
        pos = sum(word in title for word in POSITIVE_WORDS)
        neg = sum(word in title for word in NEGATIVE_WORDS)
        score = pos - neg
        scored.append({"title": item.get("title"), "score": score})
    return scored


def analyze_sentiment(data: GatheredData, analysis: AnalysisResult) -> SentimentResult:
    result = SentimentResult(ticker=data.ticker)
    result.headline_scores = score_headlines(data.news)

    total = sum(h["score"] for h in result.headline_scores)
    if total > 0:
        result.overall_sentiment = "positive"
    elif total < 0:
        result.overall_sentiment = "negative"
    else:
        result.overall_sentiment = "neutral"

    if analysis.ratios.get("net_margin") is not None and analysis.ratios["net_margin"] < 0:
        result.risk_flags.append("Negative net margin.")
    if analysis.benchmark.get("leverage_vs_sector") == "weaker than sector avg":
        result.risk_flags.append("Debt-to-equity worse than sector average.")
    if analysis.trend.get("volatility_pct", 0) and analysis.trend["volatility_pct"] > 3:
        result.risk_flags.append("High recent price volatility.")

    return result
