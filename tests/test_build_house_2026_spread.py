import pandas as pd
import pytest

from src.predict_stat_arb.analysis.build_house_2026_spread import (
    build_spread_table,
    validate_spread_table,
)


def test_validate_spread_table_rejects_empty_dataframe():
    df = pd.DataFrame(
        columns=[
            "kalshi_yes_price",
            "polymarket_yes_price",
            "dem_spread",
        ]
    )

    with pytest.raises(ValueError, match="No overlapping"):
        validate_spread_table(df)

def test_validate_spread_table_rejects_prices_above_one():
    df = pd.DataFrame(
        {
            "kalshi_yes_price": [1.2],
            "polymarket_yes_price": [0.8],
            "dem_spread": [-0.4],
        },
        index=pd.to_datetime(["2026-04-01 00:00:00"], utc=True),
    )

    with pytest.raises(ValueError, match="kalshi_yes_price"):
        validate_spread_table(df)

def test_validate_spread_table_rejects_duplicate_timestamps():
    df = pd.DataFrame(
        {
            "kalshi_yes_price": [0.6, 0.7],
            "polymarket_yes_price": [0.5, 0.8],
            "dem_spread": [-0.1, 0.1],
        },
        index=pd.to_datetime(
            [
                "2026-04-01 00:00:00",
                "2026-04-01 00:00:00",
            ],
            utc=True,
        ),
    )

    with pytest.raises(ValueError, match="Duplicate timestamps"):
        validate_spread_table(df)

def test_validate_spread_table_accepts_valid_data():
    df = pd.DataFrame(
        {
            "kalshi_yes_price": [0.6, 0.7],
            "polymarket_yes_price": [0.65, 0.68],
            "dem_spread": [0.05, -0.02],
        },
        index=pd.to_datetime(
            [
                "2026-04-01 00:00:00",
                "2026-04-01 01:00:00",
            ],
            utc=True,
        ),
    )

    validate_spread_table(df)

def test_build_spread_table_calculates_polymarket_minus_kalshi():
    kalshi_dem = pd.DataFrame(
        {
            "CONTROLH-2026-D": [0.60, 0.70],
        },
        index=pd.to_datetime(
            [
                "2026-04-01 00:00:00",
                "2026-04-01 01:00:00",
            ],
            utc=True,
        ),
    )

    poly = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                [
                    "2026-04-01 00:00:30",
                    "2026-04-01 01:00:30",
                ],
                utc=True,
            ),
            "poly_dem": [0.65, 0.68],
        }
    )

    result = build_spread_table(kalshi_dem, poly)

    assert list(result["dem_spread"]) == [0.05, -0.02]

