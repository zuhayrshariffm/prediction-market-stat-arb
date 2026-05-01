from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


project_root = Path(__file__).resolve().parents[3]
data_path = project_root / "data" / "processed" / "house_2026_dem_spread_latest.csv"

df = pd.read_csv(data_path)
df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df["dem_spread_cents"] = df["dem_spread"] * 100

plt.figure(figsize=(12, 6))
plt.plot(df["timestamp"], df["dem_spread_cents"], linewidth=1.5)
plt.axhline(0, color="black", linewidth=1)
plt.axhline(1, color="gray", linestyle="--", linewidth=1)
plt.axhline(-1, color="gray", linestyle="--", linewidth=1)

plt.title("House 2026 DEM Spread: Polymarket - Kalshi")
plt.xlabel("Timestamp")
plt.ylabel("Spread (cents)")

plt.gcf().autofmt_xdate()
plt.tight_layout()

plot_path = (
    project_root
    / "data"
    / "processed"
    / "house_2026_dem_spread_plot.png"
)

plt.savefig(plot_path, dpi=150)

print(f"Saved spread plot to: {plot_path}")

plt.show()

