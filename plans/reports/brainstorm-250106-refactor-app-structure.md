# Refactor Plan: GFI Quant Project

**Date:** 2025-01-06
**Status:** Approved
**Approach:** Option A - Module-Based Split (Phase-based)

---

## Problem Statement

`app.py` has grown to **1949 lines**, making it:
- Hard to navigate and debug
- Difficult for multiple developers to work on
- Prone to merge conflicts
- Challenging to test individual components

### Current Structure Analysis

```
app.py (1949 lines)
├── [1-140]     Imports & Session State Init (~140 lines)
├── [140-475]   CDC Tracker Functions (~335 lines)
├── [476-570]   ENDPOINT_MAPPING (~95 lines)
├── [572-638]   Helper Functions (~66 lines)
├── [639-1300]  fetch_all_data() (~660 lines) 🔴
├── [1305-1344] Tab 6: CDC Tracker UI
├── [1344-1497] Tab 1: Tracking Log UI
├── [1497-1584] Tab 2: Token Tracker UI
├── [1584-1807] Tab 3: Profiler UI
├── [1807-1947] Tab 4: Dune Export UI
└── [1947-1949] Tab 5: Social Listening UI
```

---

## Target Structure

```
gfi-quant-project/
├── app.py                        # Main entry point (~150 lines)
│
├── constants/
│   ├── __init__.py
│   └── endpoints.py              # ENDPOINT_MAPPING, chains config
│
├── services/
│   ├── __init__.py
│   ├── base_fetcher.py           # Base class, common utilities
│   ├── defillama_fetcher.py      # DefiLlama fetch logic
│   ├── coingecko_fetcher.py      # CoinGecko fetch logic
│   └── nansen_fetcher.py         # Nansen fetch logic
│
├── components/
│   ├── __init__.py
│   ├── cdc_tracker.py            # CDC Tracker tab + functions
│   ├── tracking_log.py           # Tab 1 - Tracking Log/Endpoints
│   ├── token_tracker.py          # Tab 2 - Token Tracker
│   ├── profiler.py               # Tab 3 - Profiler
│   ├── dune_export.py            # Tab 4 - Dune Export
│   └── social_listening.py       # Tab 5 - Social Listening
│
├── api_clients/                  # Keep as-is
├── data_handlers/                # Keep as-is
├── visualizations/               # Keep as-is
└── utils/                        # Keep as-is
```

---

## Implementation Phases

### Phase 1: Constants & CDC Tracker (Est: 1 hour)

**Priority:** High (Quick wins, immediate impact)

#### Task 1.1: Extract ENDPOINT_MAPPING
```python
# constants/endpoints.py
ENDPOINT_MAPPING = {
    # DefiLlama
    "DL: All Protocols TVL": ("defillama", "all_protocols"),
    ...
}

SUPPORTED_CHAINS = {...}  # Move from config if needed
```

#### Task 1.2: Extract CDC Tracker
```python
# components/cdc_tracker.py
import streamlit as st
from orderbook_sync import OrderbookEngineSync

def init_session_state():
    """Initialize CDC-related session state"""
    if 'cdc_engine' not in st.session_state:
        st.session_state.cdc_engine = None
    ...

def init_cdc_engine_if_needed(target_symbol):
    ...

def update_cdc_chart_history(data):
    ...

def build_cdc_chart_data(cvd_key):
    ...

def render_cdc_dashboard(data, ohlcv_data=None):
    ...

def render_tab():
    """Main entry point for Tab 6"""
    st.header("CDC Tracker (Orderbook CVD)")
    ...
```

#### Task 1.3: Update app.py imports
```python
# app.py
from constants.endpoints import ENDPOINT_MAPPING
from components.cdc_tracker import render_tab as render_cdc_tab

# In tab section:
with tab6:
    render_cdc_tab()
```

**Outcome:** app.py reduced by ~430 lines → ~1520 lines

---

### Phase 2: Split Fetchers (Est: 2 hours)

**Priority:** High (fetch_all_data is 660 lines)

#### Task 2.1: Create base fetcher
```python
# services/base_fetcher.py
import streamlit as st
from utils.logger import log_to_ui
from data_handlers.storage import save_json

class BaseFetcher:
    def __init__(self, chain_name, contract_address, user_id):
        self.chain_name = chain_name
        self.contract_address = contract_address
        self.user_id = user_id

    def log(self, msg, level="info"):
        log_to_ui(msg, level)

    def save(self, data, source, endpoint):
        save_json(data, source, self.chain_name,
                  self.contract_address, endpoint, self.user_id)

    def update_status(self, key, success=True):
        status = "✅ done" if success else "❌ failed"
        st.session_state.endpoint_status[key] = status
```

