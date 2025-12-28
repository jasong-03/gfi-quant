import json
import requests
from config import API_URLS, API_KEYS

class NansenClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or API_KEYS.get('NANSEN_API_KEY')
        self.base_url = API_URLS['NANSEN']
        
    def _make_request(self, endpoint, data):
        url = f"{self.base_url}{endpoint}"
        headers = {
            'apiKey': self.api_key,
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))
        self.last_headers = response.headers
        response.raise_for_status()
        return response.json()

    def get_token_who_bought_sold(self, address, chain, start_date=None, end_date=None, buy_or_sell="BUY", page=1, per_page=10):
        """
        Token Who Bought/Sold
        """
        data = {
            "chain": chain,
            "token_address": address,
            "buy_or_sell": buy_or_sell,
            "pagination": {
                "page": page,
                "per_page": per_page
            }
        }
        
        if start_date and end_date:
            data["date"] = {
                "from": start_date,
                "to": end_date
            }
            
        return self._make_request('/tgm/who-bought-sold', data)

    def get_token_perp_trades(self, token_symbol, start_date, end_date, page=1, per_page=10, filters=None, order_by=None):
        """
        Token Perp Trades
        """
        data = {
            "token_symbol": token_symbol,
            "date": {
                "from": start_date,
                "to": end_date
            },
            "pagination": {
                "page": page,
                "per_page": per_page
            }
        }

        if filters:
            data["filters"] = filters
        
        if order_by:
            data["order_by"] = order_by

        return self._make_request('/tgm/perp-trades', data)

    def get_token_transfers(self, address, chain, start_date, end_date, page=1, per_page=10):
        """
        Token Transfers
        """
        data = {
            "token_address": address,
            "chain": chain,
            "pagination": {
                "page": page,
                "per_page": per_page
            }
        }
        
        if start_date and end_date:
            data["date"] = {
                "from": start_date,
                "to": end_date
            }
            
        return self._make_request('/tgm/transfers', data)

    def get_token_holders(self, address, chain, page=1, per_page=100):
        """
        Token Holders
        """
        data = {
            "token_address": address,
            "chain": chain,
            "aggregate_by_entity": False,
            "pagination": {
                "page": page,
                "per_page": per_page
            },
            "order_by": [
                {
                    "field": "ownership_percentage",
                    "direction": "DESC"
                }
            ]
        }
        return self._make_request('/tgm/holders', data)

    def get_token_flow_intelligence(self, address, chain):
        """
        Token Flow Intelligence
        Fetches data for multiple timeframes: 5m, 1h, 6h, 12h, 1d, 7d
        """
        timeframes = ["5m", "1h", "6h", "12h", "1d", "7d"]
        results = {}
        
        for tf in timeframes:
            try:
                data = {
                    "chain": chain,
                    "token_address": address,
                    "timeframe": tf,
                    "filters": {}
                }
                response = self._make_request('/tgm/flow-intelligence', data)
                results[tf] = response
            except Exception as e:
                results[tf] = {"error": str(e)}
        
        return results
