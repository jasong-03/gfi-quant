# DefiLlama API Endpoints Reference

**Last Updated**: 2024-12-29
**Base URL**: `https://api.llama.fi`
**Pro URL**: `https://pro-api.llama.fi/<API-KEY>/`
**Documentation**: https://api-docs.defillama.com/
**Pricing**: FREE (most endpoints) | Pro: $300/mo

---

## Authentication

```python
import requests

# Free endpoints - no auth needed
BASE_URL = "https://api.llama.fi"

# Pro endpoints - API key in URL path
PRO_BASE_URL = "https://pro-api.llama.fi/<YOUR-API-KEY>"
```

---

## TVL Endpoints

| Endpoint | Method | Description | Params | Pro |
|----------|--------|-------------|--------|-----|
| `/protocols` | GET | List all protocols with TVL | - | No |
| `/protocol/{protocol}` | GET | Historical TVL of a protocol | `protocol`: slug (e.g., "aave") | No |
| `/v2/historicalChainTvl` | GET | Historical TVL of all chains | - | No |
| `/v2/historicalChainTvl/{chain}` | GET | Historical TVL of a chain | `chain`: chain name (e.g., "Ethereum") | No |
| `/tvl/{protocol}` | GET | Current TVL of a protocol (number only) | `protocol`: slug | No |
| `/v2/chains` | GET | Current TVL of all chains | - | No |
| `/api/tokenProtocols/{symbol}` | GET | Token usage across protocols | `symbol`: token (e.g., "usdt") | **Yes** |
| `/api/inflows/{protocol}/{timestamp}` | GET | Inflows/outflows at date | `protocol`, `timestamp`: unix | **Yes** |
| `/api/chainAssets` | GET | Assets of all chains | - | **Yes** |

### Python Samples - TVL

```python
import requests

# List all protocols
def get_all_protocols():
    url = "https://api.llama.fi/protocols"
    response = requests.get(url)
    return response.json()

# Get protocol TVL history
def get_protocol_tvl(protocol: str):
    url = f"https://api.llama.fi/protocol/{protocol}"
    response = requests.get(url)
    return response.json()

# Get current TVL (simple number)
def get_current_tvl(protocol: str):
    url = f"https://api.llama.fi/tvl/{protocol}"
    response = requests.get(url)
    return response.json()  # Returns float like 4962012809.795062

# Get chain TVL history
def get_chain_tvl(chain: str):
    url = f"https://api.llama.fi/v2/historicalChainTvl/{chain}"
    response = requests.get(url)
    return response.json()

# Get all chains TVL
def get_all_chains():
    url = "https://api.llama.fi/v2/chains"
    response = requests.get(url)
    return response.json()
```

---

## Coins/Prices Endpoints

| Endpoint | Method | Description | Params | Pro |
|----------|--------|-------------|--------|-----|
| `/prices/current/{coins}` | GET | Current prices | `coins`: comma-separated (e.g., "coingecko:ethereum,coingecko:bitcoin") | No |
| `/prices/historical/{timestamp}/{coins}` | GET | Historical prices | `timestamp`: unix, `coins`: list | No |
| `/batchHistorical` | GET | Batch historical prices | `coins`, `timestamp`, `searchWidth` | No |
| `/chart/{coins}` | GET | Price chart data | `coins`, `start`, `end`, `span`, `period` | No |
| `/percentage/{coins}` | GET | Price percentage change | `coins`, `timestamp`, `lookForward`, `period` | No |
| `/prices/first/{coins}` | GET | First recorded price | `coins` | No |
| `/block/{chain}/{timestamp}` | GET | Block number at timestamp | `chain`, `timestamp` | No |

### Python Samples - Coins

```python
# Get current prices
def get_prices(coins: list):
    """
    coins format: ["coingecko:ethereum", "coingecko:bitcoin"]
    or ["ethereum:0x...", "bsc:0x..."] for tokens
    """
    coins_str = ",".join(coins)
    url = f"https://api.llama.fi/prices/current/{coins_str}"
    response = requests.get(url)
    return response.json()

# Get historical price
def get_historical_price(coins: list, timestamp: int):
    coins_str = ",".join(coins)
    url = f"https://api.llama.fi/prices/historical/{timestamp}/{coins_str}"
    response = requests.get(url)
    return response.json()

# Get price chart
def get_price_chart(coins: list, start: int = None, end: int = None):
    coins_str = ",".join(coins)
    url = f"https://api.llama.fi/chart/{coins_str}"
    params = {}
    if start: params["start"] = start
    if end: params["end"] = end
    response = requests.get(url, params=params)
    return response.json()

# Get block at timestamp
def get_block(chain: str, timestamp: int):
    url = f"https://api.llama.fi/block/{chain}/{timestamp}"
    response = requests.get(url)
    return response.json()
```

