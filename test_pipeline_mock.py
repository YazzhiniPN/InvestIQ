"""Sanity check the pipeline logic end-to-end using mock data
(no network needed) — this is what real ticker data looks like shaped
into the same objects `main.py` consumes."""

import pandas as pd
from src.data_gathering import GatheredData
from src.validation import validate
from src.analysis import analyze
from src.sentiment import analyze_sentiment
from src.report import build_report, format_report

dates = pd.date_range("2025-01-01", periods=60, freq="D")
prices = pd.DataFrame({"Close": [150 + i * 0.5 for i in range(60)]}, index=dates)

financials = pd.DataFrame(
    {pd.Timestamp("2025-01-01"): [400000.0, 60000.0]},
    index=["Total Revenue", "Net Income"],
)
balance_sheet = pd.DataFrame(
    {pd.Timestamp("2025-01-01"): [80000.0, 150000.0]},
    index=["Total Debt", "Stockholders Equity"],
)

data = GatheredData(
    ticker="MOCK",
    info={
        "sector": "Technology",
        "trailingPE": 25.0,
        "marketCap": 2_000_000_000,
        "currentPrice": 179.5,
    },
    price_history=prices,
    financials=financials,
    balance_sheet=balance_sheet,
    cashflow=pd.DataFrame(),
    news=[
        {"title": "Company beats earnings expectations, strong growth"},
        {"title": "Analysts upgrade stock after record profit"},
    ],
)

validation = validate(data)
print("Validation:", validation)
assert validation.is_valid, "Mock data should pass validation"

analysis = analyze(data)
print("\nAnalysis KPIs:", analysis.kpis)
print("Analysis ratios:", analysis.ratios)
print("Benchmark:", analysis.benchmark)
print("Trend:", analysis.trend)

sentiment = analyze_sentiment(data, analysis)
print("\nSentiment:", sentiment)

report = build_report(data, validation, analysis, sentiment)
print("\n" + format_report(report))
