# Services Module - API Reference

## Overview

Module `services/` chứa logic fetch data từ các API sources. Được thiết kế theo pattern **Template Method** với `BaseFetcher` làm base class.

---

## BaseFetcher

**File:** `services/base_fetcher.py`

### Class Definition

```python
class BaseFetcher:
    """Base class for all API fetchers with common utilities."""

    def __init__(self, chain_name: str, contract_address: str, user_id: str,
                 chain_config: dict, log_callback=None):
        """
        Initialize base fetcher.

        Args:
            chain_name: Blockchain name (e.g., 'Ethereum', 'Solana')
            contract_address: Token contract address
            user_id: User identifier for multi-user storage
            chain_config: Chain configuration from SUPPORTED_CHAINS
            log_callback: Optional callback for logging
        """
```

### Methods

#### log(message, status)
```python
def log(self, message: str, status: str = "info"):
    """
    Log message to UI.

    Args:
        message: Message to log
        status: Log level - "info", "success", "error", "warning"
    """
```

#### save(data, source, endpoint_key)
```python
def save(self, data, source: str, endpoint_key: str):
    """
    Save data to storage (GCS/BigQuery/Local).

    Args:
        data: Data to save (dict or list)
        source: Data source name (e.g., 'coingecko')
        endpoint_key: Endpoint identifier (e.g., 'simple_price')
    """
```

#### update_status(key, success)
```python
def update_status(self, key: str, success: bool = True):
    """
    Update endpoint status in session state.

    Args:
        key: Endpoint key
        success: True for ✅, False for ❌
    """
```

#### skip_status(key)
```python
def skip_status(self, key: str):
    """Mark endpoint as skipped (⚠️)."""
```

---

## DefiLlamaFetcher

**File:** `services/defillama_fetcher.py`

### Endpoints Covered (19)

| Endpoint Key | Description |
|--------------|-------------|
| all_protocols | All protocols TVL |
| protocol_tvl | Single protocol TVL |
| chain_tvl | Historical chain TVL |
| all_chains | All chains TVL |
| current_prices | Current token prices |
| price_chart | Historical price chart |
| price_percentage | Price percentage change |
| stablecoins | All stablecoins |
| stablecoin_chains | Stablecoin by chains |
| yield_pools | Yield farming pools |
| dex_overview | DEX overview |
| dex_chain_volume | DEX volume by chain |
| fees_overview | Fees overview |
| fees_chain | Fees by chain |
| bridges | All bridges |
| bridge_volume | Bridge volume by chain |
| open_interest | Derivatives OI |
| hacks | Security incidents |
| raises | Funding raises |

### Usage

```python
from services.defillama_fetcher import DefiLlamaFetcher

fetcher = DefiLlamaFetcher(
    chain_name="Ethereum",
    contract_address="0x...",
    user_id="user123",
    chain_config={"defillama": "ethereum"},
    log_callback=my_log_function
)

fetcher.fetch_all()  # Fetch all endpoints
```

### Internal Methods

```python
def _fetch_tvl_endpoints(self):
    """Fetch: all_protocols, chain_tvl, all_chains, protocol_tvl"""

def _fetch_price_endpoints(self):
    """Fetch: current_prices, price_chart, price_percentage"""

def _fetch_stablecoin_endpoints(self):
    """Fetch: stablecoins, stablecoin_chains"""

def _fetch_yield_endpoints(self):
    """Fetch: yield_pools"""

def _fetch_dex_endpoints(self):
    """Fetch: dex_overview, dex_chain_volume"""

def _fetch_fees_endpoints(self):
    """Fetch: fees_overview, fees_chain"""

def _fetch_bridge_endpoints(self):
    """Fetch: bridges, bridge_volume"""

def _fetch_other_endpoints(self):
    """Fetch: open_interest, hacks, raises"""
```

---

## CoinGeckoFetcher

**File:** `services/coingecko_fetcher.py`

### Endpoints Covered (27)

| Category | Endpoints |
|----------|-----------|
| Price | simple_price, simple_token_price |
| Coins | coins_list, coins_markets, coin_data, coin_tickers, coin_market_chart, coin_ohlc |
| Contract | coin_info, historical_chart |
| Categories | categories_list, categories |
| Exchanges | exchanges, exchanges_list |
| Derivatives | derivatives, derivatives_exchanges |
| General | asset_platforms, exchange_rates, search, trending, global, global_defi |
| Onchain | onchain_networks, onchain_token, onchain_token_pools, onchain_trending_pools, onchain_new_pools |

### Usage

```python
from services.coingecko_fetcher import CoinGeckoFetcher

fetcher = CoinGeckoFetcher(
    chain_name="Ethereum",
    contract_address="0x...",
    user_id="user123",
    chain_config={"coingecko": "ethereum"},
    cg_days="90",  # Number of days for historical data
    log_callback=my_log_function
)

token_symbol, coin_id = fetcher.fetch_all()
# Returns token_symbol and coin_id for use by other fetchers
```

### Special Notes

1. **coin_info phải được gọi trước** - để lấy `coin_id` cho các endpoints khác
2. Một số endpoints cần `coin_id`, nếu không có sẽ được skip
3. `cg_days` parameter xác định historical data range

---

## NansenFetcher

**File:** `services/nansen_fetcher.py`

### Endpoints Covered (21)

