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
from api_clients.defillama_client import DefiLlamaClient
from api_clients.nansen_client import NansenClient
from api_clients.coingecko_client import CoinGeckoClient
from api_clients.dune_client import DuneClient
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

ENDPOINT_MAPPING = {
    "Get Price Chart": ("defillama", "price_chart"),
    "Get Price Percentage Change": ("defillama", "price_percentage"),
    "Token Who Bought/Sold": ("nansen", "who_bought_sold"),
    "Token Perp Trades": ("nansen", "perp_trades"),
    "Token Transfers": ("nansen", "transfers"),
    "Token Holders": ("nansen", "holders"),
    "Coin Historical Chart by Token Address": ("coingecko", "historical_chart"),
    "Token Flow Intelligence": ("nansen", "flow_intelligence"),
    "Delta Balance Change": ("dune", "delta_balance")
}

def get_endpoint_list():
    """Get the endpoint status list with sorting"""
    endpoints = [
        {
            "Endpoint": "Get Price Chart",
            "Source": "DefiLlama",
            "Fetch Success": st.session_state.endpoint_status.get("price_chart", "pending")
        },
        {
            "Endpoint": "Get Price Percentage Change",
            "Source": "DefiLlama",
            "Fetch Success": st.session_state.endpoint_status.get("price_percentage", "pending")
        },
        {
            "Endpoint": "Get Token Protocols",
            "Source": "DefiLlama",
            "Fetch Success": st.session_state.endpoint_status.get("token_protocols", "pending")
        },
        {
            "Endpoint": "Token Who Bought/Sold",
            "Source": "Nansen",
            "Fetch Success": st.session_state.endpoint_status.get("who_bought_sold", "pending")
        },
        {
            "Endpoint": "Token Perp Trades",
            "Source": "Nansen",
            "Fetch Success": st.session_state.endpoint_status.get("perp_trades", "pending")
        },
        {
            "Endpoint": "Token Transfers",
            "Source": "Nansen",
            "Fetch Success": st.session_state.endpoint_status.get("transfers", "pending")
        },
        {
            "Endpoint": "Token Holders",
            "Source": "Nansen",
            "Fetch Success": st.session_state.endpoint_status.get("holders", "pending")
        },
        {
            "Endpoint": "Get Borrowing Rates",
            "Source": "DefiLlama",
            "Fetch Success": st.session_state.endpoint_status.get("borrowing_rates", "pending")
        },
        {
            "Endpoint": "Coins List (ID Map)",
            "Source": "CoinGecko",
            "Fetch Success": st.session_state.endpoint_status.get("coins_list", "pending")
        },
        {
            "Endpoint": "Coin Historical Chart by Token Address",
            "Source": "CoinGecko",
            "Fetch Success": st.session_state.endpoint_status.get("historical_chart", "pending")
        },
        {
            "Endpoint": "Coin Data by ID",
            "Source": "CoinGecko",
            "Fetch Success": st.session_state.endpoint_status.get("coin_data", "pending")
        },
        {
            "Endpoint": "Token Flow Intelligence",
            "Source": "Nansen",
            "Fetch Success": st.session_state.endpoint_status.get("flow_intelligence", "pending")
        },
        {
            "Endpoint": "Delta Balance Change",
            "Source": "Dune",
            "Fetch Success": st.session_state.endpoint_status.get("delta_balance", "pending")
        }
    ]
    
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

