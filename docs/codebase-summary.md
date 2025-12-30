# Codebase Summary

## Overview

This document provides a comprehensive reference for all modules, classes, and functions in the GFI Quant Token Tracker Dashboard. Use this as a developer reference when extending or maintaining the codebase.

---

## Directory Structure

```
gfi-quant-project/
├── app.py                          # Main Streamlit application (entry point)
├── config.py                       # Runtime configuration with API keys
├── config_template.py              # Template for config setup
├── integrate_nansen_cg.py          # Integration example script
├── delta_balance_change_dune_query.txt  # SQL template for Dune queries
├── api_clients/                    # API client implementations
│   ├── dune_client.py             # Dune Analytics API client
│   ├── defillama_client.py        # DeFi Llama API client
│   ├── nansen_client.py           # Nansen blockchain intelligence client
│   └── coingecko_client.py        # CoinGecko price data client
├── data_handlers/                  # Data management
│   ├── processors.py              # Data transformation (stubs)
│   └── storage.py                 # JSON persistence with timestamps
├── utils/                          # Utility functions
│   ├── logger.py                  # Dual-channel logging
│   └── validators.py              # Address validation
├── visualizations/                 # Chart and table components
│   ├── charts.py                  # Plotly chart functions
│   └── tables.py                  # DataFrame processing
├── endpoint/                       # API documentation and testing
│   ├── test_api_endpoints.py      # API endpoint testing
│   ├── api-endpoints-*.md         # Provider-specific documentation
│   └── api_test_report.md         # Test results
├── assets/                         # Static resources
│   ├── icon.jpg                   # Application icon
│   └── {provider}.jpg             # Provider logos
└── data/                           # Cached data (auto-created)
```

---

## Core Application

### app.py

**Purpose**: Main Streamlit application entry point. Handles UI layout, user input, data fetching orchestration, and visualization rendering.

#### Key Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `check_credits(api_name)` | Verify API connectivity and credits | `api_name: str` | None (updates session state) |
| `get_image_base64(path)` | Convert image to base64 for HTML embedding | `path: str` | `str` or `None` |
| `get_endpoint_list()` | Get sorted endpoint status list | None | `List[Dict]` |
| `load_dune_query(chain, address, period)` | Format Dune SQL query with parameters | `chain, address, period: str` | `str` or `None` |
| `fetch_all_data(...)` | Main orchestration function for all API calls | See below | None |

#### fetch_all_data Parameters

```python
def fetch_all_data(
    chain_name: str,        # Blockchain network name
    contract_address: str,  # Token contract address
    period: str,            # Time period ("3 months", "6 months", "1 year", "All")
    log_placeholder=None    # Streamlit placeholder for live logging
) -> None
```

#### Session State Variables

| Variable | Type | Purpose |
|----------|------|---------|
| `st.session_state.logs` | `List[str]` | Log message history |
| `st.session_state.fetched_data` | `Dict` | Cached fetch results |
| `st.session_state.endpoint_status` | `Dict[str, str]` | Endpoint fetch statuses |
| `st.session_state.preview_endpoint` | `str` or `None` | Currently previewed endpoint |
| `st.session_state.api_usage` | `Dict` | API connectivity status |

#### Endpoint Mapping

```python
ENDPOINT_MAPPING = {
    "Get Price Chart": ("defillama", "price_chart"),
    "Get Price Percentage Change": ("defillama", "price_percentage"),
    "Token Who Bought/Sold": ("nansen", "who_bought_sold"),
    "Token Perp Trades": ("nansen", "perp_trades"),
    "Token Transfers": ("nansen", "transfers"),
    "Token Holders": ("nansen", "holders"),
    "Coin Historical Chart by Token Address": ("coingecko", "historical_chart"),
    "Token Flow Intelligence": ("nansen", "flow_intelligence"),
    "Delta Balance Change": ("dune", "delta_balance")
}
```

---

## Configuration

### config.py

**Purpose**: Runtime configuration loading with multi-source fallback (local settings, Streamlit secrets, environment variables).

#### Exports

