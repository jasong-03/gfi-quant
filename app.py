"""
Token Tracker Metrics Dashboard
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import base64
from pathlib import Path

from config import API_KEYS, SUPPORTED_CHAINS, SOURCE_ICONS
from api_clients.nansen_client import NansenClient
from api_clients.coingecko_client import CoinGeckoClient
from data_handlers.storage import save_json, load_latest_json
from utils.logger import log_to_ui as log_to_ui_util
from utils.validators import validate_contract_address
from visualizations.charts import (
    create_price_chart, 
    create_holders_pie_chart, 
    create_delta_balance_chart,
    create_holders_bar_chart
)
from visualizations.tables import create_flow_intelligence_table, create_transfers_table

# Page configuration
try:
    icon_path = Path(__file__).parent / "assets" / "icon.jpg"
    page_icon = str(icon_path) if icon_path.exists() else "📊"
except Exception:
    page_icon = "📊"

st.set_page_config(
    page_title="Token Tracker",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # User Selection
    DEFAULT_MEMBERS = ["Andrew", "Minh", "Linh"]
    if 'team_members' not in st.session_state:
        st.session_state.team_members = DEFAULT_MEMBERS.copy()

    current_user = st.selectbox("👤 Bạn là ai?", st.session_state.team_members, index=0)
    st.session_state.current_user = current_user

    # Add new member
    with st.expander("➕ Thêm thành viên"):
        new_member = st.text_input("Tên mới", placeholder="Nhập tên...")
        if st.button("Thêm", use_container_width=True):
            if new_member and new_member not in st.session_state.team_members:
                st.session_state.team_members.append(new_member)
                st.rerun()

    st.markdown("---")

    # Theme Switcher
    theme = st.selectbox("Theme", ["Dark", "Light"], index=0)

    st.markdown("---")

    st.markdown("### API Status & Credits")
    
    if 'api_usage' not in st.session_state:
        st.session_state.api_usage = {}

    def check_credits(api_name):
        try:
            if api_name == "Nansen":
                client = NansenClient()
                # Lightweight call to check connectivity/headers
                client.get_token_holders("0x0000000000000000000000000000000000000000", "ethereum", page=1, per_page=1)
                st.session_state.api_usage[api_name] = "✅ Connected"
                # Nansen headers might contain rate limits but usually not total credits on standard plans
                
            elif api_name == "CoinGecko":
                client = CoinGeckoClient()
                client.get_coins_list() # Simple call
                headers = getattr(client, 'last_headers', {})
                # Check for rate limit headers
                remaining = headers.get('x-rate-limit-remaining-month')
                if remaining:
                    st.session_state.api_usage[api_name] = f"✅ Credits: {remaining}"
                else:
                    st.session_state.api_usage[api_name] = "✅ Connected"

            elif api_name == "Dune":
                client = DuneClient()
                # No simple ping, check execution status of a dummy ID or just assume connected if key present
                # Credits often in x-dune-remaining-credits
                # We can't easily make a valid call without spending credits or having a query ID.
                # Just show Key status
                st.session_state.api_usage[api_name] = "✅ Key Present"
                
            elif api_name == "DefiLlama":
                 st.session_state.api_usage[api_name] = "✅ Public/Free"

        except Exception as e:
            st.session_state.api_usage[api_name] = f"❌ Error: {str(e)[:20]}..."

    # Display API Status
    api_list = ["Nansen", "CoinGecko", "Dune", "DefiLlama"]
    
    for api in api_list:
        c1, c2 = st.columns([2, 1])
        c1.write(f"**{api}**")
        if c2.button("Check", key=f"check_{api}", use_container_width=True):
            check_credits(api)
        
        status = st.session_state.api_usage.get(api, "Not checked")
        st.caption(status)
        st.markdown("---")
    
    # About Section
    st.markdown("### About")
    
    def get_image_base64(path):
        try:
            with open(path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()
            return encoded_string
        except Exception:
            return None

    icon_html = ""
    if icon_path.exists():
        icon_b64 = get_image_base64(icon_path)
        if icon_b64:
            icon_html = f'<a href="https://x.com/pupuOnW3" target="_blank"><img src="data:image/jpeg;base64,{icon_b64}" width="25" style="vertical-align: middle; margin-left: 5px; border-radius: 50%;"></a>'

    st.markdown(f"""
    Build with <3 by Andrew {icon_html}
    
    **Token Tracker Metrics** aggregates data from:
    - DefiLlama
    - Nansen
    - CoinGecko  
    - Dune Analytics
    
    Version: 1.0.0
    """, unsafe_allow_html=True)

# Custom CSS based on Theme
if theme == "Dark":
    st.markdown("""
        <style>
        .main {
            background-color: #0e1117;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #262730;
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
        }
        .log-success {
            color: #00ff00;
        }
        .log-error {
            color: #ff0000;
        }
        .endpoint-table {
            font-size: 12px;
        }
        div.stButton > button {
            width: 100%;
            padding-top: 2px;
            padding-bottom: 2px;
            min-height: 0px;
            height: auto;
        }
        /* Reduce markdown paragraph margin */
        div[data-testid="stMarkdownContainer"] p {
            margin-bottom: 0px;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    # Light Theme Adjustments
    st.markdown("""
        <style>
        div.stButton > button {
            width: 100%;
            padding-top: 2px;
            padding-bottom: 2px;
            min-height: 0px;
            height: auto;
        }
        div[data-testid="stMarkdownContainer"] p {
            margin-bottom: 0px;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'fetched_data' not in st.session_state:
    st.session_state.fetched_data = {}
if 'endpoint_status' not in st.session_state:
    st.session_state.endpoint_status = {}
if 'preview_endpoint' not in st.session_state:
    st.session_state.preview_endpoint = None
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

ENDPOINT_MAPPING = {
    # ==================== CoinGecko ====================
    # Simple/Price
    "CG: Simple Price": ("coingecko", "simple_price"),
    "CG: Token Price by Contract": ("coingecko", "simple_token_price"),
    # Coins
    "CG: Coins List": ("coingecko", "coins_list"),
    "CG: Coins Markets": ("coingecko", "coins_markets"),
    "CG: Coin Data by ID": ("coingecko", "coin_data"),
    "CG: Coin Tickers": ("coingecko", "coin_tickers"),
    "CG: Coin Market Chart": ("coingecko", "coin_market_chart"),
    "CG: Coin OHLC": ("coingecko", "coin_ohlc"),
    # Contract
    "CG: Coin Info by Contract": ("coingecko", "coin_info"),
    "CG: Chart by Contract": ("coingecko", "historical_chart"),
    # Categories
    "CG: Categories List": ("coingecko", "categories_list"),
    "CG: Categories": ("coingecko", "categories"),
    # Exchanges
    "CG: Exchanges": ("coingecko", "exchanges"),
    "CG: Exchanges List": ("coingecko", "exchanges_list"),
    # Derivatives
    "CG: Derivatives": ("coingecko", "derivatives"),
    "CG: Derivatives Exchanges": ("coingecko", "derivatives_exchanges"),
    # General
    "CG: Asset Platforms": ("coingecko", "asset_platforms"),
    "CG: Exchange Rates": ("coingecko", "exchange_rates"),
    "CG: Search": ("coingecko", "search"),
    "CG: Trending": ("coingecko", "trending"),
    "CG: Global": ("coingecko", "global"),
    "CG: Global DeFi": ("coingecko", "global_defi"),
    # Onchain DEX
    "CG: Onchain Networks": ("coingecko", "onchain_networks"),
    "CG: Onchain Token": ("coingecko", "onchain_token"),
    "CG: Onchain Token Pools": ("coingecko", "onchain_token_pools"),
    "CG: Onchain Trending Pools": ("coingecko", "onchain_trending_pools"),
    "CG: Onchain New Pools": ("coingecko", "onchain_new_pools"),

    # ==================== Nansen ====================
    # Smart Money
    "NS: Smart Money Netflow": ("nansen", "sm_netflow"),
    "NS: Smart Money Holdings": ("nansen", "sm_holdings"),
    "NS: Smart Money DEX Trades": ("nansen", "sm_dex_trades"),
    # Profiler
    "NS: Address Balance": ("nansen", "address_balance"),
    "NS: Address Transactions": ("nansen", "address_transactions"),
    "NS: Address Related Wallets": ("nansen", "address_related_wallets"),
    "NS: Address Counterparties": ("nansen", "address_counterparties"),
    "NS: Address PnL": ("nansen", "address_pnl"),
    # TGM - Token
    "NS: Token Screener": ("nansen", "token_screener"),
    "NS: Token Flows": ("nansen", "token_flows"),
    "NS: Token Flow Intelligence": ("nansen", "flow_intelligence"),
    "NS: Token Who Bought/Sold": ("nansen", "who_bought_sold"),
    "NS: Token DEX Trades": ("nansen", "token_dex_trades"),
    "NS: Token Transfers": ("nansen", "transfers"),
    "NS: Token Holders": ("nansen", "holders"),
    "NS: Token PnL Leaderboard": ("nansen", "token_pnl_leaderboard"),
    # TGM - Perp
    "NS: Perp Screener": ("nansen", "perp_screener"),
    "NS: Token Perp Trades": ("nansen", "perp_trades"),
    "NS: Token Perp Positions": ("nansen", "perp_positions"),
    "NS: Perp PnL Leaderboard": ("nansen", "perp_pnl_leaderboard"),
    # Portfolio
    "NS: DeFi Holdings": ("nansen", "defi_holdings"),
}

def get_endpoint_list():
    """Get the endpoint status list with sorting - auto-generated from ENDPOINT_MAPPING"""
    endpoints = []
    for name, (source, key) in ENDPOINT_MAPPING.items():
        source_display = "CoinGecko" if source == "coingecko" else "Nansen"
        endpoints.append({
            "Endpoint": name,
            "Source": source_display,
            "Fetch Success": st.session_state.endpoint_status.get(key, "pending")
        })

    # Sorting logic: done (0) -> failed (1) -> warning (2) -> pending (3)
    def get_sort_key(ep):
        status = ep["Fetch Success"]
        if "done" in status: return 0
        if "failed" in status: return 1
        if "⚠️" in status: return 2
        return 3

    return sorted(endpoints, key=get_sort_key)

def load_dune_query(chain, address, period):
    try:
        # Use relative path for robustness
        query_path = Path(__file__).parent / "delta_balance_change_dune_query.txt"
        with open(query_path, 'r') as f:
            query_sql = f.read()
        
        # Format parameters
        contract_addr_sql = f"'{address}'"
        chain_sql = f"'{chain.lower()}'" 
        
        # Period Mapping
        # 3 months, 6 months, 1 year, All
        interval_val = None
        if "3" in period:
            interval_val = "3"
        elif "6" in period:
            interval_val = "6"
        elif "1" in period or "year" in period:
            interval_val = "12"
        # else "All" -> None

        if interval_val:
            # Fix Trino/Dune SQL interval syntax: interval '3' month
            time_filter_clause_day = f"AND day >= now() - interval '{interval_val}' month"
            time_filter_clause_timestamp = f"AND timestamp >= now() - interval '{interval_val}' month"
        else:
            time_filter_clause_day = ""
            time_filter_clause_timestamp = ""
        
        formatted_sql = query_sql.format(
            contract_addr_sql=contract_addr_sql,
            chain_sql=chain_sql,
            time_filter_clause_day=time_filter_clause_day,
            time_filter_clause_timestamp=time_filter_clause_timestamp
        )
        return formatted_sql
    except Exception as e:
        log_to_ui_util(f"Error loading Dune SQL: {str(e)}", "error")
        return None

def fetch_all_data(chain_name, contract_address, period="3 months", log_placeholder=None, user_id=None):
    """
    Main function to fetch data from all API sources (CoinGecko + Nansen)
    Total: 50+ endpoints

    Args:
        user_id: User identifier for multi-user storage
    """
    st.session_state.logs = []
    st.session_state.endpoint_status = {}

    bg_color = "#0c0c0c" if theme == "Dark" else "#f0f2f6"
    text_color = "#00ff00" if theme == "Dark" else "#006400"

    def log_to_ui(message, status="info"):
        log_to_ui_util(message, status)
        if log_placeholder:
            log_content = "<br>".join(st.session_state.logs)
            log_placeholder.markdown(f"""
                <div style="background-color: {bg_color}; color: {text_color}; font-family: monospace; padding: 15px; height: 300px; overflow-y: scroll; border: 1px solid #333; border-radius: 5px; font-size: 12px; line-height: 1.5;">
                    {log_content}
                </div>
            """, unsafe_allow_html=True)

    def fetch_endpoint(key, func, *args, **kwargs):
        """Helper to fetch and save endpoint data"""
        try:
            data = func(*args, **kwargs)
            save_json(data, kwargs.get('source', 'unknown'), chain_name, contract_address, key, user_id)
            st.session_state.endpoint_status[key] = "✅ done"
            return data
        except Exception as e:
            log_to_ui(f"{key} error: {str(e)[:50]}", "error")
            st.session_state.endpoint_status[key] = "❌ failed"
            return None

    log_to_ui(f"Starting fetch for {chain_name}: {contract_address} ({period}) by {user_id}", "info")

    chain_config = SUPPORTED_CHAINS.get(chain_name)
    if not chain_config:
        log_to_ui(f"Chain {chain_name} not found", "error")
        return

    # Calculate dates
    end_date_obj = datetime.now()
    days = {"3 months": 90, "6 months": 180, "1 year": 365}.get(period, 365*3)
    start_date_obj = end_date_obj - timedelta(days=days)
    start_date_str = start_date_obj.strftime("%Y-%m-%d")
    end_date_str = end_date_obj.strftime("%Y-%m-%d")
    cg_days = str(days) if period != "All" else "max"

    # Init clients
    try:
        log_to_ui("Initializing API clients...", "info")
        nansen = NansenClient()
        coingecko = CoinGeckoClient()
    except Exception as e:
        log_to_ui(f"Client init error: {str(e)}", "error")
        return

    cg_chain = chain_config.get('coingecko')
    nansen_chain = chain_config.get('nansen')
    token_symbol = None
    coin_id = None

    # ==================== COINGECKO ====================
    log_to_ui("=" * 40, "info")
    log_to_ui("COINGECKO ENDPOINTS", "info")
    log_to_ui("=" * 40, "info")

    # --- Contract-specific (to get coin_id and symbol first) ---
    try:
        coin_info = coingecko.get_coin_info_by_contract(cg_chain, contract_address)
        save_json(coin_info, 'coingecko', chain_name, contract_address, 'coin_info', user_id)
        st.session_state.endpoint_status["coin_info"] = "✅ done"
        token_symbol = coin_info.get('symbol', '').upper()
        coin_id = coin_info.get('id')
        log_to_ui(f"Coin Info: {token_symbol} (ID: {coin_id})", "success")
    except Exception as e:
        log_to_ui(f"Coin Info error: {str(e)[:50]}", "error")
        st.session_state.endpoint_status["coin_info"] = "❌ failed"

    # --- Simple/Price ---
    try:
        if coin_id:
            data = coingecko.get_simple_price([coin_id])
            save_json(data, 'coingecko', chain_name, contract_address, 'simple_price', user_id)
            st.session_state.endpoint_status["simple_price"] = "✅ done"
            log_to_ui("Simple Price fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["simple_price"] = "❌ failed"

    try:
        data = coingecko.get_simple_token_price(cg_chain, contract_address)
        save_json(data, 'coingecko', chain_name, contract_address, 'simple_token_price', user_id)
        st.session_state.endpoint_status["simple_token_price"] = "✅ done"
        log_to_ui("Token Price by Contract fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["simple_token_price"] = "❌ failed"

    # --- Coins ---
    try:
        data = coingecko.get_coins_list()
        save_json(data, 'coingecko', chain_name, contract_address, 'coins_list', user_id)
        st.session_state.endpoint_status["coins_list"] = "✅ done"
        log_to_ui(f"Coins List: {len(data)} coins", "success")
    except Exception as e:
        st.session_state.endpoint_status["coins_list"] = "❌ failed"

    try:
        data = coingecko.get_coins_markets(per_page=100)
        save_json(data, 'coingecko', chain_name, contract_address, 'coins_markets', user_id)
        st.session_state.endpoint_status["coins_markets"] = "✅ done"
        log_to_ui("Coins Markets fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["coins_markets"] = "❌ failed"

    if coin_id:
        try:
            data = coingecko.get_coin_data(coin_id)
            save_json(data, 'coingecko', chain_name, contract_address, 'coin_data', user_id)
            st.session_state.endpoint_status["coin_data"] = "✅ done"
            log_to_ui("Coin Data by ID fetched", "success")
        except Exception as e:
            st.session_state.endpoint_status["coin_data"] = "❌ failed"

        try:
            data = coingecko.get_coin_tickers(coin_id)
            save_json(data, 'coingecko', chain_name, contract_address, 'coin_tickers', user_id)
            st.session_state.endpoint_status["coin_tickers"] = "✅ done"
            log_to_ui("Coin Tickers fetched", "success")
        except Exception as e:
            st.session_state.endpoint_status["coin_tickers"] = "❌ failed"

        try:
            data = coingecko.get_coin_market_chart(coin_id, days=cg_days)
            save_json(data, 'coingecko', chain_name, contract_address, 'coin_market_chart', user_id)
            st.session_state.endpoint_status["coin_market_chart"] = "✅ done"
            log_to_ui("Coin Market Chart fetched", "success")
        except Exception as e:
            st.session_state.endpoint_status["coin_market_chart"] = "❌ failed"

        try:
            data = coingecko.get_coin_ohlc(coin_id, days=30)
            save_json(data, 'coingecko', chain_name, contract_address, 'coin_ohlc', user_id)
            st.session_state.endpoint_status["coin_ohlc"] = "✅ done"
            log_to_ui("Coin OHLC fetched", "success")
        except Exception as e:
            st.session_state.endpoint_status["coin_ohlc"] = "❌ failed"
    else:
        for k in ["coin_data", "coin_tickers", "coin_market_chart", "coin_ohlc"]:
            st.session_state.endpoint_status[k] = "⚠️ skip"

    # --- Chart by Contract ---
    try:
        data = coingecko.get_coin_historical_chart_by_contract(cg_chain, contract_address, days=cg_days)
        save_json(data, 'coingecko', chain_name, contract_address, 'historical_chart', user_id)
        st.session_state.endpoint_status["historical_chart"] = "✅ done"
        log_to_ui("Chart by Contract fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["historical_chart"] = "❌ failed"

    # --- Categories ---
    try:
        data = coingecko.get_categories_list()
        save_json(data, 'coingecko', chain_name, contract_address, 'categories_list', user_id)
        st.session_state.endpoint_status["categories_list"] = "✅ done"
        log_to_ui("Categories List fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["categories_list"] = "❌ failed"

    try:
        data = coingecko.get_categories()
        save_json(data, 'coingecko', chain_name, contract_address, 'categories', user_id)
        st.session_state.endpoint_status["categories"] = "✅ done"
        log_to_ui("Categories fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["categories"] = "❌ failed"

    # --- Exchanges ---
    try:
        data = coingecko.get_exchanges(per_page=50)
        save_json(data, 'coingecko', chain_name, contract_address, 'exchanges', user_id)
        st.session_state.endpoint_status["exchanges"] = "✅ done"
        log_to_ui("Exchanges fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["exchanges"] = "❌ failed"

    try:
        data = coingecko.get_exchanges_list()
        save_json(data, 'coingecko', chain_name, contract_address, 'exchanges_list', user_id)
        st.session_state.endpoint_status["exchanges_list"] = "✅ done"
        log_to_ui("Exchanges List fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["exchanges_list"] = "❌ failed"

    # --- Derivatives ---
    try:
        data = coingecko.get_derivatives()
        save_json(data, 'coingecko', chain_name, contract_address, 'derivatives', user_id)
        st.session_state.endpoint_status["derivatives"] = "✅ done"
        log_to_ui("Derivatives fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["derivatives"] = "❌ failed"

    try:
        data = coingecko.get_derivatives_exchanges()
        save_json(data, 'coingecko', chain_name, contract_address, 'derivatives_exchanges', user_id)
        st.session_state.endpoint_status["derivatives_exchanges"] = "✅ done"
        log_to_ui("Derivatives Exchanges fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["derivatives_exchanges"] = "❌ failed"

    # --- General ---
    try:
        data = coingecko.get_asset_platforms()
        save_json(data, 'coingecko', chain_name, contract_address, 'asset_platforms', user_id)
        st.session_state.endpoint_status["asset_platforms"] = "✅ done"
        log_to_ui("Asset Platforms fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["asset_platforms"] = "❌ failed"

    try:
        data = coingecko.get_exchange_rates()
        save_json(data, 'coingecko', chain_name, contract_address, 'exchange_rates', user_id)
        st.session_state.endpoint_status["exchange_rates"] = "✅ done"
        log_to_ui("Exchange Rates fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["exchange_rates"] = "❌ failed"

    if token_symbol:
        try:
            data = coingecko.search(token_symbol)
            save_json(data, 'coingecko', chain_name, contract_address, 'search', user_id)
            st.session_state.endpoint_status["search"] = "✅ done"
            log_to_ui(f"Search for {token_symbol} done", "success")
        except Exception as e:
            st.session_state.endpoint_status["search"] = "❌ failed"
    else:
        st.session_state.endpoint_status["search"] = "⚠️ skip"

    try:
        data = coingecko.get_trending()
        save_json(data, 'coingecko', chain_name, contract_address, 'trending', user_id)
        st.session_state.endpoint_status["trending"] = "✅ done"
        log_to_ui("Trending fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["trending"] = "❌ failed"

    try:
        data = coingecko.get_global()
        save_json(data, 'coingecko', chain_name, contract_address, 'global', user_id)
        st.session_state.endpoint_status["global"] = "✅ done"
        log_to_ui("Global data fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["global"] = "❌ failed"

    try:
        data = coingecko.get_global_defi()
        save_json(data, 'coingecko', chain_name, contract_address, 'global_defi', user_id)
        st.session_state.endpoint_status["global_defi"] = "✅ done"
        log_to_ui("Global DeFi fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["global_defi"] = "❌ failed"

    # --- Onchain DEX ---
    try:
        data = coingecko.get_onchain_networks()
        save_json(data, 'coingecko', chain_name, contract_address, 'onchain_networks', user_id)
        st.session_state.endpoint_status["onchain_networks"] = "✅ done"
        log_to_ui("Onchain Networks fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["onchain_networks"] = "❌ failed"

    try:
        data = coingecko.get_onchain_token(cg_chain, contract_address)
        save_json(data, 'coingecko', chain_name, contract_address, 'onchain_token', user_id)
        st.session_state.endpoint_status["onchain_token"] = "✅ done"
        log_to_ui("Onchain Token fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["onchain_token"] = "❌ failed"

    try:
        data = coingecko.get_onchain_token_pools(cg_chain, contract_address)
        save_json(data, 'coingecko', chain_name, contract_address, 'onchain_token_pools', user_id)
        st.session_state.endpoint_status["onchain_token_pools"] = "✅ done"
        log_to_ui("Onchain Token Pools fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["onchain_token_pools"] = "❌ failed"

    try:
        data = coingecko.get_onchain_trending_pools()
        save_json(data, 'coingecko', chain_name, contract_address, 'onchain_trending_pools', user_id)
        st.session_state.endpoint_status["onchain_trending_pools"] = "✅ done"
        log_to_ui("Onchain Trending Pools fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["onchain_trending_pools"] = "❌ failed"

    try:
        data = coingecko.get_onchain_new_pools()
        save_json(data, 'coingecko', chain_name, contract_address, 'onchain_new_pools', user_id)
        st.session_state.endpoint_status["onchain_new_pools"] = "✅ done"
        log_to_ui("Onchain New Pools fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["onchain_new_pools"] = "❌ failed"

    # ==================== NANSEN ====================
    log_to_ui("=" * 40, "info")
    log_to_ui("NANSEN ENDPOINTS", "info")
    log_to_ui("=" * 40, "info")

    # --- Smart Money ---
    try:
        data = nansen.get_smart_money_netflow([nansen_chain])
        save_json(data, 'nansen', chain_name, contract_address, 'sm_netflow', user_id)
        st.session_state.endpoint_status["sm_netflow"] = "✅ done"
        log_to_ui("Smart Money Netflow fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["sm_netflow"] = "❌ failed"

    try:
        data = nansen.get_smart_money_holdings([nansen_chain])
        save_json(data, 'nansen', chain_name, contract_address, 'sm_holdings', user_id)
        st.session_state.endpoint_status["sm_holdings"] = "✅ done"
        log_to_ui("Smart Money Holdings fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["sm_holdings"] = "❌ failed"

    try:
        data = nansen.get_smart_money_dex_trades([nansen_chain])
        save_json(data, 'nansen', chain_name, contract_address, 'sm_dex_trades', user_id)
        st.session_state.endpoint_status["sm_dex_trades"] = "✅ done"
        log_to_ui("Smart Money DEX Trades fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["sm_dex_trades"] = "❌ failed"

    # --- Profiler (using contract_address as address) ---
    try:
        data = nansen.get_address_current_balance(contract_address, nansen_chain)
        save_json(data, 'nansen', chain_name, contract_address, 'address_balance', user_id)
        st.session_state.endpoint_status["address_balance"] = "✅ done"
        log_to_ui("Address Balance fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["address_balance"] = "❌ failed"

    try:
        data = nansen.get_address_transactions(contract_address, nansen_chain)
        save_json(data, 'nansen', chain_name, contract_address, 'address_transactions', user_id)
        st.session_state.endpoint_status["address_transactions"] = "✅ done"
        log_to_ui("Address Transactions fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["address_transactions"] = "❌ failed"

    try:
        data = nansen.get_address_related_wallets(contract_address, nansen_chain)
        save_json(data, 'nansen', chain_name, contract_address, 'address_related_wallets', user_id)
        st.session_state.endpoint_status["address_related_wallets"] = "✅ done"
        log_to_ui("Address Related Wallets fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["address_related_wallets"] = "❌ failed"

    try:
        data = nansen.get_address_counterparties(contract_address, nansen_chain)
        save_json(data, 'nansen', chain_name, contract_address, 'address_counterparties', user_id)
        st.session_state.endpoint_status["address_counterparties"] = "✅ done"
        log_to_ui("Address Counterparties fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["address_counterparties"] = "❌ failed"

    try:
        data = nansen.get_address_pnl(contract_address, nansen_chain)
        save_json(data, 'nansen', chain_name, contract_address, 'address_pnl', user_id)
        st.session_state.endpoint_status["address_pnl"] = "✅ done"
        log_to_ui("Address PnL fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["address_pnl"] = "❌ failed"

    # --- TGM Token ---
    try:
        data = nansen.get_token_screener([nansen_chain])
        save_json(data, 'nansen', chain_name, contract_address, 'token_screener', user_id)
        st.session_state.endpoint_status["token_screener"] = "✅ done"
        log_to_ui("Token Screener fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["token_screener"] = "❌ failed"

    try:
        data = nansen.get_token_flows(contract_address, nansen_chain)
        save_json(data, 'nansen', chain_name, contract_address, 'token_flows', user_id)
        st.session_state.endpoint_status["token_flows"] = "✅ done"
        log_to_ui("Token Flows fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["token_flows"] = "❌ failed"

    try:
        data = nansen.get_token_flow_intelligence(contract_address, nansen_chain)
        save_json(data, 'nansen', chain_name, contract_address, 'flow_intelligence', user_id)
        st.session_state.endpoint_status["flow_intelligence"] = "✅ done"
        log_to_ui("Flow Intelligence fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["flow_intelligence"] = "❌ failed"

    try:
        data = nansen.get_token_who_bought_sold(contract_address, nansen_chain, start_date_str, end_date_str)
        save_json(data, 'nansen', chain_name, contract_address, 'who_bought_sold', user_id)
        st.session_state.endpoint_status["who_bought_sold"] = "✅ done"
        log_to_ui("Who Bought/Sold fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["who_bought_sold"] = "❌ failed"

    try:
        data = nansen.get_token_dex_trades(contract_address, nansen_chain)
        save_json(data, 'nansen', chain_name, contract_address, 'token_dex_trades', user_id)
        st.session_state.endpoint_status["token_dex_trades"] = "✅ done"
        log_to_ui("Token DEX Trades fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["token_dex_trades"] = "❌ failed"

    try:
        data = nansen.get_token_transfers(contract_address, nansen_chain, start_date_str, end_date_str)
        save_json(data, 'nansen', chain_name, contract_address, 'transfers', user_id)
        st.session_state.endpoint_status["transfers"] = "✅ done"
        log_to_ui("Token Transfers fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["transfers"] = "❌ failed"

    try:
        data = nansen.get_token_holders(contract_address, nansen_chain)
        save_json(data, 'nansen', chain_name, contract_address, 'holders', user_id)
        st.session_state.endpoint_status["holders"] = "✅ done"
        log_to_ui("Token Holders fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["holders"] = "❌ failed"

    try:
        data = nansen.get_token_pnl_leaderboard(contract_address, nansen_chain)
        save_json(data, 'nansen', chain_name, contract_address, 'token_pnl_leaderboard', user_id)
        st.session_state.endpoint_status["token_pnl_leaderboard"] = "✅ done"
        log_to_ui("Token PnL Leaderboard fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["token_pnl_leaderboard"] = "❌ failed"

    # --- TGM Perp ---
    try:
        data = nansen.get_perp_screener()
        save_json(data, 'nansen', chain_name, contract_address, 'perp_screener', user_id)
        st.session_state.endpoint_status["perp_screener"] = "✅ done"
        log_to_ui("Perp Screener fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["perp_screener"] = "❌ failed"

    if token_symbol:
        try:
            data = nansen.get_token_perp_trades(token_symbol, start_date_str, end_date_str)
            save_json(data, 'nansen', chain_name, contract_address, 'perp_trades', user_id)
            st.session_state.endpoint_status["perp_trades"] = "✅ done"
            log_to_ui(f"Perp Trades for {token_symbol} fetched", "success")
        except Exception as e:
            st.session_state.endpoint_status["perp_trades"] = "❌ failed"

        try:
            data = nansen.get_token_perp_positions(token_symbol)
            save_json(data, 'nansen', chain_name, contract_address, 'perp_positions', user_id)
            st.session_state.endpoint_status["perp_positions"] = "✅ done"
            log_to_ui(f"Perp Positions for {token_symbol} fetched", "success")
        except Exception as e:
            st.session_state.endpoint_status["perp_positions"] = "❌ failed"
    else:
        st.session_state.endpoint_status["perp_trades"] = "⚠️ skip"
        st.session_state.endpoint_status["perp_positions"] = "⚠️ skip"

    try:
        data = nansen.get_perp_pnl_leaderboard()
        save_json(data, 'nansen', chain_name, contract_address, 'perp_pnl_leaderboard', user_id)
        st.session_state.endpoint_status["perp_pnl_leaderboard"] = "✅ done"
        log_to_ui("Perp PnL Leaderboard fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["perp_pnl_leaderboard"] = "❌ failed"

    # --- Portfolio ---
    try:
        data = nansen.get_defi_holdings([contract_address], [nansen_chain])
        save_json(data, 'nansen', chain_name, contract_address, 'defi_holdings', user_id)
        st.session_state.endpoint_status["defi_holdings"] = "✅ done"
        log_to_ui("DeFi Holdings fetched", "success")
    except Exception as e:
        st.session_state.endpoint_status["defi_holdings"] = "❌ failed"

    # ==================== DONE ====================
    log_to_ui("=" * 40, "info")
    total = len(ENDPOINT_MAPPING)
    done = sum(1 for v in st.session_state.endpoint_status.values() if "done" in v)
    log_to_ui(f"COMPLETED: {done}/{total} endpoints", "success")
    st.session_state.fetched_data['last_updated'] = datetime.now()


# Main UI
st.title("Token Tracker Metrics")

# Tabs
tab1, tab2, tab3 = st.tabs(["Tracking log/Enpoints", "Token Tracker", "Social Listening"])

with tab1:
    st.header("Market Data Analysis")
    
    # Input section
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        chain = st.selectbox(
            "Chain",
            list(SUPPORTED_CHAINS.keys()),
            index=1  # Default to Solana
        )
    
    with col2:
        period = st.selectbox(
            "Period",
            ["3 months", "6 months", "1 year", "All"],
            index=0
        )

    with col3:
        contract_address = st.text_input(
            "Contract Address",
            placeholder="0x... or So11111111111111111111111111111111111111112",
            value="So11111111111111111111111111111111111111112"  # Example Solana address
        )
    
    # Fetch Button
    fetch_button = st.button("Fetch", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    # Check Phase State
    has_data = 'last_updated' in st.session_state.fetched_data

    # PHASE 2: Fetching in progress (Transient State)
    if fetch_button:
        if not validate_contract_address(contract_address, chain):
            st.error(f"Invalid contract address format for {chain}")
        else:
            # Render Log Monitoring (Live)
            st.subheader("📋 Log Monitoring")
            log_placeholder = st.empty()
            
            with st.spinner("Fetching data from multiple sources..."):
                fetch_all_data(chain, contract_address, period, log_placeholder, current_user)
            
            # Transition to Phase 3 on next rerun
            st.rerun()

    # PHASE 3: Data Available (Post-Fetch)
    elif has_data:
        # Layout: Table (Left, 40%) and Panel (Right, 60%)
        left_status, right_panel = st.columns([2, 3])
        
        with left_status:
            # Endpoints Status Section
            st.subheader("Endpoints Fetching Status")
            
            endpoints = get_endpoint_list()
            
            # Header
            c1, c2, c3, c4 = st.columns([1, 0.5, 0.5, 1])
            c1.markdown("**Endpoint**")
            c2.markdown("**Source**")
            c3.markdown("**Status**")
            c4.markdown("**Action**")
            st.markdown('<hr style="margin: 0.1em 0; border-color: #333;">', unsafe_allow_html=True)

            for ep in endpoints:
                # Use vertical alignment center if available in future streamlit versions, otherwise rely on CSS
                c1, c2, c3, c4 = st.columns([1, 0.5, 0.5, 1])
                
                # Endpoint Name
                c1.markdown(f"<div style='padding-top: 5px; font-size: 14px;'>{ep['Endpoint']}</div>", unsafe_allow_html=True)
                
                # Source Icon
                source_name = ep["Source"]
                icon_file = SOURCE_ICONS.get(source_name)
                if icon_file:
                    icon_path_full = Path(__file__).parent / "assets" / icon_file
                    if icon_path_full.exists():
                        c2.image(str(icon_path_full), width=30)
                    else:
                        c2.markdown(f"<div style='padding-top: 5px; font-size: 12px;'>{source_name}</div>", unsafe_allow_html=True)
                else:
                    c2.markdown(f"<div style='padding-top: 5px; font-size: 12px;'>{source_name}</div>", unsafe_allow_html=True)
                
                # Status
                c3.markdown(f"<div style='padding-top: 5px; font-size: 14px;'>{ep['Fetch Success']}</div>", unsafe_allow_html=True)
                
                # Preview Button (Green Text Label)
                if c4.button(":green[preview]", key=f"btn_{ep['Endpoint']}", use_container_width=True):
                    st.session_state.preview_endpoint = ep["Endpoint"]
                
                # Row Divider - Reduced margin
                st.markdown('<hr style="margin: 0px 0; border-color: #333;">', unsafe_allow_html=True)
            
        with right_panel:
            # Log Monitoring Section (Summary)
            st.subheader("📋 Log Monitoring")
            
            # Use <br> for explicit newlines in HTML
            log_content = "<br>".join(st.session_state.logs)
            bg_color = "#0c0c0c" if theme == "Dark" else "#f0f2f6"
            text_color = "#00ff00" if theme == "Dark" else "#006400"
            
            st.markdown(f"""
                <div style="background-color: {bg_color}; color: {text_color}; font-family: monospace; padding: 15px; height: 300px; overflow-y: scroll; border: 1px solid #333; border-radius: 5px; font-size: 11px; line-height: 1.4;">
                    {log_content}
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Preview Area (Moved here)
            if st.session_state.preview_endpoint:
                 endpoint_name = st.session_state.preview_endpoint
                 if endpoint_name in ENDPOINT_MAPPING:
                    source, key = ENDPOINT_MAPPING[endpoint_name]
                    st.subheader(f"Preview: {endpoint_name}")
                    
                    data = load_latest_json(source, chain, contract_address, key, current_user)
                    if data:
                        # Extract "data" list if exists (common API pattern)
                        if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                             st.dataframe(data["data"], use_container_width=True)
                        # CoinGecko Chart
                        elif isinstance(data, dict) and "prices" in data and isinstance(data["prices"], list):
                             df = pd.DataFrame(data["prices"], columns=["Timestamp", "Price"])
                             df["Date"] = pd.to_datetime(df["Timestamp"], unit='ms')
                             st.dataframe(df[["Date", "Price"]], use_container_width=True)
                        elif isinstance(data, list):
                             st.dataframe(data, use_container_width=True)
                        else:
                             st.json(data)
                    else:
                        st.warning("No data found to preview.")
                    
                    # Button to close preview
                    if st.button("Close Preview"):
                        st.session_state.preview_endpoint = None
                        st.rerun()
        
    # PHASE 1: Initial State (Empty)
    else:
        st.info("Select chain and contract, then click Fetch to start analysis.")


with tab2:
    st.header("Token Tracker")
    
    if 'last_updated' in st.session_state.fetched_data:
        # Load Data
        coin_info = load_latest_json('coingecko', chain, contract_address, 'coin_info', current_user)
        dune_data = load_latest_json('dune', chain, contract_address, 'delta_balance', current_user)
        flow_data = load_latest_json('nansen', chain, contract_address, 'flow_intelligence', current_user)
        holders_data = load_latest_json('nansen', chain, contract_address, 'holders', current_user)
        transfers_data = load_latest_json('nansen', chain, contract_address, 'transfers', current_user)
        
        # 1. Token Summary
        if coin_info:
            c1, c2 = st.columns([1, 4])
            with c1:
                img_url = coin_info.get('image', {}).get('large')
                if img_url:
                    st.image(img_url, width=100)
            with c2:
                st.subheader(f"{coin_info.get('name')} ({coin_info.get('symbol').upper()})")
                md = coin_info.get('market_data', {})
                m1, m2, m3 = st.columns(3)
                m1.metric("Price", f"${md.get('current_price', {}).get('usd', 0)}")
                m2.metric("Market Cap", f"${md.get('market_cap', {}).get('usd', 0):,}")
                m3.metric("Volume (24h)", f"${md.get('total_volume', {}).get('usd', 0):,}")
        
        st.markdown("---")
        
        # 2. Delta Balance Change
        st.subheader("Delta Balance Change (Dune)")
        if dune_data:
            fig_dune = create_delta_balance_chart(dune_data)
            st.plotly_chart(fig_dune, use_container_width=True)
        else:
            st.info("No Dune data available")
            
        st.markdown("---")
        
        # 3. Token Flow Intelligence
        st.subheader("Token Flow Intelligence (Nansen)")
        if flow_data:
            net_df, avg_df, wallet_df = create_flow_intelligence_table(flow_data)
            if net_df is not None:
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown("**Net Flow (USD)**")
                    st.dataframe(net_df, use_container_width=True)
                with c2:
                    st.markdown("**Avg Flow (USD)**")
                    st.dataframe(avg_df, use_container_width=True)
                with c3:
                    st.markdown("**Wallet Count**")
                    st.dataframe(wallet_df, use_container_width=True)
            else:
                st.warning("Flow Intelligence data format invalid. Please fetch again.")
        else:
            st.info("No Flow Intelligence data available")

        st.markdown("---")

        # 4. Token Holders
        st.subheader("Token Holders (Nansen)")
        if holders_data:
            fig_holders = create_holders_bar_chart(holders_data)
            if fig_holders:
                st.plotly_chart(fig_holders, use_container_width=True)
            else:
                st.info("No Holders data available (invalid format)")
        else:
            st.info("No Holders data available")
            
        st.markdown("---")

        # 5. Last Token Transfer
        st.subheader("Last Token Transfer (Nansen)")
        if transfers_data:
            transfers_df = create_transfers_table(transfers_data)
            if not transfers_df.empty:
                st.dataframe(transfers_df, use_container_width=True)
            else:
                st.info("No Transfers data available (invalid format)")
        else:
            st.info("No Transfers data available")

    else:
        st.info("Fetch data in 'Tracking log/Enpoints' tab to see visualizations.")

with tab3:
    st.header("Social Listening")
    st.info("Social listening features coming soon...")