| Category | Endpoints |
|----------|-----------|
| Smart Money | sm_netflow, sm_holdings, sm_dex_trades |
| Profiler | address_balance, address_transactions, address_related_wallets, address_counterparties, address_pnl |
| Token (TGM) | token_screener, token_flows, flow_intelligence, who_bought_sold, token_dex_trades, transfers, holders, token_pnl_leaderboard |
| Perp (TGM) | perp_screener, perp_trades, perp_positions, perp_pnl_leaderboard |
| Portfolio | defi_holdings |

### Usage

```python
from services.nansen_fetcher import NansenFetcher

fetcher = NansenFetcher(
    chain_name="Ethereum",
    contract_address="0x...",
    user_id="user123",
    chain_config={"nansen": "ethereum"},
    start_date="2024-01-01",
    end_date="2024-03-01",
    token_symbol="ETH",  # Optional, from CoinGecko
    log_callback=my_log_function
)

fetcher.fetch_all()
```

### Special Notes

1. Nhiều endpoints cần `start_date` và `end_date`
2. `token_symbol` cần cho perp endpoints
3. Nansen chain names khác với CoinGecko (check `config.py`)

---

## data_fetcher.py (Orchestrator)

**File:** `services/data_fetcher.py`

### Main Function

```python
def fetch_all_data(
    chain_name: str,
    contract_address: str,
    period: str = "3 months",
    log_placeholder=None,
    user_id: str = None,
    theme: str = "Dark"
):
    """
    Main function to fetch data from all API sources.

    Args:
        chain_name: Blockchain name
        contract_address: Token contract address
        period: Time period ('3 months', '6 months', '1 year', 'All')
        log_placeholder: Streamlit placeholder for live log
        user_id: User identifier
        theme: UI theme for log styling

    Flow:
        1. Reset session state
        2. Calculate date ranges from period
        3. Run DefiLlamaFetcher.fetch_all()
        4. Run CoinGeckoFetcher.fetch_all() → get token_symbol
        5. Run NansenFetcher.fetch_all(token_symbol)
        6. Log completion summary
    """
```

### Period to Days Mapping

| Period | Days |
|--------|------|
| 3 months | 90 |
| 6 months | 180 |
| 1 year | 365 |
| All | 1095 (3 years) |

---

## Adding New Fetcher

### Step 1: Create API Client

```python
# api_clients/newsource_client.py
class NewSourceClient:
    def __init__(self):
        self.base_url = "https://api.newsource.com"
        self.api_key = API_KEYS.get('NEWSOURCE_API_KEY')

    def get_endpoint_a(self, param):
        return self._get(f"/endpoint-a?param={param}")

    def _get(self, path):
        response = requests.get(f"{self.base_url}{path}", headers=...)
        return response.json()
```

### Step 2: Create Fetcher

```python
# services/newsource_fetcher.py
from services.base_fetcher import BaseFetcher
from api_clients.newsource_client import NewSourceClient

class NewSourceFetcher(BaseFetcher):
    SOURCE = "newsource"

    def __init__(self, chain_name, contract_address, user_id, chain_config, log_callback=None):
        super().__init__(chain_name, contract_address, user_id, chain_config, log_callback)
        self.client = NewSourceClient()

    def fetch_all(self):
        self.log("NEWSOURCE ENDPOINTS", "info")
        self._fetch_endpoint_a()
        self._fetch_endpoint_b()

    def _fetch_endpoint_a(self):
        try:
            data = self.client.get_endpoint_a(self.contract_address)
            self.save(data, self.SOURCE, 'endpoint_a')
            self.update_status("endpoint_a", True)
            self.log("Endpoint A fetched", "success")
        except Exception as e:
            self.update_status("endpoint_a", False)
            self.log(f"Endpoint A error: {e}", "error")
```

### Step 3: Add to Orchestrator

```python
# services/data_fetcher.py
from services.newsource_fetcher import NewSourceFetcher

def fetch_all_data(...):
    ...
    # Add new fetcher
    ns_fetcher = NewSourceFetcher(
        chain_name, contract_address, user_id, chain_config,
        log_callback=log_to_ui
    )
    ns_fetcher.fetch_all()
```

### Step 4: Register Endpoints

```python
# constants/endpoints.py
ENDPOINT_MAPPING = {
    ...
    # NewSource
    "NS2: Endpoint A": ("newsource", "endpoint_a"),
    "NS2: Endpoint B": ("newsource", "endpoint_b"),
}

SOURCE_DISPLAY_MAP = {
    ...
    "newsource": "NewSource",
}
```

---

## Error Handling Pattern

```python
def _fetch_something(self):
    try:
        # 1. Fetch data
        data = self.client.get_something(...)

        # 2. Save to storage
        self.save(data, self.SOURCE, 'endpoint_key')

        # 3. Update status to success
        self.update_status("endpoint_key", True)

        # 4. Log success message
        self.log(f"Fetched {len(data)} items", "success")

        return data

    except Exception as e:
        # On error: update status and log
        self.update_status("endpoint_key", False)
        self.log(f"Error: {str(e)[:50]}", "error")
        return None
```

---

## Testing Fetchers

```python
# Test individual fetcher
python -c "
from services.defillama_fetcher import DefiLlamaFetcher
from config import SUPPORTED_CHAINS

fetcher = DefiLlamaFetcher(
    'Ethereum',
    '0x...',
    'test_user',
    SUPPORTED_CHAINS['Ethereum']
)
# Don't call fetch_all() in test - just verify import
print('DefiLlamaFetcher OK')
"
```
