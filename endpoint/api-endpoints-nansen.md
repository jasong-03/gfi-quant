# Nansen API Endpoints Reference

**Last Updated**: 2024-12-29
**Base URL**: `https://api.nansen.ai`
**Documentation**: https://docs.nansen.ai/
**Official SDK**: None (use `requests`)

---

## Pricing & Credits

| Plan | Subscription | Credits Included |
|------|-------------|------------------|
| Free | $0 | 100 one-time trial credits |
| Pro | $49/mo (annual) or $69/mo (monthly) | 1,000 starter credits |

### Credit Packages
| Amount | Credits |
|--------|---------|
| $100 | 100,000 |
| $500 | 500,000 |
| $1,000 | 1,000,000 |

### Credit Cost by Endpoint Type
| Endpoint Type | Credits/Call |
|---------------|--------------|
| Basic Profiler (balances, txns, etc.) | 1 |
| Advanced Profiler (counterparties, leaderboard) | 5 |
| Smart Money (all endpoints) | 5 |
| TGM Basic (screener, flows, trades) | 1 |
| TGM Advanced (holders, leaderboards) | 5 |
| Labels | 500 |

---

## Authentication

```python
import requests

BASE_URL = "https://api.nansen.ai"
API_KEY = "your-api-key"

headers = {
    "apiKey": API_KEY,
    "Content-Type": "application/json"
}

# All endpoints use POST method with JSON body
response = requests.post(
    f"{BASE_URL}/api/v1/endpoint",
    headers=headers,
    json={"param": "value"}
)
```

---

## Supported Chains

| Chain | Parameter Value | Profiler | TGM | Smart Money |
|-------|-----------------|----------|-----|-------------|
| Ethereum | `ethereum` | ✅ | ✅ | ✅ |
| Solana | `solana` | ✅ | ✅ | ✅ |
| Base | `base` | ✅ | ✅ | ✅ |
| Arbitrum | `arbitrum` | ✅ | ✅ | ✅ |
| BNB | `bnb` | ✅ | ✅ | ✅ |
| Polygon | `polygon` | ✅ | ✅ | ✅ |
| Avalanche | `avalanche` | ✅ | ✅ | ✅ |
| Optimism | `optimism` | ✅ | ✅ | ✅ |
| zkSync | `zksync` | ✅ | ✅ | ✅ |
| Linea | `linea` | ✅ | ✅ | ✅ |
| Scroll | `scroll` | ✅ | ✅ | ✅ |
| Mantle | `mantle` | ✅ | ✅ | ✅ |
| HyperEVM | `hyperevm` | ✅ | ✅ | ✅ |
| Monad | `monad` | ✅ | ✅ | ✅ |
| Sonic | `sonic` | ✅ | ✅ | ✅ |
| IOTA | `iotaevm` | ✅ | ✅ | ✅ |
| Sei | `sei` | ✅ | ✅ | ✅ |
| Ronin | `ronin` | ✅ | ✅ | ✅ |
| Unichain | `unichain` | ✅ | ✅ | ✅ |
| Plasma | `plasma` | ✅ | ✅ | ✅ |
| Bitcoin | `bitcoin` | ✅ | ✅ | - |
| Starknet | `starknet` | ✅ | ✅ | - |
| TON | `ton` | ✅ | ✅ | - |
| TRON | `tron` | ✅ | ✅ | - |

Use `all` to query across all chains.

---

## Smart Money Endpoints

Smart Money = Top 5,000 highest-performing wallets (30D/90D/180D Smart Traders, Funds)

| Endpoint | Method | Description | Credits | Free Tier |
|----------|--------|-------------|---------|-----------|
| `/api/v1/smart-money/netflow` | POST | Net capital flows (inflows vs outflows) | 5 | No |
| `/api/v1/smart-money/holdings` | POST | Current token holdings | 5 | No |
| `/api/v1/smart-money/historical-holdings` | POST | Historical holdings over time | 5 | No |
| `/api/v1/smart-money/dex-trades` | POST | DEX trades in last 24h | 5 | No |
| `/api/v1/smart-money/dcas` | POST | Jupiter DCA orders (Solana) | 5 | No |
| `/api/v1/smart-money/perp-trades` | POST | Hyperliquid perp trades | 5 | No |

