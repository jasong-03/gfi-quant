# Token Tracker Metrics Dashboard - Build Prompt

## Project Overview
Build a comprehensive Token Tracker Metrics dashboard that fetches data from multiple crypto data APIs (DefiLlama, Nansen, CoinGecko, Dune), stores it locally/cloud, and presents it through an interactive Streamlit interface.

## System Architecture

### 1. Data Layer (Backend)
Create a modular data fetching system with the following components:

#### API Clients
Build separate client classes for each data source:
- `DefiLlamaClient`: Handles DefiLlama API calls
- `NansenClient`: Handles Nansen API calls (POST requests with JSON body)
- `CoinGeckoClient`: Handles CoinGecko API calls
- `DuneClient`: Handles Dune Analytics API calls

#### Configuration Management
- Load API keys from a separate `config.py` or `.env` file
- API keys should be configurable for:
  - `DEFILLAMA_API_KEY` (for pro endpoints)
  - `NANSEN_API_KEY`
  - `COINGECKO_API_KEY`
  - `DUNE_API_KEY`
- Include fallback handling for endpoints that don't require keys

#### Data Storage
Implement local storage using:
- JSON files for raw API responses
- CSV files for processed/tabular data
- SQLite database as an option for structured storage
- Folder structure: `data/{source}/{chain}/{contract_address}/{endpoint_name}_{timestamp}.json`

### 2. Required API Endpoints Integration

Implement data fetching for these specific endpoints:

#### DefiLlama (4 endpoints)
1. **Get Price Chart**
   - Endpoint: `/coins/chart/{chain}:{address}?period={period}`
   - No API key required
   - Returns: Price history data

2. **Get Price Percentage Change**
   - Endpoint: `/coins/percentage/{chain}:{address}`
   - No API key required
   - Returns: Percentage change data

3. **Get Token Protocols**
   - Endpoint: `/api/tokenProtocols/{symbol}`
   - Requires API key
   - Returns: Protocols using the token

4. **Get Borrowing Rates**
   - Endpoint: `/yields/poolsBorrow`
   - Requires API key
   - Returns: Borrowing rates across protocols

#### Nansen (5 endpoints)
All Nansen endpoints use POST method with JSON body and require API key in header `x-api-key`

1. **Token Who Bought/Sold**
   - Endpoint: `/api/v1/tgm/who-bought-sold`
   - Credit cost: 1
   - Returns: Recent buyers and sellers

2. **Token Perp Trades**
   - Endpoint: `/api/v1/tgm/perp-trades`
   - Credit cost: 1
   - Returns: Perpetual futures trades

3. **Token Transfers**
   - Endpoint: `/api/v1/tgm/transfers`
   - Credit cost: 1
   - Returns: Token transfer events

4. **Token Holders**
   - Endpoint: `/api/v1/tgm/holders`
   - Credit cost: 5
   - Returns: Top holders by category

5. **Token Flow Intelligence**
   - Endpoint: `/api/v1/tgm/flow-intelligence`
   - Credit cost: Varies
   - Returns: Flow summary across smart money, exchanges, etc.

#### CoinGecko (3 endpoints)
All use header `x-cg-pro-api-key`

1. **Coins List (ID Map)**
   - Endpoint: `/api/v3/coins/list`
   - Returns: All coins with IDs

2. **Coin Historical Chart by Token Address**
   - Endpoint: `/api/v3/coins/{id}/contract/{contract_address}/market_chart`
   - Returns: Historical price/volume/market cap

3. **Coin Data by ID**
   - Endpoint: `/api/v3/coins/{id}`
   - Returns: Complete coin metadata

#### Dune Analytics (1 endpoint)
1. **Execute Query**
   - Endpoint: `/api/v1/query/{query_id}/execute`
   - Requires API key in header `X-Dune-API-Key`
   - Credit cost: Varies
   - Returns: Query execution results

### 3. Dashboard UI (Streamlit)

#### Layout Structure
Create a Streamlit app with the following structure:

**Header Section:**
- Title: "Token Tracker Metrics"
- Three tabs: "Market Data", "Token Tracker", "Social Listening"

**Input Section:**
- Chain dropdown: Support Ethereum, Solana, Polygon, Arbitrum, Base, etc.
- Contract address text input
- "Fetch Data" button

**Main Content Area:**
Split into two columns:

**Left Column - Log Monitoring:**
Display real-time status of data fetching:
```
Log Monitoring
✅ Load market data...
✅ Save market data to local
✅ Load delta balance change data...
✅ Save delta balance to local
✅ Load Market Flow Intelligence data...
✅ Save Market Flow Intelligence data
```

Include:
- Real-time status updates using `st.empty()` containers
- Success (✅) and failure (❌) indicators
- Timestamp for each operation
- Error messages when API calls fail

**Right Column - Endpoints Status:**
Table showing all available endpoints:
- Endpoint name
- Source (DefiLlama/Nansen/CoinGecko/Dune)
- Key required? (✅/❌)
- Credit amount
- Documentation link
- Fetch successful? (✅/❌)

#### Data Visualization Sections

1. **Price Charts** (using Plotly)
   - Line chart for historical prices (from DefiLlama/CoinGecko)
   - Candlestick chart option
   - Volume bars overlay
   - Configurable timeframe (1D, 7D, 30D, 90D, 1Y)

