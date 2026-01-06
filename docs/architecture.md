# GFI Quant Project - Architecture Documentation

## Overview

GFI Quant Project là một Streamlit dashboard để theo dõi và phân tích token trên nhiều blockchain. Project sử dụng kiến trúc modular với separation of concerns rõ ràng.

**Tech Stack:**
- Frontend: Streamlit
- Data Sources: DefiLlama, CoinGecko, Nansen, Dune Analytics
- Storage: Google Cloud Storage, BigQuery
- Exchange Data: CCXT (cho CDC Tracker)

---

## Project Structure

```
gfi-quant-project/
├── app.py                      # Main entry point (~140 lines)
│
├── config.py                   # Configuration & API keys
│
├── constants/
│   ├── __init__.py
│   └── endpoints.py            # ENDPOINT_MAPPING, SOURCE_DISPLAY_MAP
│
├── services/
│   ├── __init__.py             # Exports fetch_all_data
│   ├── base_fetcher.py         # BaseFetcher class
│   ├── data_fetcher.py         # Main orchestrator
│   ├── defillama_fetcher.py    # DefiLlama API fetcher
│   ├── coingecko_fetcher.py    # CoinGecko API fetcher
│   └── nansen_fetcher.py       # Nansen API fetcher
│
├── components/
│   ├── __init__.py             # Exports all tab components
│   ├── cdc_tracker.py          # Tab 6: CDC Tracker (Orderbook CVD)
│   ├── tracking_log.py         # Tab 1: Tracking Log/Endpoints
│   ├── token_tracker.py        # Tab 2: Token Tracker
│   ├── profiler.py             # Tab 3: Wallet Profiler
│   ├── dune_export.py          # Tab 4: Dune Export
│   └── social_listening.py     # Tab 5: Social Listening
│
├── api_clients/
│   ├── coingecko_client.py     # CoinGecko API wrapper
│   ├── defillama_client.py     # DefiLlama API wrapper
│   ├── nansen_client.py        # Nansen API wrapper
│   └── dune_client.py          # Dune Analytics API wrapper
│
├── data_handlers/
│   └── storage.py              # GCS & BigQuery storage
│
├── visualizations/
│   ├── charts.py               # Plotly chart functions
│   └── tables.py               # DataFrame table functions
│
├── utils/
│   ├── logger.py               # Logging utilities
│   └── validators.py           # Input validation
│
├── docs/                       # Documentation
└── assets/                     # Static assets (icons)
```

---

## Module Descriptions

### 1. app.py (Entry Point)

File chính, giữ vai trò:
- Page configuration
- Sidebar setup
- Session state initialization
- Tab routing

```python
# Cấu trúc chính
st.set_page_config(...)
# Sidebar
# Session state init
# Tab routing với component calls
```

**Tại sao chỉ 140 lines?**
- Tất cả logic được delegate sang components/
- Tất cả data fetching được delegate sang services/
- app.py chỉ làm nhiệm vụ "routing"

---

### 2. constants/ Module

#### endpoints.py

Chứa mapping giữa display name và API endpoint:

```python
ENDPOINT_MAPPING = {
    # Format: "Display Name": ("source", "endpoint_key")

    # DefiLlama (19 endpoints)
    "DL: All Protocols TVL": ("defillama", "all_protocols"),
    "DL: Protocol TVL": ("defillama", "protocol_tvl"),
    ...

    # CoinGecko (27 endpoints)
    "CG: Simple Price": ("coingecko", "simple_price"),
    ...

    # Nansen (21 endpoints)
    "NS: Smart Money Netflow": ("nansen", "sm_netflow"),
    ...
}

SOURCE_DISPLAY_MAP = {
    "coingecko": "CoinGecko",
    "nansen": "Nansen",
    "defillama": "DefiLlama",
    "dune": "Dune"
}
```

**Cách thêm endpoint mới:**
1. Thêm vào `ENDPOINT_MAPPING`
2. Implement trong fetcher tương ứng (services/)
3. UI sẽ tự động hiển thị endpoint mới

---

### 3. services/ Module

#### base_fetcher.py

