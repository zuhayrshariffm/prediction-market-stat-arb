import argparse
from pathlib import Path

import pandas as pd

from src.predict_stat_arb.database.db import get_connection


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--spread-path",
        type=str,
        default=None,
        help="Path to processed spread CSV.",
    )
    return parser.parse_args()


def load_spread_csv(spread_path):
    df = pd.read_csv(spread_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)

    return df


def upsert_spread_rows(df):
    query = """
        INSERT INTO house_2026_dem_spread (
            timestamp,
            kalshi_yes_price,
            polymarket_yes_price,
            dem_spread
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (timestamp)
        DO UPDATE SET
            kalshi_yes_price = EXCLUDED.kalshi_yes_price,
            polymarket_yes_price = EXCLUDED.polymarket_yes_price,
            dem_spread = EXCLUDED.dem_spread,
            loaded_at = NOW();
    """

    rows = [
        (
            row.timestamp,
            row.kalshi_yes_price,
            row.polymarket_yes_price,
            row.dem_spread,
        )
        for row in df.itertuples(index=False)
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(query, rows)

    print(f"Loaded {len(rows)} spread rows into Postgres.")


def main():
    args = parse_args()
    project_root = Path(__file__).resolve().parents[3]

    if args.spread_path is not None:
        spread_path = Path(args.spread_path)
    else:
        spread_path = (
            project_root
            / "data"
            / "processed"
            / "house_2026_dem_spread_latest.csv"
        )

    df = load_spread_csv(spread_path)
    upsert_spread_rows(df)


if __name__ == "__main__":
    main()
