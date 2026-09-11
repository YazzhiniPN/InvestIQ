"""
Paste this into a Langflow "Custom Component" node to run the real
InvestIQ pipeline (main.py) inside your flow, wired as:

  Chat Input -> [this Custom Component] -> Chat Output

The exact base-class import can shift between Langflow versions —
if `from langflow.custom import Component` fails on your version,
check Langflow's "Custom Component" docs panel (it shows the correct
import for your installed version) and swap the import line only;
the run() logic below does not need to change.
"""

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
