from pathlib import Path
from datetime import datetime, timedelta, timezone
import argparse
import pandas as pd

from src.predict_stat_arb.ingestion.kalshi_client import KalshiClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", nargs="+", required=True)
    parser.add_argument("--days", type=int, default=30)


    args = parser.parse_args()

    client = KalshiClient()

    end_ts = int(datetime.now(timezone.utc).timestamp())
    start_ts = int(
        (datetime.now(timezone.utc) - timedelta(days=args.days)).timestamp()
    )

    frames = []

    for ticker in args.tickers:
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

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    output_path = (
        project_root
        / "data/raw"
        / f"kalshi_prices_{'_'.join(args.tickers)}_{timestamp}.csv"
    )

    latest_path = (
        project_root
        / "data/raw"
        / f"kalshi_prices_{'_'.join(args.tickers)}_latest.csv"
    )

    df.to_csv(output_path, index=False)
    df.to_csv(latest_path, index=False)

    print(f"Saved {len(df)} rows for {args.tickers}")


if __name__ == "__main__":
    main()