import sys
import os
import json
from datetime import datetime, timedelta

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from api_clients.nansen_client import NansenClient
except ImportError:
    # Handle case where we might be running from parent directory
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dashboard_builder_v4'))
    from api_clients.nansen_client import NansenClient

def run_tests():
    client = NansenClient()
    
    results = []
    
    # Test Data - Using PEPE on Ethereum for token endpoints
    # PEPE: 0x6982508145454Ce325dDbE47a25d4ec3d2311933
    token_address = "0x6982508145454Ce325dDbE47a25d4ec3d2311933" 
    chain = "ethereum"
    
    # Dates for perp trades (last 7 days)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # 1. get_token_who_bought_sold
    func_name = "get_token_who_bought_sold"
    try:
        print(f"Testing {func_name}...")
        resp = client.get_token_who_bought_sold(token_address, chain, start_date=start_date, end_date=end_date)
        results.append((func_name, "success", resp))
    except Exception as e:
        results.append((func_name, "failure", str(e)))

    # 2. get_token_perp_trades
    func_name = "get_token_perp_trades"
    try:
        print(f"Testing {func_name}...")
        # Using "ETH" as token symbol for perp trades
        resp = client.get_token_perp_trades("ETH", start_date, end_date)
        results.append((func_name, "success", resp))
    except Exception as e:
        results.append((func_name, "failure", str(e)))

    # 3. get_token_transfers
    func_name = "get_token_transfers"
    try:
        print(f"Testing {func_name}...")
        resp = client.get_token_transfers(token_address, chain, start_date=start_date, end_date=end_date)
        results.append((func_name, "success", resp))
    except Exception as e:
        results.append((func_name, "failure", str(e)))

    # 4. get_token_holders
    func_name = "get_token_holders"
    try:
        print(f"Testing {func_name}...")
        resp = client.get_token_holders(token_address, chain)
        results.append((func_name, "success", resp))
    except Exception as e:
        results.append((func_name, "failure", str(e)))
        
    # 5. get_token_flow_intelligence
    func_name = "get_token_flow_intelligence"
    try:
        print(f"Testing {func_name}...")
        resp = client.get_token_flow_intelligence(token_address, chain)
        results.append((func_name, "success", resp))
    except Exception as e:
        results.append((func_name, "failure", str(e)))

    # Print results in requested format
    print("\n" + "="*50 + "\nRESULTS\n" + "="*50)
    print(f"Total results: {len(results)}")
    for func, status, resp in results:
        # Simplify output to avoid encoding issues
        resp_str = str(resp)
        if len(resp_str) > 200:
            resp_str = resp_str[:200] + "..."
        print(f"('{func}', {status}, {resp_str})\n")
    sys.stdout.flush()

if __name__ == "__main__":
    run_tests()
