# Prediction Market Stat-Arb Pipeline

This project builds a production-style prediction-market data pipeline that ingests Kalshi and Polymarket prices, creates structured time-series datasets, analyzes cross-market pricing spreads, and eventually serves reproducible statistical signals through deployed APIs and dashboards.

The current phase focuses on historical spread analysis between comparable Kalshi and Polymarket markets.

## Current Market

The first analysis compares the 2026 House-control Democratic contract across both venues:

- Kalshi: `CONTROLH-2026-D`
- Polymarket: Democratic House-control YES token

The processed spread is calculated as:

```text
dem_spread = polymarket_yes_price - kalshi_yes_price
