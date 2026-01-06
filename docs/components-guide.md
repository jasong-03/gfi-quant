# Components Module - Developer Guide

## Overview

Module `components/` chứa UI logic cho từng tab trong Streamlit app. Mỗi file là một tab độc lập với function `render_tab()` làm entry point.

---

## Component Structure

Mỗi component tuân theo pattern:

```python
"""
Component Name Tab
Brief description.
"""

import streamlit as st
# Other imports

def helper_function():
    """Internal helper functions"""
    pass

def render_tab(required_params, optional_params=None):
    """
    Main entry point.

    Args:
        required_params: Description
        optional_params: Description

    Returns:
        Optional return values for cross-tab communication
    """
    st.header("Tab Title")
    # Tab logic
```

---

## Tab 1: tracking_log.py

### Purpose
- Input chain, contract, period
- Trigger data fetching
- Display endpoint status
- Show log monitoring
- Data preview

### Function Signature

```python
def render_tab(
    fetch_callback,      # Function to call for fetching
    current_user: str,   # Token/user name
    theme: str = "Dark"  # UI theme
) -> tuple[str, str]:    # Returns (chain, contract_address)
```

### UI Structure

```
┌─────────────────────────────────────────────────────────────┐
│  [Chain ▼]  [Period ▼]  [Contract Address...............]   │
│  [            Fetch Button (Primary)                    ]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐    ┌────────────────────────────┐  │
│  │ Endpoints Status    │    │ Log Monitoring             │  │
│  │                     │    │ ┌────────────────────────┐ │  │
│  │ Endpoint | St | Act │    │ │ > Starting fetch...    │ │  │
│  │ ─────────────────── │    │ │ > DefiLlama done       │ │  │
│  │ DL: TVL  | ✅ | 👁  │    │ │ > CoinGecko done       │ │  │
│  │ CG: Price| ✅ | 👁  │    │ └────────────────────────┘ │  │
│  │ NS: Flow | ❌ | 👁  │    │                            │  │
│  └─────────────────────┘    │ Preview: [Endpoint Name]   │  │
│                             │ ┌────────────────────────┐ │  │
│                             │ │ DataFrame/JSON view    │ │  │
│                             │ └────────────────────────┘ │  │
│                             └────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

1. **3-Phase State Machine:**
   - Phase 1: Initial (no data)
   - Phase 2: Fetching (transient)
   - Phase 3: Data available

2. **Endpoint Status Sorting:**
   ```python
   # Sort order: done → failed → skip → pending
   def get_sort_key(ep):
       if "done" in status: return 0
       if "failed" in status: return 1
       if "⚠️" in status: return 2
       return 3
   ```

3. **Preview Modal:**
   - Click "preview" button sets `st.session_state.preview_endpoint`
   - Displays data in appropriate format (DataFrame/JSON)

---

## Tab 2: token_tracker.py

### Purpose
- Display token analytics
- Visualize fetched data
- Show charts and tables

### Function Signature

```python
def render_tab(
    chain: str,           # Selected chain from Tab 1
    contract_address: str, # Contract from Tab 1
    current_user: str      # Token/user name
):
```

### Data Sources

| Section | Source | Endpoint |
|---------|--------|----------|
| Token Summary | CoinGecko | coin_info |
| Delta Balance | Dune | delta_balance |
| Flow Intelligence | Nansen | flow_intelligence |
| Token Holders | Nansen | holders |
| Transfers | Nansen | transfers |

### UI Structure

```
┌─────────────────────────────────────────────────────────────┐
│  [Token Logo]  Token Name (SYMBOL)                          │
│                Price: $X.XX | MCap: $X | Vol: $X            │
├─────────────────────────────────────────────────────────────┤
│  Delta Balance Change (Dune)                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  [Bar Chart - Balance Changes Over Time]            │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Token Flow Intelligence (Nansen)                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│  │ Net Flow    │ │ Avg Flow    │ │ Wallet Cnt  │            │
│  │ DataFrame   │ │ DataFrame   │ │ DataFrame   │            │
│  └─────────────┘ └─────────────┘ └─────────────┘            │
├─────────────────────────────────────────────────────────────┤
│  Token Holders (Nansen)                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  [Bar Chart - Top Holders]                          │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Last Token Transfer (Nansen)                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  [DataFrame - Recent Transfers]                     │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Visualization Functions

