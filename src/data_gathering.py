"""
Stage 1: Data Gathering
Pulls stock price history, key financial statement figures, and recent
news headlines for a given ticker.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import yfinance as yf


@dataclass
class GatheredData:
    ticker: str
    info: Dict[str, Any] = field(default_factory=dict)
    price_history: Any = None
    financials: Any = None
    balance_sheet: Any = None
    cashflow: Any = None
    news: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def gather(ticker: str, period: str = "1y") -> GatheredData:
    """Fetch everything the later stages need for one ticker."""
    data = GatheredData(ticker=ticker.upper())
    stock = yf.Ticker(data.ticker)

    try:
        data.info = stock.info or {}
    except Exception as e:
        data.errors.append(f"info fetch failed: {e}")

    try:
        data.price_history = stock.history(period=period)
    except Exception as e:
        data.errors.append(f"price history fetch failed: {e}")

    try:
        data.financials = stock.financials
    except Exception as e:
        data.errors.append(f"financials fetch failed: {e}")

    try:
        data.balance_sheet = stock.balance_sheet
    except Exception as e:
        data.errors.append(f"balance sheet fetch failed: {e}")

    try:
        data.cashflow = stock.cashflow
    except Exception as e:
        data.errors.append(f"cashflow fetch failed: {e}")

    try:
        data.news = stock.news or []
    except Exception as e:
        data.errors.append(f"news fetch failed: {e}")

    return data
