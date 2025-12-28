import os
import sys

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_clients.coingecko_client import CoinGeckoClient
from api_clients.nansen_client import NansenClient
from datetime import datetime, timedelta

def main():
    # Initialize clients
    cg_client = CoinGeckoClient()
    nansen_client = NansenClient()

    # Example: We have a contract address and want to get perp trades
    # Let's use WETH on Ethereum as an example
    contract_address = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2" 
    platform_id = "ethereum"

    print(f"Fetching info for contract {contract_address} on {platform_id}...")

    try:
        # 1. Get Coin Info from CoinGecko
        coin_info = cg_client.get_coin_info_by_contract(platform_id, contract_address)
        
        # 2. Extract Symbol
        symbol = coin_info.get('symbol', '').upper()
        if not symbol:
            print("Could not find symbol for this contract.")
            return

        print(f"Found symbol: {symbol}")

        # 3. Call Nansen Perp Trades Endpoint
        # Define date range (last 7 days)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"Fetching perp trades for {symbol} from {start_date} to {end_date}...")

        perp_trades = nansen_client.get_token_perp_trades(
            token_symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            page=1,
            per_page=10,
            filters={
                "order_type": ["MARKET"],
                "side": ["Long"]
            },
            order_by=[
                {
                    "field": "block_timestamp",
                    "direction": "ASC"
                }
            ]
        )

        print("Perp Trades Response:")
        print(perp_trades)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
