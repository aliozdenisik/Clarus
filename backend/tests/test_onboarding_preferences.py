"""
Tests for onboarding preferences API schema validation and helper functions.

Tests cover:
- PreferencesUpdate Pydantic v2 schema validation (valid/invalid values)
- Default preferences values (_get_default_preferences)
- Preferences-to-dict conversion (_preferences_to_dict)

Does NOT test API endpoints or require running services.
"""

import sys
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

# Add backend to path for imports
sys.path.insert(0, "/home/freyja/qdrant/backend")

from app.api.preferences import PreferencesUpdate, _get_default_preferences, _preferences_to_dict


class TestUsagePurposeValidation:
    """Test usage_purpose field validation."""

    def test_valid_usage_purpose_academic(self):
        """academic is a valid usage_purpose value."""
        obj = PreferencesUpdate.model_validate({"usage_purpose": "academic"})
        assert obj.usage_purpose == "academic"

    def test_valid_usage_purpose_personal(self):
        """personal is a valid usage_purpose value."""
        obj = PreferencesUpdate.model_validate({"usage_purpose": "personal"})
        assert obj.usage_purpose == "personal"

    def test_valid_usage_purpose_preaching(self):
        """preaching is a valid usage_purpose value."""
        obj = PreferencesUpdate.model_validate({"usage_purpose": "preaching"})
        assert obj.usage_purpose == "preaching"

    def test_valid_usage_purpose_comparative(self):
        """comparative is a valid usage_purpose value."""
        obj = PreferencesUpdate.model_validate({"usage_purpose": "comparative"})
        assert obj.usage_purpose == "comparative"

    def test_valid_usage_purpose_textual(self):
        """textual is a valid usage_purpose value."""
        obj = PreferencesUpdate.model_validate({"usage_purpose": "textual"})
        assert obj.usage_purpose == "textual"

    def test_valid_usage_purpose_none(self):
        """None is accepted (field is optional)."""
        obj = PreferencesUpdate.model_validate({"usage_purpose": None})
        assert obj.usage_purpose is None

    def test_usage_purpose_defaults_to_none(self):
        """usage_purpose defaults to None when not provided."""
        obj = PreferencesUpdate.model_validate({})
        assert obj.usage_purpose is None

    def test_invalid_usage_purpose_rejected(self):
        """Invalid usage_purpose raises ValidationError."""
        with pytest.raises(ValidationError):
            PreferencesUpdate.model_validate({"usage_purpose": "entertainment"})

    def test_invalid_usage_purpose_random_string_rejected(self):
        """Arbitrary string is rejected for usage_purpose."""
        with pytest.raises(ValidationError):
            PreferencesUpdate.model_validate({"usage_purpose": "random_value"})

    def test_invalid_usage_purpose_uppercase_rejected(self):
        """Uppercase version is rejected (pattern is case-sensitive)."""
        with pytest.raises(ValidationError):
            PreferencesUpdate.model_validate({"usage_purpose": "ACADEMIC"})


class TestArabicProficiencyValidation:
    """Test arabic_proficiency field validation."""

    def test_valid_arabic_proficiency_none_value(self):
        """'none' string is a valid arabic_proficiency value."""
        obj = PreferencesUpdate.model_validate({"arabic_proficiency": "none"})
        assert obj.arabic_proficiency == "none"

    def test_valid_arabic_proficiency_basic(self):
        """basic is a valid arabic_proficiency value."""
        obj = PreferencesUpdate.model_validate({"arabic_proficiency": "basic"})
        assert obj.arabic_proficiency == "basic"

    def test_valid_arabic_proficiency_intermediate(self):
        """intermediate is a valid arabic_proficiency value."""
        obj = PreferencesUpdate.model_validate({"arabic_proficiency": "intermediate"})
        assert obj.arabic_proficiency == "intermediate"

    def test_valid_arabic_proficiency_advanced(self):
        """advanced is a valid arabic_proficiency value."""
        obj = PreferencesUpdate.model_validate({"arabic_proficiency": "advanced"})
        assert obj.arabic_proficiency == "advanced"

    def test_arabic_proficiency_null_accepted(self):
        """Null/None is accepted for arabic_proficiency."""
        obj = PreferencesUpdate.model_validate({"arabic_proficiency": None})
        assert obj.arabic_proficiency is None

    def test_arabic_proficiency_defaults_to_none(self):
        """arabic_proficiency defaults to None when not provided."""
        obj = PreferencesUpdate.model_validate({})
        assert obj.arabic_proficiency is None

    def test_invalid_arabic_proficiency_rejected(self):
        """Invalid arabic_proficiency raises ValidationError."""
        with pytest.raises(ValidationError):
            PreferencesUpdate.model_validate({"arabic_proficiency": "expert"})

    def test_invalid_arabic_proficiency_fluent_rejected(self):
        """'fluent' is not a valid arabic_proficiency value."""
        with pytest.raises(ValidationError):
            PreferencesUpdate.model_validate({"arabic_proficiency": "fluent"})


