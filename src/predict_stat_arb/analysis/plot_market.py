from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

project_root = Path(__file__).resolve().parents[3]
data_path = project_root / "data/raw/polymarket_markets_latest.csv"

df = pd.read_csv(data_path)

plt.plot(df["liquidityNum"])
plt.title("Liquidity across markets")
plt.show()