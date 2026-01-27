#!/usr/bin/env python3
"""
Sentry Integration Test Script

This script helps verify Sentry integration without modifying production code.
Run this AFTER configuring Sentry environment variables.

Usage:
    python scripts/test_sentry.py [--backend] [--spans] [--all]

Options:
    --backend   Test backend error capture (Task 4)
    --spans     Test performance spans (Task 6)
    --all       Run all tests

Prerequisites:
    1. Set environment variables in backend/.env:
       SENTRY_ENABLED=true
       SENTRY_DSN_BACKEND=https://xxx@sentry.io/project
       SENTRY_ENVIRONMENT=development
       SENTRY_TRACES_SAMPLE_RATE=1.0

    2. Ensure Qdrant is running:
       docker compose up -d

After running, check Sentry dashboard:
    - Issues: New errors should appear within 30 seconds
    - Performance: Transactions should show span breakdown
"""

import sys
import os
import argparse
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
)


def check_sentry_config():
    """Verify Sentry is configured before running tests."""
    from app.config import settings

    if not settings.sentry_enabled:
        print("❌ SENTRY_ENABLED is not set to true")
        print("   Add to backend/.env: SENTRY_ENABLED=true")
        return False

    if not settings.sentry_dsn_backend:
        print("❌ SENTRY_DSN_BACKEND is not configured")
        print(
            "   Add to backend/.env: SENTRY_DSN_BACKEND=https://xxx@sentry.io/project"
        )
        return False

    print(f"✅ Sentry configured for environment: {settings.sentry_environment}")
    print(f"   DSN: {settings.sentry_dsn_backend[:50]}...")
    print(f"   Traces sample rate: {settings.sentry_traces_sample_rate}")
    return True


def test_backend_error():
    """
    Task 4: Test backend error capture.

    This triggers a test error and captures it to Sentry.
    Check Sentry dashboard → Issues for the error.
    """
    print("\n" + "=" * 60)
    print("TASK 4: Testing Backend Error Capture")
    print("=" * 60)

    try:
        import sentry_sdk

        # Initialize Sentry if not already done
        from app.config import settings

        if not sentry_sdk.get_client():
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.starlette import StarletteIntegration

            sentry_sdk.init(
                dsn=settings.sentry_dsn_backend,
                environment=settings.sentry_environment,
                traces_sample_rate=settings.sentry_traces_sample_rate,
            )
            print("   Sentry initialized for test")

        # Capture a test error
        print("\n📤 Sending test error to Sentry...")
        try:
            raise ValueError("Sentry test error from backend - Task 4 verification")
        except ValueError as e:
            sentry_sdk.capture_exception(e)
            print(f"   Captured: {e}")

        # Flush to ensure delivery
        sentry_sdk.flush(timeout=5)
        print("   Flushed to Sentry")

        print("\n✅ Test error sent!")
        print("\n📋 VERIFICATION STEPS:")
        print("   1. Open Sentry dashboard: https://sentry.io")
        print("   2. Go to Issues → Select your backend project")
        print("   3. Look for: 'ValueError: Sentry test error from backend'")
        print("   4. Verify:")
        print("      - Stack trace points to this file")
        print("      - Environment matches your SENTRY_ENVIRONMENT")
        print("   5. Error should appear within 30 seconds")

        return True

    except ImportError:
        print("❌ sentry_sdk not installed. Run: pip install sentry-sdk[fastapi]")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_performance_spans():
    """
    Task 6: Test performance spans in RAG pipeline.

    This runs a search query and generates performance traces.
    Check Sentry dashboard → Performance for the transaction.
    """
    print("\n" + "=" * 60)
    print("TASK 6: Testing Performance Spans")
    print("=" * 60)

    try:
        import sentry_sdk
        from src.ultimate_rag import UltimateRAG

        # Initialize Sentry with tracing
        from app.config import settings

        if not sentry_sdk.get_client():
            sentry_sdk.init(
                dsn=settings.sentry_dsn_backend,
                environment=settings.sentry_environment,
                traces_sample_rate=1.0,  # 100% for testing
            )
            print("   Sentry initialized with tracing")

        # Start a transaction for the test
        print("\n📤 Running search query with performance tracing...")

        with sentry_sdk.start_transaction(
            op="test", name="sentry-test-search"
        ) as transaction:
            rag = UltimateRAG(verbose=False)

            # Run a simple search
            results = rag.search_quran("sabır", top_k=3)

            transaction.set_data("result_count", len(results))
            print(f"   Search returned {len(results)} results")

        # Flush to ensure delivery
        sentry_sdk.flush(timeout=10)
        print("   Flushed to Sentry")

        print("\n✅ Performance trace sent!")
        print("\n📋 VERIFICATION STEPS:")
        print("   1. Open Sentry dashboard: https://sentry.io")
        print("   2. Go to Performance → Select your backend project")
        print("   3. Look for transaction: 'sentry-test-search'")
        print("   4. Click to see span breakdown:")
        print("      - rag.pipeline.quran (top level)")
        print("      - rag.enhance_query (LLM enhancement)")
        print("      - rag.multi_query (query variants)")
        print("      - rag.search (RRF fusion)")
        print("      - db.query.qdrant (Qdrant search)")
        print("   5. Transaction should appear within 60 seconds")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're in the backend directory with venv activated")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Test Sentry integration for Clarus backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--backend", action="store_true", help="Test backend error capture (Task 4)"
    )
    parser.add_argument(
        "--spans", action="store_true", help="Test performance spans (Task 6)"
    )
    parser.add_argument("--all", action="store_true", help="Run all tests")

    args = parser.parse_args()

    # Default to --all if no args
    if not (args.backend or args.spans or args.all):
        args.all = True

    print("🔍 Sentry Integration Test Script")
    print("=" * 60)

    # Check configuration first
    if not check_sentry_config():
        print("\n❌ Sentry not configured. Please set environment variables first.")
        sys.exit(1)

    results = []

    if args.backend or args.all:
        results.append(("Backend Error Capture", test_backend_error()))

    if args.spans or args.all:
        results.append(("Performance Spans", test_performance_spans()))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {name}: {status}")

    print("\n📝 Next steps:")
    print("   1. Check Sentry dashboard for the test data")
    print("   2. If tests pass, mark Tasks 4 and 6 as complete in the plan")
    print("   3. For Task 10 (frontend), run: npm run dev and test in browser")


if __name__ == "__main__":
    main()
