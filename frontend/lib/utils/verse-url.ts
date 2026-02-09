/**
 * Builds a verse page URL from a raw citation reference string.
 * Used when verse_details is unavailable (LLM cited a verse not in search results).
 *
 * Bible format: "BookName Chapter:Verse" -> /bible/{book_nr}?chapter={chapter}&verse={verse}
 * Quran format: "SurahName:VerseId"     -> /quran/{surah_id}?verse={verse}
 */

const BIBLE_BOOK_NR: Record<string, number> = {
  // Old Testament (1-39)
  Genesis: 1,
  Exodus: 2,
  Leviticus: 3,
  Numbers: 4,
  Deuteronomy: 5,
  Joshua: 6,
  Judges: 7,
  Ruth: 8,
  "1 Samuel": 9,
  "2 Samuel": 10,
  "1 Kings": 11,
  "2 Kings": 12,
  "1 Chronicles": 13,
  "2 Chronicles": 14,
  Ezra: 15,
  Nehemiah: 16,
  Esther: 17,
  Job: 18,
  Psalms: 19,
  Proverbs: 20,
  Ecclesiastes: 21,
  "Song of Solomon": 22,
  Isaiah: 23,
  Jeremiah: 24,
  Lamentations: 25,
  Ezekiel: 26,
  Daniel: 27,
  Hosea: 28,
  Joel: 29,
  Amos: 30,
  Obadiah: 31,
  Jonah: 32,
  Micah: 33,
  Nahum: 34,
  Habakkuk: 35,
  Zephaniah: 36,
  Haggai: 37,
  Zechariah: 38,
  Malachi: 39,
  // New Testament (40-66)
  Matthew: 40,
  Mark: 41,
  Luke: 42,
  John: 43,
  Acts: 44,
  Romans: 45,
  "1 Corinthians": 46,
  "2 Corinthians": 47,
  Galatians: 48,
  Ephesians: 49,
  Philippians: 50,
  Colossians: 51,
  "1 Thessalonians": 52,
  "2 Thessalonians": 53,
  "1 Timothy": 54,
  "2 Timothy": 55,
  Titus: 56,
  Philemon: 57,
  Hebrews: 58,
  James: 59,
  "1 Peter": 60,
  "2 Peter": 61,
  "1 John": 62,
  "2 John": 63,
  "3 John": 64,
  Jude: 65,
  "Revelation of John": 66,
  // Apocrypha (67-81)
  "1 Esdras": 67,
  "2 Esdras": 68,
  Tobit: 69,
  Judith: 70,
  "Additions to Esther": 71,
  Wisdom: 73,
  Sirach: 74,
  Baruch: 75,
  "Prayer of Azariah": 76,
  Susanna: 77,
  "Bel and the Dragon": 78,
  "Prayer of Manasses": 79,
  "1 Maccabees": 80,
  "2 Maccabees": 81,
};

