from pathlib import Path

import pandas as pd
import streamlit as st
import os
from src.predict_stat_arb.database.db import get_connection

def load_spread_from_postgres():
    query = """
        SELECT
            timestamp,
            kalshi_yes_price,
            polymarket_yes_price,
            dem_spread
        FROM house_2026_dem_spread
        ORDER BY timestamp;
    """

    with get_connection() as conn:
        df = pd.read_sql(query, conn)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["dem_spread"] = df["dem_spread"].astype(float)
    df["spread_cents"] = df["dem_spread"] * 100

    return df

def load_spread_data():
    if os.getenv("DATABASE_URL"):
        return load_spread_from_postgres(), "PostgreSQL"

    return load_spread_from_csv(), "CSV"

def load_spread_from_csv():
    project_root = Path(__file__).resolve().parents[3]
    spread_path = (
        project_root
        / "data"
        / "processed"
        / "house_2026_dem_spread_latest.csv"
    )

    df = pd.read_csv(spread_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["dem_spread"] = df["dem_spread"].astype(float)
    df["spread_cents"] = df["dem_spread"] * 100

    return df


st.set_page_config(
    page_title="Which party will win the U.S. House? DEM",
    layout="wide",
)

st.title("Which party will win the U.S. House? DEM")
st.subheader("Polymarket - Kalshi spread monitor")

df, data_source = load_spread_data()
st.caption(f"Data source: {data_source}")

latest = df.sort_values("timestamp").iloc[-1]
latest_timestamp = latest["timestamp"].strftime("%Y-%m-%d %H:%M UTC")

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Latest Spread", f"{latest['spread_cents']:.2f} cents")
col2.metric("Mean Spread", f"{df['spread_cents'].mean():.2f} cents")
col3.metric("Max Spread", f"{df['spread_cents'].max():.2f} cents")
col4.metric("Min Spread", f"{df['spread_cents'].min():.2f} cents")
col5.metric("Latest Timestamp", latest_timestamp)

st.line_chart(
    df.set_index("timestamp")[["spread_cents"]],
    height=400,
)
st.subheader("Recent Observations")

recent_df = df.sort_values("timestamp", ascending=False).head(20)

st.dataframe(
    recent_df[
        [
            "timestamp",
            "kalshi_yes_price",
            "polymarket_yes_price",
            "dem_spread",
            "spread_cents",
        ]
    ],
    use_container_width=True,
)
large_spread_count = (df["dem_spread"].abs() > 0.01).sum()
large_spread_share = large_spread_count / len(df)

st.caption(
    f"{large_spread_count} of {len(df)} observations "
    f"({large_spread_share:.1%}) have an absolute spread greater than 1 cent."
)
