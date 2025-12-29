# CoinGecko API Endpoints Reference

**Last Updated**: 2024-12-29
**Demo Base URL**: `https://api.coingecko.com/api/v3`
**Pro Base URL**: `https://pro-api.coingecko.com/api/v3`
**WebSocket URL**: `wss://ws.coingecko.com/v1/ws`
**Documentation**: https://docs.coingecko.com/
**Official SDK**: `pycoingecko` (Python), `coingecko-typescript` (TS)

---

## Pricing Plans

| Plan | Rate Limit | Price |
|------|------------|-------|
| Demo | 30 calls/min | FREE |
| Analyst | 500 calls/min | $129/mo |
| Lite | 500 calls/min | $499/mo |
| Pro | 1000 calls/min | $999/mo |
| Enterprise | Custom | Custom |

**Legend**:
- No icon = Free/Demo
- 💼 = Analyst Plan & above
- 👑 = Enterprise only

---

## Authentication

```python
import requests

# Demo API (free)
DEMO_URL = "https://api.coingecko.com/api/v3"

# Pro API
PRO_URL = "https://pro-api.coingecko.com/api/v3"
API_KEY = "your-api-key"

# Method 1: Header (recommended)
headers = {"x-cg-pro-api-key": API_KEY}
response = requests.get(f"{PRO_URL}/ping", headers=headers)

# Method 2: Query param
response = requests.get(f"{PRO_URL}/ping", params={"x_cg_pro_api_key": API_KEY})
```

---

## Ping & Status

| Endpoint | Method | Description | Params | Plan |
|----------|--------|-------------|--------|------|
| `/ping` | GET | Check API server status | - | Free |
| `/key` | GET | Check API usage | - | 💼 |

```python
def ping():
    url = f"{PRO_URL}/ping"
    return requests.get(url, headers=headers).json()

def get_api_usage():
    url = f"{PRO_URL}/key"
    return requests.get(url, headers=headers).json()
```

---

## Simple (Price) Endpoints

| Endpoint | Method | Description | Params | Plan |
|----------|--------|-------------|--------|------|
| `/simple/price` | GET | Get coin prices | `ids`, `vs_currencies`, `include_market_cap`, `include_24hr_vol`, `include_24hr_change`, `include_last_updated_at`, `precision` | Free |
| `/simple/token_price/{id}` | GET | Get token prices by contract | `id` (platform), `contract_addresses`, `vs_currencies`, same as above | Free |
| `/simple/supported_vs_currencies` | GET | List supported currencies | - | Free |

```python
# Get price of multiple coins
def get_prices(coin_ids: list, vs_currencies: list = ["usd"]):
    url = f"{PRO_URL}/simple/price"
    params = {
        "ids": ",".join(coin_ids),
        "vs_currencies": ",".join(vs_currencies),
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true"
    }
    return requests.get(url, headers=headers, params=params).json()

# Get token price by contract address
def get_token_price(platform: str, contract_addresses: list):
    url = f"{PRO_URL}/simple/token_price/{platform}"
    params = {
        "contract_addresses": ",".join(contract_addresses),
        "vs_currencies": "usd"
    }
    return requests.get(url, headers=headers, params=params).json()

# Get supported currencies
def get_supported_currencies():
    url = f"{PRO_URL}/simple/supported_vs_currencies"
    return requests.get(url, headers=headers).json()
```

---

## Coins Endpoints

| Endpoint | Method | Description | Params | Plan |
|----------|--------|-------------|--------|------|
| `/coins/list` | GET | List all coins (ID map) | `include_platform` | Free |
| `/coins/markets` | GET | Coins with market data | `vs_currency`, `ids`, `category`, `order`, `per_page`, `page`, `sparkline`, `price_change_percentage`, `locale`, `precision` | Free |
| `/coins/{id}` | GET | Coin data by ID | `id`, `localization`, `tickers`, `market_data`, `community_data`, `developer_data`, `sparkline` | Free |
| `/coins/{id}/tickers` | GET | Coin tickers | `id`, `exchange_ids`, `include_exchange_logo`, `page`, `order`, `depth` | Free |
| `/coins/{id}/history` | GET | Historical data at date | `id`, `date` (dd-mm-yyyy), `localization` | Free |
| `/coins/{id}/market_chart` | GET | Market chart by days | `id`, `vs_currency`, `days`, `interval`, `precision` | Free |
| `/coins/{id}/market_chart/range` | GET | Market chart by range | `id`, `vs_currency`, `from`, `to`, `precision` | Free |
| `/coins/{id}/ohlc` | GET | OHLC data | `id`, `vs_currency`, `days`, `precision` | Free |
| `/coins/top_gainers_losers` | GET | Top gainers/losers | `vs_currency`, `duration`, `top_coins` | 💼 |
| `/coins/list/new` | GET | Recently listed coins | - | 💼 |
| `/coins/{id}/ohlc/range` | GET | OHLC by range | `id`, `vs_currency`, `from`, `to` | 💼 |
| `/coins/{id}/circulating_supply_chart` | GET | Circulating supply chart | `id`, `days`, `interval` | 👑 |
| `/coins/{id}/circulating_supply_chart/range` | GET | Circulating supply range | `id`, `from`, `to` | 👑 |
| `/coins/{id}/total_supply_chart` | GET | Total supply chart | `id`, `days`, `interval` | 👑 |
| `/coins/{id}/total_supply_chart/range` | GET | Total supply range | `id`, `from`, `to` | 👑 |

