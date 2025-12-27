"""
Turkish Text Normalization Utilities

Provides text normalization for Turkish search queries.
Handles ş/s, ü/u, ö/o, ç/c, ğ/g, ı/i character mappings.
"""


# Turkish character mappings
TURKISH_CHAR_MAP = {
    'ş': 's', 'Ş': 'S',
    'ü': 'u', 'Ü': 'U',
    'ö': 'o', 'Ö': 'O',
    'ç': 'c', 'Ç': 'C',
    'ğ': 'g', 'Ğ': 'G',
    'ı': 'i', 'İ': 'I',
}

# Reverse mapping for expansion
TURKISH_CHAR_REVERSE = {v: k for k, v in TURKISH_CHAR_MAP.items() if v.islower()}


def normalize_turkish(text: str) -> str:
    """
    Normalize Turkish characters to ASCII equivalents.
    
    Args:
        text: Input text with Turkish characters
        
    Returns:
        Text with Turkish characters replaced by ASCII equivalents
        
    Example:
        >>> normalize_turkish("şükür")
        "sukur"
    """
    result = text
    for tr_char, ascii_char in TURKISH_CHAR_MAP.items():
        result = result.replace(tr_char, ascii_char)
    return result


def expand_turkish_query(query: str) -> str:
    """
    Expand query to include both Turkish and ASCII variants.
    
    Args:
        query: Search query
        
    Returns:
        Query expanded with Turkish character variants
        
    Example:
        >>> expand_turkish_query("sukur")
        "sukur şükür"
    """
    words = query.split()
    expanded_words = set(words)
    
    for word in words:
        # Add normalized version
        normalized = normalize_turkish(word)
        expanded_words.add(normalized)
        
        # Add Turkish version (reverse)
        turkish_version = word.lower()
        for ascii_char, tr_char in TURKISH_CHAR_REVERSE.items():
            turkish_version = turkish_version.replace(ascii_char, tr_char)
        if turkish_version != word.lower():
            expanded_words.add(turkish_version)
    
    return ' '.join(expanded_words)


def create_search_variants(query: str) -> list:
    """
    Create multiple search variants for a Turkish query.
    
    Args:
        query: Original search query
        
    Returns:
        List of query variants to search
        
    Example:
        >>> create_search_variants("şükür etmek")
        ["şükür etmek", "sukur etmek", "şükür", "sukur"]
    """
    variants = [query]
    
    # Add normalized version
    normalized = normalize_turkish(query)
    if normalized != query:
        variants.append(normalized)
    
    # Add individual word variants
    words = query.split()
    if len(words) > 1:
        for word in words:
            if word not in variants:
                variants.append(word)
            norm_word = normalize_turkish(word)
            if norm_word != word and norm_word not in variants:
                variants.append(norm_word)
    
    return variants


if __name__ == "__main__":
    print("Turkish Text Normalization Test")
    print("=" * 40)
    
    test_cases = [
        "şükür",
        "Allah'ın rahmeti",
        "sabır ve namaz",
        "öğrenmek",
        "çalışmak"
    ]
    
    for text in test_cases:
        print(f"\nOriginal: {text}")
        print(f"Normalized: {normalize_turkish(text)}")
        print(f"Expanded: {expand_turkish_query(text)}")
        print(f"Variants: {create_search_variants(text)}")
