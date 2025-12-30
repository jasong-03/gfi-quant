# System Architecture

## Overview

The GFI Quant Token Tracker Dashboard is a multi-layer application that aggregates cryptocurrency data from four external API providers and presents it through an interactive Streamlit interface. This document describes the system architecture, component interactions, and data flow patterns.

---

## Architecture Diagram

```
+------------------------------------------------------------------+
|                         PRESENTATION LAYER                        |
|  +------------------------------------------------------------+  |
|  |                    Streamlit Application                    |  |
|  |  +----------------+  +----------------+  +----------------+ |  |
|  |  | Tab 1:        |  | Tab 2:        |  | Tab 3:        | |  |
|  |  | Tracking/Logs |  | Token Tracker |  | Social        | |  |
|  |  +----------------+  +----------------+  +----------------+ |  |
|  +------------------------------------------------------------+  |
|                              |                                    |
|  +------------------------------------------------------------+  |
|  |                  VISUALIZATION LAYER                        |  |
|  |  +------------------+  +------------------+                 |  |
|  |  | charts.py       |  | tables.py       |                 |  |
|  |  | - Price charts  |  | - Flow tables   |                 |  |
|  |  | - Delta balance |  | - Transfer list |                 |  |
|  |  | - Holder bars   |  |                  |                 |  |
|  |  +------------------+  +------------------+                 |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
                               |
+------------------------------------------------------------------+
|                         BUSINESS LOGIC LAYER                      |
|  +------------------------------------------------------------+  |
|  |                    app.py Orchestration                     |  |
|  |  - fetch_all_data()     - User input processing            |  |
|  |  - get_endpoint_list()  - Session state management         |  |
|  |  - load_dune_query()    - Status tracking                  |  |
|  +------------------------------------------------------------+  |
|                              |                                    |
|  +------------------+  +------------------+  +------------------+ |
|  | UTILITIES        |  | DATA HANDLERS    |  | CONFIGURATION   | |
|  | - logger.py      |  | - storage.py     |  | - config.py     | |
|  | - validators.py  |  | - processors.py  |  |                  | |
|  +------------------+  +------------------+  +------------------+ |
+------------------------------------------------------------------+
                               |
+------------------------------------------------------------------+
|                           API LAYER                               |
|  +-------------+  +-------------+  +-------------+  +-----------+ |
|  | DuneClient |  | DefiLlama  |  | Nansen     |  | CoinGecko | |
|  |            |  | Client     |  | Client     |  | Client    | |
|  +-------------+  +-------------+  +-------------+  +-----------+ |
|        |                |                |               |        |
+------------------------------------------------------------------+
         |                |                |               |
         v                v                v               v
+------------------------------------------------------------------+
|                      EXTERNAL SERVICES                            |
|  +-------------+  +-------------+  +-------------+  +-----------+ |
|  | Dune       |  | DefiLlama  |  | Nansen     |  | CoinGecko | |
|  | Analytics  |  | API        |  | API        |  | API       | |
|  | api.dune   |  | llama.fi   |  | nansen.ai  |  | coingecko | |
|  +-------------+  +-------------+  +-------------+  +-----------+ |
+------------------------------------------------------------------+
         |                |                |               |
         v                v                v               v
+------------------------------------------------------------------+
|                       DATA STORAGE                                |
|  +------------------------------------------------------------+  |
|  |                    Local File System                        |  |
|  |  data/{source}/{chain}/{address}/{endpoint}_{timestamp}.json |  |
|  +------------------------------------------------------------+  |
+------------------------------------------------------------------+
```

---

## Layer Descriptions

### 1. Presentation Layer

**Location**: `app.py` (UI sections), `visualizations/`

**Responsibility**: User interface rendering and interaction handling.

**Components**:

| Component | Purpose |
|-----------|---------|
| Sidebar | Configuration, API status, theme selection |
| Tab 1 (Tracking) | Data fetching controls, endpoint status, logs |
| Tab 2 (Token Tracker) | Visualizations and analytics |
| Tab 3 (Social) | Placeholder for future features |

**Technologies**: Streamlit, Custom HTML/CSS

### 2. Visualization Layer

**Location**: `visualizations/charts.py`, `visualizations/tables.py`

**Responsibility**: Transform data into visual representations.

**Components**:

| Function | Input | Output |
|----------|-------|--------|
| `create_price_chart()` | Price data dict | Plotly Figure |
| `create_delta_balance_chart()` | Dune result dict | Plotly Figure |
| `create_holders_bar_chart()` | Holder data dict | Plotly Figure |
| `create_flow_intelligence_table()` | Flow data dict | 3 DataFrames |
| `create_transfers_table()` | Transfer data dict | DataFrame |

### 3. Business Logic Layer

**Location**: `app.py` (orchestration functions)

**Responsibility**: Coordinate data fetching, state management, and business rules.

**Key Functions**:

| Function | Purpose |
|----------|---------|
| `fetch_all_data()` | Orchestrate multi-API data retrieval |
| `get_endpoint_list()` | Generate sorted endpoint status |
| `load_dune_query()` | Format SQL templates with parameters |
| `check_credits()` | Verify API connectivity |