| Name | Type | Description |
|------|------|-------------|
| `API_KEYS` | `Dict[str, str]` | API key mapping for all providers |
| `API_URLS` | `Dict[str, str]` | Base URL mapping for all providers |
| `DATA_DIR` | `str` | Path to data storage directory |
| `CACHE_DURATION` | `int` | Cache TTL in seconds (default: 300) |
| `SOURCE_ICONS` | `Dict[str, str]` | Provider name to icon filename mapping |
| `SUPPORTED_CHAINS` | `Dict[str, Dict]` | Chain configuration with API-specific identifiers |
| `REQUEST_TIMEOUT` | `int` | HTTP request timeout in seconds |
| `RATE_LIMITS` | `Dict[str, int]` | Requests per minute by provider |

#### API URLs

```python
API_URLS = {
    'DEFILLAMA': 'https://coins.llama.fi',
    'DEFILLAMA_YIELDS': 'https://yields.llama.fi',
    'DEFILLAMA_API': 'https://api.llama.fi',
    'NANSEN': 'https://api.nansen.ai/api/v1',
    'COINGECKO': 'https://pro-api.coingecko.com/api/v3',
    'DUNE': 'https://api.dune.com/api/v1'
}
```

#### Chain Configuration Structure

```python
SUPPORTED_CHAINS = {
    'Ethereum': {
        'defillama': 'ethereum',
        'nansen': 'ethereum',
        'coingecko': 'ethereum',
        'id': 'ethereum'
    },
    # ... additional chains
}
```

---

## API Clients

### api_clients/dune_client.py

**Class**: `DuneClient`

**Purpose**: Interface with Dune Analytics API for SQL query execution.

#### Constructor

```python
def __init__(self, api_key: str = None)
```

#### Methods

| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `create_query(name, query_sql)` | Create a new private query | `name: str, query_sql: str` | `Dict` with `query_id` |
| `execute_query(query_id, params)` | Execute a query | `query_id: int, params: Dict` | `Dict` with `execution_id` |
| `get_execution_status(execution_id)` | Poll execution status | `execution_id: str` | `Dict` with `state` |
| `get_execution_results(execution_id)` | Retrieve query results | `execution_id: str` | `Dict` with `result.rows` |

#### Example Usage

```python
dune = DuneClient()

# Create and execute query
query_resp = dune.create_query("My Query", "SELECT * FROM ethereum.transactions LIMIT 10")
query_id = query_resp['query_id']

exec_resp = dune.execute_query(query_id)
execution_id = exec_resp['execution_id']

# Poll for completion
status = dune.get_execution_status(execution_id)
if status['state'] == 'QUERY_STATE_COMPLETED':
    results = dune.get_execution_results(execution_id)
```

---

### api_clients/defillama_client.py

**Class**: `DefiLlamaClient`

**Purpose**: Interface with DefiLlama API for price and DeFi protocol data.

#### Constructor

```python
def __init__(self, api_key: str = None)
```

#### Methods

| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `get_price_chart(chain, address, period)` | Historical price data | `chain, address, period: str` | `Dict` with price array |
| `get_price_percentage_change(chain, address)` | Price change percentages | `chain, address: str` | `Dict` with percentages |
| `get_token_protocols(symbol)` | Protocols using token | `symbol: str` | `Dict` with protocol list |
| `get_borrowing_rates()` | DeFi borrowing rates | None | `Dict` with pool data |

#### Example Usage

```python
client = DefiLlamaClient()

# Get price chart for USDC on Ethereum
prices = client.get_price_chart(
    'ethereum',
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    '7d'
)
```

---

### api_clients/nansen_client.py

**Class**: `NansenClient`

**Purpose**: Interface with Nansen API for blockchain intelligence data.

#### Constructor

```python
def __init__(self, api_key: str = None)
```

#### Methods

| Method | Purpose | Key Parameters | Returns |
|--------|---------|----------------|---------|
| `get_token_who_bought_sold(...)` | Buy/sell activity by smart money | `address, chain, start_date, end_date, buy_or_sell` | `Dict` with wallet data |
| `get_token_perp_trades(...)` | Perpetual trading activity | `token_symbol, start_date, end_date, filters` | `Dict` with trade data |
| `get_token_transfers(...)` | Token transfer history | `address, chain, start_date, end_date` | `Dict` with transfer data |
| `get_token_holders(...)` | Top token holders | `address, chain, page, per_page` | `Dict` with holder data |
| `get_token_flow_intelligence(...)` | Multi-timeframe flow data | `address, chain` | `Dict` keyed by timeframe |

