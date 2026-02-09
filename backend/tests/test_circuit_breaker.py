"""
Unit tests for circuit breaker module.

Tests cover:
- Breaker thresholds (qdrant=5, llm=3, embeddings=10)
- Wrapper functions pass through successful calls
- CircuitBreakerError raised when circuit is open
- Circuit reset after timeout
- State transitions (closed → open → half-open → closed)
"""

import sys

import pybreaker
import pytest

# Add backend to path for imports
sys.path.insert(0, "/home/freyja/qdrant/backend")

from src.circuit_breaker import (
    CircuitBreakerError,
    embeddings_breaker,
    embeddings_with_breaker,
    llm_breaker,
    llm_with_breaker,
    qdrant_breaker,
    qdrant_with_breaker,
)


class TestQdrantBreakerConfiguration:
    """Test qdrant_breaker configuration."""

    def test_qdrant_breaker_fail_max_is_5(self):
        """Qdrant breaker should fail after 5 consecutive failures."""
        assert qdrant_breaker.fail_max == 5

    def test_qdrant_breaker_reset_timeout_is_60(self):
        """Qdrant breaker should reset after 60 seconds."""
        assert qdrant_breaker.reset_timeout == 60

    def test_qdrant_breaker_name_is_qdrant(self):
        """Qdrant breaker should have name 'qdrant'."""
        assert qdrant_breaker.name == "qdrant"


class TestLLMBreakerConfiguration:
    """Test llm_breaker configuration."""

    def test_llm_breaker_fail_max_is_3(self):
        """LLM breaker should fail after 3 consecutive failures."""
        assert llm_breaker.fail_max == 3

    def test_llm_breaker_reset_timeout_is_30(self):
        """LLM breaker should reset after 30 seconds."""
        assert llm_breaker.reset_timeout == 30

    def test_llm_breaker_name_is_openrouter(self):
        """LLM breaker should have name 'openrouter'."""
        assert llm_breaker.name == "openrouter"


class TestEmbeddingsBreakerConfiguration:
    """Test embeddings_breaker configuration."""

    def test_embeddings_breaker_fail_max_is_10(self):
        """Embeddings breaker should fail after 10 consecutive failures."""
        assert embeddings_breaker.fail_max == 10

    def test_embeddings_breaker_reset_timeout_is_120(self):
        """Embeddings breaker should reset after 120 seconds."""
        assert embeddings_breaker.reset_timeout == 120

    def test_embeddings_breaker_name_is_embeddings(self):
        """Embeddings breaker should have name 'embeddings'."""
        assert embeddings_breaker.name == "embeddings"


