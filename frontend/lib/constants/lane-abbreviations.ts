export interface LaneAbbreviation {
  abbreviation: string
  category: "Source" | "Grammar" | "Reference" | "Semantics"
  meaning_en: string
  meaning_tr: string
}

export const LANE_ABBREVIATIONS: LaneAbbreviation[] = [
  {
    abbreviation: "S",
    category: "Source",
    meaning_en: "The Siháh (Es-Sihâh) by El-Jowharee",
    meaning_tr: "Es-Sıhâh (el-Cevherî) — Temel Arapça Sözlük",
  },
  {
    abbreviation: "K",
    category: "Source",
    meaning_en: "The Kámoos (El-Kâmûs) by El-Feiroozábádee",
    meaning_tr: "El-Kâmûs (el-Firûzâbâdî) — Okyanus Sözlük",
  },
  {
    abbreviation: "Msb",
    category: "Source",
    meaning_en: "The Misbáh (El-Misbâh) by El-Feiyoomee",
    meaning_tr: "El-Misbâhu'l-Münîr (el-Feyyûmî) — Sözlük",
  },
  {
    abbreviation: "TA",
    category: "Source",
    meaning_en: "The Táj el-'Aroos (Tâcu'l-Arûs) by Ez-Zebeedee",
    meaning_tr: "Tâcu'l-Arûs (ez-Zebîdî) — En Kapsamlı Kaynak",
  },
  {
    abbreviation: "Bd",
    category: "Source",
    meaning_en: "The Exposition of El-Beydáwee",
    meaning_tr: "Beyzâvî Tefsiri (Envâru't-Tenzîl)",
  },
  {
    abbreviation: "A",
    category: "Source",
    meaning_en: "The Asás (Esâsu'l-Belâga) by Ez-Zemakhsheree",
    meaning_tr: "Esâsu'l-Belâga (ez-Zemahşerî) — Mecaz Sözlüğü",
  },
  {
    abbreviation: "Lh",
    category: "Source",
    meaning_en: "El-Lihyánee (Linguist)",
    meaning_tr: "El-Lihyânî (Dilbilimci)",
  },
  {
    abbreviation: "IAar",
    category: "Source",
    meaning_en: "Ibn-El-Aawrábee (Linguist)",
    meaning_tr: "İbnu'l-A'râbî (Dilbilimci)",
  },
  {
    abbreviation: "MF",
    category: "Source",
    meaning_en: "Mohammad Ibn-Et-Taiyib (Commentator)",
    meaning_tr: "Muhammed Murtazâ (Tâcu'l-Arûs Şerhçisi)",
  },
  {
    abbreviation: "aor.",
    category: "Grammar",
    meaning_en: "Aorist (Imperfect/Present Tense)",
    meaning_tr: "Muzari Fiil (Geniş/Şimdiki Zaman)",
  },
  {
    abbreviation: "inf. n.",
    category: "Grammar",
    meaning_en: "Infinitive Noun",
    meaning_tr: "Mastar (Fiilin İsim Hali)",
  },
  {
    abbreviation: "subst.",
    category: "Grammar",
    meaning_en: "Substantive (Noun)",
    meaning_tr: "İsim (Sıfat veya fiil olmayan)",
  },
  {
    abbreviation: "pl.",
    category: "Grammar",
    meaning_en: "Plural",
    meaning_tr: "Çoğul",
  },
  {
    abbreviation: "q. v.",
    category: "Reference",
    meaning_en: "Quod vide (which see)",
    meaning_tr: "Bkz. (Bakınız / O maddeye gidiniz)",
  },
  {
    abbreviation: "accord.",
    category: "Reference",
    meaning_en: "According to",
    meaning_tr: "...-e göre (Referans verirken)",
  },
  {
    abbreviation: "app.",
    category: "Reference",
    meaning_en: "Apparently",
    meaning_tr: "Zahiren / Görünüşe göre",
  },
  {
    abbreviation: "tropical",
    category: "Semantics",
    meaning_en: "Tropical (Figurative/Metaphorical)",
    meaning_tr: "Mecaz (Mecazi Anlam)",
  },
  {
    abbreviation: "assumed tropical",
    category: "Semantics",
    meaning_en: "Assumed to be tropical/figurative",
    meaning_tr: "Varsayılan Mecaz (Yazara göre mecaz olması muhtemel)",
  },
]

const CATEGORY_LABELS: Record<LaneAbbreviation["category"], { tr: string; en: string }> = {
  Source: { tr: "Kaynaklar", en: "Sources" },
  Grammar: { tr: "Gramer Terimleri", en: "Grammar Terms" },
  Reference: { tr: "Referans Kısaltmaları", en: "Reference Abbreviations" },
  Semantics: { tr: "Anlam Belirteçleri", en: "Semantic Markers" },
}

export function getAbbreviationsByCategory(lang: "tr" | "en"): {
  category: LaneAbbreviation["category"]
  label: string
  items: LaneAbbreviation[]
}[] {
  const groups = new Map<LaneAbbreviation["category"], LaneAbbreviation[]>()
  for (const abbr of LANE_ABBREVIATIONS) {
    const existing = groups.get(abbr.category) ?? []
    existing.push(abbr)
    groups.set(abbr.category, existing)
  }

  const order: LaneAbbreviation["category"][] = ["Source", "Grammar", "Reference", "Semantics"]
  return order
    .filter((cat) => groups.has(cat))
    .map((cat) => ({
      category: cat,
      label: CATEGORY_LABELS[cat][lang],
      items: groups.get(cat)!,
    }))
}