#### Flow Intelligence Timeframes

The `get_token_flow_intelligence` method fetches data for: `5m`, `1h`, `6h`, `12h`, `1d`, `7d`

#### Example Usage

```python
nansen = NansenClient()

# Get top 100 holders
holders = nansen.get_token_holders(
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'ethereum',
    page=1,
    per_page=100
)

# Get flow intelligence (returns data for all timeframes)
flows = nansen.get_token_flow_intelligence(
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'ethereum'
)
```

---

### api_clients/coingecko_client.py

**Class**: `CoinGeckoClient`

**Purpose**: Interface with CoinGecko API for market data.

#### Constructor

```python
def __init__(self, api_key: str = None)
```

#### Methods

| Method | Purpose | Parameters | Returns |
|--------|---------|------------|---------|
| `get_coins_list()` | Get all coins with IDs | None | `List[Dict]` |
| `get_coin_historical_chart_by_contract(...)` | Historical OHLC by contract | `coin_id, contract_address, vs_currency, days` | `Dict` with prices |
| `get_coin_data(coin_id)` | Full coin metadata | `coin_id: str` | `Dict` with coin info |
| `get_coin_info_by_contract(...)` | Coin info by contract address | `platform_id, contract_address` | `Dict` with coin info |

#### Example Usage

```python
cg = CoinGeckoClient()

# Get historical chart for WETH on Ethereum
chart = cg.get_coin_historical_chart_by_contract(
    'ethereum',
    '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    vs_currency='usd',
    days='30'
)

# Get coin metadata
info = cg.get_coin_info_by_contract('ethereum', '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2')
symbol = info['symbol'].upper()  # 'WETH'
```

---

## Data Handlers

### data_handlers/storage.py

**Purpose**: JSON file persistence with automatic directory creation and timestamp-based naming.

#### Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `ensure_directory(path)` | Create directory tree if not exists | `path: str` | None |
| `save_json(...)` | Save API response to timestamped JSON | See below | `str` (filepath) |
| `load_latest_json(...)` | Load most recent JSON for endpoint | See below | `Dict` or `None` |

#### save_json Signature

```python
def save_json(
    data: Dict,           # Raw API response
    source: str,          # API provider name
    chain: str,           # Blockchain network
    address: str,         # Contract address
    endpoint_name: str    # Endpoint identifier
) -> str
```

#### Storage Path Format

```
data/{source}/{chain}/{address}/{endpoint_name}_{YYYYMMDD_HHMMSS}.json
```

#### Example Usage

```python
from data_handlers.storage import save_json, load_latest_json

# Save fetched data
filepath = save_json(
    response_data,
    'nansen',
    'ethereum',
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'holders'
)

# Load latest cached data
data = load_latest_json(
    'nansen',
    'ethereum',
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'holders'
)
```

---

### data_handlers/processors.py

**Purpose**: Data transformation utilities (stub implementations).

#### Functions

| Function | Purpose | Status |
|----------|---------|--------|
| `process_price_chart(data)` | Transform price data to DataFrame | Stub |
| `process_holders(data)` | Transform holder data to DataFrame | Stub |

---

## Utilities

### utils/logger.py

**Purpose**: Dual-channel logging to console and Streamlit UI.

#### Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `setup_logger()` | Configure Python logging | None | `Logger` instance |
| `log_to_ui(message, status)` | Log to console and session state | `message: str, status: str` | None |

#### Status Icons

| Status | Icon |
|--------|------|
| `"success"` | checkmark |
| `"error"` | X mark |
| `"info"` | hourglass |

#### Example Usage

```python
from utils.logger import log_to_ui

log_to_ui("Starting data fetch...", "info")
log_to_ui("Holders fetched successfully", "success")
log_to_ui("API request failed", "error")
```

---

### utils/validators.py

**Purpose**: Input validation utilities.

#### Functions

| Function | Purpose | Parameters | Returns |
|----------|---------|------------|---------|
| `validate_contract_address(address, chain)` | Validate address format by chain | `address, chain: str` | `bool` |

#### Validation Rules

