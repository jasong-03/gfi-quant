# Code Standards and Conventions

This document defines the coding standards, naming conventions, and patterns used throughout the GFI Quant Token Tracker Dashboard project. All contributors should follow these guidelines to maintain consistency.

---

## Table of Contents

1. [Python Style Guide](#1-python-style-guide)
2. [Naming Conventions](#2-naming-conventions)
3. [Project Structure Patterns](#3-project-structure-patterns)
4. [API Client Pattern](#4-api-client-pattern)
5. [Error Handling](#5-error-handling)
6. [Data Storage Conventions](#6-data-storage-conventions)
7. [Logging Standards](#7-logging-standards)
8. [Configuration Management](#8-configuration-management)
9. [Documentation Standards](#9-documentation-standards)
10. [Streamlit UI Patterns](#10-streamlit-ui-patterns)

---

## 1. Python Style Guide

### General Rules

This project follows **PEP 8** with the following specifics:

| Rule | Standard |
|------|----------|
| Indentation | 4 spaces (no tabs) |
| Line length | 100 characters max (120 for URLs/strings) |
| Blank lines | 2 between top-level definitions, 1 within classes |
| Imports | Grouped: stdlib, third-party, local |
| Quotes | Single quotes for strings, double for docstrings |

### Import Organization

```python
# Standard library imports
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

# Third-party imports
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# Local imports
from config import API_KEYS, SUPPORTED_CHAINS
from api_clients.nansen_client import NansenClient
from utils.logger import log_to_ui
```

### Type Hints

Use type hints for function signatures:

```python
def validate_contract_address(address: str, chain: str) -> bool:
    """Validate contract address format based on chain."""
    ...

def save_json(
    data: dict,
    source: str,
    chain: str,
    address: str,
    endpoint_name: str
) -> str:
    """Save raw API response to JSON file."""
    ...
```

---

## 2. Naming Conventions

### Files and Modules

| Type | Convention | Example |
|------|------------|---------|
| Modules | `snake_case.py` | `nansen_client.py` |
| Test files | `test_{module}.py` | `test_api_endpoints.py` |
| Config files | `snake_case.py` | `config_template.py` |
| Documentation | `kebab-case.md` | `api-endpoints-nansen.md` |

### Classes

| Type | Convention | Example |
|------|------------|---------|
| API Clients | `{Provider}Client` | `DuneClient`, `NansenClient` |
| Exceptions | `{Description}Error` | `ValidationError` |
| Data Models | `PascalCase` | `TokenMetadata` |

### Functions and Methods

| Type | Convention | Example |
|------|------------|---------|
| Public functions | `snake_case` | `create_price_chart()` |
| Private functions | `_snake_case` | `_make_request()` |
| Helper functions | `{action}_{noun}` | `load_latest_json()` |

### Variables

| Type | Convention | Example |
|------|------------|---------|
| Constants | `UPPER_SNAKE_CASE` | `API_KEYS`, `BASE_DIR` |
| Local variables | `snake_case` | `contract_address`, `chain_config` |
| Boolean variables | `is_`, `has_`, `can_` prefix | `is_valid`, `has_data` |

### API and Data Keys

| Type | Convention | Example |
|------|------------|---------|
| Endpoint names | `snake_case` | `price_chart`, `who_bought_sold` |
| JSON keys | `snake_case` | `token_address`, `block_timestamp` |
| Session state | `snake_case` | `fetched_data`, `endpoint_status` |

---

## 3. Project Structure Patterns

### Module Organization

```
project/
├── Core Application
│   ├── app.py              # Entry point, UI logic
│   └── config.py           # Configuration
│
├── API Layer
│   └── api_clients/        # One file per provider
│       ├── __init__.py
│       └── {provider}_client.py
│
├── Data Layer
│   └── data_handlers/      # Storage and processing
│       ├── storage.py      # Persistence
│       └── processors.py   # Transformations
│
├── Utility Layer
│   └── utils/              # Cross-cutting concerns
│       ├── logger.py       # Logging
│       └── validators.py   # Validation
│
└── Presentation Layer
    └── visualizations/     # Charts and tables
        ├── charts.py
        └── tables.py
```

### Separation of Concerns

| Layer | Responsibility | Dependencies |
|-------|---------------|--------------|
| API Clients | HTTP requests, response parsing | `config`, `requests` |
| Data Handlers | Persistence, transformation | `config`, `pathlib` |
| Utilities | Validation, logging | `streamlit` (optional) |
| Visualizations | Chart creation | `plotly`, `pandas` |
| Application | Orchestration, UI | All layers |

---

## 4. API Client Pattern

### Standard Client Structure

```python
import requests
from config import API_URLS, API_KEYS

class ProviderClient:
    """API client for Provider service."""

    def __init__(self, api_key: str = None):
        """Initialize client with optional API key override."""
        self.api_key = api_key or API_KEYS.get('PROVIDER_API_KEY')
        self.base_url = API_URLS['PROVIDER']
        self.last_headers = {}  # Store response headers

    def _get_headers(self) -> dict:
        """Build request headers with authentication."""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        json_data: dict = None
    ) -> dict:
        """Execute HTTP request with error handling."""
        url = f"{self.base_url}{endpoint}"
        response = requests.request(
            method,
            url,
            headers=self._get_headers(),
            params=params,
            json=json_data
        )
        self.last_headers = response.headers
        response.raise_for_status()
        return response.json()

    def get_resource(self, resource_id: str) -> dict:
        """
        Get a specific resource.

        Args:
            resource_id: Unique resource identifier

        Returns:
            Resource data dictionary
        """
        return self._make_request('GET', f'/resource/{resource_id}')
```

### Authentication Patterns

| Provider | Header Name | Format |
|----------|-------------|--------|
| Dune | `X-Dune-API-Key` | Plain key |
| Nansen | `apiKey` | Plain key |
| CoinGecko | `x-cg-pro-api-key` | Plain key |
| DefiLlama | URL path or query | Key in URL |

---

## 5. Error Handling

### Exception Handling Pattern

```python
def fetch_data(address: str, chain: str) -> dict:
    """Fetch data with proper error handling."""
    try:
        # Primary operation
        result = client.get_data(address, chain)
        log_to_ui(f"Data fetched for {address}", "success")
        return result

    except requests.exceptions.HTTPError as e:
        # API-specific errors (4xx, 5xx)
        log_to_ui(f"API error: {e.response.status_code}", "error")
        raise

    except requests.exceptions.ConnectionError:
        # Network errors
        log_to_ui("Network connection failed", "error")
        raise

    except requests.exceptions.Timeout:
        # Timeout errors
        log_to_ui("Request timed out", "error")
        raise

    except Exception as e:
        # Unexpected errors
        log_to_ui(f"Unexpected error: {str(e)}", "error")
        raise
```

### Error Status Codes

| Status | Meaning | User Action |
|--------|---------|-------------|
| `checkmark done` | Success | None |
| `X failed` | API error | Check logs, retry |
| `warning` | Partial/skipped | Review data availability |
| `pending` | Not attempted | Wait or retry |

### Graceful Degradation

```python
# Handle missing data gracefully
if holders_data:
    fig = create_holders_bar_chart(holders_data)
    if fig:
        st.plotly_chart(fig)
    else:
        st.info("Holder data format invalid")
else:
    st.info("No holder data available")
```

---

## 6. Data Storage Conventions

### File Naming Pattern

```
{endpoint_name}_{YYYYMMDD}_{HHMMSS}.json
```

Examples:
- `holders_20241226_143022.json`
- `price_chart_20241226_143025.json`

### Directory Structure

```
data/
└── {source}/           # API provider (lowercase)
    └── {chain}/        # Chain name (as-is from config)
        └── {address}/  # Contract address (as-is)
            └── {files}
```

### JSON Structure

All saved files maintain the original API response structure:

```json
{
    "data": [...],
    "pagination": {...},
    "metadata": {...}
}
```

---

## 7. Logging Standards

### Log Message Format

```
{icon} [{HH:MM:SS}] {message}
```

Examples:
- `hourglass [14:30:22] Starting data fetch for Ethereum: 0xA0b8...`
- `checkmark [14:30:25] Nansen Holders fetched`
- `X [14:30:28] DefiLlama error: Rate limit exceeded`

### Log Levels

| Level | Icon | Use Case |
|-------|------|----------|
| `info` | hourglass | Progress updates, starting operations |
| `success` | checkmark | Completed operations |
| `error` | X | Failed operations |

### Logging Best Practices

```python
# Log operation start
log_to_ui(f"Fetching {endpoint_name}...", "info")

# Log success with context
log_to_ui(f"{provider} {endpoint_name} fetched", "success")

# Log errors with details
log_to_ui(f"{provider} error: {str(e)[:50]}", "error")
```

---

## 8. Configuration Management

### Key Priority Order

1. Local settings (`local_settings.py`)
2. Streamlit secrets (`st.secrets`)
3. Environment variables
4. Empty string (fallback)

### Configuration File Security

| File | Git Tracking | Purpose |
|------|--------------|---------|
| `config.py` | Ignored | Runtime config with keys |
| `config_template.py` | Tracked | Template for setup |
| `local_settings.py` | Ignored | Local development overrides |
| `.env` | Ignored | Environment variables |

### Adding New Configuration

```python
# In config.py
SUPPORTED_CHAINS = {
    'NewChain': {
        'defillama': 'newchain',
        'nansen': 'newchain',
        'coingecko': 'newchain-network',
        'id': 'newchain'
    }
}
```

---

## 9. Documentation Standards

### Docstrings

Use Google-style docstrings:

```python
def create_price_chart(data: dict) -> go.Figure:
    """
    Create a price chart from API data.

    Supports both CoinGecko and DefiLlama data formats.
    Returns empty figure if data is invalid.

    Args:
        data: Raw API response containing price data.
            CoinGecko format: {'prices': [[ts, price], ...]}
            DefiLlama format: {'coins': {'key': {'prices': [...]}}}

    Returns:
        Plotly Figure object with price line chart.

    Example:
        >>> chart = create_price_chart(coingecko_response)
        >>> st.plotly_chart(chart)
    """
```

### Inline Comments

```python
# Use sparingly for non-obvious logic
# Sort ascending for horizontal bar (top holder at top)
df = df.sort_values(balance_col, ascending=True)
```

### Module Headers

```python
"""
Token Tracker Metrics Dashboard
Main Streamlit Application

This module provides the entry point for the dashboard application.
"""
```

---

## 10. Streamlit UI Patterns

### Layout Structure

```python
# Page config at top
st.set_page_config(page_title="...", layout="wide")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    # Settings and status

# Main content in tabs
tab1, tab2, tab3 = st.tabs(["Tab1", "Tab2", "Tab3"])

with tab1:
    # Tab content
    col1, col2 = st.columns([1, 2])
```

### Session State Initialization

```python
# Initialize at module level after imports
if 'logs' not in st.session_state:
    st.session_state.logs = []

if 'fetched_data' not in st.session_state:
    st.session_state.fetched_data = {}
```

### Dynamic Updates

```python
# Use placeholders for live updates
log_placeholder = st.empty()

# Update content
log_placeholder.markdown(f"<div>...</div>", unsafe_allow_html=True)

# Force refresh
st.rerun()
```

### Theme Support

```python
# Apply theme-specific CSS
if theme == "Dark":
    st.markdown("""
        <style>
        .main { background-color: #0e1117; }
        </style>
    """, unsafe_allow_html=True)
```

---

## Checklist for Code Review

### Before Submitting

- [ ] Code follows PEP 8 style
- [ ] All functions have docstrings
- [ ] Type hints are present
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] No hardcoded API keys
- [ ] Tests pass (if applicable)

### Pull Request Requirements

- [ ] Clear description of changes
- [ ] Documentation updated if needed
- [ ] No debug code or print statements
- [ ] Configuration changes documented

