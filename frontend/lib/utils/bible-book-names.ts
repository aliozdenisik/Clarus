/**
 * Turkish Bible book name mappings.
 * Book names in Qdrant and the metadata API are always English.
 * These maps provide Turkish equivalents for locale-aware display.
 */

/** Old Testament book names: English → Turkish */
export const TURKISH_OT_NAMES: Record<string, string> = {
  Genesis: "Yaratılış",
  Exodus: "Mısır'dan Çıkış",
  Leviticus: "Levililer",
  Numbers: "Çölde Sayım",
  Deuteronomy: "Yasa'nın Tekrarı",
  Joshua: "Yeşu",
  Judges: "Hâkimler",
  Ruth: "Rut",
  "1 Samuel": "1. Samuel",
  "2 Samuel": "2. Samuel",
  "1 Kings": "1. Krallar",
  "2 Kings": "2. Krallar",
  "1 Chronicles": "1. Tarihler",
  "2 Chronicles": "2. Tarihler",
  Ezra: "Ezra",
  Nehemiah: "Nehemya",
  Esther: "Ester",
  Job: "Eyüp",
  Psalms: "Mezmurlar",
  Proverbs: "Süleyman'ın Özdeyişleri",
  Ecclesiastes: "Vaiz",
  "Song of Solomon": "Ezgiler Ezgisi",
  "Song of Songs": "Ezgiler Ezgisi",
  Isaiah: "Yeşaya",
  Jeremiah: "Yeremya",
  Lamentations: "Ağıtlar",
  Ezekiel: "Hezekiel",
  Daniel: "Daniel",
  Hosea: "Hoşea",
  Joel: "Yoel",
  Amos: "Amos",
  Obadiah: "Ovadya",
  Jonah: "Yunus",
  Micah: "Mika",
  Nahum: "Nahum",
  Habakkuk: "Habakkuk",
  Zephaniah: "Sefanya",
  Haggai: "Hagay",
  Zechariah: "Zekeriya",
  Malachi: "Malaki",
}

/** New Testament book names: English → Turkish */
export const TURKISH_NT_NAMES: Record<string, string> = {
  Matthew: "Matta",
  Mark: "Markos",
  Luke: "Luka",
  John: "Yuhanna",
  Acts: "Elçilerin İşleri",
  Romans: "Romalılar",
  "1 Corinthians": "1. Korintliler",
  "2 Corinthians": "2. Korintliler",
  Galatians: "Galatyalılar",
  Ephesians: "Efesliler",
  Philippians: "Filipililer",
  Colossians: "Koloseliler",
  "1 Thessalonians": "1. Selanikliler",
  "2 Thessalonians": "2. Selanikliler",
  "1 Timothy": "1. Timoteos",
  "2 Timothy": "2. Timoteos",
  Titus: "Titus",
  Philemon: "Filimon",
  Hebrews: "İbraniler",
  James: "Yakup",
  "1 Peter": "1. Petrus",
  "2 Peter": "2. Petrus",
  "1 John": "1. Yuhanna",
  "2 John": "2. Yuhanna",
  "3 John": "3. Yuhanna",
  Jude: "Yahuda",
  Revelation: "Vahiy",
  "Revelation of John": "Vahiy",
}

/** Apocrypha book names: English → Turkish */
export const TURKISH_APOCRYPHA_NAMES: Record<string, string> = {
  "1 Esdras": "1. Esdras",
  "2 Esdras": "2. Esdras",
  Tobit: "Tobit",
  Judith: "Yudit",
  "Additions to Esther": "Ester'e Ekler",
  "Wisdom of Solomon": "Süleyman'ın Bilgeliği",
  Wisdom: "Süleyman'ın Bilgeliği",
  Sirach: "Sirak",
  Baruch: "Baruk",
  "Letter of Jeremiah": "Yeremya'nın Mektubu",
  "Prayer of Azariah": "Azarya'nın Duası",
  Susanna: "Suzanna",
  "Bel and the Dragon": "Bel ve Ejderha",
  "Prayer of Manasseh": "Manaşşe'nin Duası",
  "Prayer of Manasses": "Manaşşe'nin Duası",
  "1 Maccabees": "1. Makabeler",
  "2 Maccabees": "2. Makabeler",
}

/** Combined lookup across all testaments */
export const ALL_TURKISH_BOOK_NAMES: Record<string, string> = {
  ...TURKISH_OT_NAMES,
  ...TURKISH_NT_NAMES,
  ...TURKISH_APOCRYPHA_NAMES,
}

/**
 * Get the display name for a Bible book based on locale.
 * Returns Turkish name when locale is "tr", original English name otherwise.
 */
export function getBibleBookDisplayName(englishName: string, locale: string): string {
  if (locale === "tr") {
    return ALL_TURKISH_BOOK_NAMES[englishName] || englishName
  }
  return englishName
}

const BIBLE_REFERENCE_PATTERN = /^(.+?)\s+(\d+:\d+(?:-\d+)?)$/

export function localizeBibleReference(reference: string, locale: string): string {
  if (locale !== "tr") {
    return reference
  }

  const match = reference.trim().match(BIBLE_REFERENCE_PATTERN)
  if (!match) {
    return reference
  }

  const [, bookName, versePart] = match
  const localizedBookName = getBibleBookDisplayName(bookName, locale)
  return `${localizedBookName} ${versePart}`
}