2. **Token Holders Analysis**
   - Pie chart showing holder distribution
   - Table of top holders with labels (Smart Money, Exchange, Whale, etc.)
   - Holder concentration metrics

3. **Flow Intelligence**
   - Sankey diagram showing token flows
   - Net inflow/outflow metrics
   - Smart Money vs Exchange flows

4. **Recent Activity**
   - Table of recent buyers/sellers
   - Transfer events timeline
   - Perp trades summary

5. **Borrowing Rates**
   - Comparison table across protocols
   - APY trends chart

### 4. Core Features

#### Error Handling
- Wrap all API calls in try-except blocks
- Log errors to console and display in UI
- Continue processing other endpoints if one fails
- Display helpful error messages (rate limit, invalid key, etc.)

#### Caching
- Use `st.cache_data` for API responses
- Cache duration: 5-15 minutes depending on data type
- Option to force refresh data

#### Rate Limiting
- Implement delays between API calls if needed
- Track API credit usage for Nansen/Dune
- Display remaining credits if available

#### Data Export
- Button to download all fetched data as JSON/CSV
- Export charts as PNG/HTML

### 5. File Structure

```
token-tracker-dashboard/
├── app.py                          # Main Streamlit application
├── config.py                       # API keys and configuration
├── requirements.txt                # Python dependencies
├── api_clients/
│   ├── __init__.py
│   ├── defillama_client.py
│   ├── nansen_client.py
│   ├── coingecko_client.py
│   └── dune_client.py
├── data_handlers/
│   ├── __init__.py
│   ├── storage.py                 # Local storage functions
│   └── processors.py              # Data processing utilities
├── utils/
│   ├── __init__.py
│   ├── logger.py                  # Logging configuration
│   └── validators.py              # Input validation
├── data/                          # Local data storage
│   ├── defillama/
│   ├── nansen/
│   ├── coingecko/
│   └── dune/
└── visualizations/
    ├── __init__.py
    ├── charts.py                  # Plotly chart functions
    └── tables.py                  # Data table components
```

### 6. Implementation Steps

**Step 1: Setup & Configuration**
- Install dependencies from requirements.txt
- Create config.py template with placeholder API keys
- Initialize project structure

**Step 2: Build API Clients**
- Implement each client class with proper authentication
- Add error handling and logging
- Test each endpoint independently

**Step 3: Data Storage Layer**
- Create storage functions for JSON/CSV
- Implement file naming convention with timestamps
- Add data retrieval functions

**Step 4: Core Dashboard**
- Build Streamlit UI layout
- Implement input handlers (chain, contract address)
- Create log monitoring display

**Step 5: Data Fetching Orchestration**
- Build main fetch function that calls all APIs
- Implement parallel fetching where appropriate
- Update UI with real-time status

**Step 6: Visualizations**
- Create Plotly charts for price data
- Build holder distribution visualizations
- Implement flow intelligence diagrams
- Add interactive tables

**Step 7: Testing & Refinement**
- Test with various tokens across different chains
- Handle edge cases (missing data, API errors)
- Optimize performance and caching

### 7. Key Requirements

**Dependencies (requirements.txt):**
```
streamlit
pandas
plotly
requests
matplotlib
coingecko-sdk
python-dotenv
```

**Python Version:** 3.8+

**API Authentication:**
- All API keys stored in config.py or .env
- Never hardcode keys in main application
- Include .env in .gitignore

**User Experience:**
- Clean, professional dark theme
- Responsive layout
- Loading spinners during data fetch
- Clear error messages
- Tooltips for technical terms

### 8. Advanced Features (Optional)

- **Auto-refresh**: Automatically fetch data at intervals
- **Alerts**: Set up notifications for specific events
- **Comparison Mode**: Compare multiple tokens side-by-side
- **Historical Analysis**: View trends over custom time ranges
- **Export Reports**: Generate PDF reports with all data
- **Cloud Storage**: Option to use S3/GCS instead of local storage

### 9. Success Criteria

The dashboard should:
1. ✅ Successfully fetch data from all 4 API sources
2. ✅ Handle API errors gracefully without crashing
3. ✅ Store all fetched data locally with proper organization
4. ✅ Display real-time status of data fetching operations
5. ✅ Present data in clear, interactive visualizations
6. ✅ Support multiple blockchain networks
7. ✅ Load quickly with proper caching
8. ✅ Be intuitive for non-technical users

### 10. Example Usage Flow

```python
# User opens dashboard
# Selects: Chain = "Solana", Contract = "So11111111111111111111111111111111111111112"
# Clicks "Fetch Data"

# System executes:
1. Validate contract address format
2. Initialize all API clients
3. Fetch data from DefiLlama endpoints → Save to local
4. Fetch data from Nansen endpoints → Save to local
5. Fetch data from CoinGecko endpoints → Save to local
6. Fetch data from Dune endpoints → Save to local
7. Process and visualize all collected data
8. Display results in dashboard

# User can:
- View price charts
- Analyze holder distribution
- See recent trading activity
- Export data
- Switch to different token
```

---

## Final Notes

- Prioritize code modularity and reusability
- Add comprehensive docstrings to all functions
- Include logging for debugging
- Follow PEP 8 style guidelines
- Make the UI visually similar to the provided wireframe
- Ensure all 13 required endpoints are implemented
- Build with scalability in mind for adding more APIs later
