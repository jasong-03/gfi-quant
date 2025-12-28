import requests
from config import API_URLS, API_KEYS

class CoinGeckoClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or API_KEYS.get('COINGECKO_API_KEY')
        self.base_url = API_URLS['COINGECKO']
        
    def _get_headers(self):
        headers = {}
        if self.api_key:
            headers['x-cg-pro-api-key'] = self.api_key
        return headers

    def _make_request(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self._get_headers(), params=params)
        self.last_headers = response.headers
        response.raise_for_status()
        return response.json()

    def get_coins_list(self):
        """
        Coins List (ID Map)
        Endpoint: /api/v3/coins/list
        """
        return self._make_request("/coins/list")

    def get_coin_historical_chart_by_contract(self, coin_id, contract_address, vs_currency='usd', days='max'):
        """
        Coin Historical Chart by Token Address
        """
        params = {
            'vs_currency': vs_currency,
            'days': days
        }
        return self._make_request(f"/coins/{coin_id}/contract/{contract_address}/market_chart", params=params)

    def get_coin_data(self, coin_id):
        """
        Coin Data by ID
        Endpoint: /api/v3/coins/{id}
        """
        return self._make_request(f"/coins/{coin_id}")

    def get_coin_info_by_contract(self, platform_id, contract_address):
        """
        Coin Info by Contract Address
        Endpoint: /api/v3/coins/{id}/contract/{contract_address}
        """
        return self._make_request(f"/coins/{platform_id}/contract/{contract_address}")
