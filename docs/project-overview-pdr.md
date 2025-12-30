# GFI Quant Token Tracker Dashboard - Project Overview

## Product Development Requirements (PDR)

**Document Version:** 1.0
**Last Updated:** December 2024
**Status:** Active Development

---

## 1. Product Vision

The GFI Quant Token Tracker Dashboard is a comprehensive cryptocurrency analytics platform designed to aggregate, analyze, and visualize token data from multiple blockchain intelligence sources. The dashboard provides traders, analysts, and researchers with a unified view of token metrics, holder distributions, flow patterns, and market dynamics across multiple blockchain networks.

### Vision Statement

*Empower crypto analysts with real-time, multi-source token intelligence through a single, intuitive interface that eliminates the need to navigate multiple platforms.*

---

## 2. Target Users

### Primary Users

| User Type | Description | Key Needs |
|-----------|-------------|-----------|
| Crypto Traders | Active traders seeking alpha signals | Real-time holder changes, whale movements, flow intelligence |
| Token Analysts | Researchers analyzing token fundamentals | Historical data, holder distribution, protocol integrations |
| Portfolio Managers | Fund managers tracking positions | Multi-chain support, data export, trend analysis |
| DeFi Researchers | Analysts studying protocol dynamics | TVL data, borrowing rates, protocol relationships |

### User Personas

**Persona 1: Alex the Alpha Hunter**
- Uses Nansen and Dune daily
- Needs quick access to holder concentration changes
- Values real-time flow intelligence data

**Persona 2: Riley the Researcher**
- Prepares detailed token reports
- Needs historical price and holder data
- Values data export and local storage capabilities

---

## 3. Product Goals

### Primary Goals

1. **Data Aggregation**: Consolidate data from four major crypto data providers (DefiLlama, Nansen, CoinGecko, Dune Analytics) into a single interface

2. **Multi-Chain Coverage**: Support token analysis across seven major blockchain networks

3. **Persistent Storage**: Enable offline analysis through automatic local data caching

4. **Real-Time Monitoring**: Provide live feedback during data fetching operations

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Coverage | 4 providers, 13+ endpoints | Endpoint status tracking |
| Chain Support | 7 networks | Successful data fetches per chain |
| Data Freshness | < 5 minutes cache | Timestamp validation |
| Fetch Success Rate | > 90% per session | Log monitoring analysis |

---

## 4. Core Features

### 4.1 Multi-Source Data Fetching

**Description**: Orchestrated data retrieval from multiple API providers with status tracking.

**Components**:
- DefiLlama: Price charts, percentage changes, protocol data, borrowing rates
- Nansen: Holder data, transfers, flow intelligence, buy/sell analysis
- CoinGecko: Historical charts, coin metadata, market data
- Dune Analytics: Custom SQL queries, delta balance analysis

**User Flow**:
1. User selects blockchain network
2. User enters token contract address
3. User selects analysis period
4. System fetches data from all sources concurrently
5. Real-time log displays progress and status

### 4.2 Interactive Visualizations

**Description**: Plotly-powered charts for data analysis and exploration.

**Visualization Types**:

| Chart Type | Data Source | Purpose |
|------------|-------------|---------|
| Price Chart | DefiLlama/CoinGecko | Historical price trends |
| Delta Balance Chart | Dune Analytics | Balance changes with price overlay |
| Holders Bar Chart | Nansen | Top 20 holder distribution |
| Flow Intelligence Tables | Nansen | Multi-timeframe flow metrics |
| Transfers Table | Nansen | Recent transfer history |

### 4.3 Local Data Persistence

**Description**: Automatic JSON caching with timestamp-based versioning.

**Storage Structure**:
```
data/{source}/{chain}/{contract_address}/{endpoint_name}_{timestamp}.json
```

**Features**:
- Automatic directory creation
- Timestamp-based file naming for version history
- Load latest data functionality
- Cache statistics in sidebar

### 4.4 Real-Time Log Monitoring

**Description**: Dual-channel logging with UI feedback during operations.

**Log Levels**:
- Info: Operation progress updates
- Success: Completed operations
- Error: Failed operations with error details

---

## 5. Technical Requirements

### 5.1 Supported Blockchains

| Network | Chain ID | API Coverage |
|---------|----------|--------------|
| Ethereum | ethereum | Full |
| Solana | solana | Full |
| Polygon | polygon-pos | Full |
| Arbitrum | arbitrum-one | Full |
| Base | base | Full |
| Optimism | optimistic-ethereum | Full |
| BSC | binance-smart-chain | Full |

### 5.2 API Authentication

| Provider | Auth Method | Requirement |
|----------|-------------|-------------|
| DefiLlama | API Key in URL (Pro) / None (Public) | Optional |
| Nansen | `apiKey` header | Required |
| CoinGecko | `x-cg-pro-api-key` header | Optional |
| Dune Analytics | `X-Dune-API-Key` header | Required |

### 5.3 Rate Limits

| Provider | Limit | Notes |
|----------|-------|-------|
| DefiLlama | 60 req/min | Public endpoints unlimited |
| Nansen | 30 req/min | Credit-based system |
| CoinGecko | 50 req/min | Varies by plan |
| Dune Analytics | 20 req/min | Credit-based system |

---

## 6. Success Criteria

### Functional Success Criteria

- [ ] Successfully fetch data from all 4 API providers
- [ ] Support all 7 blockchain networks
- [ ] Display all visualization types correctly
- [ ] Persist data to local storage with proper structure
- [ ] Handle API errors gracefully with user feedback

### Performance Success Criteria

- [ ] Complete full data fetch in < 3 minutes
- [ ] Render visualizations in < 2 seconds
- [ ] Handle Dune query polling efficiently (up to 180 seconds timeout)

### User Experience Success Criteria

- [ ] Provide clear feedback during data fetching
- [ ] Display intuitive endpoint status indicators
- [ ] Enable data preview for each endpoint
- [ ] Support theme switching (Dark/Light)

---

## 7. Constraints and Limitations

### Technical Constraints

1. **API Dependencies**: Functionality depends on external API availability
2. **Rate Limiting**: Cannot exceed provider rate limits
3. **Dune Latency**: SQL query execution requires polling with variable wait times
4. **Browser-Based**: All processing occurs client-side via Streamlit

### Business Constraints

1. **API Costs**: Some endpoints require paid API keys (Nansen, Dune, CoinGecko Pro)
2. **Data Freshness**: Cannot guarantee real-time data for all endpoints

---

## 8. Future Roadmap

### Phase 2 - Planned Features

| Feature | Priority | Status |
|---------|----------|--------|
| WebSocket real-time updates | High | Planned |
| Multi-token comparison view | High | Planned |
| Automated alerts | Medium | Planned |
| PDF report generation | Medium | Planned |
| Cloud storage integration | Low | Planned |
| Social sentiment analysis | Low | Planned |

### Phase 3 - Extended Features

- Portfolio tracking across wallets
- Advanced charting tools (TradingView-style)
- Custom Dune query builder
- API rate limit optimization
- Webhook notifications

---

## 9. Glossary

| Term | Definition |
|------|------------|
| TVL | Total Value Locked - total value of assets deposited in a protocol |
| Flow Intelligence | Analysis of token movements between wallet categories |
| Delta Balance | Net change in token holdings over a period |
| Smart Trader | Nansen label for wallets with historically profitable trades |
| Whale | Wallet holding significant token position (typically top 1%) |

---

## 10. Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2024 | GFI Team | Initial PDR creation |