Base class với common utilities:

```python
class BaseFetcher:
    def __init__(self, chain_name, contract_address, user_id, chain_config, log_callback=None):
        ...

    def log(self, message, status="info"):
        """Log to UI"""

    def save(self, data, source, endpoint_key):
        """Save to storage"""

    def update_status(self, key, success=True):
        """Update endpoint status in session state"""

    def skip_status(self, key):
        """Mark endpoint as skipped"""
```

#### data_fetcher.py (Orchestrator)

Main function để fetch từ tất cả sources:

```python
def fetch_all_data(chain_name, contract_address, period, log_placeholder, user_id, theme):
    """
    Orchestrates data fetching from all API sources.

    Flow:
    1. Initialize session state
    2. Calculate date ranges
    3. Run DefiLlamaFetcher
    4. Run CoinGeckoFetcher
    5. Run NansenFetcher
    6. Log summary
    """
```

#### Source-specific Fetchers

Mỗi fetcher kế thừa từ `BaseFetcher`:

```python
# defillama_fetcher.py
class DefiLlamaFetcher(BaseFetcher):
    def fetch_all(self):
        self._fetch_tvl_endpoints()
        self._fetch_price_endpoints()
        self._fetch_stablecoin_endpoints()
        ...

# coingecko_fetcher.py
class CoinGeckoFetcher(BaseFetcher):
    def fetch_all(self):
        self._fetch_coin_info()
        self._fetch_price_endpoints()
        ...

# nansen_fetcher.py
class NansenFetcher(BaseFetcher):
    def fetch_all(self):
        self._fetch_smart_money_endpoints()
        self._fetch_token_endpoints()
        ...
```

**Cách thêm data source mới:**
1. Tạo `api_clients/new_source_client.py`
2. Tạo `services/new_source_fetcher.py` kế thừa `BaseFetcher`
3. Thêm vào `data_fetcher.py`
4. Thêm endpoints vào `constants/endpoints.py`

---

### 4. components/ Module

Mỗi component là một tab trong UI:

#### tracking_log.py (Tab 1)

```python
def render_tab(fetch_callback, current_user, theme):
    """
    Render Tracking Log tab.

    Features:
    - Chain/Period/Contract input
    - Fetch button
    - Endpoint status table
    - Log monitoring
    - Data preview

    Returns:
        tuple: (chain, contract_address) for use by other tabs
    """
```

#### token_tracker.py (Tab 2)

```python
def render_tab(chain, contract_address, current_user):
    """
    Render Token Tracker tab.

    Displays:
    - Token summary (from CoinGecko)
    - Delta balance chart (from Dune)
    - Flow intelligence (from Nansen)
    - Token holders chart
    - Transfer history
    """
```

#### profiler.py (Tab 3)

```python
def render_tab(current_user):
    """
    Render Wallet Profiler tab.

    Features:
    - Wallet address input
    - Date range filter
    - 10 Nansen Profiler endpoints:
      1. Current Balances
      2. Historical Balances
      3. Transactions
      4. Counterparties
      5. Related Wallets
      6. PnL & Trade Performance
      7. Address Labels (500 credits)
      8. Perp Positions (Hyperliquid)
      9. Perp Trades (Hyperliquid)
      10. DeFi Holdings
    """
```

#### dune_export.py (Tab 4)

```python
def render_tab(current_user):
    """
    Render Dune Export tab.

    Features:
    - SQL editor
    - Execute & auto-save to BigQuery
    - Download CSV
    """
```

#### cdc_tracker.py (Tab 6)

```python
def init_session_state():
    """Initialize CDC-related session state"""

def init_engine_if_needed(target_symbol):
    """Initialize orderbook sync engine"""

def update_chart_history(data):
    """Update CVD chart history"""

def build_chart_data(cvd_key):
    """Build chart.js compatible data"""

def render_dashboard(data, ohlcv_data=None):
    """Render CDC dashboard with charts"""

def render_tab():
    """Main entry point for CDC Tracker tab"""
```

---

## Data Flow

