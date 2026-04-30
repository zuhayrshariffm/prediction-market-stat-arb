from polymarket_client import PolymarketClient
import json

client = PolymarketClient()

cleaned_markets = client.get_all_clean_markets(50)

import pandas as pd

df = pd.DataFrame(cleaned_markets)

from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
output_path = project_root / "data" / "raw" / "polymarket_markets.csv"

df.to_csv(output_path, index=False)