| Chain Type | Pattern | Length |
|------------|---------|--------|
| EVM (Ethereum, Polygon, etc.) | `^0x[a-fA-F0-9]{40}$` | 42 chars |
| Solana | `^[1-9A-HJ-NP-Za-km-z]{32,44}$` | 32-44 chars |

#### Example Usage

```python
from utils.validators import validate_contract_address

# EVM address
is_valid = validate_contract_address(
    '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'Ethereum'
)  # True

# Solana address
is_valid = validate_contract_address(
    'So11111111111111111111111111111111111111112',
    'Solana'
)  # True
```

---

## Visualizations

### visualizations/charts.py

**Purpose**: Plotly chart generation functions.

#### Functions

| Function | Data Source | Description |
|----------|-------------|-------------|
| `create_price_chart(data)` | DefiLlama/CoinGecko | Line chart of historical prices |
| `create_holders_pie_chart(data)` | Nansen | Legacy pie chart (placeholder) |
| `create_holders_bar_chart(data)` | Nansen | Horizontal bar chart of top 20 holders |
| `create_delta_balance_chart(data)` | Dune | Dual-axis bar/line chart |

#### create_price_chart

Supports two data formats:
- CoinGecko: `{'prices': [[timestamp_ms, price], ...]}`
- DefiLlama: `{'coins': {'chain:address': {'prices': [{'timestamp': t, 'price': p}]}}}`

#### create_delta_balance_chart

Creates a dual-axis chart with:
- **Y1 (Right)**: Balance change bars (green/red for positive/negative)
- **Y2 (Left)**: Price line overlay

Expected data format:
```python
{
    'result': {
        'rows': [
            {'timestamp': '...', 'positive_delta': 100, 'negative_delta': -50, 'price': 1.0},
            ...
        ]
    }
}
```

---

### visualizations/tables.py

**Purpose**: DataFrame creation and formatting for tabular display.

#### Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `create_flow_intelligence_table(data)` | Process multi-timeframe flow data | `Tuple[DataFrame, DataFrame, DataFrame]` |
| `create_transfers_table(data)` | Format transfer history | `DataFrame` |

#### create_flow_intelligence_table

Returns three DataFrames:
1. **Net Flow USD**: Net token flow by wallet category and timeframe
2. **Avg Flow USD**: Average flow by wallet category and timeframe
3. **Wallet Count**: Active wallets by category and timeframe

Categories: `public_figure`, `top_pnl`, `whale`, `smart_trader`, `exchange`, `fresh_wallets`

#### create_transfers_table

Columns included (when available):
- `block_timestamp`
- `from_address`
- `to_address`
- `transfer_value_usd` or `value_usd`
- `transaction_hash`

---

## Integration Example

### integrate_nansen_cg.py

**Purpose**: Demonstrates integration pattern between CoinGecko (for token metadata) and Nansen (for trading data).

#### Workflow

1. Initialize CoinGecko and Nansen clients
2. Get token info from CoinGecko by contract address
3. Extract token symbol from metadata
4. Use symbol to query Nansen perp trades endpoint

#### Example Pattern

```python
# Get symbol from contract address
coin_info = cg_client.get_coin_info_by_contract(platform_id, contract_address)
symbol = coin_info.get('symbol', '').upper()

# Use symbol for Nansen query
perp_trades = nansen_client.get_token_perp_trades(
    token_symbol=symbol,
    start_date=start_date,
    end_date=end_date
)
```

---

## Dependencies

### Runtime Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| streamlit | - | Web framework |
| pandas | - | Data manipulation |
| plotly | - | Interactive charts |
| requests | - | HTTP client |
| python-dotenv | - | Environment variables |

### Development Dependencies

| Package | Purpose |
|---------|---------|
| watchdog | File system monitoring for hot reload |

---

## File Types

| Extension | Location | Purpose |
|-----------|----------|---------|
| `.py` | Root, `api_clients/`, `data_handlers/`, `utils/`, `visualizations/` | Python source |
| `.json` | `data/` (auto-generated) | Cached API responses |
| `.md` | `endpoint/`, `docs/` | Documentation |
| `.txt` | Root | SQL query templates |
| `.jpg` | `assets/` | UI icons and logos |

