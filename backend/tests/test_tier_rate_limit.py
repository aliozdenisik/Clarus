from __future__ import annotations

import inspect

from app.api.auth import check_rate_limit


class TestCheckRateLimitSourceContainsGetTier:
    def test_source_references_get_tier(self) -> None:
        source = inspect.getsource(check_rate_limit)
        assert "get_tier" in source


class TestCheckRateLimitSignature:
    def test_signature_is_user_db_locale(self) -> None:
        sig = inspect.signature(check_rate_limit)
        params = list(sig.parameters.keys())

        assert params[0] == "user"
        assert params[1] == "db"
        assert params[2] == "locale"
        assert sig.parameters["locale"].default == "tr"