const QURAN_SURAH_ID: Record<string, number> = {
  "Fatiha": 1,
  "Bakara": 2,
  "Ali Imran": 3,
  "Nisa": 4,
  "Maide": 5,
  "En'am": 6,
  "A'raf": 7,
  "Enfal": 8,
  "Tevbe": 9,
  "Yunus": 10,
  "Hud": 11,
  "Yusuf": 12,
  "Ra'd": 13,
  "Ibrahim": 14,
  "Hicr": 15,
  "Nahl": 16,
  "Isra": 17,
  "Kehf": 18,
  "Meryem": 19,
  "Taha": 20,
  "Enbiya": 21,
  "Hac": 22,
  "Mu'minun": 23,
  "Nur": 24,
  "Furkan": 25,
  "Suara": 26,
  "Neml": 27,
  "Kasas": 28,
  "Ankebut": 29,
  "Rum": 30,
  "Lokman": 31,
  "Secde": 32,
  "Ahzab": 33,
  "Sebe'": 34,
  "Fatir": 35,
  "Yasin": 36,
  "Saffat": 37,
  "Sad": 38,
  "Zumer": 39,
  "Mu'min": 40,
  "Fussilet": 41,
  "Sura": 42,
  "Zuhruf": 43,
  "Duhan": 44,
  "Casiye": 45,
  "Ahkaf": 46,
  "Muhammed": 47,
  "Fetih": 48,
  "Hucurat": 49,
  "Kaf": 50,
  "Zariyat": 51,
  "Tur": 52,
  "Necm": 53,
  "Kamer": 54,
  "Rahman": 55,
  "Vakia": 56,
  "Hadid": 57,
  "Mucadele": 58,
  "Hasr": 59,
  "Mumtehine": 60,
  "Saf": 61,
  "Cuma": 62,
  "Munafikun": 63,
  "Tegabun": 64,
  "Talak": 65,
  "Tahrim": 66,
  "Mulk": 67,
  "Kalem": 68,
  "Hakka": 69,
  "Mearic": 70,
  "Nuh": 71,
  "Cin": 72,
  "Muzzemmil": 73,
  "Muddessir": 74,
  "Kiyamet": 75,
  "Insan": 76,
  "Murselat": 77,
  "Nebe": 78,
  "Naziat": 79,
  "Abese": 80,
  "Tekvir": 81,
  "Infitar": 82,
  "Mutaffifin": 83,
  "Insikak": 84,
  "Buruc": 85,
  "Tarik": 86,
  "A'la": 87,
  "Gasiye": 88,
  "Fecr": 89,
  "Beled": 90,
  "Sems": 91,
  "Leyl": 92,
  "Duha": 93,
  "Insirah": 94,
  "Tin": 95,
  "Alak": 96,
  "Kadir": 97,
  "Beyyine": 98,
  "Zilzal": 99,
  "Adiyat": 100,
  "Karia": 101,
  "Tekasur": 102,
  "Asr": 103,
  "Humeze": 104,
  "Fil": 105,
  "Kureys": 106,
  "Maun": 107,
  "Kevser": 108,
  "Kafirun": 109,
  "Nasr": 110,
  "Tebbet": 111,
  "Ihlas": 112,
  "Felak": 113,
  "Nas": 114,
};

function stripDiacritics(value: string): string {
  return value
    .replace(/[âÂ]/g, "a")
    .replace(/[îÎ]/g, "i")
    .replace(/[ûÛ]/g, "u")
    .replace(/[ôÔ]/g, "o")
    .replace(/[êÊ]/g, "e")
    .replace(/[şŞ]/g, "s")
    .replace(/[çÇ]/g, "c")
    .replace(/[öÖ]/g, "o")
    .replace(/[üÜ]/g, "u")
    .replace(/[ğĞ]/g, "g")
    .replace(/[ıI]/g, "i")
    .replace(/[İ]/g, "i")
    .replace(/[']/g, "'");
}

const QURAN_NORMALIZED: Array<[string, number]> = Object.entries(QURAN_SURAH_ID).map(
  ([name, id]) => [stripDiacritics(name).toLowerCase(), id]
);

function lookupBibleBookNr(bookName: string): number | null {
  return BIBLE_BOOK_NR[bookName] ?? null;
}

function lookupQuranSurahId(surahName: string): number | null {
  const exactMatch = QURAN_SURAH_ID[surahName];
  if (exactMatch !== undefined) {
    return exactMatch;
  }

  const normalizedName = stripDiacritics(surahName).toLowerCase();
  const normalizedMatch = QURAN_NORMALIZED.find(([name]) => name === normalizedName);
  return normalizedMatch ? normalizedMatch[1] : null;
}

/**
 * Parse a citation reference string and return a verse page URL.
 * Returns null if the reference cannot be resolved.
 *
 * @example
 * buildUrlFromReference("1 Corinthians 15:46") -> "/bible/46?chapter=15&verse=46"
 * buildUrlFromReference("Bakara:153") -> "/quran/2?verse=153"
 */
export function buildUrlFromReference(reference: string): string | null {
  const bibleMatch = reference.match(/^(.+)\s+(\d+):(\d+)$/);
  if (bibleMatch) {
    const [, bookName, chapter, verse] = bibleMatch;
    const bookNr = lookupBibleBookNr(bookName);
    if (bookNr !== null) {
      return `/bible/${bookNr}?chapter=${chapter}&verse=${verse}`;
    }
  }

  const quranMatch = reference.match(/^(.+):(\d+)$/);
  if (quranMatch) {
    const [, surahName, verse] = quranMatch;
    const surahId = lookupQuranSurahId(surahName);
    if (surahId !== null) {
      return `/quran/${surahId}?verse=${verse}`;
    }
  }

  return null;
}
