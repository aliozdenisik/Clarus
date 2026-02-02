/**
 * Strip Arabic diacritical marks (tashkeel/harakat) from text.
 *
 * First normalizes alef variants:
 *  - U+0670 (superscript alef) → U+0627 (regular alef)
 *  - U+0671 (alef wasla) → U+0627 (regular alef)
 *
 * Then removes Unicode ranges:
 *  - U+0610–U+061A  (Quranic annotations)
 *  - U+064B–U+065F  (standard harakat: fathah, dammah, kasrah, tanwin, shadda, sukun)
 *  - U+06D6–U+06DC  (Quranic marks)
 *  - U+06DF–U+06E8  (Quranic marks)
 *  - U+06EA–U+06ED  (Quranic marks)
 *  - U+08D3–U+08E1  (extended Arabic marks)
 *  - U+08E3–U+08FF  (extended Arabic marks)
 *  - U+FE70–U+FE7F  (Arabic presentation forms)
 */
const ALEF_NORMALIZATIONS: [RegExp, string][] = [
  [/\u0670/g, '\u0627'],  // superscript alef → regular alef
  [/\u0671/g, '\u0627'],  // alef wasla → regular alef
];

const ARABIC_DIACRITICS_RE =
  /[\u0610-\u061A\u064B-\u065F\u06D6-\u06DC\u06DF-\u06E8\u06EA-\u06ED\u08D3-\u08E1\u08E3-\u08FF\uFE70-\uFE7F]/g;

export function stripArabicDiacritics(text: string): string {
  let result = text;
  for (const [pattern, replacement] of ALEF_NORMALIZATIONS) {
    result = result.replace(pattern, replacement);
  }
  return result.replace(ARABIC_DIACRITICS_RE, "");
}