From `visualizations/charts.py`:
- `create_delta_balance_chart(data)` → Plotly figure
- `create_holders_bar_chart(data)` → Plotly figure

From `visualizations/tables.py`:
- `create_flow_intelligence_table(data)` → (net_df, avg_df, wallet_df)
- `create_transfers_table(data)` → DataFrame

---

## Tab 3: profiler.py

### Purpose
- Analyze any wallet address
- 10 Nansen Profiler endpoints
- Date range filtering

### Function Signature

```python
def render_tab(current_user: str):
```

### Endpoints Called

| # | Endpoint | Date Filter | Notes |
|---|----------|-------------|-------|
| 1 | Current Balances | No | |
| 2 | Historical Balances | Yes | |
| 3 | Transactions | Yes | |
| 4 | Counterparties | Yes | |
| 5 | Related Wallets | No | |
| 6 | PnL & Trade | Yes | |
| 7 | Address Labels | No | 500 credits! |
| 8 | Perp Positions | No | Hyperliquid only |
| 9 | Perp Trades | Yes | Hyperliquid only |
| 10 | DeFi Holdings | No | Portfolio summary |

### UI Flow

```
1. User enters wallet address
2. User selects date range
3. User clicks "Analyze Wallet"
4. Component calls NansenClient directly (not through services/)
5. Results displayed section by section
6. Data saved to storage for each endpoint
```

### Special Considerations

- **Labels endpoint costs 500 credits** - opt-in checkbox
- **Perp endpoints only work with Hyperliquid addresses**
- **Each section has try/except for resilience**

---

## Tab 4: dune_export.py

### Purpose
- Execute raw SQL on Dune Analytics
- Auto-save to BigQuery
- Download as CSV

### Function Signature

```python
def render_tab(current_user: str):
```

### UI Structure

```
┌─────────────────────────────────────────────────────────────┐
│  Export Name: [________________________]                    │
├─────────────────────────────────────────────────────────────┤
│  SQL Editor                                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  SELECT                                             │    │
│  │    block_time,                                      │    │
│  │    hash,                                            │    │
│  │    "from",                                          │    │
│  │    "to"                                             │    │
│  │  FROM ethereum.transactions                         │    │
│  │  WHERE block_time >= ...                            │    │
│  │  LIMIT 100                                          │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  [           Execute & Save (Primary)                   ]   │
├─────────────────────────────────────────────────────────────┤
│  Query Results                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  [DataFrame with results]                           │    │
│  └─────────────────────────────────────────────────────┘    │
│  [Download CSV]                                             │
└─────────────────────────────────────────────────────────────┘
```

### Session State

```python
st.session_state.dune_results = None  # Raw API response
st.session_state.dune_df = None       # Pandas DataFrame
```

### Save Flow

```
Execute SQL → Dune API → DataFrame
                           ↓
                    save_dune_to_bigquery()
                           ↓
                    BigQuery table created
```

---

## Tab 5: social_listening.py

### Purpose
- Placeholder for social media monitoring
- Coming soon feature

### Function Signature

```python
def render_tab():
    st.header("Social Listening")
    st.info("Social listening features coming soon...")
```

---

## Tab 6: cdc_tracker.py

### Purpose
- Real-time orderbook CVD (Cumulative Volume Delta)
- Exchange data via CCXT
- Live charting with streamlit-elements

### Function Signatures

```python
def init_session_state():
    """Initialize CDC-related session state variables."""

def init_engine_if_needed(target_symbol: str):
    """
    Initialize OrderbookEngineSync if not already running.

    Args:
        target_symbol: Trading pair (e.g., 'BTC/USDT')
    """

def update_chart_history(data: dict):
    """
    Update chart history with new CVD data.

    Args:
        data: CVD data from orderbook engine
    """

def build_chart_data(cvd_key: str) -> dict:
    """
    Build chart.js compatible data structure.

    Args:
        cvd_key: Key identifying CVD type

    Returns:
        Chart.js data object with labels and datasets
    """

def render_dashboard(data: dict, ohlcv_data=None):
    """
    Render the CDC dashboard with charts.

    Args:
        data: Current CVD data
        ohlcv_data: Optional OHLCV data for price chart
    """

def render_tab():
    """Main entry point for CDC Tracker tab."""
```