```python
# List all coins
def get_coins_list(include_platform: bool = False):
    url = f"{PRO_URL}/coins/list"
    params = {"include_platform": str(include_platform).lower()}
    return requests.get(url, headers=headers, params=params).json()

# Get coins with market data
def get_coins_markets(vs_currency: str = "usd", per_page: int = 100, page: int = 1):
    url = f"{PRO_URL}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": "false"
    }
    return requests.get(url, headers=headers, params=params).json()

# Get coin details
def get_coin(coin_id: str):
    url = f"{PRO_URL}/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "true",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false"
    }
    return requests.get(url, headers=headers, params=params).json()

# Get market chart
def get_market_chart(coin_id: str, vs_currency: str = "usd", days: int = 30):
    url = f"{PRO_URL}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    return requests.get(url, headers=headers, params=params).json()

# Get OHLC
def get_ohlc(coin_id: str, vs_currency: str = "usd", days: int = 30):
    url = f"{PRO_URL}/coins/{coin_id}/ohlc"
    params = {"vs_currency": vs_currency, "days": days}
    return requests.get(url, headers=headers, params=params).json()

# Get historical data
def get_coin_history(coin_id: str, date: str):
    """date format: dd-mm-yyyy"""
    url = f"{PRO_URL}/coins/{coin_id}/history"
    params = {"date": date, "localization": "false"}
    return requests.get(url, headers=headers, params=params).json()
```

---

## Contract Endpoints

| Endpoint | Method | Description | Params | Plan |
|----------|--------|-------------|--------|------|
| `/coins/{id}/contract/{contract_address}` | GET | Coin data by contract | `id` (platform), `contract_address` | Free |
| `/coins/{id}/contract/{contract_address}/market_chart` | GET | Market chart by contract | `id`, `contract_address`, `vs_currency`, `days` | Free |
| `/coins/{id}/contract/{contract_address}/market_chart/range` | GET | Market chart range | `id`, `contract_address`, `vs_currency`, `from`, `to` | Free |

```python
# Get coin by contract address
def get_coin_by_contract(platform: str, contract: str):
    url = f"{PRO_URL}/coins/{platform}/contract/{contract}"
    return requests.get(url, headers=headers).json()

# Get market chart by contract
def get_contract_market_chart(platform: str, contract: str, days: int = 30):
    url = f"{PRO_URL}/coins/{platform}/contract/{contract}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    return requests.get(url, headers=headers, params=params).json()
```

---

## Categories Endpoints

| Endpoint | Method | Description | Params | Plan |
|----------|--------|-------------|--------|------|
| `/coins/categories/list` | GET | List all categories | - | Free |
| `/coins/categories` | GET | Categories with market data | `order` | Free |

```python
# Get all categories
def get_categories_list():
    url = f"{PRO_URL}/coins/categories/list"
    return requests.get(url, headers=headers).json()

# Get categories with market data
def get_categories():
    url = f"{PRO_URL}/coins/categories"
    return requests.get(url, headers=headers).json()
```

---

## NFT Endpoints

| Endpoint | Method | Description | Params | Plan |
|----------|--------|-------------|--------|------|
| `/nfts/list` | GET | List all NFTs | `order`, `per_page`, `page` | Free |
| `/nfts/{id}` | GET | NFT data by ID | `id` | Free |
| `/nfts/{asset_platform_id}/contract/{contract_address}` | GET | NFT by contract | `asset_platform_id`, `contract_address` | Free |
| `/nfts/markets` | GET | NFTs with market data | `order`, `per_page`, `page` | 💼 |
| `/nfts/{id}/market_chart` | GET | NFT market chart | `id`, `days` | 💼 |
| `/nfts/{asset_platform_id}/contract/{contract_address}/market_chart` | GET | NFT chart by contract | same + `days` | 💼 |
| `/nfts/{id}/tickers` | GET | NFT tickers | `id` | 💼 |

