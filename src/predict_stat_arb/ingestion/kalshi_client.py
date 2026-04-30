import requests

class KalshiClient:
    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

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

    def get_markets(self, limit=100, status="open", cursor=None):
        params = {
            "limit": limit,
            "status": status,
            "mve_filter": "exclude",
        }

        if cursor is not None:
            params["cursor"] = cursor

        return self._get("/markets", params=params)

    def get_clean_markets(self, limit=100, status="open"):
        data = self.get_markets(limit=limit, status=status)
        markets = data["markets"]

        return [self.clean_market(m) for m in markets]

    def clean_market(self, m):
        return {
            "ticker": m["ticker"],
            "title": m["title"],
            "status": m["status"],
            "yes_bid": m["yes_bid_dollars"],
            "yes_ask": m["yes_ask_dollars"],
            "last_price": m["last_price_dollars"],
            "volume": m["volume_fp"],
            "liquidity": m["liquidity_dollars"],
            "close_time": m["close_time"],
            "event_ticker": m["event_ticker"],
        }

    def get_all_clean_markets(self, total_limit=100, status="open"):
        markets = []
        cursor = None
        batch_size = 100

        while len(markets) < total_limit:
            data = self.get_markets(
                limit=batch_size,
                status=status,
                cursor=cursor,
            )

            batch = data["markets"]

            if not batch:
                break

            markets.extend(batch)
            cursor = data.get("cursor")

            if not cursor:
                break

        markets = markets[:total_limit]

        return [self.clean_market(m) for m in markets]

    def get_market_candlesticks(
            self,
            ticker,
            start_ts,
            end_ts,
            period_interval=60,
    ):
        series_ticker = ticker.split("-")[0]

        endpoint = f"/series/{series_ticker}/markets/{ticker}/candlesticks"

        params = {
            "start_ts": start_ts,
            "end_ts": end_ts,
            "period_interval": period_interval,
        }

        return self._get(endpoint, params=params)

    def get_market(self, ticker):
        return self._get(f"/markets/{ticker}")["market"]
