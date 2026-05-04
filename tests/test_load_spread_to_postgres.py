import pandas as pd

from src.predict_stat_arb.database.load_spread_to_postgres import load_spread_csv


def test_load_spread_csv_parses_timestamp_as_utc(tmp_path):
    spread_path = tmp_path / "spread.csv"

    pd.DataFrame(
        {
            "timestamp": ["2026-04-01 00:00:00+00:00"],
            "kalshi_yes_price": [0.6],
            "polymarket_yes_price": [0.65],
            "dem_spread": [0.05],
        }
    ).to_csv(spread_path, index=False)

    df = load_spread_csv(spread_path)

    assert len(df) == 1
    assert str(df["timestamp"].dt.tz) == "UTC"
