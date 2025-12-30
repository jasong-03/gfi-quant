# Token Tracker Metrics Dashboard

A cryptocurrency analytics dashboard aggregating data from DefiLlama, Nansen, CoinGecko, and Dune Analytics.

## Quick Start

### Prerequisites

- Python 3.8+
- API keys for Nansen and Dune Analytics (required)
- API keys for CoinGecko and DefiLlama (optional, for pro features)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd token-tracker-dashboard

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp config_template.py config.py
# Edit config.py and add your API keys
```

### Run the Dashboard

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Features

| Feature | Description |
|---------|-------------|
| Multi-Source Aggregation | Fetch from 4 major crypto data APIs in one click |
| Multi-Chain Support | Ethereum, Solana, Polygon, Arbitrum, Base, Optimism, BSC |
| Interactive Charts | Plotly-powered visualizations with zoom and hover |
| Local Data Storage | Automatic JSON caching for offline analysis |
| Real-Time Logging | Live progress monitoring during data fetching |
| Theme Support | Dark and Light mode |

---

## Supported API Endpoints

### DefiLlama (Free/Pro)

| Endpoint | Status |
|----------|--------|
| Get Price Chart | Available |
| Get Price Percentage Change | Available |
| Get Token Protocols | Pro only |
| Get Borrowing Rates | Available |

### Nansen (Requires API Key)

| Endpoint | Status |
|----------|--------|
| Token Who Bought/Sold | Available |
| Token Flow Intelligence | Available |
| Token Holders | Available |
| Token Transfers | Available |
| Token Perp Trades | Requires symbol |

### CoinGecko (Free/Pro)

| Endpoint | Status |
|----------|--------|
| Coins List (ID Map) | Available |
| Historical Chart by Contract | Available |
| Coin Data by ID | Available |

### Dune Analytics (Requires API Key)

| Endpoint | Status |
|----------|--------|
| Delta Balance Change | Available |

---

## Configuration

### API Keys Setup

Create `config.py` from the template:

```python
API_KEYS = {
    'DEFILLAMA_API_KEY': '',      # Optional (for pro endpoints)
    'NANSEN_API_KEY': 'your-key', # Required
    'COINGECKO_API_KEY': '',      # Optional (for pro endpoints)
    'DUNE_API_KEY': 'your-key',   # Required
}
```

**Security**: Never commit `config.py` to version control.

### Rate Limits

| Provider | Limit |
|----------|-------|
| DefiLlama | 60 req/min |
| Nansen | 30 req/min |
| CoinGecko | 50 req/min |
| Dune | 20 req/min |

---

## Usage

1. **Select Chain**: Choose blockchain network from dropdown
2. **Enter Contract Address**: Paste token contract address
3. **Select Period**: Choose analysis timeframe (3 months to All)
4. **Fetch Data**: Click "Fetch" to start data collection
5. **Monitor Progress**: Watch real-time logs
6. **Analyze**: Switch to "Token Tracker" tab for visualizations

### Example Tokens

| Token | Chain | Address |
|-------|-------|---------|
| SOL | Solana | `So11111111111111111111111111111111111111112` |
| USDC | Ethereum | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| USDT | Ethereum | `0xdac17f958d2ee523a2206206994597c13d831ec7` |

---

## Project Structure

```
gfi-quant-project/
├── app.py                 # Main Streamlit application
├── config.py              # API keys and configuration
├── api_clients/           # API client implementations
│   ├── dune_client.py
│   ├── defillama_client.py
│   ├── nansen_client.py
│   └── coingecko_client.py
├── data_handlers/         # Data storage and processing
│   └── storage.py
├── utils/                 # Utilities (logger, validators)
├── visualizations/        # Charts and tables
├── docs/                  # Documentation
└── data/                  # Cached data (auto-created)
```

---

## Documentation

Detailed documentation is available in the `docs/` directory:

| Document | Description |
|----------|-------------|
| [Project Overview (PDR)](docs/project-overview-pdr.md) | Product vision, goals, and success criteria |
| [Codebase Summary](docs/codebase-summary.md) | Complete module and function reference |
| [Code Standards](docs/code-standards.md) | Coding conventions and patterns |
| [System Architecture](docs/system-architecture.md) | Architecture diagrams and data flows |

---

## Data Storage

Fetched data is saved to the `data/` directory:

```
data/{source}/{chain}/{address}/{endpoint}_{timestamp}.json
```

Example:
```
data/nansen/ethereum/0xA0b8.../holders_20241226_143022.json
```

---

## Troubleshooting

### Common Issues

| Error | Solution |
|-------|----------|
| `API key is required` | Add API key to `config.py` |
| `ModuleNotFoundError` | Run from project root directory |
| `ConnectionError` | Check internet connection |
| `Rate limit exceeded` | Wait before retrying |

### Viewing Logs

Check the "Log Monitoring" panel in the dashboard for real-time status updates during data fetching.

---

## Development

### Adding a New API Endpoint

1. Add method to appropriate client in `api_clients/`
2. Update `fetch_all_data()` in `app.py`
3. Add visualization function if needed
4. Update endpoint status tracking

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Use type hints
- Log important operations

See [Code Standards](docs/code-standards.md) for details.

---

## Roadmap

| Feature | Status |
|---------|--------|
| Core data fetching | Complete |
| Visualizations | Complete |
| WebSocket real-time | Planned |
| Multi-token comparison | Planned |
| Automated alerts | Planned |
| PDF report generation | Planned |

---

## Credits

### Data Sources
- [DefiLlama](https://defillama.com) - DeFi analytics
- [Nansen](https://nansen.ai) - Blockchain intelligence
- [CoinGecko](https://coingecko.com) - Market data
- [Dune Analytics](https://dune.com) - Blockchain queries

### Built With
- [Streamlit](https://streamlit.io) - Web framework
- [Plotly](https://plotly.com/python/) - Interactive charts
- [Pandas](https://pandas.pydata.org) - Data manipulation

---

## License

This project is provided as-is for educational and personal use.

---

**Note**: This dashboard is for informational purposes only. Always conduct your own research before making investment decisions.

