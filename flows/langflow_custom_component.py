
from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema import Message

import sys
import os

# Make the project's src/ package importable from within Langflow.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import run_pipeline  # noqa: E402


class InvestIQAgent(Component):
    display_name = "InvestIQ Sequential Agent"
    description = (
        "Runs the 5-stage InvestIQ pipeline (gather -> validate -> "
        "analyze -> sentiment -> report) for a stock ticker."
    )

    inputs = [
        MessageTextInput(
            name="ticker",
            display_name="Ticker",
            info="Stock ticker symbol, e.g. AAPL",
        ),
    ]

    outputs = [
        Output(display_name="Report", name="report", method="build_response"),
    ]

    def build_response(self) -> Message:
        ticker = self.ticker.strip().upper()
        report_text = run_pipeline(ticker)
        return Message(text=report_text)