#### Task 2.2: DefiLlama fetcher
```python
# services/defillama_fetcher.py
from services.base_fetcher import BaseFetcher
from api_clients.defillama_client import DefiLlamaClient

class DefiLlamaFetcher(BaseFetcher):
    def __init__(self, chain_name, contract_address, user_id, chain_config):
        super().__init__(chain_name, contract_address, user_id)
        self.client = DefiLlamaClient()
        self.dl_chain = chain_config.get('defillama', chain_name.lower())

    def fetch_all(self):
        self.log("=" * 40, "info")
        self.log("DEFILLAMA ENDPOINTS", "info")

        self._fetch_protocols()
        self._fetch_chain_tvl()
        self._fetch_prices()
        ...

    def _fetch_protocols(self):
        try:
            data = self.client.get_all_protocols()
            self.save(data, 'defillama', 'all_protocols')
            self.update_status("all_protocols", True)
            self.log(f"All Protocols: {len(data)} protocols", "success")
        except Exception as e:
            self.update_status("all_protocols", False)
            self.log(f"Error: {str(e)[:50]}", "error")
```

#### Task 2.3: Similar for CoinGecko & Nansen

#### Task 2.4: Update fetch_all_data
```python
# app.py (simplified)
def fetch_all_data(chain_name, contract_address, period, log_placeholder, user_id):
    # Init
    chain_config = SUPPORTED_CHAINS.get(chain_name)

    # Fetch from all sources
    DefiLlamaFetcher(chain_name, contract_address, user_id, chain_config).fetch_all()
    CoinGeckoFetcher(chain_name, contract_address, user_id, chain_config).fetch_all()
    NansenFetcher(chain_name, contract_address, user_id, chain_config).fetch_all()

    # Summary
    log_to_ui(f"COMPLETED: {done}/{total} endpoints", "success")
```

**Outcome:** app.py reduced by ~660 lines → ~860 lines

---

### Phase 3: Split Tab Components (Est: 1.5 hours)

**Priority:** Medium

#### Task 3.1: Extract each tab to component
```python
# components/tracking_log.py
import streamlit as st

def render_tab(chain, contract_address, period, user_id, fetch_callback):
    st.header("Market Data Analysis")

    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        chain = st.selectbox("Chain", list(SUPPORTED_CHAINS.keys()))
    ...

    if st.button("Fetch"):
        fetch_callback(chain, contract_address, period, user_id)
```

#### Task 3.2: Update app.py
```python
# app.py (~150 lines final)
import streamlit as st
from constants.endpoints import ENDPOINT_MAPPING
from components import (
    cdc_tracker, tracking_log, token_tracker,
    profiler, dune_export, social_listening
)
from services import fetch_all_data

st.title("Token Tracker Metrics")

tabs = st.tabs([
    "Tracking log/Endpoints", "Token Tracker", "Profiler",
    "Dune Export", "Social Listening", "CDC Tracker"
])

with tabs[0]:
    tracking_log.render_tab(fetch_callback=fetch_all_data)
with tabs[1]:
    token_tracker.render_tab()
with tabs[2]:
    profiler.render_tab()
with tabs[3]:
    dune_export.render_tab()
with tabs[4]:
    social_listening.render_tab()
with tabs[5]:
    cdc_tracker.render_tab()
```

**Outcome:** app.py reduced to ~150 lines

---

## File Size Targets

| File | Current | Target |
|------|---------|--------|
| app.py | 1949 | ~150 |
| constants/endpoints.py | - | ~100 |
| services/base_fetcher.py | - | ~50 |
| services/defillama_fetcher.py | - | ~150 |
| services/coingecko_fetcher.py | - | ~200 |
| services/nansen_fetcher.py | - | ~250 |
| components/cdc_tracker.py | - | ~350 |
| components/tracking_log.py | - | ~200 |
| components/token_tracker.py | - | ~100 |
| components/profiler.py | - | ~250 |
| components/dune_export.py | - | ~150 |
| components/social_listening.py | - | ~50 |

**All files under 350 lines** - easier to maintain

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Session state across modules | Medium | Pass st.session_state explicitly or use global access |
| Circular imports | Low | Use lazy imports, proper __init__.py |
| Breaking existing functionality | High | Test each phase before proceeding |
| Streamlit reruns | Medium | Use @st.cache_data, @st.fragment appropriately |

---

## Success Metrics

- [ ] No file exceeds 350 lines
- [ ] app.py under 200 lines
- [ ] All existing functionality works
- [ ] Faster to locate and fix bugs
- [ ] Clear separation of concerns

---

## Next Steps

1. **Approve this plan**
2. **Start Phase 1** - Constants & CDC Tracker extraction
3. **Test Phase 1** - Verify app still works
4. **Continue to Phase 2 & 3**

---

## Commands to Verify Progress

```bash
# Check file sizes
find . -name "*.py" -exec wc -l {} \; | sort -rn | head -20

# Run app
streamlit run app.py

# Check imports work
python -c "from constants.endpoints import ENDPOINT_MAPPING; print(len(ENDPOINT_MAPPING))"
```
