import time
from api_clients.dune_client import DuneClient

def main():
    print("Initializing Dune Client...")
    dune = DuneClient()
    
    # Parameters
    token_contract = '85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmQ'
    chain = 'solana'
    
    # Prepare SQL Replacements
    contract_addr_sql = f"'{token_contract}'"
    chain_sql = f"'{chain}'"
    # Fix Trino/Dune SQL interval syntax: interval '3' month
    time_filter_clause_day = "AND day >= now() - interval '3' month"
    time_filter_clause_timestamp = "AND timestamp >= now() - interval '3' month"
    
    print(f"Reading query template from delta_balance_change_dune_query.txt...")
    try:
        with open('delta_balance_change_dune_query.txt', 'r') as f:
            query_template = f.read()
    except FileNotFoundError:
        print("Error: delta_balance_change_dune_query.txt not found.")
        return

    # Format Query
    query_sql = query_template.format(
        contract_addr_sql=contract_addr_sql,
        chain_sql=chain_sql,
        time_filter_clause_day=time_filter_clause_day,
        time_filter_clause_timestamp=time_filter_clause_timestamp
    )
    
    print("Query prepared.")
    print("-" * 20)
    # print(query_sql) # Uncomment to see full query
    print("-" * 20)
    
    # Reuse valid query ID (Syntax Fixed)
    query_id = 6429530
    print(f"Using Query ID: {query_id}")

    # Execute Query
    print(f"Executing query {query_id}...")
    try:
        exec_resp = dune.execute_query(query_id)
        execution_id = exec_resp.get('execution_id')
        print(f"Execution started. ID: {execution_id}")
    except Exception as e:
        print(f"Error executing query: {e}")
        return

    # Poll for results
    print("Waiting for results...")
    while True:
        status_resp = dune.get_execution_status(execution_id)
        state = status_resp.get('state')
        print(f"Status: {state}")
        
        if state == 'QUERY_STATE_COMPLETED':
            break
        elif state in ['QUERY_STATE_FAILED', 'QUERY_STATE_CANCELLED']:
            print(f"Query failed or cancelled. Full response: {status_resp}")
            return
        
        time.sleep(2)

    # Get Results
    print("Fetching results...")
    results_resp = dune.get_execution_results(execution_id)
    rows = results_resp.get('result', {}).get('rows', [])
    
    print(f"Got {len(rows)} rows.")
    if rows:
        print("Sample row:")
        print(rows[0])
    
if __name__ == "__main__":
    main()
