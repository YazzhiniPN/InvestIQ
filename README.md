# InvestIQ - Sequential Task Agent for Investment Analysis

An agent that automates the investment-analyst workflow as one sequential
pipeline: **gather → validate → analyze → sentiment → report**, ending in a
plain-language recommendation (Accumulate / Hold / Underweight).

## Problem it solves

Investment analysts work across fragmented sources - company financials,
stock prices, market news, analyst opinions - and manually running the
same sequence of steps (gather, validate, analyze, benchmark, report) for
every ticker is slow and error-prone. InvestIQ automates that sequence.

## Pipeline stages

| Stage | File | What it does |
|---|---|---|
| 1. Data Gathering | `src/data_gathering.py` | Pulls price history, financial statements, and news via `yfinance`. |
| 2. Validation | `src/validation.py` | Flags missing/stale data before analysis runs on it. |
| 3. Analysis | `src/analysis.py` | Extracts KPIs, computes ratios (P/E, net margin, debt-to-equity), benchmarks vs. sector. |
| 4. Sentiment & Insight | `src/sentiment.py` | Scores recent headlines, surfaces risk flags. |
| 5. Reporting | `src/report.py` | Combines everything into a structured report + recommendation. |

## Setup

```bash
pip install -r requirements.txt
python main.py AAPL
python main.py AAPL MSFT GOOGL   # multiple tickers
```

## Testing without network access

`test_pipeline_mock.py` runs the full pipeline against mock data (no
internet required) - useful for CI or restricted environments:

```bash
python test_pipeline_mock.py
```

## Running as a Langflow flow

The components on the project slide map to this codebase as follows:

1. **Chat Input** - user enters a ticker symbol.
2. **Custom Component** - paste `flows/langflow_custom_component.py` into
   a Langflow "Custom Component" node. It imports and runs `main.run_pipeline()`
   directly, so the flow executes the exact same code as the CLI.
3. **Chat Output** - displays the returned report text.
4. *(Optional)* Add a **Vector Store (Chroma)** node upstream of the
   sentiment step if you want to retrieve a larger corpus of news/analyst
   commentary rather than relying on `yfinance`'s built-in news feed.

Steps to wire it up in the Langflow UI:
1. Create a new flow.
2. Drag in **Chat Input**, a **Custom Component**, and **Chat Output**.
3. Open the Custom Component's code editor and paste the contents of
   `flows/langflow_custom_component.py`.
4. Connect Chat Input → Custom Component → Chat Output.
5. Run it with a ticker like `AAPL` and confirm the report renders.
6. Take a screenshot of the built flow for your slide deck.

## Known limitations / future scope

- Sector benchmark figures in `analysis.py` are illustrative placeholders -
  swap in a live peer-comparison feed for production use.
- Sentiment scoring is a lightweight keyword lexicon; swapping in an LLM
  call (e.g., Langflow's model component rating each headline) improves
  quality without changing the rest of the pipeline.
- No portfolio-level aggregation yet - each run analyzes one ticker.
