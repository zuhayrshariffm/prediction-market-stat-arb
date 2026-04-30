import requests
import json
from pathlib import Path
import pandas as pd

class PolymarketClient:
    """
    Client for interacting with the Polymarket Gamma API.
    Docs: https://gamma-api.polymarket.com
    """

    BASE_URL = "https://gamma-api.polymarket.com"

    def __init__(self, timeout=10):
        self.timeout = timeout

    def _get(self, endpoint, params=None):
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed for {url}: {e}")

    def get_markets(self, limit=10, offset=0):
        params = {
            "limit": limit,
            "offset": offset,
        }
        return self._get("/markets", params=params)

    def _parse_clob_token_ids(self, value):
        if value is None:
            return []

        if isinstance(value, list):
            return value

        return json.loads(value)

    def clean_market(self, market):
        return {
            "id": market.get("id"),
            "question": market.get("question"),
            "active": market.get("active"),
            "closed": market.get("closed"),
            "endDate": market.get("endDate"),
            "liquidityNum": market.get("liquidityNum"),
            "volumeNum": market.get("volumeNum"),
            "clobTokenIds": self._parse_clob_token_ids(market.get("clobTokenIds")),
            "bestBid": market.get("bestBid"),
            "bestAsk": market.get("bestAsk"),
            "lastTradePrice": market.get("lastTradePrice"),
        }
    def get_clean_markets(self, limit=10):
        markets = self.get_markets(limit=limit)
        return [self.clean_market(market) for market in markets]

    def get_all_clean_markets(self, total_limit=100):
        markets = []
        offset = 0
        batch_size = 100

        while len(markets) < total_limit:
            batch = self.get_markets(limit=batch_size, offset=offset)

            if not batch:
                break

            markets.extend(batch)
            offset += batch_size

        markets = markets[:total_limit]

        return [self.clean_market(m) for m in markets]

    def get_price_history(self, token_id, interval="1h", fidelity=60):
        params = {
            "market": token_id,
            "interval": interval,
            "fidelity": fidelity,
        }

        data = requests.get(
            "https://clob.polymarket.com/prices-history",
            params=params
        ).json()

        return data["history"]

    def get_price_history(self, token_id, interval="1h", fidelity=60):
        params = {
            "market": token_id,
            "interval": interval,
            "fidelity": fidelity,
        }

        response = requests.get(
            "https://clob.polymarket.com/prices-history",
            params=params
        )

        data = response.json()

        history = data["history"]

        df = pd.DataFrame(history)
        df["timestamp"] = pd.to_datetime(df["t"], unit="s")
        df["token_id"] = token_id

        return df[["token_id", "timestamp", "p"]]