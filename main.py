"""
InvestIQ — Sequential Task Agent for Investment Analysis

Runs the five-stage pipeline end to end for one or more tickers:
  1. Data Gathering
  2. Validation
  3. Analysis (KPIs, ratios, benchmarking)
  4. Sentiment & Insight
  5. Reporting

Usage:
    python main.py AAPL
    python main.py AAPL MSFT GOOGL
"""

import sys
from src.data_gathering import gather
from src.validation import validate
from src.analysis import analyze
from src.sentiment import analyze_sentiment
from src.report import build_report, format_report


def run_pipeline(ticker: str) -> str:
    data = gather(ticker)
    validation = validate(data)

    if not validation.is_valid:
        return (
            f"=== InvestIQ Report: {ticker} ===\n"
            f"Could not produce a recommendation — blocking data issues:\n"
            + "\n".join(f"  - {issue}" for issue in validation.blocking_issues)
        )

    analysis = analyze(data)
    sentiment = analyze_sentiment(data, analysis)
    report = build_report(data, validation, analysis, sentiment)
    return format_report(report)


if __name__ == "__main__":
    tickers = sys.argv[1:] or ["AAPL"]
    for t in tickers:
        print(run_pipeline(t))
        print()