---

## Stablecoins Endpoints

| Endpoint | Method | Description | Params | Pro |
|----------|--------|-------------|--------|-----|
| `/stablecoins` | GET | List all stablecoins | `includePrices`: bool | No |
| `/stablecoincharts/all` | GET | Historical mcap of all stablecoins | `stablecoin`: id | No |
| `/stablecoincharts/{chain}` | GET | Historical mcap on chain | `chain`, `stablecoin` | No |
| `/stablecoin/{asset}` | GET | Stablecoin details | `asset`: stablecoin id | No |
| `/stablecoinchains` | GET | All chains with stablecoin data | - | No |
| `/stablecoinprices` | GET | Current stablecoin prices | - | No |
| `/stablecoins/stablecoindominance/{chain}` | GET | Stablecoin dominance | `chain` | **Yes** |

### Python Samples - Stablecoins

```python
# Get all stablecoins
def get_stablecoins(include_prices: bool = True):
    url = "https://api.llama.fi/stablecoins"
    params = {"includePrices": str(include_prices).lower()}
    response = requests.get(url, params=params)
    return response.json()

# Get stablecoin details
def get_stablecoin(asset_id: int):
    url = f"https://api.llama.fi/stablecoin/{asset_id}"
    response = requests.get(url)
    return response.json()

# Get stablecoin charts for chain
def get_stablecoin_chart(chain: str):
    url = f"https://api.llama.fi/stablecoincharts/{chain}"
    response = requests.get(url)
    return response.json()
```

---

## Yields Endpoints

| Endpoint | Method | Description | Params | Pro |
|----------|--------|-------------|--------|-----|
| `/pools` | GET | All yield pools | - | No |
| `/chart/{pool}` | GET | Pool APY history | `pool`: pool UUID | No |
| `/yields/poolsOld` | GET | Legacy pools format | - | **Yes** |
| `/yields/poolsBorrow` | GET | Borrow pools | - | **Yes** |
| `/yields/chartLendBorrow/{pool}` | GET | Lend/borrow chart | `pool` | **Yes** |
| `/yields/perps` | GET | Perp funding rates | - | **Yes** |
| `/yields/lsdRates` | GET | LSD rates | - | **Yes** |

### Python Samples - Yields

```python
# Get all yield pools
def get_yield_pools():
    url = "https://api.llama.fi/pools"
    response = requests.get(url)
    return response.json()

# Get pool APY history
def get_pool_chart(pool_id: str):
    url = f"https://api.llama.fi/chart/{pool_id}"
    response = requests.get(url)
    return response.json()

# Pro: Get perp funding rates
def get_perp_yields(api_key: str):
    url = f"https://pro-api.llama.fi/{api_key}/yields/perps"
    response = requests.get(url)
    return response.json()
```

---

## Volumes (DEX) Endpoints

| Endpoint | Method | Description | Params | Pro |
|----------|--------|-------------|--------|-----|
| `/overview/dexs` | GET | DEX volumes overview | `excludeTotalDataChart`, `excludeTotalDataChartBreakdown`, `dataType` | No |
| `/overview/dexs/{chain}` | GET | DEX volumes on chain | `chain`, same as above | No |
| `/summary/dexs/{protocol}` | GET | DEX protocol summary | `protocol`, `dataType` | No |
| `/overview/options` | GET | Options volumes | same params | No |
| `/overview/options/{chain}` | GET | Options on chain | `chain` | No |
| `/summary/options/{protocol}` | GET | Options protocol summary | `protocol` | No |

### Python Samples - Volumes

```python
# Get DEX volumes overview
def get_dex_volumes():
    url = "https://api.llama.fi/overview/dexs"
    response = requests.get(url)
    return response.json()

# Get DEX volumes for chain
def get_dex_volumes_chain(chain: str):
    url = f"https://api.llama.fi/overview/dexs/{chain}"
    response = requests.get(url)
    return response.json()

# Get specific DEX summary
def get_dex_summary(protocol: str):
    url = f"https://api.llama.fi/summary/dexs/{protocol}"
    response = requests.get(url)
    return response.json()
```

---

## Fees & Revenue Endpoints

