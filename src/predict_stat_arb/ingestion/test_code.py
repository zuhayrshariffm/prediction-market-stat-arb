from polymarket_client import PolymarketClient
import json

### Kalshi API

from datetime import datetime, timedelta, timezone
from kalshi_client import KalshiClient

client = KalshiClient()

end_ts = int(datetime.now(timezone.utc).timestamp())
start_ts = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())

candles = client.get_market_candlesticks(
    ticker="CONTROLH-2026-D",
    start_ts=start_ts,
    end_ts=end_ts,
    period_interval=60,
)

print(candles.keys())
print(len(candles["candlesticks"]))
print(candles["candlesticks"][:3])