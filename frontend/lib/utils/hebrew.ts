/**
 * Strip Hebrew diacritical marks (nikud/cantillation) from text.
 *
 * Removes Unicode ranges:
 *  - U+0591-U+05BD (cantillation marks and nikud)
 *  - U+05BF-U+05C7 (additional vowel marks)
 * Preserves U+05BE (Maqaf/hyphen).
 */
const HEBREW_DIACRITICS_RE = /[\u0591-\u05BD\u05BF-\u05C7]/g

export function stripHebrewDiacritics(text: string): string {
  return text.replace(HEBREW_DIACRITICS_RE, "")
}