```
User Input (app.py)
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  components/tracking_log.py                         │
│  - Collect chain, contract, period                  │
│  - Call fetch_callback(fetch_all_data)              │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  services/data_fetcher.py                           │
│  - Orchestrate all fetchers                         │
└─────────────────────────────────────────────────────┘
       │
       ├──► DefiLlamaFetcher ──► DefiLlamaClient ──► API
       │
       ├──► CoinGeckoFetcher ──► CoinGeckoClient ──► API
       │
       └──► NansenFetcher ──► NansenClient ──► API
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  data_handlers/storage.py                           │
│  - Save to GCS                                      │
│  - Save to BigQuery                                 │
│  - Save locally                                     │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│  components/token_tracker.py                        │
│  - Load saved data                                  │
│  - Render visualizations                            │
└─────────────────────────────────────────────────────┘
```

---

## Session State Management

Streamlit session state được quản lý tập trung:

```python
# app.py khởi tạo
st.session_state.logs = []              # Log messages
st.session_state.fetched_data = {}      # Fetched data cache
st.session_state.endpoint_status = {}   # Endpoint status tracking
st.session_state.preview_endpoint = None # Current preview
st.session_state.current_user = None    # Token name

# CDC Tracker specific (cdc_tracker.py)
st.session_state.cdc_engine = None
st.session_state.cdc_running = False
st.session_state.cdc_data = {}
st.session_state.cdc_chart_history = {}
```

---

## Adding New Features

### Add New API Endpoint

1. **API Client** (`api_clients/`):
```python
# api_clients/source_client.py
def get_new_endpoint(self, params):
    return self._get(f"/api/new-endpoint?{params}")
```

2. **Fetcher** (`services/`):
```python
# services/source_fetcher.py
def _fetch_new_endpoints(self):
    try:
        data = self.client.get_new_endpoint(...)
        self.save(data, self.SOURCE, 'new_endpoint')
        self.update_status("new_endpoint", True)
    except Exception as e:
        self.update_status("new_endpoint", False)
```

3. **Endpoint Mapping** (`constants/endpoints.py`):
```python
ENDPOINT_MAPPING = {
    ...
    "Source: New Endpoint": ("source", "new_endpoint"),
}
```

### Add New Tab

1. **Create component** (`components/new_tab.py`):
```python
import streamlit as st

def render_tab(current_user):
    st.header("New Tab")
    # Tab logic here
```

2. **Register in __init__.py**:
```python
from components import new_tab
```

3. **Add to app.py**:
```python
tab1, tab2, ..., tab_new = st.tabs([..., "New Tab"])

with tab_new:
    new_tab.render_tab(current_user)
```

---

## Best Practices

### 1. Keep Components Focused
- Mỗi component chỉ làm một việc
- Không vượt quá 400 lines/file

### 2. Use BaseFetcher
- Tất cả fetchers kế thừa từ BaseFetcher
- Sử dụng các methods có sẵn: `log()`, `save()`, `update_status()`

### 3. Error Handling
```python
try:
    data = self.client.get_something()
    self.save(data, source, key)
    self.update_status(key, True)
except Exception as e:
    self.update_status(key, False)
    self.log(f"Error: {str(e)[:50]}", "error")
```

### 4. Session State
- Khởi tạo trong app.py
- Truy cập thông qua `st.session_state`
- Không mutate trực tiếp trong components

---

## File Size Guidelines

| File Type | Max Lines | Reason |
|-----------|-----------|--------|
| app.py | 200 | Entry point only |
| Component | 400 | Single tab focus |
| Fetcher | 350 | Single source |
| API Client | 600 | Many endpoints |

---

## Testing

```bash
# Test imports
python -c "from components import tracking_log; print('OK')"

# Test app loads
python -c "import app; print('App loads OK')"

# Run app
streamlit run app.py
```

---

## Refactoring History

| Date | app.py Lines | Change |
|------|--------------|--------|
| Before | 1949 | Monolithic |
| Phase 1 | 1459 | Extract constants & CDC |
| Phase 2 | 800 | Extract services |
| Phase 3 | 140 | Extract components |

**Total reduction: 93%**
