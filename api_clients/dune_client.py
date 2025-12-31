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

    def execute_sql(self, query_sql, query_name=None, timeout=300, poll_interval=2):
        """
        Execute raw SQL and wait for results.

        Flow:
        1. Create a temporary query with the SQL
        2. Execute the query
        3. Poll for completion
        4. Return results

        Args:
            query_sql: Raw SQL to execute
            query_name: Optional name for the query (default: auto-generated)
            timeout: Max seconds to wait for results (default: 300s = 5min)
            poll_interval: Seconds between status checks (default: 2s)

        Returns:
            dict with 'rows' (list of dicts) and 'metadata'
        """
        import time as time_module

        # Generate query name if not provided
        if not query_name:
            query_name = f"gfi_query_{int(time_module.time())}"

        # Step 1: Create query
        create_response = self.create_query(query_name, query_sql)
        query_id = create_response.get('query_id')
        if not query_id:
            raise Exception(f"Failed to create query: {create_response}")

        # Step 2: Execute query
        exec_response = self.execute_query(query_id)
        execution_id = exec_response.get('execution_id')
        if not execution_id:
            raise Exception(f"Failed to execute query: {exec_response}")

        # Step 3: Poll for completion
        start_time = time_module.time()
        while True:
            elapsed = time_module.time() - start_time
            if elapsed > timeout:
                raise Exception(f"Query execution timed out after {timeout}s")

            status_response = self.get_execution_status(execution_id)
            state = status_response.get('state', '').lower()

            if state == 'completed':
                break
            elif state in ('failed', 'cancelled'):
                error = status_response.get('error', 'Unknown error')
                raise Exception(f"Query execution {state}: {error}")

            # Still pending/executing
            time_module.sleep(poll_interval)

        # Step 4: Get results
        results = self.get_execution_results(execution_id)

        return {
            'query_id': query_id,
            'execution_id': execution_id,
            'rows': results.get('result', {}).get('rows', []),
            'metadata': results.get('result', {}).get('metadata', {}),
            'state': 'completed'
        }
