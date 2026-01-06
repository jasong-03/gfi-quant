"""
Token Tracker Metrics Dashboard
Main Streamlit Application
"""

import streamlit as st

from config import SUPPORTED_CHAINS
from components import (
    cdc_tracker, tracking_log, token_tracker,
    profiler, dune_export, social_listening
)
from services import fetch_all_data

# Page configuration
st.set_page_config(
    page_title="Token Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")

    # User Input (for BigQuery dataset naming)
    current_user = st.text_input("What is token name", placeholder="Enter token name...", value="")
    if current_user:
        st.session_state.current_user = current_user
    else:
        st.session_state.current_user = "anonymous"

# Default theme
theme = "Dark"

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

# CDC Tracker Session State
cdc_tracker.init_session_state()


# Main UI
st.title("Token Tracker Metrics")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Tracking log/Enpoints", "Token Tracker", "Profiler",
    "Dune Export", "Social Listening", "CDC tracker"
])

# Store chain/contract from tab1 for use in tab2
chain = "Solana"
contract_address = ""

with tab1:
    chain, contract_address = tracking_log.render_tab(
        fetch_callback=fetch_all_data,
        current_user=current_user,
        theme=theme
    )

with tab2:
    token_tracker.render_tab(chain, contract_address, current_user)

with tab3:
    profiler.render_tab(current_user)

with tab4:
    dune_export.render_tab(current_user)

with tab5:
    social_listening.render_tab()

with tab6:
    cdc_tracker.render_tab()
