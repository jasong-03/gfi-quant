
import sys
import os
from pathlib import Path

# Add current directory to path to allow imports
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

from api_clients.nansen_client import NansenClient
from datetime import datetime, timedelta

def debug_nansen():
    client = NansenClient()
    
    # Test Parameters (Solana example from user context)
    chain = "solana"
    address = "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN" # JUP token
    
    # Dates for transfers
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    
    print(f"Testing Nansen API for {address} on {chain}...")
    print("-" * 50)

    # 1. Test Holders
    print("\n1. Testing get_token_holders...")
    try:
        holders = client.get_token_holders(address, chain)
        print("✅ Holders Success!")
        print(f"Keys returned: {list(holders.keys()) if isinstance(holders, dict) else 'Not dict'}")
        if isinstance(holders, dict):
            # Print sample data
            print(str(holders)[:500]) 
    except Exception as e:
        print("❌ Holders Failed!")
        print(f"Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response Status: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")

    # 2. Test Transfers
    print("\n2. Testing get_token_transfers...")
    try:
        transfers = client.get_token_transfers(address, chain, start_date=start_date, end_date=end_date)
        print("✅ Transfers Success!")
        print(f"Keys returned: {list(transfers.keys()) if isinstance(transfers, dict) else 'Not dict'}")
        if isinstance(transfers, dict):
            print(str(transfers)[:500])
    except Exception as e:
        print("❌ Transfers Failed!")
        print(f"Error: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Response Status: {e.response.status_code}")
            print(f"Response Body: {e.response.text}")

if __name__ == "__main__":
    debug_nansen()