### 4. Utility Layer

**Location**: `utils/`, `data_handlers/`

**Components**:

| Module | Purpose |
|--------|---------|
| `logger.py` | Dual-channel logging (console + UI) |
| `validators.py` | Input validation (addresses) |
| `storage.py` | JSON file persistence |
| `processors.py` | Data transformation (stubs) |

### 5. API Layer

**Location**: `api_clients/`

**Responsibility**: Communicate with external API services.

| Client | Base URL | Auth |
|--------|----------|------|
| `DuneClient` | `api.dune.com/api/v1` | Header |
| `DefiLlamaClient` | `coins.llama.fi` | URL/None |
| `NansenClient` | `api.nansen.ai/api/v1` | Header |
| `CoinGeckoClient` | `pro-api.coingecko.com/api/v3` | Header |

### 6. External Services

Third-party APIs providing blockchain and market data.

### 7. Data Storage

**Location**: `data/` directory (auto-created)

**Pattern**: Hierarchical JSON storage with timestamp versioning.

---

## Data Flow Diagrams

### Primary Data Flow: Fetch Operation

```
User Input                     Application                      External APIs
    |                              |                                  |
    | 1. Select chain, address     |                                  |
    |----------------------------->|                                  |
    |                              |                                  |
    |                              | 2. Validate input                |
    |                              |--------------.                   |
    |                              |              |                   |
    |                              |<-------------'                   |
    |                              |                                  |
    |                              | 3. Initialize API clients        |
    |                              |--------------.                   |
    |                              |              |                   |
    |                              |<-------------'                   |
    |                              |                                  |
    | 4. Display "Fetching..."     |                                  |
    |<-----------------------------|                                  |
    |                              |                                  |
    |                              | 5. Fetch DefiLlama data          |
    |                              |--------------------------------->|
    |                              |                                  |
    |                              | 6. Response                      |
    |                              |<---------------------------------|
    |                              |                                  |
    | 7. Log: "DefiLlama fetched"  |                                  |
    |<-----------------------------|                                  |
    |                              |                                  |
    |                              | 8. Save to storage               |
    |                              |--------------.                   |
    |                              |              |                   |
    |                              |<-------------'                   |
    |                              |                                  |
    |                              | 9. Repeat for Nansen, CG, Dune   |
    |                              |--------------------------------->|
    |                              |<---------------------------------|
    |                              |                                  |
    | 10. Display visualizations   |                                  |
    |<-----------------------------|                                  |
```

### Dune Query Execution Flow

```
Application                  DuneClient                    Dune API
    |                            |                            |
    | 1. load_dune_query()       |                            |
    |-----------.                |                            |
    |           |                |                            |
    |<----------'                |                            |
    |                            |                            |
    | 2. create_query(sql)       |                            |
    |--------------------------->|                            |
    |                            | POST /query                |
    |                            |--------------------------->|
    |                            |                            |
    |                            | {query_id: 123}            |
    |                            |<---------------------------|
    |                            |                            |
    | {query_id: 123}            |                            |
    |<---------------------------|                            |
    |                            |                            |
    | 3. execute_query(123)      |                            |
    |--------------------------->|                            |
    |                            | POST /query/123/execute    |
    |                            |--------------------------->|
    |                            |                            |
    |                            | {execution_id: "abc"}      |
    |                            |<---------------------------|
    |                            |                            |
    | 4. Poll loop               |                            |
    |----.                       |                            |
    |    | get_execution_status  |                            |
    |    |---------------------->|                            |
    |    |                       | GET /execution/abc/status  |
    |    |                       |--------------------------->|
    |    |                       |                            |
    |    |                       | {state: "PENDING"}         |
    |    |                       |<---------------------------|
    |    |                       |                            |
    |    | sleep(2)              |                            |
    |<---'                       |                            |
    |                            |                            |
    | ... repeat until COMPLETED |                            |
    |                            |                            |
    | 5. get_execution_results   |                            |
    |--------------------------->|                            |
    |                            | GET /execution/abc/results |
    |                            |--------------------------->|
    |                            |                            |
    |                            | {result: {rows: [...]}}    |
    |                            |<---------------------------|
    |                            |                            |
    | {result: {rows: [...]}}    |                            |
    |<---------------------------|                            |
```

### Data Storage Flow

```
API Response              storage.py                    File System
    |                         |                             |
    | 1. save_json(data, ...) |                             |
    |------------------------>|                             |
    |                         |                             |
    |                         | 2. Build path               |
    |                         | data/{source}/{chain}/{addr}|
    |                         |-------------.               |
    |                         |             |               |
    |                         |<------------'               |
    |                         |                             |
    |                         | 3. ensure_directory()       |
    |                         |---------------------------->|
    |                         |                             |
    |                         |                             | mkdir -p
    |                         |                             |-----.
    |                         |                             |     |
    |                         |                             |<----'
    |                         |                             |
    |                         | 4. Write JSON               |
    |                         |---------------------------->|
    |                         |                             |
    |                         |                             | {endpoint}_{ts}.json
    |                         |                             |-----.
    |                         |                             |     |
    |                         |                             |<----'
    |                         |                             |
    | filepath                |                             |
    |<------------------------|                             |
```

