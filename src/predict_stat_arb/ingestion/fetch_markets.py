from pathlib import Path
import pandas as pd
from polymarket_client import PolymarketClient
from datetime import datetime
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=200)
    args = parser.parse_args()

    client = PolymarketClient()

    markets = client.get_all_clean_markets(args.limit)
    df = pd.DataFrame(markets)

    project_root = Path(__file__).resolve().parents[3]

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    latest_path = project_root / "data" / "raw" / "polymarket_markets_latest.csv"
    df.to_csv(latest_path, index=False)
    output_path = project_root / "data" / "raw" / f"polymarket_markets_{timestamp}.csv"

    df.to_csv(output_path, index=False)
    print(f"Saved {len(df)} markets")
    print(f"Timestamped file: {output_path.name}")
    print(f"Latest snapshot: {latest_path.name}")


if __name__ == "__main__":
    main()