| Endpoint | Method | Description | Params | Pro |
|----------|--------|-------------|--------|-----|
| `/overview/fees` | GET | Fees overview | `excludeTotalDataChart`, `excludeTotalDataChartBreakdown`, `dataType` | No |
| `/overview/fees/{chain}` | GET | Fees on chain | `chain` | No |
| `/summary/fees/{protocol}` | GET | Protocol fees summary | `protocol` | No |

### Python Samples - Fees

```python
# Get fees overview
def get_fees_overview():
    url = "https://api.llama.fi/overview/fees"
    response = requests.get(url)
    return response.json()

# Get protocol fees
def get_protocol_fees(protocol: str):
    url = f"https://api.llama.fi/summary/fees/{protocol}"
    response = requests.get(url)
    return response.json()
```

---

## Perps Endpoints

| Endpoint | Method | Description | Params | Pro |
|----------|--------|-------------|--------|-----|
| `/overview/open-interest` | GET | Open interest overview | - | No |
| `/api/overview/derivatives` | GET | Derivatives overview | - | **Yes** |
| `/api/summary/derivatives/{protocol}` | GET | Derivatives protocol summary | `protocol` | **Yes** |

---

## Bridges Endpoints (Pro Only)

| Endpoint | Method | Description | Params | Pro |
|----------|--------|-------------|--------|-----|
| `/bridges` | GET | All bridges | - | **Yes** |
| `/bridge/{id}` | GET | Bridge details | `id` | **Yes** |
| `/bridgevolume/{chain}` | GET | Bridge volume on chain | `chain` | **Yes** |
| `/bridgedaystats/{timestamp}/{chain}` | GET | Bridge day stats | `timestamp`, `chain` | **Yes** |
| `/transactions/{id}` | GET | Bridge transactions | `id`, `starttimestamp`, `endtimestamp`, etc. | **Yes** |

---

## Unlocks Endpoints (Pro Only)

| Endpoint | Method | Description | Params | Pro |
|----------|--------|-------------|--------|-----|
| `/api/emissions` | GET | All token emissions | - | **Yes** |
| `/api/emission/{protocol}` | GET | Protocol emissions | `protocol` | **Yes** |

---

## Other Endpoints (Pro Only)

| Endpoint | Method | Description | Params | Pro |
|----------|--------|-------------|--------|-----|
| `/api/categories` | GET | Protocol categories | - | **Yes** |
| `/api/forks` | GET | Protocol forks | - | **Yes** |
| `/api/oracles` | GET | Oracle data | - | **Yes** |
| `/api/hacks` | GET | Hack incidents | - | **Yes** |
| `/api/raises` | GET | Funding raises | - | **Yes** |
| `/api/treasuries` | GET | Protocol treasuries | - | **Yes** |
| `/api/entities` | GET | Entities data | - | **Yes** |
| `/api/historicalLiquidity/{token}` | GET | Token liquidity | `token` | **Yes** |
| `/etfs/snapshot` | GET | ETF snapshot | - | **Yes** |
| `/etfs/flows` | GET | ETF flows | - | **Yes** |
| `/fdv/performance/{period}` | GET | FDV performance | `period`: 1d,7d,30d,90d,180d,365d | **Yes** |
| `/usage/APIKEY` | GET | API usage stats | - | **Yes** |

---

## Quick Test Script

```python
import requests

def test_defillama_endpoints():
    """Test key DefiLlama endpoints are live"""

    tests = [
        ("protocols", "https://api.llama.fi/protocols"),
        ("chains", "https://api.llama.fi/v2/chains"),
        ("stablecoins", "https://api.llama.fi/stablecoins"),
        ("pools", "https://api.llama.fi/pools"),
        ("dex_volumes", "https://api.llama.fi/overview/dexs"),
        ("fees", "https://api.llama.fi/overview/fees"),
        ("prices", "https://api.llama.fi/prices/current/coingecko:ethereum"),
    ]

    results = []
    for name, url in tests:
        try:
            r = requests.get(url, timeout=10)
            status = "OK" if r.status_code == 200 else f"FAIL ({r.status_code})"
        except Exception as e:
            status = f"ERROR ({e})"
        results.append((name, status))
        print(f"{name}: {status}")

    return results

if __name__ == "__main__":
    test_defillama_endpoints()
```

---

## Notes

1. **Rate Limits**: Free tier has standard rate limits. Pro ($300/mo) removes most limits.
2. **Caching**: Data is cached, may not be real-time. TVL updates every ~hour.
3. **Coin Format**: Use `coingecko:coin_id` or `chain:token_address` format for prices.
4. **No Auth for Free**: Most endpoints work without any authentication.
