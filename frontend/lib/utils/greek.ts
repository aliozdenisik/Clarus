/**
 * Strip Greek diacritical marks (polytonic accents) from text.
 *
 * Removes Unicode ranges:
 *  - U+0300–U+036F (combining diacritical marks)
 *  - U+1F00–U+1FFF (Greek extended - precomposed characters with diacritics)
 * Normalizes to NFD (decomposed form) first, then strips combining marks.
 */
const GREEK_DIACRITICS_RE = /[\u0300-\u036F]/g

export function stripGreekDiacritics(text: string): string {
  // Normalize to NFD (decomposed form) to separate base characters from diacritics
  return text.normalize("NFD").replace(GREEK_DIACRITICS_RE, "")
}
