from pathlib import Path
from datetime import datetime, timedelta, timezone
import argparse
import pandas as pd

from src.predict_stat_arb.ingestion.kalshi_client import KalshiClient


def fetch_kalshi_prices(tickers, days=30, output_dir=None):
    client = KalshiClient()

    end_ts = int(datetime.now(timezone.utc).timestamp())
    start_ts = int(
        (datetime.now(timezone.utc) - timedelta(days=days)).timestamp()
    )

    frames = []

    for ticker in tickers:
        data = client.get_market_candlesticks(
            ticker=ticker,
            start_ts=start_ts,
            end_ts=end_ts,
            period_interval=60,
        )

        df = pd.DataFrame(data["candlesticks"])
        df["ticker"] = ticker

        frames.append(df)

    df = pd.concat(frames, ignore_index=True)

    project_root = Path(__file__).resolve().parents[3]

    if output_dir is None:
        output_dir = project_root / "data" / "raw"
    else:
        output_dir = Path(output_dir)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    output_path = output_dir / f"kalshi_prices_{'_'.join(tickers)}_{timestamp}.csv"
    latest_path = output_dir / f"kalshi_prices_{'_'.join(tickers)}_latest.csv"

    df.to_csv(output_path, index=False)
    df.to_csv(latest_path, index=False)

    print(f"Saved {len(df)} rows for {tickers}")

    return latest_path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", nargs="+", required=True)
    parser.add_argument("--days", type=int, default=30)
    args = parser.parse_args()

    fetch_kalshi_prices(
        tickers=args.tickers,
        days=args.days,
    )
