#!/usr/bin/env python3
"""
DefiLlama API Endpoints Test Script
Tests all available endpoints (Free and Pro if API key is set)
"""

import os
import sys
import time
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api_clients.defillama_client import DefiLlamaClient


def test_endpoint(name: str, func, *args, **kwargs):
    """Test a single endpoint and return result"""
    try:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start

        # Check if result is valid
        if result is not None:
            if isinstance(result, dict):
                data_preview = f"keys: {list(result.keys())[:5]}"
            elif isinstance(result, list):
                data_preview = f"items: {len(result)}"
            elif isinstance(result, (int, float)):
                data_preview = f"value: {result}"
            else:
                data_preview = f"type: {type(result).__name__}"

            print(f"  [OK] {name} ({elapsed:.2f}s) - {data_preview}")
            return True, None
        else:
            print(f"  [WARN] {name} - No data returned")
            return False, "No data"

    except ValueError as e:
        # API key required for pro endpoints
        print(f"  [SKIP] {name} - {str(e)}")
        return None, str(e)
    except Exception as e:
        print(f"  [FAIL] {name} - {str(e)[:80]}")
        return False, str(e)


def main():
    print("=" * 60)
    print("DefiLlama API Test Suite")
    print("=" * 60)

    # Check for API key
    api_key = os.getenv('DEFILLAMA_API_KEY')
    if api_key:
        print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    else:
        print("API Key: Not set (Pro endpoints will be skipped)")
    print()

    # Initialize client
    client = DefiLlamaClient()

    # Test parameters
    test_protocol = "aave"
    test_chain = "Ethereum"
    test_coins = ["coingecko:ethereum", "coingecko:bitcoin"]
    test_timestamp = int((datetime.now() - timedelta(days=7)).timestamp())

    results = {
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }

    # ========================
    # TVL Endpoints (Free)
    # ========================
    print("\n[TVL Endpoints - Free]")

    tests = [
        ("get_all_protocols", client.get_all_protocols),
        ("get_protocol", client.get_protocol, test_protocol),
        ("get_historical_chain_tvl_all", client.get_historical_chain_tvl_all),
        ("get_historical_chain_tvl", client.get_historical_chain_tvl, test_chain),
        ("get_current_tvl", client.get_current_tvl, test_protocol),
        ("get_all_chains", client.get_all_chains),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # TVL Endpoints (Pro)
    # ========================
    print("\n[TVL Endpoints - Pro]")

    tests = [
        ("get_token_protocols", client.get_token_protocols, "usdt"),
        ("get_inflows", client.get_inflows, test_protocol, test_timestamp),
        ("get_chain_assets", client.get_chain_assets),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Coins/Prices Endpoints (Free)
    # ========================
    print("\n[Coins/Prices Endpoints - Free]")

    tests = [
        ("get_current_prices", client.get_current_prices, test_coins),
        ("get_historical_prices", client.get_historical_prices, test_coins, test_timestamp),
        ("get_price_chart", client.get_price_chart, test_coins),
        ("get_price_percentage_change", client.get_price_percentage_change, test_coins),
        ("get_first_price", client.get_first_price, test_coins),
        ("get_block_at_timestamp", client.get_block_at_timestamp, "ethereum", test_timestamp),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Stablecoins Endpoints (Free)
    # ========================
    print("\n[Stablecoins Endpoints - Free]")

    tests = [
        ("get_stablecoins", client.get_stablecoins),
        ("get_stablecoin_charts_all", client.get_stablecoin_charts_all),
        ("get_stablecoin_charts_chain", client.get_stablecoin_charts_chain, test_chain),
        ("get_stablecoin", client.get_stablecoin, 1),  # USDT = 1
        ("get_stablecoin_chains", client.get_stablecoin_chains),
        ("get_stablecoin_prices", client.get_stablecoin_prices),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Stablecoins Endpoints (Pro)
    # ========================
    print("\n[Stablecoins Endpoints - Pro]")

    tests = [
        ("get_stablecoin_dominance", client.get_stablecoin_dominance, test_chain),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Yields Endpoints (Free)
    # ========================
    print("\n[Yields Endpoints - Free]")

    tests = [
        ("get_yield_pools", client.get_yield_pools),
        # Skip pool_chart as we need a valid pool_id
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Yields Endpoints (Pro)
    # ========================
    print("\n[Yields Endpoints - Pro]")

    tests = [
        ("get_pools_old", client.get_pools_old),
        ("get_pools_borrow", client.get_pools_borrow),
        ("get_perp_yields", client.get_perp_yields),
        ("get_lsd_rates", client.get_lsd_rates),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Volumes (DEX) Endpoints (Free)
    # ========================
    print("\n[Volumes/DEX Endpoints - Free]")

    tests = [
        ("get_dex_overview", client.get_dex_overview),
        ("get_dex_overview_chain", client.get_dex_overview_chain, test_chain),
        ("get_dex_summary", client.get_dex_summary, "uniswap"),
        ("get_options_overview", client.get_options_overview),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Fees & Revenue Endpoints (Free)
    # ========================
    print("\n[Fees & Revenue Endpoints - Free]")

    tests = [
        ("get_fees_overview", client.get_fees_overview),
        ("get_fees_overview_chain", client.get_fees_overview_chain, test_chain),
        ("get_fees_summary", client.get_fees_summary, "aave"),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Perps Endpoints (Free)
    # ========================
    print("\n[Perps Endpoints - Free]")

    tests = [
        ("get_open_interest", client.get_open_interest),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Perps Endpoints (Pro)
    # ========================
    print("\n[Perps Endpoints - Pro]")

    tests = [
        ("get_derivatives_overview", client.get_derivatives_overview),
        ("get_derivatives_summary", client.get_derivatives_summary, "hyperliquid"),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Bridges Endpoints (Pro)
    # ========================
    print("\n[Bridges Endpoints - Pro]")

    tests = [
        ("get_bridges", client.get_bridges),
        ("get_bridge", client.get_bridge, 1),
        ("get_bridge_volume", client.get_bridge_volume, test_chain),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Unlocks/Emissions Endpoints (Pro)
    # ========================
    print("\n[Unlocks/Emissions Endpoints - Pro]")

    tests = [
        ("get_emissions", client.get_emissions),
        ("get_emission", client.get_emission, "uniswap"),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Other Endpoints (Pro)
    # ========================
    print("\n[Other Endpoints - Pro]")

    tests = [
        ("get_categories", client.get_categories),
        ("get_forks", client.get_forks),
        ("get_oracles", client.get_oracles),
        ("get_hacks", client.get_hacks),
        ("get_raises", client.get_raises),
        ("get_treasuries", client.get_treasuries),
        ("get_entities", client.get_entities),
        ("get_etf_snapshot", client.get_etf_snapshot),
        ("get_etf_flows", client.get_etf_flows),
        ("get_fdv_performance", client.get_fdv_performance, "7d"),
    ]

    for test in tests:
        name = test[0]
        func = test[1]
        args = test[2:] if len(test) > 2 else ()
        success, _ = test_endpoint(name, func, *args)
        if success is True:
            results["passed"] += 1
        elif success is False:
            results["failed"] += 1
        else:
            results["skipped"] += 1

    # ========================
    # Summary
    # ========================
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    total = results["passed"] + results["failed"] + results["skipped"]
    print(f"  Total:   {total}")
    print(f"  Passed:  {results['passed']} ({results['passed']/total*100:.1f}%)")
    print(f"  Failed:  {results['failed']} ({results['failed']/total*100:.1f}%)")
    print(f"  Skipped: {results['skipped']} ({results['skipped']/total*100:.1f}%)")
    print("=" * 60)

    # Return exit code
    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    exit(main())
