from pathlib import Path
from datetime import datetime
import argparse
import pandas as pd

from src.predict_stat_arb.ingestion.kalshi_client import KalshiClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    client = KalshiClient()

    markets = client.get_all_clean_markets(total_limit=args.limit)

    df = pd.DataFrame(markets)

    project_root = Path(__file__).resolve().parents[3]

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    output_path = project_root / "data" / "raw" / f"kalshi_markets_{timestamp}.csv"
    latest_path = project_root / "data" / "raw" / "kalshi_markets_latest.csv"

    df.to_csv(output_path, index=False)
    df.to_csv(latest_path, index=False)

    print(f"Saved {len(df)} Kalshi markets")
    print(f"Timestamped file: {output_path.name}")
    print(f"Latest snapshot: {latest_path.name}")


if __name__ == "__main__":
    main()