```python
# Get NFT list
def get_nfts_list(per_page: int = 100, page: int = 1):
    url = f"{PRO_URL}/nfts/list"
    params = {"per_page": per_page, "page": page}
    return requests.get(url, headers=headers, params=params).json()

# Get NFT details
def get_nft(nft_id: str):
    url = f"{PRO_URL}/nfts/{nft_id}"
    return requests.get(url, headers=headers).json()

# Get NFT markets (Analyst+)
def get_nfts_markets():
    url = f"{PRO_URL}/nfts/markets"
    return requests.get(url, headers=headers).json()
```

---

## Exchanges Endpoints

| Endpoint | Method | Description | Params | Plan |
|----------|--------|-------------|--------|------|
| `/exchanges` | GET | All exchanges | `per_page`, `page` | Free |
| `/exchanges/list` | GET | Exchange ID map | - | Free |
| `/exchanges/{id}` | GET | Exchange by ID | `id` | Free |
| `/exchanges/{id}/tickers` | GET | Exchange tickers | `id`, `coin_ids`, `include_exchange_logo`, `page`, `depth`, `order` | Free |
| `/exchanges/{id}/volume_chart` | GET | Volume chart | `id`, `days` | Free |
| `/exchanges/{id}/volume_chart/range` | GET | Volume chart range | `id`, `from`, `to` | 💼 |

```python
# Get all exchanges
def get_exchanges(per_page: int = 100, page: int = 1):
    url = f"{PRO_URL}/exchanges"
    params = {"per_page": per_page, "page": page}
    return requests.get(url, headers=headers, params=params).json()

# Get exchange details
def get_exchange(exchange_id: str):
    url = f"{PRO_URL}/exchanges/{exchange_id}"
    return requests.get(url, headers=headers).json()

# Get exchange tickers
def get_exchange_tickers(exchange_id: str):
    url = f"{PRO_URL}/exchanges/{exchange_id}/tickers"
    return requests.get(url, headers=headers).json()
```

---

## Derivatives Endpoints

| Endpoint | Method | Description | Params | Plan |
|----------|--------|-------------|--------|------|
| `/derivatives` | GET | All derivatives tickers | `include_tickers` | Free |
| `/derivatives/exchanges` | GET | Derivatives exchanges | `order`, `per_page`, `page` | Free |
| `/derivatives/exchanges/{id}` | GET | Derivatives exchange by ID | `id`, `include_tickers` | Free |
| `/derivatives/exchanges/list` | GET | Derivatives exchange list | - | Free |

```python
# Get derivatives tickers
def get_derivatives():
    url = f"{PRO_URL}/derivatives"
    return requests.get(url, headers=headers).json()

# Get derivatives exchanges
def get_derivatives_exchanges():
    url = f"{PRO_URL}/derivatives/exchanges"
    return requests.get(url, headers=headers).json()
```

---

## Public Treasuries Endpoints

| Endpoint | Method | Description | Params | Plan |
|----------|--------|-------------|--------|------|
| `/entities/list` | GET | List entities | - | Free |
| `/companies/public_treasury/{coin_id}` | GET | Companies holding coin | `coin_id`: bitcoin, ethereum | Free |
| `/public_treasury/{entity_id}` | GET | Entity treasury | `entity_id` | Free |
| `/public_treasury/{entity_id}/{coin_id}/holding_chart` | GET | Holding chart | `entity_id`, `coin_id`, `days` | Free |
| `/public_treasury/{entity_id}/transaction_history` | GET | Transaction history | `entity_id`, `coin_id` | Free |

```python
# Get companies holding bitcoin
def get_btc_treasuries():
    url = f"{PRO_URL}/companies/public_treasury/bitcoin"
    return requests.get(url, headers=headers).json()

# Get entities list
def get_entities():
    url = f"{PRO_URL}/entities/list"
    return requests.get(url, headers=headers).json()
```

---

## General Endpoints

| Endpoint | Method | Description | Params | Plan |
|----------|--------|-------------|--------|------|
| `/asset_platforms` | GET | All asset platforms | `filter` | Free |
| `/token_lists/{asset_platform_id}/all.json` | GET | Token list | `asset_platform_id` | Free |
| `/exchange_rates` | GET | BTC exchange rates | - | Free |
| `/search` | GET | Search coins, exchanges, etc | `query` | Free |
| `/search/trending` | GET | Trending searches | - | Free |
| `/global` | GET | Global crypto data | - | Free |
| `/global/decentralized_finance_defi` | GET | DeFi global data | - | Free |
| `/global/market_cap_chart` | GET | Global market cap chart | `days` | 💼 |