class TestInterestsValidation:
    """Test interests field validation."""

    def test_interests_accepts_list_of_strings(self):
        """interests accepts a list of strings."""
        obj = PreferencesUpdate.model_validate({"interests": ["prayer", "fasting", "wisdom"]})
        assert obj.interests == ["prayer", "fasting", "wisdom"]

    def test_interests_accepts_empty_list(self):
        """interests accepts an empty list."""
        obj = PreferencesUpdate.model_validate({"interests": []})
        assert obj.interests == []

    def test_interests_accepts_single_item_list(self):
        """interests accepts a list with a single string."""
        obj = PreferencesUpdate.model_validate({"interests": ["theology"]})
        assert obj.interests == ["theology"]

    def test_interests_accepts_none(self):
        """None is accepted for interests (field is optional)."""
        obj = PreferencesUpdate.model_validate({"interests": None})
        assert obj.interests is None

    def test_interests_defaults_to_none(self):
        """interests defaults to None when not provided."""
        obj = PreferencesUpdate.model_validate({})
        assert obj.interests is None


class TestOnboardingCompletedValidation:
    """Test onboarding_completed field validation."""

    def test_onboarding_completed_true(self):
        """True is a valid onboarding_completed value."""
        obj = PreferencesUpdate.model_validate({"onboarding_completed": True})
        assert obj.onboarding_completed is True

    def test_onboarding_completed_false(self):
        """False is a valid onboarding_completed value."""
        obj = PreferencesUpdate.model_validate({"onboarding_completed": False})
        assert obj.onboarding_completed is False

    def test_onboarding_completed_none_accepted(self):
        """None is accepted for onboarding_completed."""
        obj = PreferencesUpdate.model_validate({"onboarding_completed": None})
        assert obj.onboarding_completed is None

    def test_onboarding_completed_defaults_to_none(self):
        """onboarding_completed defaults to None when not provided."""
        obj = PreferencesUpdate.model_validate({})
        assert obj.onboarding_completed is None


class TestDefaultPreferences:
    """Test _get_default_preferences() helper function."""

    def test_default_preferences_include_usage_purpose(self):
        """Default preferences include usage_purpose field set to None."""
        defaults = _get_default_preferences()
        assert "usage_purpose" in defaults
        assert defaults["usage_purpose"] is None

    def test_default_preferences_include_arabic_proficiency(self):
        """Default preferences include arabic_proficiency field set to 'none'."""
        defaults = _get_default_preferences()
        assert "arabic_proficiency" in defaults
        assert defaults["arabic_proficiency"] == "none"

    def test_default_preferences_include_interests(self):
        """Default preferences include interests field as empty list."""
        defaults = _get_default_preferences()
        assert "interests" in defaults
        assert defaults["interests"] == []

    def test_default_preferences_include_onboarding_completed(self):
        """Default preferences include onboarding_completed field set to False."""
        defaults = _get_default_preferences()
        assert "onboarding_completed" in defaults
        assert defaults["onboarding_completed"] is False

    def test_default_preferences_existing_fields_intact(self):
        """Existing fields remain correct in defaults."""
        defaults = _get_default_preferences()
        assert defaults["theme"] == "system"
        assert defaults["language"] == "tr"
        assert defaults["default_search_source"] == "quran"
        assert defaults["results_per_page"] == 10
        assert defaults["enable_streaming"] is True
        assert defaults["enable_multi_agent"] is True

    def test_default_preferences_returns_dict(self):
        """_get_default_preferences returns a dictionary."""
        defaults = _get_default_preferences()
        assert isinstance(defaults, dict)


