# Token Tracker Metrics Dashboard

A comprehensive cryptocurrency analytics dashboard that aggregates data from multiple sources: DefiLlama, Nansen, CoinGecko, and Dune Analytics.

![Dashboard Preview](wireframe_ideas.png)

## Features

- 📊 **Multi-Source Data Aggregation**: Fetch data from 4 major crypto data APIs
- 💾 **Local Data Storage**: Save all fetched data locally for offline analysis
- 📈 **Interactive Visualizations**: Plotly-powered charts and graphs
- 🔄 **Real-Time Monitoring**: Live status updates during data fetching
- 🎯 **Token Tracking**: Comprehensive token analysis across multiple chains
- 🌐 **Multi-Chain Support**: Ethereum, Solana, Polygon, Arbitrum, Base, and more

## Architecture

```
token-tracker-dashboard/
├── app.py                      # Main Streamlit application
├── config.py                   # API keys and configuration
├── requirements.txt            # Python dependencies
├── api_clients/               # API client implementations
│   ├── defillama_client.py
│   ├── nansen_client.py
│   ├── coingecko_client.py
│   └── dune_client.py
├── data_handlers/             # Data storage and processing
│   └── storage.py
└── data/                      # Local data storage (auto-created)
    ├── defillama/
    ├── nansen/
    ├── coingecko/
    └── dune/
```

## Prerequisites

- Python 3.8 or higher
- API keys for:
  - DefiLlama (optional, for pro endpoints)
  - Nansen (required)
  - CoinGecko (optional, for pro endpoints)
  - Dune Analytics (required)

## Installation

### 1. Clone or Download the Repository

```bash
git clone <your-repo-url>
cd token-tracker-dashboard
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `config.py` file from the template:

```bash
cp config_template.py config.py
```

Edit `config.py` and add your API keys:

```python
API_KEYS = {
    'DEFILLAMA_API_KEY': 'your-defillama-key',  # Optional
    'NANSEN_API_KEY': 'your-nansen-key',        # Required
    'COINGECKO_API_KEY': 'your-coingecko-key',  # Optional
    'DUNE_API_KEY': 'your-dune-key',            # Required
}
```

**⚠️ Security Note**: Never commit `config.py` to version control. It's included in `.gitignore`.

## Usage

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Using the Dashboard

1. **Select Chain**: Choose the blockchain network (Ethereum, Solana, etc.)
2. **Enter Contract Address**: Paste the token contract address
3. **Fetch Data**: Click the "🚀 Fetch Data" button
4. **Monitor Progress**: Watch real-time logs in the Log Monitoring panel
5. **Analyze Results**: View charts, tables, and insights

### Example Tokens to Try

- **Solana (SOL)**: `So11111111111111111111111111111111111111112` on Solana
- **USDC**: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` on Ethereum
- **USDT**: `0xdac17f958d2ee523a2206206994597c13d831ec7` on Ethereum

## API Endpoints Implemented

### DefiLlama (4 endpoints)
- ✅ Get Price Chart
- ✅ Get Price Percentage Change
- ✅ Get Token Protocols
- ✅ Get Borrowing Rates

### Nansen (5 endpoints)
- ✅ Token Who Bought/Sold
- ✅ Token Perp Trades
- ✅ Token Transfers
- ✅ Token Holders
- ✅ Token Flow Intelligence

### CoinGecko (3 endpoints)
- ✅ Coins List (ID Map)
- ✅ Coin Historical Chart by Token Address
- ✅ Coin Data by ID

### Dune Analytics (1 endpoint)
- ✅ Delta Balance Change

## Data Storage

All fetched data is automatically saved to the `data/` directory:

```
data/
├── defillama/
│   └── ethereum/
│       └── 0xA0b8.../
│           ├── price_chart_20241226_143022.json
│           └── price_percentage_20241226_143023.json
├── nansen/
│   └── solana/
│       └── So1111.../
│           ├── who_bought_sold_20241226_143025.json
│           └── holders_20241226_143027.json
└── ...
```

### Managing Cached Data

View storage statistics in the sidebar:
- Total cached files
- Storage size
- Files per API source

Clear cache using the "🗑️ Clear Cache" button

## Development

### Project Structure

- **`app.py`**: Main Streamlit application with UI layout
- **`api_clients/`**: Separate client classes for each API
- **`data_handlers/storage.py`**: Local data storage management
- **`config.py`**: Configuration and API keys (not in git)

### Adding New Features

1. **New API Endpoint**: Add method to relevant client in `api_clients/`
2. **New Visualization**: Add chart function to `app.py`
3. **New Data Processing**: Add processor to `data_handlers/`

### Code Style

- Follow PEP 8 guidelines
- Add docstrings to all functions
- Use type hints
- Log important operations

## API Rate Limits

Be aware of rate limits for each API:

- **DefiLlama**: 60 requests/minute
- **Nansen**: 30 requests/minute (credit-based)
- **CoinGecko**: 50 requests/minute (varies by plan)
- **Dune**: 20 requests/minute (credit-based)

The dashboard implements proper error handling for rate limits.

## Troubleshooting

### API Key Errors

```
Error: Nansen API key is required
```
**Solution**: Add your Nansen API key to `config.py`

### Module Import Errors

```
ModuleNotFoundError: No module named 'api_clients'
```
**Solution**: Ensure you're running from the project root directory

### Data Fetch Failures

- Check API key validity
- Verify contract address format
- Check rate limits
- Review logs in the monitoring panel

### Network Issues

```
requests.exceptions.ConnectionError
```
**Solution**: Check your internet connection and firewall settings

## Credits

### Data Sources
- [DefiLlama](https://defillama.com) - DeFi analytics
- [Nansen](https://nansen.ai) - Blockchain analytics
- [CoinGecko](https://coingecko.com) - Crypto market data
- [Dune Analytics](https://dune.com) - Blockchain queries

### Built With
- [Streamlit](https://streamlit.io) - Web framework
- [Plotly](https://plotly.com/python/) - Interactive charts
- [Pandas](https://pandas.pydata.org) - Data manipulation

## License

This project is provided as-is for educational and personal use.

## Support

For issues, questions, or contributions:
1. Check existing documentation
2. Review error logs in the dashboard
3. Consult API documentation links in the endpoint table

## Roadmap

### Planned Features
- [ ] WebSocket support for real-time updates
- [ ] Multi-token comparison view
- [ ] Automated alerts and notifications
- [ ] Cloud storage integration (S3/GCS)
- [ ] PDF report generation
- [ ] Portfolio tracking
- [ ] Social sentiment analysis
- [ ] Advanced charting tools

### Current Version
**v1.0.0** - Initial release with core features

---

**Note**: This dashboard is for informational purposes only. Always do your own research before making investment decisions.