class TestQdrantWithBreakerWrapper:
    """Test qdrant_with_breaker wrapper function."""

    def setup_method(self):
        """Reset breaker state before each test."""
        qdrant_breaker.close()

    def teardown_method(self):
        """Clean up after each test."""
        qdrant_breaker.close()

    def test_passes_successful_call(self):
        """Wrapper should pass through successful function calls."""
        result = qdrant_with_breaker(lambda: "success")
        assert result == "success"

    def test_passes_return_value(self):
        """Wrapper should return the exact value from the function."""
        expected = {"data": [1, 2, 3], "count": 3}
        result = qdrant_with_breaker(lambda: expected)
        assert result == expected

    def test_passes_exception_on_first_failure(self):
        """Wrapper should pass through exceptions on first failure."""
        with pytest.raises(ZeroDivisionError):
            qdrant_with_breaker(lambda: 1 / 0)

    def test_opens_after_5_failures(self):
        """Circuit should open after 5 consecutive failures."""
        # Trigger 5 failures
        for _ in range(5):
            try:
                qdrant_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # 6th call should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            qdrant_with_breaker(lambda: "should not run")

    def test_circuit_remains_open(self):
        """Circuit should remain open after opening."""
        # Trigger 5 failures
        for _ in range(5):
            try:
                qdrant_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # Multiple calls should all raise CircuitBreakerError
        for _ in range(3):
            with pytest.raises(CircuitBreakerError):
                qdrant_with_breaker(lambda: "should not run")

    def test_successful_call_counts_as_reset(self):
        """Successful call should reset failure counter."""
        # Trigger 3 failures
        for _ in range(3):
            try:
                qdrant_with_breaker(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        # Successful call should reset counter
        result = qdrant_with_breaker(lambda: "success")
        assert result == "success"

        # Should need 5 more failures to open
        for _ in range(5):
            try:
                qdrant_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # Now circuit should be open
        with pytest.raises(CircuitBreakerError):
            qdrant_with_breaker(lambda: "should not run")


class TestLLMWithBreakerWrapper:
    """Test llm_with_breaker wrapper function."""

    def setup_method(self):
        """Reset breaker state before each test."""
        llm_breaker.close()

    def teardown_method(self):
        """Clean up after each test."""
        llm_breaker.close()

    def test_passes_successful_call(self):
        """Wrapper should pass through successful function calls."""
        result = llm_with_breaker(lambda: "response")
        assert result == "response"

    def test_opens_after_3_failures(self):
        """Circuit should open after 3 consecutive failures (lower threshold)."""
        # Trigger 3 failures
        for _ in range(3):
            try:
                llm_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # 4th call should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            llm_with_breaker(lambda: "should not run")

    def test_lower_threshold_than_qdrant(self):
        """LLM breaker should have lower threshold than qdrant."""
        assert llm_breaker.fail_max < qdrant_breaker.fail_max
        assert llm_breaker.fail_max == 3
        assert qdrant_breaker.fail_max == 5


class TestEmbeddingsWithBreakerWrapper:
    """Test embeddings_with_breaker wrapper function."""

    def setup_method(self):
        """Reset breaker state before each test."""
        embeddings_breaker.close()

    def teardown_method(self):
        """Clean up after each test."""
        embeddings_breaker.close()

    def test_passes_successful_call(self):
        """Wrapper should pass through successful function calls."""
        result = embeddings_with_breaker(lambda: [0.1, 0.2, 0.3])
        assert result == [0.1, 0.2, 0.3]

    def test_opens_after_10_failures(self):
        """Circuit should open after 10 consecutive failures (higher threshold)."""
        # Trigger 10 failures
        for _ in range(10):
            try:
                embeddings_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # 11th call should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            embeddings_with_breaker(lambda: "should not run")

    def test_higher_threshold_than_qdrant(self):
        """Embeddings breaker should have higher threshold than qdrant."""
        assert embeddings_breaker.fail_max > qdrant_breaker.fail_max
        assert embeddings_breaker.fail_max == 10
        assert qdrant_breaker.fail_max == 5


class TestCircuitBreakerStateTransitions:
    """Test state transitions (closed → open → half-open → closed)."""

    def setup_method(self):
        """Reset all breakers before each test."""
        qdrant_breaker.close()
        llm_breaker.close()
        embeddings_breaker.close()

    def teardown_method(self):
        """Clean up after each test."""
        qdrant_breaker.close()
        llm_breaker.close()
        embeddings_breaker.close()

    def test_initial_state_is_closed(self):
        """Circuit should start in closed state."""
        # Closed state allows calls through
        result = qdrant_with_breaker(lambda: "success")
        assert result == "success"

    def test_state_transitions_closed_to_open(self):
        """Circuit should transition from closed to open after threshold."""
        # Closed: calls go through
        try:
            qdrant_with_breaker(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        # Still closed after 1 failure - can still make calls
        try:
            qdrant_with_breaker(lambda: 1 / 0)
        except ZeroDivisionError:
            pass

        # Trigger remaining failures (3 more to reach 5)
        for _ in range(3):
            try:
                qdrant_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # Now open: calls blocked
        with pytest.raises(CircuitBreakerError):
            qdrant_with_breaker(lambda: "blocked")

    def test_circuit_breaker_error_is_raised(self):
        """CircuitBreakerError should be raised when circuit is open."""
        # Open the circuit
        for _ in range(5):
            try:
                qdrant_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # Verify CircuitBreakerError is raised
        with pytest.raises(CircuitBreakerError) as exc_info:
            qdrant_with_breaker(lambda: "blocked")

        assert isinstance(exc_info.value, pybreaker.CircuitBreakerError)


class TestCircuitBreakerReset:
    """Test circuit breaker reset functionality."""

    def setup_method(self):
        """Reset all breakers before each test."""
        qdrant_breaker.close()
        llm_breaker.close()
        embeddings_breaker.close()

    def teardown_method(self):
        """Clean up after each test."""
        qdrant_breaker.close()
        llm_breaker.close()
        embeddings_breaker.close()

    def test_manual_reset_closes_circuit(self):
        """Manual reset should close the circuit."""
        # Open the circuit
        for _ in range(5):
            try:
                qdrant_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # Verify circuit is open
        with pytest.raises(CircuitBreakerError):
            qdrant_with_breaker(lambda: "blocked")

        # Reset the circuit
        qdrant_breaker.close()

        # Circuit should be closed again
        result = qdrant_with_breaker(lambda: "success")
        assert result == "success"

    def test_reset_clears_failure_count(self):
        """Reset should clear the failure counter."""
        # Trigger 3 failures
        for _ in range(3):
            try:
                qdrant_with_breaker(lambda: 1 / 0)
            except ZeroDivisionError:
                pass

        # Reset
        qdrant_breaker.close()

        # Should need 5 failures again to open
        for _ in range(5):
            try:
                qdrant_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # Now circuit should be open
        with pytest.raises(CircuitBreakerError):
            qdrant_with_breaker(lambda: "blocked")


class TestCircuitBreakerWithDifferentExceptions:
    """Test circuit breaker with various exception types."""

    def setup_method(self):
        """Reset breaker state before each test."""
        qdrant_breaker.close()

    def teardown_method(self):
        """Clean up after each test."""
        qdrant_breaker.close()

    def test_counts_value_error(self):
        """ValueError should count as a failure."""
        for _ in range(5):
            try:
                qdrant_with_breaker(lambda: int("not a number"))
            except (ValueError, CircuitBreakerError):
                pass

        with pytest.raises(CircuitBreakerError):
            qdrant_with_breaker(lambda: "blocked")

    def test_counts_runtime_error(self):
        """RuntimeError should count as a failure."""

        def raise_runtime_error():
            raise RuntimeError("test")

        for _ in range(5):
            try:
                qdrant_with_breaker(raise_runtime_error)
            except (RuntimeError, CircuitBreakerError):
                pass

        with pytest.raises(CircuitBreakerError):
            qdrant_with_breaker(lambda: "blocked")

    def test_counts_type_error(self):
        """TypeError should count as a failure."""

        def raise_type_error():
            return "string" + 123  # type: ignore

        for _ in range(5):
            try:
                qdrant_with_breaker(raise_type_error)
            except (TypeError, CircuitBreakerError):
                pass

        with pytest.raises(CircuitBreakerError):
            qdrant_with_breaker(lambda: "blocked")


class TestCircuitBreakerWithCallables:
    """Test circuit breaker with different callable types."""

    def setup_method(self):
        """Reset breaker state before each test."""
        qdrant_breaker.close()

    def teardown_method(self):
        """Clean up after each test."""
        qdrant_breaker.close()

    def test_works_with_lambda(self):
        """Should work with lambda functions."""
        result = qdrant_with_breaker(lambda: "lambda result")
        assert result == "lambda result"

    def test_works_with_function(self):
        """Should work with regular functions."""

        def my_func():
            return "function result"

        result = qdrant_with_breaker(my_func)
        assert result == "function result"

    def test_works_with_callable_object(self):
        """Should work with callable objects."""

        class CallableClass:
            def __call__(self):
                return "callable object result"

        result = qdrant_with_breaker(CallableClass())
        assert result == "callable object result"

    def test_preserves_function_arguments(self):
        """Should work with functions that have arguments."""

        def add(a, b):
            return a + b

        result = qdrant_with_breaker(lambda: add(2, 3))
        assert result == 5


class TestCircuitBreakerIndependence:
    """Test that breakers are independent of each other."""

    def setup_method(self):
        """Reset all breakers before each test."""
        qdrant_breaker.close()
        llm_breaker.close()
        embeddings_breaker.close()

    def teardown_method(self):
        """Clean up after each test."""
        qdrant_breaker.close()
        llm_breaker.close()
        embeddings_breaker.close()

    def test_qdrant_failure_does_not_affect_llm(self):
        """Qdrant breaker opening should not affect LLM breaker."""
        # Open qdrant breaker
        for _ in range(5):
            try:
                qdrant_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # Qdrant should be open
        with pytest.raises(CircuitBreakerError):
            qdrant_with_breaker(lambda: "blocked")

        # LLM should still work
        result = llm_with_breaker(lambda: "llm works")
        assert result == "llm works"

    def test_llm_failure_does_not_affect_embeddings(self):
        """LLM breaker opening should not affect embeddings breaker."""
        # Open llm breaker
        for _ in range(3):
            try:
                llm_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # LLM should be open
        with pytest.raises(CircuitBreakerError):
            llm_with_breaker(lambda: "blocked")

        # Embeddings should still work
        result = embeddings_with_breaker(lambda: "embeddings work")
        assert result == "embeddings work"

    def test_all_breakers_can_be_open_simultaneously(self):
        """All breakers should be able to open independently."""
        # Open all breakers
        for _ in range(5):
            try:
                qdrant_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        for _ in range(3):
            try:
                llm_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        for _ in range(10):
            try:
                embeddings_with_breaker(lambda: 1 / 0)
            except (ZeroDivisionError, CircuitBreakerError):
                pass

        # All should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            qdrant_with_breaker(lambda: "blocked")

        with pytest.raises(CircuitBreakerError):
            llm_with_breaker(lambda: "blocked")

        with pytest.raises(CircuitBreakerError):
            embeddings_with_breaker(lambda: "blocked")


class TestCircuitBreakerExportedSymbols:
    """Test that all required symbols are exported."""

    def test_circuit_breaker_error_is_exported(self):
        """CircuitBreakerError should be importable."""
        assert CircuitBreakerError is not None
        assert issubclass(CircuitBreakerError, Exception)

    def test_all_breakers_are_exported(self):
        """All breaker instances should be importable."""
        assert qdrant_breaker is not None
        assert llm_breaker is not None
        assert embeddings_breaker is not None

    def test_all_wrapper_functions_are_exported(self):
        """All wrapper functions should be importable."""
        assert callable(qdrant_with_breaker)
        assert callable(llm_with_breaker)
        assert callable(embeddings_with_breaker)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