```python
# Get asset platforms
def get_asset_platforms():
    url = f"{PRO_URL}/asset_platforms"
    return requests.get(url, headers=headers).json()

# Search
def search(query: str):
    url = f"{PRO_URL}/search"
    params = {"query": query}
    return requests.get(url, headers=headers, params=params).json()

# Get trending
def get_trending():
    url = f"{PRO_URL}/search/trending"
    return requests.get(url, headers=headers).json()

# Get global data
def get_global():
    url = f"{PRO_URL}/global"
    return requests.get(url, headers=headers).json()
```

---

## Onchain DEX Endpoints (GeckoTerminal)

| Endpoint | Method | Description | Params | Plan |
|----------|--------|-------------|--------|------|
| `/onchain/simple/networks/{network}/token_price/{addresses}` | GET | Token prices | `network`, `addresses` | Free |
| `/onchain/networks` | GET | All networks | `page` | Free |
| `/onchain/networks/{network}/dexes` | GET | DEXes on network | `network`, `page` | Free |
| `/onchain/networks/{network}/pools/{address}` | GET | Pool by address | `network`, `address` | Free |
| `/onchain/networks/{network}/pools/multi/{addresses}` | GET | Multiple pools | `network`, `addresses` | Free |
| `/onchain/networks/trending_pools` | GET | Trending pools all | `include`, `page`, `duration` | Free |
| `/onchain/networks/{network}/trending_pools` | GET | Trending pools network | `network`, `include`, `page` | Free |
| `/onchain/networks/{network}/pools` | GET | Top pools network | `network`, `include`, `page`, `sort` | Free |
| `/onchain/networks/{network}/dexes/{dex}/pools` | GET | Top pools DEX | `network`, `dex`, `include`, `page`, `sort` | Free |
| `/onchain/networks/new_pools` | GET | New pools all | `include`, `page` | Free |
| `/onchain/networks/{network}/new_pools` | GET | New pools network | `network`, `include`, `page` | Free |
| `/onchain/search/pools` | GET | Search pools | `query`, `network`, `include`, `page` | Free |
| `/onchain/networks/{network}/tokens/{address}/pools` | GET | Top pools for token | `network`, `address`, `include`, `page`, `sort` | Free |
| `/onchain/networks/{network}/tokens/{address}` | GET | Token data | `network`, `address`, `include` | Free |
| `/onchain/networks/{network}/tokens/multi/{addresses}` | GET | Multiple tokens | `network`, `addresses`, `include` | Free |
| `/onchain/networks/{network}/tokens/{address}/info` | GET | Token info | `network`, `address` | Free |
| `/onchain/networks/{network}/pools/{address}/info` | GET | Pool info | `network`, `address` | Free |
| `/onchain/tokens/info_recently_updated` | GET | Recently updated tokens | `include`, `network` | Free |
| `/onchain/networks/{network}/pools/{address}/ohlcv/{timeframe}` | GET | Pool OHLCV | `network`, `address`, `timeframe`, `aggregate`, `before_timestamp`, `limit`, `currency`, `token` | Free |
| `/onchain/networks/{network}/pools/{address}/trades` | GET | Pool trades | `network`, `address`, `trade_volume_in_usd_greater_than` | Free |
| `/onchain/pools/megafilter` | GET | Advanced pool filter | Many filters | 💼 |
| `/onchain/pools/trending_search` | GET | Trending search pools | - | 💼 |
| `/onchain/networks/{network}/tokens/{address}/top_traders` | GET | Top token traders | `network`, `address` | 💼 |
| `/onchain/networks/{network}/tokens/{address}/top_holders` | GET | Top token holders | `network`, `address` | 💼 |
| `/onchain/networks/{network}/tokens/{address}/holders_chart` | GET | Holders chart | `network`, `address` | 💼 |
| `/onchain/networks/{network}/tokens/{address}/ohlcv/{timeframe}` | GET | Token OHLCV | `network`, `address`, `timeframe` | 💼 |
| `/onchain/networks/{network}/tokens/{address}/trades` | GET | Token trades | `network`, `address` | 💼 |
| `/onchain/categories` | GET | Onchain categories | - | 💼 |
| `/onchain/categories/{category_id}/pools` | GET | Category pools | `category_id` | 💼 |

