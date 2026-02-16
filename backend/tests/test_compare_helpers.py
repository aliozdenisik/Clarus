from app.api.compare_helpers import VALID_COMPARE_COLLECTIONS, normalize_compare_collections


def test_normalize_compare_collections_maps_legacy_quran_alias_to_translator() -> None:
    result = normalize_compare_collections(["quran_tr", "bible_ot", "bible_nt"], "yazir")
    assert result == ["quran_tr_yazir", "bible_ot", "bible_nt"]


def test_normalize_compare_collections_deduplicates_while_preserving_order() -> None:
    result = normalize_compare_collections(
        ["quran_tr", "quran_tr_diyanet", "bible_ot", "bible_ot"],
        "diyanet",
    )
    assert result == ["quran_tr_diyanet", "bible_ot"]


def test_normalized_collections_are_valid_compare_collections() -> None:
    result = normalize_compare_collections(["quran_tr", "bible_apocrypha"], "vakfi")
    assert set(result).issubset(VALID_COMPARE_COLLECTIONS)
