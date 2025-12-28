import requests
from config import API_URLS, API_KEYS

class DefiLlamaClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or API_KEYS.get('DEFILLAMA_API_KEY')
        # Base URLs
        self.public_coins_url = "https://coins.llama.fi"
        self.public_api_url = "https://api.llama.fi"
        self.public_yields_url = "https://yields.llama.fi"
        self.pro_base_url = "https://pro-api.llama.fi"

    def get_price_chart(self, chain, address, period='1y'):
        """
        Get Price Chart
        Sample: curl "https://pro-api.llama.fi/coins/chart/ethereum:0xA0...?period=7d"
        Using public endpoint which corresponds to this.
        """
        url = f"{self.public_coins_url}/chart/{chain}:{address}"
        params = {'period': period}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_price_percentage_change(self, chain, address):
        """
        Get Price Percentage Change
        Sample: curl https://pro-api.llama.fi/coins/percentage/ethereum:0xA0...
        Using public endpoint.
        """
        url = f"{self.public_coins_url}/percentage/{chain}:{address}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_token_protocols(self, symbol):
        """
        Get Token Protocols
        Sample: curl https://pro-api.llama.fi/<API_KEY>/api/tokenProtocols/usdt
        """
        if self.api_key:
            url = f"{self.pro_base_url}/{self.api_key}/api/tokenProtocols/{symbol}"
        else:
            # Try public fallback
            url = f"{self.public_api_url}/tokenProtocols/{symbol}"
            
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_borrowing_rates(self):
        """
        Get Borrowing Rates
        Sample: curl https://pro-api.llama.fi/<API_KEY>/yields/poolsBorrow
        """
        if self.api_key:
            url = f"{self.pro_base_url}/{self.api_key}/yields/poolsBorrow"
        else:
            # Public fallback
            url = f"{self.public_yields_url}/poolsBorrow"
            
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
