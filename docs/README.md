# GFI Quant Project Documentation

## Quick Links

| Document | Description |
|----------|-------------|
| [Architecture](architecture.md) | Project structure, data flow, best practices |
| [Services API](services-api.md) | Data fetching module reference |
| [Components Guide](components-guide.md) | UI components development guide |

---

## Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run Application

```bash
streamlit run app.py
```

### Environment Variables

Create `.streamlit/secrets.toml`:

```toml
NANSEN_API_KEY = "your_key"
COINGECKO_API_KEY = "your_key"
DUNE_API_KEY = "your_key"
DEFILLAMA_API_KEY = "your_key"
STORAGE_MODE = "all"  # all, local, gcs

[gcp_service_account]
type = "service_account"
project_id = "your_project"
# ... other GCP credentials
```

---

## Project Structure Summary

```
gfi-quant-project/
├── app.py              # Entry point (140 lines)
├── config.py           # Configuration
├── constants/          # Static mappings
├── services/           # Data fetching logic
├── components/         # UI tab components
├── api_clients/        # API wrappers
├── data_handlers/      # Storage logic
├── visualizations/     # Charts & tables
├── utils/              # Helpers
└── docs/               # This documentation
```

---

## Key Concepts

### Modular Architecture

- **app.py**: Routing only, delegates to components
- **services/**: All data fetching logic
- **components/**: All UI logic

### Data Flow

```
User Input → Component → Service → API Client → Storage
                                        ↓
            Visualization ← Component ← Load Data
```

### Session State

```python
st.session_state.logs           # Log messages
st.session_state.fetched_data   # Data cache
st.session_state.endpoint_status # Endpoint status
```

---

## Common Tasks

### Add New API Endpoint

1. Add method to `api_clients/source_client.py`
2. Add fetch logic to `services/source_fetcher.py`
3. Register in `constants/endpoints.py`

### Add New Tab

1. Create `components/new_tab.py` with `render_tab()`
2. Import in `components/__init__.py`
3. Add tab in `app.py`

### Add New Data Source

1. Create `api_clients/newsource_client.py`
2. Create `services/newsource_fetcher.py`
3. Add to `services/data_fetcher.py` orchestrator
4. Register endpoints in `constants/endpoints.py`

---

## File Size Guidelines

| File Type | Max Lines |
|-----------|-----------|
| app.py | 200 |
| Component | 400 |
| Service/Fetcher | 350 |
| API Client | 600 |

---

## Refactoring Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| app.py lines | 1949 | 140 | -93% |
| Max file size | 1949 | 372 | -81% |
| Modules | 1 | 12 | +11 |

---

## Contributing

1. Follow existing patterns in components/services
2. Keep files under size guidelines
3. Add tests for new fetchers
4. Update docs for new features
