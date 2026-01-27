#!/usr/bin/env python3
"""
Chaos Test Script for Sentry Alert Verification

Triggers specific alert types to verify Sentry monitoring is working correctly.

Usage:
    python scripts/chaos_sentry_test.py --error-burst    # 100 errors
    python scripts/chaos_sentry_test.py --slow-query     # 35s slow query
    python scripts/chaos_sentry_test.py --circuit-open   # Force breaker open
    python scripts/chaos_sentry_test.py --all            # All tests

NEVER run in production!
"""

import sys
import os
import argparse
import time
import logging

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
)
load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def check_not_production():
    """Refuse to run in production environment."""
    from app.config import settings

    if settings.app_env == "production":
        print("❌ REFUSED: Cannot run chaos tests in production!")
        print("   Set APP_ENV to 'development' or 'staging'")
        sys.exit(1)

    print(f"✅ Environment: {settings.app_env}")


def test_error_burst():
    """Send 100 errors to trigger error rate alert."""
    import sentry_sdk
    from app.config import settings

    # Initialize Sentry if not already done
    if not sentry_sdk.get_client():
        if settings.sentry_dsn_backend:
            sentry_sdk.init(
                dsn=settings.sentry_dsn_backend,
                environment=settings.sentry_environment,
                traces_sample_rate=settings.sentry_traces_sample_rate,
            )
        else:
            print("⚠️  Sentry DSN not configured, skipping error burst test")
            return

    print("\n" + "=" * 60)
    print("TEST: Error Burst (100 errors)")
    print("=" * 60)

    for i in range(100):
        try:
            raise ValueError(f"Chaos test error #{i + 1}")
        except ValueError as e:
            sentry_sdk.capture_exception(e)

        if (i + 1) % 20 == 0:
            print(f"   Sent {i + 1}/100 errors...")

    sentry_sdk.flush(timeout=10)
    print("\n✅ Error burst complete!")
    print("   ⏰ Alert should fire within 5 minutes")


def test_slow_query():
    """Simulate a 35s slow operation."""
    import sentry_sdk
    from app.config import settings

    # Initialize Sentry if not already done
    if not sentry_sdk.get_client():
        if settings.sentry_dsn_backend:
            sentry_sdk.init(
                dsn=settings.sentry_dsn_backend,
                environment=settings.sentry_environment,
                traces_sample_rate=1.0,  # 100% for performance monitoring
            )
        else:
            print("⚠️  Sentry DSN not configured, skipping slow query test")
            return

    print("\n" + "=" * 60)
    print("TEST: Slow Query (35s)")
    print("=" * 60)

    with sentry_sdk.start_transaction(op="test", name="chaos-slow-query") as txn:
        with sentry_sdk.start_span(
            op="rag.search", description="Simulated slow search"
        ):
            print("   Sleeping for 35 seconds...")
            time.sleep(35)

    sentry_sdk.flush(timeout=10)
    print("\n✅ Slow query complete!")
    print("   ⏰ Latency alert should fire within 5 minutes")


def test_circuit_open():
    """Force circuit breaker to open state."""
    import sentry_sdk
    from app.config import settings
    from src.circuit_breaker import qdrant_breaker, CircuitBreakerError

    # Initialize Sentry if not already done
    if not sentry_sdk.get_client():
        if settings.sentry_dsn_backend:
            sentry_sdk.init(
                dsn=settings.sentry_dsn_backend,
                environment=settings.sentry_environment,
                traces_sample_rate=settings.sentry_traces_sample_rate,
            )
        else:
            print("⚠️  Sentry DSN not configured, skipping circuit breaker test")
            return

    print("\n" + "=" * 60)
    print("TEST: Circuit Breaker Open")
    print("=" * 60)

    # Force failures to open breaker (fail_max=5)
    for i in range(6):
        try:
            # Call with a lambda that raises an exception
            qdrant_breaker.call(
                lambda: (_ for _ in ()).throw(Exception("forced failure"))
            )
        except (Exception, CircuitBreakerError):
            print(f"   Forced failure {i + 1}/6")

    sentry_sdk.flush(timeout=10)
    print("\n✅ Circuit breaker should be OPEN!")
    print("   ⏰ Circuit breaker alert should fire within 5 minutes")

    # Reset for next time
    qdrant_breaker.close()
    print("   ✓ Breaker reset for next test")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Chaos test for Sentry alerts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/chaos_sentry_test.py --error-burst    # Send 100 errors
  python scripts/chaos_sentry_test.py --slow-query     # 35s slow operation
  python scripts/chaos_sentry_test.py --circuit-open   # Force breaker open
  python scripts/chaos_sentry_test.py --all            # Run all tests
        """,
    )
    parser.add_argument("--error-burst", action="store_true", help="Send 100 errors")
    parser.add_argument("--slow-query", action="store_true", help="35s slow query")
    parser.add_argument(
        "--circuit-open", action="store_true", help="Force breaker open"
    )
    parser.add_argument("--all", action="store_true", help="Run all tests")

    args = parser.parse_args()

    # Show help if no args
    if not any([args.error_burst, args.slow_query, args.circuit_open, args.all]):
        parser.print_help()
        sys.exit(0)

    print("🔥 Chaos Sentry Test Script")
    print("=" * 60)

    check_not_production()

    try:
        if args.error_burst or args.all:
            test_error_burst()

        if args.slow_query or args.all:
            test_slow_query()

        if args.circuit_open or args.all:
            test_circuit_open()

        print("\n" + "=" * 60)
        print("CHAOS TESTS COMPLETE")
        print("=" * 60)
        print("✓ Check Sentry dashboard for alerts!")
        print("✓ Alerts should appear within 5 minutes")

    except Exception as e:
        print(f"\n❌ Error during chaos tests: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