```python
# Get onchain token price
def get_onchain_price(network: str, addresses: list):
    url = f"{PRO_URL}/onchain/simple/networks/{network}/token_price/{','.join(addresses)}"
    return requests.get(url, headers=headers).json()

# Get all networks
def get_onchain_networks():
    url = f"{PRO_URL}/onchain/networks"
    return requests.get(url, headers=headers).json()

# Get trending pools
def get_trending_pools():
    url = f"{PRO_URL}/onchain/networks/trending_pools"
    return requests.get(url, headers=headers).json()

# Get pool data
def get_pool(network: str, pool_address: str):
    url = f"{PRO_URL}/onchain/networks/{network}/pools/{pool_address}"
    return requests.get(url, headers=headers).json()

# Get pool OHLCV
def get_pool_ohlcv(network: str, pool_address: str, timeframe: str = "day"):
    url = f"{PRO_URL}/onchain/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}"
    return requests.get(url, headers=headers).json()

# Search pools
def search_pools(query: str):
    url = f"{PRO_URL}/onchain/search/pools"
    params = {"query": query}
    return requests.get(url, headers=headers, params=params).json()

# Get token data
def get_onchain_token(network: str, address: str):
    url = f"{PRO_URL}/onchain/networks/{network}/tokens/{address}"
    return requests.get(url, headers=headers).json()

# Get pool trades
def get_pool_trades(network: str, pool_address: str):
    url = f"{PRO_URL}/onchain/networks/{network}/pools/{pool_address}/trades"
    return requests.get(url, headers=headers).json()
```

---

## WebSocket Endpoints

**URL**: `wss://ws.coingecko.com/v1/ws`
**Requires**: Analyst plan & above

### Channels

| Channel | Description | Subscription Format |
|---------|-------------|---------------------|
| `CGSimplePrice` | Real-time coin prices | `{"type":"CGSimplePrice","coin_ids":["bitcoin"],"currency":"usd"}` |
| `OnchainSimpleTokenPrice` | Real-time token prices | `{"type":"OnchainSimpleTokenPrice","network":"eth","token_addresses":["0x..."]}` |
| `OnchainTrade` | Real-time trades | `{"type":"OnchainTrade","network":"eth","pool_address":"0x..."}` |
| `OnchainOHLCV` | Real-time OHLCV | `{"type":"OnchainOHLCV","network":"eth","pool_address":"0x...","timeframe":"minute"}` |

```python
import asyncio
import websockets
import json

async def subscribe_price():
    uri = "wss://ws.coingecko.com/v1/ws"

    async with websockets.connect(uri, extra_headers={"x-cg-pro-api-key": API_KEY}) as ws:
        # Subscribe to Bitcoin price
        subscribe_msg = {
            "method": "subscribe",
            "params": {
                "type": "CGSimplePrice",
                "coin_ids": ["bitcoin", "ethereum"],
                "currency": "usd"
            }
        }
        await ws.send(json.dumps(subscribe_msg))

        # Listen for updates
        while True:
            response = await ws.recv()
            data = json.loads(response)
            print(data)

# Run
# asyncio.run(subscribe_price())
```

---

## Quick Test Script

```python
import requests
import time

API_KEY = "your-api-key"
PRO_URL = "https://pro-api.coingecko.com/api/v3"
headers = {"x-cg-pro-api-key": API_KEY}

def test_coingecko_endpoints():
    """Test key CoinGecko endpoints"""

    tests = [
        ("ping", f"{PRO_URL}/ping"),
        ("simple_price", f"{PRO_URL}/simple/price?ids=bitcoin&vs_currencies=usd"),
        ("coins_list", f"{PRO_URL}/coins/list"),
        ("coins_markets", f"{PRO_URL}/coins/markets?vs_currency=usd&per_page=10"),
        ("trending", f"{PRO_URL}/search/trending"),
        ("global", f"{PRO_URL}/global"),
        ("exchanges", f"{PRO_URL}/exchanges?per_page=10"),
        ("onchain_networks", f"{PRO_URL}/onchain/networks"),
    ]

    results = []
    for name, url in tests:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            status = "OK" if r.status_code == 200 else f"FAIL ({r.status_code})"
        except Exception as e:
            status = f"ERROR ({e})"
        results.append((name, status))
        print(f"{name}: {status}")
        time.sleep(0.5)  # Rate limit

    return results

if __name__ == "__main__":
    test_coingecko_endpoints()
```

---

## Notes

1. **Rate Limits**: Demo = 30/min, Pro plans = 500-1000/min
2. **Pagination**: Most list endpoints support `per_page` and `page`
3. **Precision**: Use `precision` param (0-18) to control decimal places
4. **Caching**: Data refreshes every 45-60 seconds for most endpoints
5. **Onchain Data**: Powered by GeckoTerminal, covers 200+ networks