### Params - Smart Money Netflow
```json
{
  "chains": ["ethereum", "solana"],
  "filters": {
    "include_smart_money_labels": ["Fund", "Smart Trader"],
    "exclude_smart_money_labels": ["30D Smart Trader"],
    "include_stablecoins": false,
    "include_native_tokens": false,
    "token_sectors": ["DeFi"]
  },
  "pagination": {"page": 1, "per_page": 10},
  "order_by": [{"field": "net_flow_24h_usd", "direction": "DESC"}]
}
```

### Python Sample - Smart Money
```python
def get_smart_money_netflow(chains: list, labels: list = None):
    url = f"{BASE_URL}/api/v1/smart-money/netflow"
    payload = {
        "chains": chains,
        "filters": {
            "include_smart_money_labels": labels or ["Fund", "Smart Trader"],
            "include_stablecoins": False
        },
        "pagination": {"page": 1, "per_page": 50},
        "order_by": [{"field": "net_flow_24h_usd", "direction": "DESC"}]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_smart_money_holdings(chains: list):
    url = f"{BASE_URL}/api/v1/smart-money/holdings"
    payload = {
        "chains": chains,
        "pagination": {"page": 1, "per_page": 50}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_smart_money_dex_trades(chains: list):
    url = f"{BASE_URL}/api/v1/smart-money/dex-trades"
    payload = {
        "chains": chains,
        "pagination": {"page": 1, "per_page": 50}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_smart_money_perp_trades():
    """Get Hyperliquid perp trades from smart money"""
    url = f"{BASE_URL}/api/v1/smart-money/perp-trades"
    payload = {"pagination": {"page": 1, "per_page": 50}}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

---

## Profiler Endpoints

Analyze any wallet address or entity cluster.

| Endpoint | Method | Description | Credits | Free Tier |
|----------|--------|-------------|---------|-----------|
| `/api/v1/profiler/address/current-balance` | POST | Current token balances | 1 | ✅ |
| `/api/v1/profiler/address/historical-balances` | POST | Historical holdings | 1 | ✅ |
| `/api/v1/profiler/address/transactions` | POST | Transaction list | 1 | ✅ |
| `/api/v1/profiler/address/related-wallets` | POST | Related wallets (1st degree) | 1 | ✅ |
| `/api/v1/profiler/address/counterparties` | POST | Top counterparties | 5 | ✅ |
| `/api/v1/profiler/address/pnl-summary` | POST | Trade summary + top 5 trades | 1 | - |
| `/api/v1/profiler/address/pnl` | POST | All past trades with PnL | 1 | - |
| `/api/v1/profiler/perp-positions` | POST | Hyperliquid positions | 1 | - |
| `/api/v1/profiler/perp-trades` | POST | Hyperliquid trades | 1 | - |
| `/api/v1/profiler/perp-leaderboard` | POST | Hyperliquid leaderboard | 5 | - |
| `/api/v1/profiler/address/labels` | POST | Address labels (entity + behavioral) | 500 | - |
| `/api/v1/profiler/entity/search` | POST | Search entity by name | - | ✅ |

### Params - Profiler Current Balance
```json
{
  "address": "0x28c6c06298d514db089934071355e5743bf21d60",
  "chain": "ethereum",
  "hide_spam_token": true,
  "filters": {
    "token_symbol": "USDC",
    "value_usd": {"min": 10}
  },
  "pagination": {"page": 1, "per_page": 10}
}
```

### Python Sample - Profiler
```python
def get_address_balance(address: str, chain: str = "ethereum"):
    url = f"{BASE_URL}/api/v1/profiler/address/current-balance"
    payload = {
        "address": address,
        "chain": chain,
        "hide_spam_token": True,
        "pagination": {"page": 1, "per_page": 100}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_address_transactions(address: str, chain: str = "ethereum"):
    url = f"{BASE_URL}/api/v1/profiler/address/transactions"
    payload = {
        "address": address,
        "chain": chain,
        "pagination": {"page": 1, "per_page": 50}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_related_wallets(address: str, chain: str = "ethereum"):
    url = f"{BASE_URL}/api/v1/profiler/address/related-wallets"
    payload = {
        "address": address,
        "chain": chain,
        "pagination": {"page": 1, "per_page": 50}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_address_counterparties(address: str, chain: str = "ethereum"):
    url = f"{BASE_URL}/api/v1/profiler/address/counterparties"
    payload = {
        "address": address,
        "chain": chain,
        "pagination": {"page": 1, "per_page": 20}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_address_pnl(address: str, chain: str = "ethereum"):
    url = f"{BASE_URL}/api/v1/profiler/address/pnl"
    payload = {
        "address": address,
        "chain": chain,
        "pagination": {"page": 1, "per_page": 50}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_address_labels(address: str, chain: str = "ethereum"):
    """Costs 500 credits per call!"""
    url = f"{BASE_URL}/api/v1/profiler/address/labels"
    payload = {
        "address": address,
        "chain": chain
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_hyperliquid_leaderboard():
    url = f"{BASE_URL}/api/v1/profiler/perp-leaderboard"
    payload = {"pagination": {"page": 1, "per_page": 50}}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def search_entity(name: str):
    url = f"{BASE_URL}/api/v1/profiler/entity/search"
    payload = {"query": name}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

---

## Token God Mode (TGM) Endpoints

Comprehensive token analytics - Smart Money, holders, exchange flows.

| Endpoint | Method | Description | Credits | Free Tier |
|----------|--------|-------------|---------|-----------|
| `/api/v1/tgm/token-screener` | POST | Real-time token analytics | 1 | ✅ |
| `/api/v1/tgm/perp-screener` | POST | Hyperliquid token screener | 1 | - |
| `/api/v1/tgm/flow-intelligence` | POST | Token flows summary | 1 | - |
| `/api/v1/tgm/flows` | POST | Inflow/outflow by category | 1 | ✅ |
| `/api/v1/tgm/who-bought-sold` | POST | Recent buyers/sellers | 1 | ✅ |
| `/api/v1/tgm/dex-trades` | POST | All DEX trades | 1 | ✅ |
| `/api/v1/tgm/transfers` | POST | Top token transfers | 1 | ✅ |
| `/api/v1/tgm/jup-dca` | POST | Jupiter DCA orders | 1 | - |
| `/api/v1/tgm/perp-trades` | POST | Perp trading history | 1 | - |
| `/api/v1/tgm/perp-positions` | POST | Open perp positions | 5 | - |
| `/api/v1/tgm/holders` | POST | Top holders by category | 5 | ✅ |
| `/api/v1/tgm/pnl-leaderboard` | POST | PnL leaderboard | 5 | - |
| `/api/v1/tgm/perp-pnl-leaderboard` | POST | Hyperliquid PnL leaderboard | 5 | - |

### Params - Token Screener
```json
{
  "chains": ["ethereum", "solana"],
  "filters": {
    "market_cap_usd": {"min": 1000000, "max": 100000000},
    "token_age_days": {"min": 7},
    "smart_money_net_flow_24h_usd": {"min": 10000}
  },
  "pagination": {"page": 1, "per_page": 50},
  "order_by": [{"field": "smart_money_net_flow_24h_usd", "direction": "DESC"}]
}
```

### Python Sample - TGM
```python
def get_token_screener(chains: list, min_mcap: int = 1000000):
    url = f"{BASE_URL}/api/v1/tgm/token-screener"
    payload = {
        "chains": chains,
        "filters": {
            "market_cap_usd": {"min": min_mcap},
            "token_age_days": {"min": 1}
        },
        "pagination": {"page": 1, "per_page": 50},
        "order_by": [{"field": "smart_money_net_flow_24h_usd", "direction": "DESC"}]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_token_flows(token_address: str, chain: str):
    url = f"{BASE_URL}/api/v1/tgm/flows"
    payload = {
        "token_address": token_address,
        "chain": chain
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_token_holders(token_address: str, chain: str):
    url = f"{BASE_URL}/api/v1/tgm/holders"
    payload = {
        "token_address": token_address,
        "chain": chain,
        "pagination": {"page": 1, "per_page": 50}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_who_bought_sold(token_address: str, chain: str):
    url = f"{BASE_URL}/api/v1/tgm/who-bought-sold"
    payload = {
        "token_address": token_address,
        "chain": chain,
        "pagination": {"page": 1, "per_page": 50}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_token_dex_trades(token_address: str, chain: str):
    url = f"{BASE_URL}/api/v1/tgm/dex-trades"
    payload = {
        "token_address": token_address,
        "chain": chain,
        "pagination": {"page": 1, "per_page": 50}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_token_transfers(token_address: str, chain: str):
    url = f"{BASE_URL}/api/v1/tgm/transfers"
    payload = {
        "token_address": token_address,
        "chain": chain,
        "pagination": {"page": 1, "per_page": 50}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_pnl_leaderboard(token_address: str, chain: str):
    url = f"{BASE_URL}/api/v1/tgm/pnl-leaderboard"
    payload = {
        "token_address": token_address,
        "chain": chain,
        "pagination": {"page": 1, "per_page": 50}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

---

## Portfolio API

| Endpoint | Method | Description | Credits | Free Tier |
|----------|--------|-------------|---------|-----------|
| `/api/v1/portfolio/defi-holdings` | POST | DeFi positions across addresses | 1 | ✅ |

### Python Sample - Portfolio
```python
def get_defi_holdings(addresses: list, chains: list = None):
    url = f"{BASE_URL}/api/v1/portfolio/defi-holdings"
    payload = {
        "addresses": addresses,
        "chains": chains or ["all"],
        "pagination": {"page": 1, "per_page": 50}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

---

## Quick Test Script

```python
import requests
import time

BASE_URL = "https://api.nansen.ai"
API_KEY = "your-api-key"
headers = {"apiKey": API_KEY, "Content-Type": "application/json"}

def test_nansen_endpoints():
    """Test key Nansen endpoints (uses credits!)"""

    tests = [
        ("profiler_balance", "/api/v1/profiler/address/current-balance", {
            "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # vitalik.eth
            "chain": "ethereum",
            "hide_spam_token": True,
            "pagination": {"page": 1, "per_page": 5}
        }),
        ("profiler_transactions", "/api/v1/profiler/address/transactions", {
            "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
            "chain": "ethereum",
            "pagination": {"page": 1, "per_page": 5}
        }),
        ("tgm_token_screener", "/api/v1/tgm/token-screener", {
            "chains": ["ethereum"],
            "pagination": {"page": 1, "per_page": 5}
        }),
    ]

    results = []
    for name, endpoint, payload in tests:
        try:
            url = f"{BASE_URL}{endpoint}"
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            if r.status_code == 200:
                data = r.json()
                status = f"OK (got {len(data.get('data', []))} items)"
            else:
                status = f"FAIL ({r.status_code}: {r.text[:100]})"
        except Exception as e:
            status = f"ERROR ({e})"

        results.append((name, status))
        print(f"{name}: {status}")
        time.sleep(1)  # Rate limit

    return results

if __name__ == "__main__":
    print("WARNING: This script will consume Nansen API credits!")
    confirm = input("Continue? (y/n): ")
    if confirm.lower() == "y":
        test_nansen_endpoints()
```

---

## Free Tier Available Endpoints

Users on Free plan can access these endpoints:

1. `/api/v1/profiler/address/transactions`
2. `/api/v1/profiler/address/current-balance`
3. `/api/v1/profiler/address/historical-balances`
4. `/api/v1/profiler/address/counterparties`
5. `/api/v1/profiler/address/related-wallets`
6. `/api/v1/tgm/flows`
7. `/api/v1/tgm/who-bought-sold`
8. `/api/v1/tgm/dex-trades`
9. `/api/v1/tgm/transfers`
10. `/api/v1/tgm/holders`
11. `/api/v1/portfolio/defi-holdings`
12. `/api/v1/tgm/token-screener`

**Note**: Free tier has 100 one-time credits only, no label access, no Smart Money endpoints.

---

## Rate Limits

| Plan | Rate Limit |
|------|------------|
| Free | 10 requests/minute |
| Pro | 60 requests/minute |

---

## Notes

1. **All endpoints use POST**: Unlike other APIs, Nansen uses POST for all data requests
2. **JSON body required**: Always send request body as JSON
3. **Pagination**: Use `pagination` object with `page` and `per_page`
4. **Sorting**: Use `order_by` array with `field` and `direction` (ASC/DESC)
5. **Filtering**: Each endpoint has specific filter fields
6. **Labels are expensive**: 500 credits per call - use sparingly
7. **Beta deprecation**: `/beta` endpoints deprecated Oct 2025, use `/v1`
