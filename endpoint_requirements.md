# Required Endpoints

| Endpoints | curl sample | Source | docs | api key required? | credit amount |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Get Price Chart | `curl "https://pro-api.llama.fi/coins/chart/ethereum:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48?period=7d"` | DefiLlama | [DefiLlama Docs](https://api-docs.defillama.com/) | No | null |
| Get Price Percentage Change | `curl https://pro-api.llama.fi/coins/percentage/ethereum:0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | DefiLlama | [DefiLlama Docs](https://api-docs.defillama.com/) | No | null |
| Get Token Protocols | `curl https://pro-api.llama.fi/<API_KEY>/api/tokenProtocols/usdt` | DefiLlama | [DefiLlama Docs](https://api-docs.defillama.com/) | Yes | null |
| Token Who Bought/Sold | `curl -X POST https://api.nansen.ai/api/v1/tgm/who-bought-sold -H "x-api-key: YOUR_API_KEY" -H "Content-Type: application/json"` | Nansen | [Nansen Docs](https://docs.nansen.ai/api/token-god-mode/who-bought-sold) | Yes | 1 |
| Token Perp Trades | `curl -X POST https://api.nansen.ai/api/v1/tgm/perp-trades -H "x-api-key: YOUR_API_KEY" -H "Content-Type: application/json"` | Nansen | [Nansen Docs](https://docs.nansen.ai/api/token-god-mode/perp-trades) | Yes | 1 |
| Token Transfers | `curl -X POST https://api.nansen.ai/api/v1/tgm/transfers -H "x-api-key: YOUR_API_KEY" -H "Content-Type: application/json"` | Nansen | [Nansen Docs](https://docs.nansen.ai/api/token-god-mode/token-transfers) | Yes | 1 |
| Token Holders | `curl -X POST https://api.nansen.ai/api/v1/tgm/holders -H "x-api-key: YOUR_API_KEY" -H "Content-Type: application/json"` | Nansen | [Nansen Docs](https://docs.nansen.ai/api/token-god-mode/holders) | Yes | 5 |
| Get Borrowing Rates | `curl https://pro-api.llama.fi/<API_KEY>/yields/poolsBorrow` | DefiLlama | [DefiLlama Docs](https://api-docs.defillama.com/) | Yes | null |
| Coins List (ID Map) | `curl https://pro-api.coingecko.com/api/v3/coins/list -H "x-cg-pro-api-key: YOUR_API_KEY"` | CoinGecko | [CoinGecko Docs](https://docs.coingecko.com/reference/coins-list) | No | null |
| Coin Historical Chart by Token Address | `curl https://pro-api.coingecko.com/api/v3/coins/{id}/contract/{contract_address}/market_chart -H "x-cg-pro-api-key: YOUR_API_KEY"` | CoinGecko | [CoinGecko Docs](https://docs.coingecko.com/reference/contract-address-market-chart) | No | |
| Coin Data by ID | `curl https://pro-api.coingecko.com/api/v3/coins/{id} -H "x-cg-pro-api-key: YOUR_API_KEY"` | CoinGecko | [CoinGecko Docs](https://docs.coingecko.com/reference/coins-id) | No | |
| Execute Query | `curl -X POST https://api.dune.com/api/v1/query/{query_id}/execute -H "X-Dune-API-Key: YOUR_API_KEY"` | Dune | [Dune Docs](https://dune.com/docs/api/) | Yes | Varies |
| Token Flow Intelligence | `curl -X POST https://api.nansen.ai/api/v1/tgm/flow-intelligence -H "x-api-key: YOUR_API_KEY" -H "Content-Type: application/json"` | Nansen | [Nansen Docs](https://docs.nansen.ai/api/token-god-mode/flow-intelligence) | Yes | Varies |
