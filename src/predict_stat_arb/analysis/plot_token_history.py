from pathlib import Path
import ast
import pandas as pd

project_root = Path(__file__).resolve().parents[3]
data_path = project_root / "data/raw/polymarket_markets_latest.csv"

df = pd.read_csv(data_path)

token_ids = ast.literal_eval(df["clobTokenIds"].iloc[0])
yes_token_id = token_ids[0]

from src.predict_stat_arb.ingestion.polymarket_client import PolymarketClient

client = PolymarketClient()

price_df = client.get_price_history(yes_token_id)

print(price_df.head())