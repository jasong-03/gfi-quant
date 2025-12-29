#!/usr/bin/env python3
"""
Crypto API Endpoints Verification Script
Tests endpoints from DefiLlama, CoinGecko, and Nansen APIs

Usage:
    python test_api_endpoints.py --all           # Test all APIs
    python test_api_endpoints.py --defillama     # Test DefiLlama only
    python test_api_endpoints.py --coingecko     # Test CoinGecko only
    python test_api_endpoints.py --nansen        # Test Nansen only

Environment Variables Required:
    COINGECKO_API_KEY - CoinGecko Pro API key
    NANSEN_API_KEY    - Nansen API key
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime
from typing import Dict, List, Tuple, Optional

try:
    import requests
except ImportError:
    print("Please install requests: pip install requests")
    sys.exit(1)


# =============================================================================
# Configuration
# =============================================================================

COINGECKO_API_KEY = os.environ.get("COINGECKO_API_KEY", "")
NANSEN_API_KEY = os.environ.get("NANSEN_API_KEY", "")

# Rate limit delays (seconds)
DEFILLAMA_DELAY = 0.5
COINGECKO_DELAY = 2.0  # More conservative for rate limits
NANSEN_DELAY = 1.0


# =============================================================================
# DefiLlama Tests
# =============================================================================

DEFILLAMA_ENDPOINTS = [
    # TVL
    ("TVL - All Protocols", "GET", "https://api.llama.fi/protocols", None),
    ("TVL - Protocol Detail", "GET", "https://api.llama.fi/protocol/aave", None),
    ("TVL - All Chains", "GET", "https://api.llama.fi/v2/chains", None),
    ("TVL - Chain History", "GET", "https://api.llama.fi/v2/historicalChainTvl/Ethereum", None),
    ("TVL - Current", "GET", "https://api.llama.fi/tvl/uniswap", None),

    # Coins
    ("Coins - Current Prices", "GET", "https://api.llama.fi/prices/current/coingecko:ethereum,coingecko:bitcoin", None),
    ("Coins - Block", "GET", "https://api.llama.fi/block/ethereum/1609459200", None),

    # Stablecoins
    ("Stablecoins - List", "GET", "https://api.llama.fi/stablecoins", None),
    ("Stablecoins - Chains", "GET", "https://api.llama.fi/stablecoinchains", None),
    ("Stablecoins - Prices", "GET", "https://api.llama.fi/stablecoinprices", None),

    # Yields
    ("Yields - All Pools", "GET", "https://api.llama.fi/pools", None),

    # Volumes
    ("Volumes - DEX Overview", "GET", "https://api.llama.fi/overview/dexs", None),
    ("Volumes - DEX Chain", "GET", "https://api.llama.fi/overview/dexs/ethereum", None),
    ("Volumes - DEX Protocol", "GET", "https://api.llama.fi/summary/dexs/uniswap", None),

    # Fees
    ("Fees - Overview", "GET", "https://api.llama.fi/overview/fees", None),
    ("Fees - Protocol", "GET", "https://api.llama.fi/summary/fees/aave", None),
]


def test_defillama() -> List[Tuple[str, str, Optional[str]]]:
    """Test DefiLlama endpoints"""
    results = []

    print("\n" + "=" * 60)
    print("Testing DefiLlama API Endpoints")
    print("=" * 60)

    for name, method, url, body in DEFILLAMA_ENDPOINTS:
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            else:
                response = requests.post(url, json=body, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    detail = f"OK ({len(data)} items)"
                elif isinstance(data, dict):
                    detail = f"OK ({len(data)} keys)"
                else:
                    detail = "OK"
                status = "PASS"
            else:
                status = "FAIL"
                detail = f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            status = "FAIL"
            detail = "Timeout"
        except Exception as e:
            status = "FAIL"
            detail = str(e)[:50]

        results.append((name, status, detail))
        icon = "✅" if status == "PASS" else "❌"
        print(f"  {icon} {name}: {detail}")
        time.sleep(DEFILLAMA_DELAY)

    return results


# =============================================================================
# CoinGecko Tests
# =============================================================================

COINGECKO_ENDPOINTS = [
    # Ping & Status
    ("Ping", "GET", "/ping", None),

    # Simple
    ("Simple - Price", "GET", "/simple/price?ids=bitcoin,ethereum&vs_currencies=usd", None),
    ("Simple - Currencies", "GET", "/simple/supported_vs_currencies", None),

    # Coins
    ("Coins - List", "GET", "/coins/list?per_page=10", None),
    ("Coins - Markets", "GET", "/coins/markets?vs_currency=usd&per_page=10", None),
    ("Coins - Detail", "GET", "/coins/bitcoin?localization=false&tickers=false", None),
    ("Coins - History", "GET", "/coins/bitcoin/history?date=01-01-2024", None),
    ("Coins - Market Chart", "GET", "/coins/bitcoin/market_chart?vs_currency=usd&days=7", None),
    ("Coins - OHLC", "GET", "/coins/bitcoin/ohlc?vs_currency=usd&days=7", None),

    # Categories
    ("Categories - List", "GET", "/coins/categories/list", None),
    ("Categories - Data", "GET", "/coins/categories", None),

    # Exchanges
    ("Exchanges - List", "GET", "/exchanges?per_page=10", None),
    ("Exchanges - Detail", "GET", "/exchanges/binance", None),

    # Derivatives
    ("Derivatives - Tickers", "GET", "/derivatives", None),
    ("Derivatives - Exchanges", "GET", "/derivatives/exchanges", None),

    # Global
    ("Global - Data", "GET", "/global", None),
    ("Global - DeFi", "GET", "/global/decentralized_finance_defi", None),

    # Search & Trending
    ("Search", "GET", "/search?query=bitcoin", None),
    ("Trending", "GET", "/search/trending", None),

    # Asset Platforms
    ("Asset Platforms", "GET", "/asset_platforms", None),

    # Exchange Rates
    ("Exchange Rates", "GET", "/exchange_rates", None),

    # Onchain (GeckoTerminal)
    ("Onchain - Networks", "GET", "/onchain/networks", None),
    ("Onchain - Trending Pools", "GET", "/onchain/networks/trending_pools", None),
    ("Onchain - Search Pools", "GET", "/onchain/search/pools?query=WETH", None),
]


def test_coingecko() -> List[Tuple[str, str, Optional[str]]]:
    """Test CoinGecko endpoints"""
    results = []

    if not COINGECKO_API_KEY:
        print("\n⚠️  COINGECKO_API_KEY not set. Using demo API (rate limited).")
        base_url = "https://api.coingecko.com/api/v3"
        headers = {}
    else:
        base_url = "https://pro-api.coingecko.com/api/v3"
        headers = {"x-cg-pro-api-key": COINGECKO_API_KEY}

    print("\n" + "=" * 60)
    print("Testing CoinGecko API Endpoints")
    print("=" * 60)

    for name, method, endpoint, body in COINGECKO_ENDPOINTS:
        url = f"{base_url}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            else:
                response = requests.post(url, headers=headers, json=body, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    detail = f"OK ({len(data)} items)"
                elif isinstance(data, dict):
                    detail = f"OK ({len(data)} keys)"
                else:
                    detail = "OK"
                status = "PASS"
            elif response.status_code == 429:
                status = "SKIP"
                detail = "Rate limited"
            else:
                status = "FAIL"
                detail = f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            status = "FAIL"
            detail = "Timeout"
        except Exception as e:
            status = "FAIL"
            detail = str(e)[:50]

        results.append((name, status, detail))
        icon = "✅" if status == "PASS" else ("⏭️" if status == "SKIP" else "❌")
        print(f"  {icon} {name}: {detail}")
        time.sleep(COINGECKO_DELAY)

    return results


# =============================================================================
# Nansen Tests
# =============================================================================

NANSEN_ENDPOINTS = [
    # Profiler (1 credit each)
    ("Profiler - Current Balance", "/api/v1/profiler/address/current-balance", {
        "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",  # vitalik.eth
        "chain": "ethereum",
        "hide_spam_token": True,
        "pagination": {"page": 1, "per_page": 5}
    }),
    ("Profiler - Transactions", "/api/v1/profiler/address/transactions", {
        "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
        "chain": "ethereum",
        "pagination": {"page": 1, "per_page": 5}
    }),
    ("Profiler - Related Wallets", "/api/v1/profiler/address/related-wallets", {
        "address": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
        "chain": "ethereum",
        "pagination": {"page": 1, "per_page": 5}
    }),

    # TGM (1-5 credits each)
    ("TGM - Token Screener", "/api/v1/tgm/token-screener", {
        "chains": ["ethereum"],
        "pagination": {"page": 1, "per_page": 5}
    }),
    ("TGM - Flows", "/api/v1/tgm/flows", {
        "token_address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
        "chain": "ethereum"
    }),

    # Smart Money (5 credits each) - Commented by default to save credits
    # ("Smart Money - Netflow", "/api/v1/smart-money/netflow", {
    #     "chains": ["ethereum"],
    #     "pagination": {"page": 1, "per_page": 5}
    # }),
]


def test_nansen() -> List[Tuple[str, str, Optional[str]]]:
    """Test Nansen endpoints"""
    results = []

    if not NANSEN_API_KEY:
        print("\n❌ NANSEN_API_KEY not set. Skipping Nansen tests.")
        return [("All Nansen Tests", "SKIP", "No API key")]

    base_url = "https://api.nansen.ai"
    headers = {
        "apiKey": NANSEN_API_KEY,
        "Content-Type": "application/json"
    }

    print("\n" + "=" * 60)
    print("Testing Nansen API Endpoints")
    print("⚠️  WARNING: These tests consume API credits!")
    print("=" * 60)

    for name, endpoint, body in NANSEN_ENDPOINTS:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.post(url, headers=headers, json=body, timeout=30)

            if response.status_code == 200:
                data = response.json()
                items = len(data.get("data", []))
                detail = f"OK ({items} items)"
                status = "PASS"
            elif response.status_code == 401:
                status = "FAIL"
                detail = "Unauthorized (check API key)"
            elif response.status_code == 403:
                status = "FAIL"
                detail = "Forbidden (plan limit?)"
            elif response.status_code == 429:
                status = "SKIP"
                detail = "Rate limited"
            else:
                status = "FAIL"
                detail = f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            status = "FAIL"
            detail = "Timeout"
        except Exception as e:
            status = "FAIL"
            detail = str(e)[:50]

        results.append((name, status, detail))
        icon = "✅" if status == "PASS" else ("⏭️" if status == "SKIP" else "❌")
        print(f"  {icon} {name}: {detail}")
        time.sleep(NANSEN_DELAY)

    return results


# =============================================================================
# Main
# =============================================================================

def print_summary(all_results: Dict[str, List[Tuple[str, str, Optional[str]]]]):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    total_pass = 0
    total_fail = 0
    total_skip = 0

    for api_name, results in all_results.items():
        passed = sum(1 for _, status, _ in results if status == "PASS")
        failed = sum(1 for _, status, _ in results if status == "FAIL")
        skipped = sum(1 for _, status, _ in results if status == "SKIP")
        total = len(results)

        total_pass += passed
        total_fail += failed
        total_skip += skipped

        print(f"\n{api_name}:")
        print(f"  ✅ Passed: {passed}/{total}")
        if failed > 0:
            print(f"  ❌ Failed: {failed}/{total}")
        if skipped > 0:
            print(f"  ⏭️  Skipped: {skipped}/{total}")

    print(f"\n{'─' * 40}")
    print(f"TOTAL: {total_pass} passed, {total_fail} failed, {total_skip} skipped")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def save_results(all_results: Dict[str, List[Tuple[str, str, Optional[str]]]], filename: str):
    """Save results to JSON file"""
    output = {
        "timestamp": datetime.now().isoformat(),
        "results": {}
    }

    for api_name, results in all_results.items():
        output["results"][api_name] = [
            {"endpoint": name, "status": status, "detail": detail}
            for name, status, detail in results
        ]

    with open(filename, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(description="Test Crypto API Endpoints")
    parser.add_argument("--all", action="store_true", help="Test all APIs")
    parser.add_argument("--defillama", action="store_true", help="Test DefiLlama only")
    parser.add_argument("--coingecko", action="store_true", help="Test CoinGecko only")
    parser.add_argument("--nansen", action="store_true", help="Test Nansen only")
    parser.add_argument("--output", "-o", type=str, help="Save results to JSON file")

    args = parser.parse_args()

    # Default to all if no specific API selected
    if not any([args.defillama, args.coingecko, args.nansen]):
        args.all = True

    all_results = {}

    print("\n🔍 Crypto API Endpoints Verification")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if args.all or args.defillama:
        all_results["DefiLlama"] = test_defillama()

    if args.all or args.coingecko:
        all_results["CoinGecko"] = test_coingecko()

    if args.all or args.nansen:
        all_results["Nansen"] = test_nansen()

    print_summary(all_results)

    if args.output:
        save_results(all_results, args.output)


if __name__ == "__main__":
    main()