class TestPreferencesToDict:
    """Test _preferences_to_dict() helper function."""

    def _make_mock_prefs(self, **kwargs) -> MagicMock:
        """Create a mock UserPreferences object with default values."""
        prefs = MagicMock()
        prefs.theme = kwargs.get("theme", "system")
        prefs.language = kwargs.get("language", "tr")
        prefs.default_search_source = kwargs.get("default_search_source", "quran")
        prefs.default_bible_testament = kwargs.get("default_bible_testament")
        prefs.results_per_page = kwargs.get("results_per_page", 10)
        prefs.enable_streaming = kwargs.get("enable_streaming", True)
        prefs.enable_multi_agent = kwargs.get("enable_multi_agent", True)
        prefs.custom_settings = kwargs.get("custom_settings")
        prefs.usage_purpose = kwargs.get("usage_purpose")
        prefs.arabic_proficiency = kwargs.get("arabic_proficiency", "none")
        prefs.interests = kwargs.get("interests", [])
        prefs.onboarding_completed = kwargs.get("onboarding_completed", False)
        prefs.updated_at = kwargs.get("updated_at")
        return prefs

    def test_preferences_to_dict_includes_usage_purpose(self):
        """_preferences_to_dict includes usage_purpose field."""
        prefs = self._make_mock_prefs(usage_purpose="academic")
        result = _preferences_to_dict(prefs)
        assert "usage_purpose" in result
        assert result["usage_purpose"] == "academic"

    def test_preferences_to_dict_includes_arabic_proficiency(self):
        """_preferences_to_dict includes arabic_proficiency field."""
        prefs = self._make_mock_prefs(arabic_proficiency="intermediate")
        result = _preferences_to_dict(prefs)
        assert "arabic_proficiency" in result
        assert result["arabic_proficiency"] == "intermediate"

    def test_preferences_to_dict_includes_interests(self):
        """_preferences_to_dict includes interests field."""
        prefs = self._make_mock_prefs(interests=["prayer", "fasting"])
        result = _preferences_to_dict(prefs)
        assert "interests" in result
        assert result["interests"] == ["prayer", "fasting"]

    def test_preferences_to_dict_includes_onboarding_completed(self):
        """_preferences_to_dict includes onboarding_completed field."""
        prefs = self._make_mock_prefs(onboarding_completed=True)
        result = _preferences_to_dict(prefs)
        assert "onboarding_completed" in result
        assert result["onboarding_completed"] is True

    def test_preferences_to_dict_returns_dict(self):
        """_preferences_to_dict returns a dictionary."""
        prefs = self._make_mock_prefs()
        result = _preferences_to_dict(prefs)
        assert isinstance(result, dict)

    def test_preferences_to_dict_updated_at_none(self):
        """_preferences_to_dict handles updated_at=None correctly."""
        prefs = self._make_mock_prefs(updated_at=None)
        result = _preferences_to_dict(prefs)
        assert result["updated_at"] is None

    def test_preferences_to_dict_updated_at_isoformat(self):
        """_preferences_to_dict formats updated_at as ISO string when set."""
        now = datetime(2026, 2, 18, 12, 0, 0, tzinfo=UTC)
        prefs = self._make_mock_prefs(updated_at=now)
        result = _preferences_to_dict(prefs)
        assert result["updated_at"] == now.isoformat()

    def test_preferences_to_dict_all_new_fields_present(self):
        """_preferences_to_dict includes all four new onboarding fields."""
        prefs = self._make_mock_prefs()
        result = _preferences_to_dict(prefs)
        for field in ("usage_purpose", "arabic_proficiency", "interests", "onboarding_completed"):
            assert field in result, f"Missing field: {field}"


class TestPreferencesUpdateAllFields:
    """Test PreferencesUpdate accepts combined updates with new fields."""

    def test_full_onboarding_update_accepted(self):
        """Full onboarding update with all new fields is accepted."""
        obj = PreferencesUpdate.model_validate(
            {
                "usage_purpose": "academic",
                "arabic_proficiency": "intermediate",
                "interests": ["theology", "linguistics"],
                "onboarding_completed": True,
            }
        )
        assert obj.usage_purpose == "academic"
        assert obj.arabic_proficiency == "intermediate"
        assert obj.interests == ["theology", "linguistics"]
        assert obj.onboarding_completed is True

    def test_partial_onboarding_update_accepted(self):
        """Partial update with only onboarding_completed is accepted."""
        obj = PreferencesUpdate.model_validate({"onboarding_completed": True})
        assert obj.onboarding_completed is True
        assert obj.usage_purpose is None
        assert obj.arabic_proficiency is None

    def test_mixed_existing_and_new_fields_accepted(self):
        """Update mixing existing fields and new onboarding fields is accepted."""
        obj = PreferencesUpdate.model_validate(
            {
                "theme": "dark",
                "language": "en",
                "usage_purpose": "personal",
                "onboarding_completed": True,
            }
        )
        assert obj.theme == "dark"
        assert obj.language == "en"
        assert obj.usage_purpose == "personal"
        assert obj.onboarding_completed is True