---

## Component Interactions

### Session State Flow

```
+-------------------+     +-------------------+     +-------------------+
|   User Action     |---->|   Session State   |---->|   UI Rendering    |
+-------------------+     +-------------------+     +-------------------+
                                   |
                                   v
                          +-------------------+
                          | State Variables:  |
                          | - logs[]          |
                          | - fetched_data{}  |
                          | - endpoint_status |
                          | - preview_endpoint|
                          | - api_usage{}     |
                          +-------------------+
```

### Visualization Pipeline

```
Raw API Data          Processing               Visualization
     |                    |                         |
     v                    v                         v
+----------+      +---------------+      +------------------+
| Nansen   |      | Extract data  |      | Plotly Figure    |
| holders  |----->| from response |----->| create_holders_  |
| response |      | {"data": [...]}|     | bar_chart()      |
+----------+      +---------------+      +------------------+
     |                    |                         |
     |                    |                         v
     |                    |              +------------------+
     |                    |              | st.plotly_chart  |
     |                    |              | (render to UI)   |
     |                    |              +------------------+
```

---

## Configuration Architecture

### Key Resolution Order

```
+------------------+
| local_settings.py|  (1) Highest priority
+------------------+
         |
         v
+------------------+
| st.secrets       |  (2) Streamlit secrets
+------------------+
         |
         v
+------------------+
| os.environ       |  (3) Environment variables
+------------------+
         |
         v
+------------------+
| '' (empty)       |  (4) Default fallback
+------------------+
```

### Chain Configuration Mapping

```
SUPPORTED_CHAINS["Ethereum"]
         |
         +---> defillama: "ethereum"
         +---> nansen: "ethereum"
         +---> coingecko: "ethereum"
         +---> id: "ethereum"

SUPPORTED_CHAINS["Polygon"]
         |
         +---> defillama: "polygon"
         +---> nansen: "polygon"
         +---> coingecko: "polygon-pos"    # Different identifier
         +---> id: "matic-network"
```

---

## Error Handling Architecture

### Error Propagation

```
External API Error
        |
        v
+------------------+
| requests.        |
| HTTPError        |
+------------------+
        |
        v
+------------------+
| API Client       |
| raise_for_status |
+------------------+
        |
        v
+------------------+
| fetch_all_data() |
| try/except block |
+------------------+
        |
        +---> Log error: log_to_ui(..., "error")
        |
        +---> Update status: endpoint_status[key] = "X failed"
        |
        v
+------------------+
| Continue with    |
| next endpoint    |
+------------------+
```

### Graceful Degradation

```
load_latest_json() returns None
        |
        v
+------------------+
| Visualization    |
| function check   |
+------------------+
        |
        +---> if data: render chart
        |
        +---> else: st.info("No data available")
```

---

## Security Architecture

### API Key Protection

```
+-------------------+       +-------------------+
|  .gitignore       |       | Runtime Loading   |
|  - config.py      |       | 1. local_settings |
|  - local_settings |       | 2. st.secrets     |
|  - .env           |       | 3. os.environ     |
+-------------------+       +-------------------+
         |                           |
         v                           v
+-------------------+       +-------------------+
| Keys never in git |       | Keys in memory    |
|                   |       | only at runtime   |
+-------------------+       +-------------------+
```

### Request Security

| Measure | Implementation |
|---------|----------------|
| HTTPS | All API calls use HTTPS |
| Header Auth | Keys in headers, not URLs (except DefiLlama Pro) |
| Timeout | 30-second default timeout |
| No Logging | API keys not written to logs |

---

## Scalability Considerations

### Current Limitations

| Aspect | Limitation | Impact |
|--------|------------|--------|
| Single-threaded | Sequential API calls | Longer fetch times |
| Browser-based | Client-side processing | Memory constraints |
| File storage | Local JSON files | No multi-user support |

### Future Improvements

| Improvement | Benefit |
|-------------|---------|
| Async API calls | Parallel fetching |
| Database storage | Multi-user support |
| Caching layer | Reduced API calls |
| Background workers | Non-blocking operations |

---

## Deployment Architecture

### Local Development

```
+-------------------+
|   Developer       |
|   Machine         |
+-------------------+
        |
        v
+-------------------+
| streamlit run     |
| app.py            |
+-------------------+
        |
        v
+-------------------+
| localhost:8501    |
+-------------------+
```

### Production (Streamlit Cloud)

```
+-------------------+       +-------------------+
|   GitHub Repo     |<----->| Streamlit Cloud   |
|   (source code)   |       | (hosting)         |
+-------------------+       +-------------------+
                                    |
                                    v
                            +-------------------+
                            | st.secrets        |
                            | (API keys)        |
                            +-------------------+
                                    |
                                    v
                            +-------------------+
                            | Public URL        |
                            | *.streamlit.app   |
                            +-------------------+
```

---

## Technology Stack Summary

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit, HTML/CSS |
| Visualization | Plotly, Pandas |
| HTTP Client | Requests |
| Data Format | JSON |
| Storage | Local File System |
| Language | Python 3.8+ |

