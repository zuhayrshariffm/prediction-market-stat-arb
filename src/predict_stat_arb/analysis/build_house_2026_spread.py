from pathlib import Path
import pandas as pd
import ast
import argparse
from datetime import datetime, timezone


def parse_kalshi_close(value):
    parsed = ast.literal_eval(value)

    if "close_dollars" in parsed:
        return float(parsed["close_dollars"])

    return None

from src.predict_stat_arb.ingestion.polymarket_client import PolymarketClient

from src.predict_stat_arb.config import (
    DEFAULT_MERGE_TOLERANCE,
    DEFAULT_PRICE_HISTORY_FIDELITY,
    DEFAULT_PRICE_HISTORY_INTERVAL,
    HOUSE_2026_KALSHI_DEM_TICKER,
    HOUSE_2026_POLYMARKET_DEM_TOKEN_ID,
)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kalshi-prices-path",
        type=str,
        default=None,
        help="Path to Kalshi price history CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory where processed outputs will be saved.",
    )
    return parser.parse_args()

def load_kalshi_yes_prices(kalshi_path):
    kalshi_df = pd.read_csv(kalshi_path)

    kalshi_df["timestamp"] = pd.to_datetime(
        kalshi_df["end_period_ts"],
        unit="s",
        utc=True,
    )

    kalshi_df["price"] = kalshi_df["price"].apply(parse_kalshi_close)
    kalshi_df = kalshi_df.dropna(subset=["price"])

    kalshi_pivot = kalshi_df.pivot_table(
        index="timestamp",
        columns="ticker",
        values="price",
    )

    return kalshi_pivot[[HOUSE_2026_KALSHI_DEM_TICKER]]

def fetch_polymarket_yes_prices(client):
    poly_dem = client.get_price_history(
        HOUSE_2026_POLYMARKET_DEM_TOKEN_ID,
        interval=DEFAULT_PRICE_HISTORY_INTERVAL,
        fidelity=DEFAULT_PRICE_HISTORY_FIDELITY,
    )

    poly_dem = poly_dem.rename(columns={"p": "poly_dem"})

    return poly_dem[["timestamp", "poly_dem"]]

def build_spread_table(kalshi_dem, poly):
    combined = pd.merge_asof(
        kalshi_dem.sort_index(),
        poly.sort_values("timestamp"),
        left_index=True,
        right_on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta(DEFAULT_MERGE_TOLERANCE)
    )

    combined = combined.dropna(subset=["poly_dem"])

    combined = combined.rename(
        columns={
            HOUSE_2026_KALSHI_DEM_TICKER: "kalshi_yes_price",
            "poly_dem": "polymarket_yes_price",
        }
    )

    combined = combined.dropna(
        subset=["kalshi_yes_price", "polymarket_yes_price"]
    )

    combined["kalshi_yes_price"] = combined["kalshi_yes_price"].round(4)
    combined["polymarket_yes_price"] = combined["polymarket_yes_price"].round(4)

    combined["dem_spread"] = (
        combined["polymarket_yes_price"] - combined["kalshi_yes_price"]
    ).round(4)

    return combined

def validate_spread_table(combined):
    if combined.empty:
        raise ValueError("No overlapping Kalshi/Polymarket timestamps found.")

    if combined.index.has_duplicates:
        raise ValueError("Duplicate timestamps found after merge.")

    price_columns = ["kalshi_yes_price", "polymarket_yes_price"]

    for column in price_columns:
        if not combined[column].between(0, 1).all():
            raise ValueError(f"{column} contains values outside [0, 1].")

def build_spread_summary(combined):
    positive_spread_hours = (combined["dem_spread"] > 0).sum()
    negative_spread_hours = (combined["dem_spread"] < 0).sum()
    large_spread_hours = (combined["dem_spread"].abs() > 0.01).sum()
    large_spread_share = large_spread_hours / len(combined)

    return {
        "rows": len(combined),
        "mean_dem_spread": combined["dem_spread"].mean(),
        "min_dem_spread": combined["dem_spread"].min(),
        "max_dem_spread": combined["dem_spread"].max(),
        "positive_spread_hours": positive_spread_hours,
        "negative_spread_hours": negative_spread_hours,
        "large_spread_hours": large_spread_hours,
        "large_spread_share": round(large_spread_share, 3),
    }

def save_outputs(combined, summary, output_dir):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    processed_path = output_dir / "house_2026_dem_spread_latest.csv"
    summary_path = output_dir / "house_2026_dem_spread_summary_latest.csv"

    timestamped_processed_path = (
        output_dir / f"house_2026_dem_spread_{timestamp}.csv"
    )
    timestamped_summary_path = (
        output_dir / f"house_2026_dem_spread_summary_{timestamp}.csv"
    )

    output_df = combined.drop(columns=["timestamp"]).reset_index()
    summary_df = pd.DataFrame([summary])

    output_df.to_csv(processed_path, index=False)
    output_df.to_csv(timestamped_processed_path, index=False)

    summary_df.to_csv(summary_path, index=False)
    summary_df.to_csv(timestamped_summary_path, index=False)

    print(f"Saved processed spread data to: {processed_path}")
    print(f"Saved timestamped spread data to: {timestamped_processed_path}")
    print(f"Saved spread summary to: {summary_path}")
    print(f"Saved timestamped summary to: {timestamped_summary_path}")

def main():
    args = parse_args()

    project_root = Path(__file__).resolve().parents[3]

    if args.output_dir is not None:
        output_dir = Path(args.output_dir)
    else:
        output_dir = project_root / "data" / "processed"

    poly_client = PolymarketClient()

    if args.kalshi_prices_path is not None:
        kalshi_path = Path(args.kalshi_prices_path)
    else:
        kalshi_path = (
                project_root
                / "data"
                / "raw"
                / "kalshi_prices_CONTROLH-2026-D_CONTROLH-2026-R_latest.csv"
        )

    poly = fetch_polymarket_yes_prices(poly_client)
    kalshi_dem = load_kalshi_yes_prices(kalshi_path)

    combined = build_spread_table(kalshi_dem, poly)
    validate_spread_table(combined)

    summary = build_spread_summary(combined)
    print("Rows:", summary["rows"])
    print("Mean DEM spread:", summary["mean_dem_spread"])
    print("Min DEM spread:", summary["min_dem_spread"])
    print("Max DEM spread:", summary["max_dem_spread"])
    print("Positive spread hours:", summary["positive_spread_hours"])
    print("Negative spread hours:", summary["negative_spread_hours"])
    print("Hours with |spread| > 1 cent:", summary["large_spread_hours"])
    print("Share with |spread| > 1 cent:", summary["large_spread_share"])

    save_outputs(combined, summary, output_dir)


if __name__ == "__main__":
    main()

