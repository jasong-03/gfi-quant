import requests
import time
from config import API_URLS, API_KEYS

class DuneClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or API_KEYS.get('DUNE_API_KEY')
        self.base_url = API_URLS['DUNE']
        self.headers = {
            'X-Dune-API-Key': self.api_key,
            'Content-Type': 'application/json'
        }

    def _make_request(self, method, endpoint, params=None, json_data=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, headers=self.headers, params=params, json=json_data)
        self.last_headers = response.headers
        response.raise_for_status()
        return response.json()

    def create_query(self, name, query_sql):
        """
        Create a new query
        Endpoint: POST /api/v1/query
        """
        payload = {
            "name": name,
            "query_sql": query_sql,
            "private": True
        }
        return self._make_request("POST", "/query", json_data=payload)

    def execute_query(self, query_id, params=None):
        """
        Execute Query
        Endpoint: POST /api/v1/query/{query_id}/execute
        """
        payload = {"query_parameters": params} if params else {}
        return self._make_request("POST", f"/query/{query_id}/execute", json_data=payload)

    def get_execution_status(self, execution_id):
        """
        Get Execution Status
        Endpoint: GET /api/v1/execution/{execution_id}/status
        """
        return self._make_request("GET", f"/execution/{execution_id}/status")

    def get_execution_results(self, execution_id):
        """
        Get Execution Results
        Endpoint: GET /api/v1/execution/{execution_id}/results
        """
        return self._make_request("GET", f"/execution/{execution_id}/results")