### Session State Variables

```python
st.session_state.cdc_engine = None        # OrderbookEngineSync instance
st.session_state.cdc_running = False      # Running state
st.session_state.cdc_data = {}            # Current data
st.session_state.cdc_chart_history = {}   # Historical data for charts
st.session_state.cdc_target_symbol = None # Trading pair
st.session_state.cdc_exchange = None      # Exchange name
```

### UI Structure

```
┌─────────────────────────────────────────────────────────────┐
│  [Exchange ▼]  [Symbol........]  [Run] [Stop]               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │  CVD Chart (streamlit-elements/nivo)                │    │
│  │  - Buy CVD line                                     │    │
│  │  - Sell CVD line                                    │    │
│  │  - Delta line                                       │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Price Chart (if OHLCV available)                   │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│  Current Values:                                            │
│  Buy CVD: X.XX | Sell CVD: X.XX | Delta: X.XX               │
└─────────────────────────────────────────────────────────────┘
```

### Bug Fix Note

Line đã được fix trong `build_chart_data()`:
```python
# Before (Bug - index out of bounds)
"data": [{"x": timestamps[i], "y": round(cvd_list[i], 2)} for i in range(len(cvd_list))]

# After (Fixed)
data_len = min(len(timestamps), len(cvd_list))
"data": [{"x": timestamps[i], "y": round(cvd_list[i], 2)} for i in range(data_len)]
```

---

## Creating New Component

### Template

```python
"""
New Feature Tab Component
Brief description of the tab's purpose.
"""

import streamlit as st
from datetime import datetime

# Additional imports as needed
from config import SUPPORTED_CHAINS
from data_handlers.storage import load_latest_json, save_json


def _helper_function():
    """Internal helper - prefix with underscore."""
    pass


def render_tab(current_user: str, **kwargs):
    """
    Render the New Feature tab.

    Args:
        current_user: Current user/token name
        **kwargs: Additional parameters

    Returns:
        Optional return value for cross-tab communication
    """
    st.header("New Feature")
    st.markdown("Description of what this tab does")

    # Input section
    col1, col2 = st.columns(2)
    with col1:
        input_a = st.text_input("Input A", key="new_feature_input_a")
    with col2:
        input_b = st.selectbox("Input B", ["Option 1", "Option 2"], key="new_feature_input_b")

    st.markdown("---")

    # Action button
    if st.button("Do Something", type="primary", key="new_feature_btn"):
        with st.spinner("Processing..."):
            try:
                # Your logic here
                result = process_something(input_a, input_b)

                # Display result
                st.success("Done!")
                st.dataframe(result)

                # Save if needed
                save_json(result, 'source', 'chain', input_a, 'endpoint', current_user)

            except Exception as e:
                st.error(f"Error: {e}")

    # Optional: Display previous results
    if 'new_feature_result' in st.session_state:
        st.subheader("Previous Result")
        st.dataframe(st.session_state.new_feature_result)


def process_something(input_a, input_b):
    """Business logic function."""
    # Implementation
    return {"result": "data"}
```

### Registering Component

1. **Add to `__init__.py`:**
```python
# components/__init__.py
from components import new_feature
```

2. **Add to `app.py`:**
```python
# Import
from components import (..., new_feature)

# Add tab
tabs = st.tabs([..., "New Feature"])

# Render
with tabs[N]:
    new_feature.render_tab(current_user)
```

---

## Best Practices

### 1. Use Unique Keys
```python
# Good - unique key per component
st.text_input("Input", key="profiler_address")
st.text_input("Input", key="tracker_address")

# Bad - key collision
st.text_input("Input", key="address")
```

### 2. Handle Missing Data Gracefully
```python
if data:
    st.dataframe(data)
else:
    st.info("No data available. Fetch data in Tab 1 first.")
```

### 3. Use Spinners for Long Operations
```python
with st.spinner("Fetching data..."):
    result = slow_operation()
```

### 4. Section Dividers
```python
st.markdown("---")  # Horizontal rule between sections
```

### 5. Column Layouts
```python
# 2 equal columns
col1, col2 = st.columns(2)

# Custom ratio
left, right = st.columns([1, 3])

# 3 columns for metrics
m1, m2, m3 = st.columns(3)
```
