"""
Configuration file for API keys
"""
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Try to load local settings first
try:
    from local_settings import API_KEYS as LOCAL_KEYS
except ImportError:
    LOCAL_KEYS = {}

# Try to load Streamlit secrets
try:
    import streamlit as st
    # Check if secrets file exists or if we are in an environment where secrets are loaded
    if hasattr(st, 'secrets'):
         ST_SECRETS = st.secrets.get("API_KEYS", {})
    else:
         ST_SECRETS = {}
except (ImportError, FileNotFoundError, AttributeError):
    ST_SECRETS = {}

def get_key(name):
    # Order: Local Settings -> Streamlit Secrets -> Env Var -> Empty
    return LOCAL_KEYS.get(name) or ST_SECRETS.get(name) or os.getenv(name) or ''

# API Keys
API_KEYS = {
    'DEFILLAMA_API_KEY': get_key('DEFILLAMA_API_KEY'),
    'NANSEN_API_KEY': get_key('NANSEN_API_KEY'),
    'COINGECKO_API_KEY': get_key('COINGECKO_API_KEY'),
    'DUNE_API_KEY': get_key('DUNE_API_KEY'),
}

# API Base URLs
API_URLS = {
    'DEFILLAMA': 'https://coins.llama.fi',
    'DEFILLAMA_YIELDS': 'https://yields.llama.fi',
    'DEFILLAMA_API': 'https://api.llama.fi',
    'NANSEN': 'https://api.nansen.ai/api/v1',
    'COINGECKO': 'https://pro-api.coingecko.com/api/v3',
    'DUNE': 'https://api.dune.com/api/v1'
}

# Data storage configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
CACHE_DURATION = 300  # 5 minutes in seconds

# Google Cloud Configuration
GCP_CONFIG = {
    'PROJECT_ID': 'gfi-455410',
    'SERVICE_ACCOUNT_FILE': os.path.join(BASE_DIR, 'gfi-455410-c5f5b0bf4d3a.json'),
    'GCS_BUCKET': 'gfi-token-tracker-data',
    'BIGQUERY_DATASET': 'token_tracker',
}

# Storage mode: 'local', 'gcs', 'bigquery', 'all'
STORAGE_MODE = get_key('STORAGE_MODE') or 'all'

# Source Icons Mapping (filename in assets folder)
SOURCE_ICONS = {
    'DefiLlama': 'defillama.jpg',
    'Nansen': 'nansen.jpg',
    'CoinGecko': 'coingecko.jpg',
    'Dune': 'dune.jpg'
}

# Supported chains and their identifiers (mapping to different API standards)
SUPPORTED_CHAINS = {
    'Ethereum': {
        'defillama': 'ethereum',
        'nansen': 'ethereum',
        'coingecko': 'ethereum',
        'id': 'ethereum'
    },
    'Solana': {
        'defillama': 'solana',
        'nansen': 'solana',
        'coingecko': 'solana',
        'id': 'solana'
    },
    'Polygon': {
        'defillama': 'polygon',
        'nansen': 'polygon',
        'coingecko': 'polygon-pos',
        'id': 'matic-network'
    },
    'Arbitrum': {
        'defillama': 'arbitrum',
        'nansen': 'arbitrum',
        'coingecko': 'arbitrum-one',
        'id': 'arbitrum'
    },
    'Base': {
        'defillama': 'base',
        'nansen': 'base',
        'coingecko': 'base',
        'id': 'base'
    },
    'Optimism': {
        'defillama': 'optimism',
        'nansen': 'optimism',
        'coingecko': 'optimistic-ethereum',
        'id': 'optimism'
    },
    'BSC': {
        'defillama': 'bsc',
        'nansen': 'nmn',
        'coingecko': 'binance-smart-chain',
        'id': 'binancecoin'
    }
}

# Default request timeout (seconds)
REQUEST_TIMEOUT = 30

# Rate limiting (requests per minute)
RATE_LIMITS = {
    'DEFILLAMA': 60,
    'NANSEN': 30,
    'COINGECKO': 50,
    'DUNE': 20
}
