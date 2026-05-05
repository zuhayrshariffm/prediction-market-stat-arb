from prefect import flow, task

from src.predict_stat_arb.analysis.build_house_2026_spread import main as build_spread
from src.predict_stat_arb.database.load_spread_to_postgres import main as load_spread

from src.predict_stat_arb.config import (
    DEFAULT_KALSHI_LOOKBACK_DAYS,
    HOUSE_2026_KALSHI_DEM_TICKER,
    HOUSE_2026_KALSHI_REP_TICKER,
)
from src.predict_stat_arb.ingestion.fetch_kalshi_prices import fetch_kalshi_prices

@task
def fetch_kalshi_price_data():
    return fetch_kalshi_prices(
        tickers=[
            HOUSE_2026_KALSHI_DEM_TICKER,
            HOUSE_2026_KALSHI_REP_TICKER,
        ],
        days=DEFAULT_KALSHI_LOOKBACK_DAYS,
    )

@task
def build_spread_dataset():
    build_spread()


@task
def load_spread_dataset_to_postgres():
    load_spread()


@flow(name="house-2026-spread-pipeline")
def house_2026_spread_pipeline():
    fetch_kalshi_price_data()
    build_spread_dataset()
    load_spread_dataset_to_postgres()


if __name__ == "__main__":
    house_2026_spread_pipeline()
