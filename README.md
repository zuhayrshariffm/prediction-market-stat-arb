# Prediction Market Stat-Arb Pipeline

This project builds a production-style prediction-market data pipeline that ingests Kalshi and Polymarket prices, creates structured time-series datasets, analyzes cross-market pricing spreads, and eventually serves reproducible statistical signals through deployed APIs and dashboards.

The current phase focuses on historical spread analysis between comparable YES/NO markets across Kalshi and Polymarket. This is not yet an executable arbitrage system; it is a reproducible data pipeline and research workflow for measuring cross-market pricing differences.

## Current Market

The first analysis compares the 2026 House-control Democratic contract across both venues:

- Kalshi: `CONTROLH-2026-D`
- Polymarket: Democratic House-control YES token

The processed spread is calculated as:

```text
dem_spread = polymarket_yes_price - kalshi_yes_price
```

Positive spread means Polymarket is pricing the contract higher than Kalshi. Negative spread means Kalshi is pricing it higher than Polymarket.

## Current Pipeline

```text
Kalshi API data
Polymarket API data
        |
        v
Normalize timestamps and prices
        |
        v
Merge comparable hourly observations
        |
        v
Validate prices, timestamps, and overlap
        |
        v
Save processed spread data, summary stats, and plot
```

## Run Current Pipeline

Fetch recent Kalshi price history:

```bash
python -m src.predict_stat_arb.ingestion.fetch_kalshi_prices --tickers CONTROLH-2026-D CONTROLH-2026-R --days 30
```

Build the processed spread dataset:

```bash
python -m src.predict_stat_arb.analysis.build_house_2026_spread
```

Build the spread dataset with explicit paths:

```bash
python -m src.predict_stat_arb.analysis.build_house_2026_spread --kalshi-prices-path data/raw/kalshi_prices_CONTROLH-2026-D_CONTROLH-2026-R_latest.csv --output-dir data/processed
```

Plot the spread:

```bash
python -m src.predict_stat_arb.analysis.plot_house_2026_spread
```

Run tests:

```bash
python -m pytest
```

## Current Outputs

The build script writes both `latest` files and timestamped snapshots:

```text
data/processed/house_2026_dem_spread_latest.csv
data/processed/house_2026_dem_spread_YYYYMMDD_HHMMSS.csv
data/processed/house_2026_dem_spread_summary_latest.csv
data/processed/house_2026_dem_spread_summary_YYYYMMDD_HHMMSS.csv
data/processed/house_2026_dem_spread_plot.png
```

## Planned Stack

- Python for ingestion, processing, and analysis
- PostgreSQL for structured time-series storage
- Prefect for scheduled data pipelines
- FastAPI for serving signals and processed data
- Streamlit for an interactive dashboard
- Docker for reproducible local deployment
- pytest for validation and testing
- scikit-learn and MLflow for later modeling and experiment tracking