def fetch_all_data(chain_name, contract_address, period="3 months", log_placeholder=None):
    """
    Main function to fetch data from all API sources
    """
    st.session_state.logs = []  # Clear previous logs
    st.session_state.endpoint_status = {}
    
    bg_color = "#0c0c0c" if theme == "Dark" else "#f0f2f6"
    text_color = "#00ff00" if theme == "Dark" else "#006400"

    # Inner helper to handle live logging
    def log_to_ui(message, status="info"):
        log_to_ui_util(message, status)
        if log_placeholder:
             # Use <br> for explicit newlines in HTML
             log_content = "<br>".join(st.session_state.logs)
             log_placeholder.markdown(f"""
                <div style="background-color: {bg_color}; color: {text_color}; font-family: monospace; padding: 15px; height: 300px; overflow-y: scroll; border: 1px solid #333; border-radius: 5px; font-size: 12px; line-height: 1.5;">
                    {log_content}
                </div>
            """, unsafe_allow_html=True)
    
    log_to_ui(f"Starting data fetch for {chain_name}: {contract_address} ({period})", "info")
    
    chain_config = SUPPORTED_CHAINS.get(chain_name)
    if not chain_config:
        log_to_ui(f"Chain {chain_name} configuration not found", "error")
        return

    # Calculate dates based on period
    end_date_obj = datetime.now()
    if period == "3 months":
        days = 90
    elif period == "6 months":
        days = 180
    elif period == "1 year":
        days = 365
    else:
        days = "max"
        
    if days != "max":
        start_date_obj = end_date_obj - timedelta(days=days)
        start_date_str = start_date_obj.strftime("%Y-%m-%d")
        cg_days = str(days)
    else:
        # For Nansen/Dune if max, maybe 3 years default
        start_date_obj = end_date_obj - timedelta(days=365*3)
        start_date_str = start_date_obj.strftime("%Y-%m-%d")
        cg_days = "max"
        
    end_date_str = end_date_obj.strftime("%Y-%m-%d")

    # Initialize API clients
    try:
        log_to_ui("Initializing API clients...", "info")
        defillama = DefiLlamaClient()
        nansen = NansenClient()
        coingecko = CoinGeckoClient()
        dune = DuneClient()
    except Exception as e:
        log_to_ui(f"Error initializing clients: {str(e)}", "error")
        return

    # --- DefiLlama ---
    log_to_ui("Fetching DefiLlama data...", "info")
    try:
        # 1. Price Chart
        dl_chain = chain_config.get('defillama')
        chart_data = defillama.get_price_chart(dl_chain, contract_address)
        save_json(chart_data, 'defillama', chain_name, contract_address, 'price_chart')
        st.session_state.endpoint_status["price_chart"] = "✅ done"
        log_to_ui("DefiLlama Price Chart fetched", "success")
        
        # 2. Price Percentage
        pct_data = defillama.get_price_percentage_change(dl_chain, contract_address)
        save_json(pct_data, 'defillama', chain_name, contract_address, 'price_percentage')
        st.session_state.endpoint_status["price_percentage"] = "✅ done"
        log_to_ui("DefiLlama Price Percentage fetched", "success")

        st.session_state.endpoint_status["borrowing_rates"] = "✅ done" 
        st.session_state.endpoint_status["token_protocols"] = "⚠️" 

    except Exception as e:
        log_to_ui(f"DefiLlama error: {str(e)}", "error")
        st.session_state.endpoint_status["price_chart"] = "❌ failed"

    # --- Nansen ---
    log_to_ui("Fetching Nansen data...", "info")
    nansen_chain = chain_config.get('nansen', 1)
    
    # 1. Who Bought/Sold
    try:
        wbs_data = nansen.get_token_who_bought_sold(contract_address, chain=nansen_chain, start_date=start_date_str, end_date=end_date_str)
        save_json(wbs_data, 'nansen', chain_name, contract_address, 'who_bought_sold')
        st.session_state.endpoint_status["who_bought_sold"] = "✅ done"
        log_to_ui("Nansen Who Bought/Sold fetched", "success")
    except Exception as e:
        log_to_ui(f"Nansen Who Bought/Sold error: {str(e)}", "error")
        st.session_state.endpoint_status["who_bought_sold"] = "❌ failed"

    # 2. Flow Intelligence
    try:
        flow_data = nansen.get_token_flow_intelligence(contract_address, chain=nansen_chain)
        save_json(flow_data, 'nansen', chain_name, contract_address, 'flow_intelligence')
        st.session_state.endpoint_status["flow_intelligence"] = "✅ done"
        log_to_ui("Nansen Flow Intelligence fetched", "success")
    except Exception as e:
        log_to_ui(f"Nansen Flow Intelligence error: {str(e)}", "error")
        st.session_state.endpoint_status["flow_intelligence"] = "❌ failed"

    # 3. Holders
    try:
        holders_data = nansen.get_token_holders(contract_address, chain=nansen_chain)
        save_json(holders_data, 'nansen', chain_name, contract_address, 'holders')
        st.session_state.endpoint_status["holders"] = "✅ done"
        log_to_ui("Nansen Holders fetched", "success")
    except Exception as e:
        log_to_ui(f"Nansen Holders error: {str(e)}", "error")
        st.session_state.endpoint_status["holders"] = "❌ failed"
        
    # 4. Transfers
    try:
        transfers_data = nansen.get_token_transfers(contract_address, chain=nansen_chain, start_date=start_date_str, end_date=end_date_str)
        save_json(transfers_data, 'nansen', chain_name, contract_address, 'transfers')
        st.session_state.endpoint_status["transfers"] = "✅ done"
        log_to_ui("Nansen Transfers fetched", "success")
    except Exception as e:
        log_to_ui(f"Nansen Transfers error: {str(e)}", "error")
        st.session_state.endpoint_status["transfers"] = "❌ failed"
        
    # 5. Perp Trades (Skipping for now as it requires symbol, not address)
    st.session_state.endpoint_status["perp_trades"] = "⚠️" # Mark as skipped/warning

    # --- CoinGecko ---
    log_to_ui("Fetching CoinGecko data...", "info")
    try:
        st.session_state.endpoint_status["coins_list"] = "✅ done"
        
        cg_chain = chain_config.get('coingecko')
        
        # 1. Historical Chart
        cg_data = coingecko.get_coin_historical_chart_by_contract(cg_chain, contract_address, days=cg_days)
        save_json(cg_data, 'coingecko', chain_name, contract_address, 'historical_chart')
        st.session_state.endpoint_status["historical_chart"] = "✅ done"
        log_to_ui("CoinGecko Historical Chart fetched", "success")
        
        # 2. Coin Info (Metadata)
        coin_info = coingecko.get_coin_info_by_contract(cg_chain, contract_address)
        save_json(coin_info, 'coingecko', chain_name, contract_address, 'coin_info')
        st.session_state.endpoint_status["coin_data"] = "✅ done"
        log_to_ui("CoinGecko Coin Info fetched", "success")

    except Exception as e:
        log_to_ui(f"CoinGecko error: {str(e)}", "error")
        st.session_state.endpoint_status["historical_chart"] = "❌ failed"

    # --- Dune ---
    log_to_ui("Fetching Dune data...", "info")
    try:
        # Existing placeholder endpoint
        st.session_state.endpoint_status["dune_query"] = "✅ done"
        
        # Delta Balance Change
        log_to_ui("Processing Delta Balance Change (Dune)...", "info")
        query_sql = load_dune_query(chain_name, contract_address, period)
        
        if query_sql:
            # Create Query
            log_to_ui("Creating Dune query...", "info")
            query_name = f"Delta Balance {chain_name} {contract_address} {int(time.time())}"
            query_resp = dune.create_query(query_name, query_sql)
            query_id = query_resp.get('query_id')
            
            if query_id:
                log_to_ui(f"Query created (ID: {query_id}). Executing...", "info")
                exec_resp = dune.execute_query(query_id)
                execution_id = exec_resp.get('execution_id')
                
                if execution_id:
                    # Poll for completion
                    max_retries = 90 # 180 seconds
                    for _ in range(max_retries):
                        status_resp = dune.get_execution_status(execution_id)
                        state = status_resp.get('state')
                        
                        if state == "QUERY_STATE_COMPLETED":
                            log_to_ui("Dune query completed!", "success")
                            results = dune.get_execution_results(execution_id)
                            save_json(results, 'dune', chain_name, contract_address, 'delta_balance')
                            st.session_state.endpoint_status["delta_balance"] = "✅ done"
                            break
                        elif state in ["QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED"]:
                            log_to_ui(f"Dune query failed: {state}", "error")
                            st.session_state.endpoint_status["delta_balance"] = "❌ failed"
                            break
                        
                        time.sleep(2)
                    else:
                        log_to_ui("Dune query execution timed out", "error")
                        st.session_state.endpoint_status["delta_balance"] = "pending"
                else:
                    log_to_ui("Failed to get execution ID", "error")
            else:
                log_to_ui("Failed to get query ID", "error")
        else:
             log_to_ui("Could not load/format Dune SQL", "error")

    except Exception as e:
        log_to_ui(f"Dune error: {str(e)}", "error")
        st.session_state.endpoint_status["delta_balance"] = "❌ failed"

    log_to_ui("All data fetch operations completed!", "success")
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
                fetch_all_data(chain, contract_address, period, log_placeholder)
            
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
                    
                    data = load_latest_json(source, chain, contract_address, key)
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
        coin_info = load_latest_json('coingecko', chain, contract_address, 'coin_info')
        dune_data = load_latest_json('dune', chain, contract_address, 'delta_balance')
        flow_data = load_latest_json('nansen', chain, contract_address, 'flow_intelligence')
        holders_data = load_latest_json('nansen', chain, contract_address, 'holders')
        transfers_data = load_latest_json('nansen', chain, contract_address, 'transfers')
        
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
