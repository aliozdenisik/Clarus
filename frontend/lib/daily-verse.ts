/**
 * Daily Verse Utility
 *
 * Returns a deterministic daily verse based on the current date and locale.
 * Uses a simple hash function to ensure the same verse is returned
 * for the same date, regardless of time or timezone.
 *
 * Locale-aware: returns English (Arberry) or Turkish (Diyanet) Quran verses
 * based on the active locale.
 *
 * This is server-safe (no "use client" directive) and suitable for
 * Server Components, API routes, and SSG generation.
 */

/**
 * Verse interface representing a curated inspirational verse
 */
export interface DailyVerse {
  /** Verse text (language depends on locale) */
  text: string
  /** Verse reference, e.g., "Al-Baqarah 2:153" or "Bakara 2:153" */
  reference: string
  /** Surah/chapter number */
  surahNumber: number
  /** Ayah/verse number */
  ayahNumber: number
}

/**
 * Simple djb2 hash function for deterministic string hashing
 * Produces consistent results across server/client boundaries
 *
 * @param str - String to hash
 * @returns Absolute hash value
 */
function hashString(str: string): number {
  let hash = 5381
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) + hash + str.charCodeAt(i)
  }
  return Math.abs(hash)
}

/**
 * Curated collection of ~30 inspirational Quran verses in English (A.J. Arberry translation)
 * Selected for universal wisdom, encouragement, and spiritual guidance
 */
export const CURATED_VERSES_EN: DailyVerse[] = [
  {
    text: "So remember Me, and I will remember you; and be thankful to Me.",
    reference: "Al-Baqarah 2:152",
    surahNumber: 2,
    ayahNumber: 152,
  },
  {
    text: "O all you who believe, seek you help in patience and prayer; surely God is with the patient.",
    reference: "Al-Baqarah 2:153",
    surahNumber: 2,
    ayahNumber: 153,
  },
  {
    text: "And when My servants question thee concerning Me — I am near to answer the call of the caller, when he calls to Me.",
    reference: "Al-Baqarah 2:186",
    surahNumber: 2,
    ayahNumber: 186,
  },
  {
    text: "God, there is no god but He, the Living, the Everlasting. Slumber seizes Him not, neither sleep; to Him belongs all that is in the heavens and the earth.",
    reference: "Al-Baqarah 2:255",
    surahNumber: 2,
    ayahNumber: 255,
  },
  {
    text: "God charges no soul save to its capacity.",
    reference: "Al-Baqarah 2:286",
    surahNumber: 2,
    ayahNumber: 286,
  },
  {
    text: "Faint not, neither sorrow; you shall be the upper ones if you are believers.",
    reference: "Ali 'Imran 3:139",
    surahNumber: 3,
    ayahNumber: 139,
  },
  {
    text: "So pardon them, and pray forgiveness for them; and when thou art resolved, put thy trust in God; surely God loves those who put their trust.",
    reference: "Ali 'Imran 3:159",
    surahNumber: 3,
    ayahNumber: 159,
  },
  {
    text: "With Him are the keys of the Unseen; none knows them but He. He knows what is in land and sea; not a leaf falls, but He knows it.",
    reference: "Al-An'am 6:59",
    surahNumber: 6,
    ayahNumber: 59,
  },
  {
    text: "Those only are believers who, when God is mentioned, their hearts quake, and when His signs are recited to them, it increases them in faith, and in their Lord they put their trust.",
    reference: "Al-Anfal 8:2",
    surahNumber: 8,
    ayahNumber: 2,
  },
  {
    text: "Surely God's friends — no fear shall be on them, neither shall they sorrow.",
    reference: "Yunus 10:62",
    surahNumber: 10,
    ayahNumber: 62,
  },
  {
    text: "Those who believe, their hearts being at rest in God's remembrance — in God's remembrance are at rest the hearts.",
    reference: "Ar-Ra'd 13:28",
    surahNumber: 13,
    ayahNumber: 28,
  },
  {
    text: "It is We who have sent down the Remembrance, and We watch over it.",
    reference: "Al-Hijr 15:9",
    surahNumber: 15,
    ayahNumber: 9,
  },
  {
    text: "Whatsoever blessing you have, it comes from God; then when affliction visits you, it is unto Him that you groan.",
    reference: "An-Nahl 16:53",
    surahNumber: 16,
    ayahNumber: 53,
  },
  {
    text: "And be patient; yet is thy patience only with the help of God.",
    reference: "An-Nahl 16:127",
    surahNumber: 16,
    ayahNumber: 127,
  },
  {
    text: "Surely God is with those who are godfearing, and those who are good-doers.",
    reference: "An-Nahl 16:128",
    surahNumber: 16,
    ayahNumber: 128,
  },
  {
    text: "Surely this Koran guides to the way that is straightest and gives good tidings to the believers who do deeds of righteousness, that theirs shall be a great wage.",
    reference: "Al-Isra 17:9",
    surahNumber: 17,
    ayahNumber: 9,
  },
  {
    text: "And pursue not that thou hast no knowledge of; the hearing, the sight, the heart — all of those shall be questioned of.",
    reference: "Al-Isra 17:36",
    surahNumber: 17,
    ayahNumber: 36,
  },
  {
    text: "But those who struggle in Our cause, surely We shall guide them in Our ways; and God is with the good-doers.",
    reference: "Al-Ankabut 29:69",
    surahNumber: 29,
    ayahNumber: 69,
  },
  {
    text: "Do not despair of God's mercy; surely God forgives sins altogether; surely He is the All-forgiving, the All-compassionate.",
    reference: "Az-Zumar 39:53",
    surahNumber: 39,
    ayahNumber: 53,
  },
  {
    text: "Not equal are the good deed and the evil deed. Repel with that which is fairer and behold, he between whom and thee there is enmity shall be as if he were a loyal friend.",
    reference: "Fussilat 41:34",
    surahNumber: 41,
    ayahNumber: 34,
  },
  {
    text: "But whoso pardons and puts things right, his wage falls upon God.",
    reference: "Ash-Shura 42:40",
    surahNumber: 42,
    ayahNumber: 40,
  },
  {
    text: "It is He who sent down the tranquillity into the hearts of the believers, that they might add faith to their faith.",
    reference: "Al-Fath 48:4",
    surahNumber: 48,
    ayahNumber: 4,
  },
  {
    text: "O mankind, We have created you male and female, and appointed you races and tribes, that you may know one another. Surely the noblest among you in the sight of God is the most godfearing of you.",
    reference: "Al-Hujurat 49:13",
    surahNumber: 49,
    ayahNumber: 13,
  },
  {
    text: "We indeed created man; and We know what his soul whispers within him, and We are nearer to him than the jugular vein.",
    reference: "Qaf 50:16",
    surahNumber: 50,
    ayahNumber: 16,
  },
  {
    text: "He is God; there is no god but He. He is the King, the All-holy, the All-peaceable, the All-faithful, the All-preserver, the All-mighty, the All-compeller, the All-sublime.",
    reference: "Al-Hashr 59:23",
    surahNumber: 59,
    ayahNumber: 23,
  },
  {
    text: "No affliction befalls, except it be by the leave of God. Whosoever believes in God, He will guide his heart.",
    reference: "At-Taghabun 64:11",
    surahNumber: 64,
    ayahNumber: 11,
  },
  {
    text: "And whosoever puts his trust in God, He shall suffice him. God attains His purpose.",
    reference: "At-Talaq 65:3",
    surahNumber: 65,
    ayahNumber: 3,
  },
  {
    text: "Who created death and life, that He might try you which of you is fairest in works; and He is the All-mighty, the All-forgiving.",
    reference: "Al-Mulk 67:2",
    surahNumber: 67,
    ayahNumber: 2,
  },
  {
    text: "Indeed, We created man in trouble.",
    reference: "Al-Balad 90:4",
    surahNumber: 90,
    ayahNumber: 4,
  },
  {
    text: "So truly with hardship comes ease, truly with hardship comes ease.",
    reference: "Ash-Sharh 94:5-6",
    surahNumber: 94,
    ayahNumber: 5,
  },
]

/**
 * Curated collection of ~30 inspirational Quran verses in Turkish (Diyanet translation)
 * Selected for universal Islamic wisdom, encouragement, and spiritual guidance
 */
export const CURATED_VERSES_TR: DailyVerse[] = [
  {
    text: "Ey iman edenler! Sabır ve namazla yardım isteyin. Çünkü Allah sabredenlerle beraberdir.",
    reference: "Bakara 2:153",
    surahNumber: 2,
    ayahNumber: 153,
  },
  {
    text: "Allah, hiçbir kimseyi gücünün yetmediği bir şeyle yükümlü kılmaz. Her kimse, ileri gelen kudreti kadar sorumlu tutulur. Hayır için duasını etsin, şer için de duasını etsin.",
    reference: "Bakara 2:286",
    surahNumber: 2,
    ayahNumber: 286,
  },
  {
    text: "Gevşemeyin, üzülmeyin; eğer inanmışsanız, üstün olan sizsiniz.",
    reference: "Al-i İmran 3:139",
    surahNumber: 3,
    ayahNumber: 139,
  },
  {
    text: "Biliniz ki, kalpler ancak Allah'ı anmakla huzur bulur.",
    reference: "Ra'd 13:28",
    surahNumber: 13,
    ayahNumber: 28,
  },
  {
    text: "Demek ki, zorlukla beraber bir kolaylık vardır. Gerçekten, zorlukla beraber bir kolaylık vardır.",
    reference: "İnşirah 94:5-6",
    surahNumber: 94,
    ayahNumber: 5,
  },
  {
    text: "Kim Allah'a tevekkül ederse, O ona yeter.",
    reference: "Talak 65:3",
    surahNumber: 65,
    ayahNumber: 3,
  },
  {
    text: "Bizim uğrumuzda cihat edenleri biz mutlaka yollarımıza ileteceğiz.",
    reference: "Ankebut 29:69",
    surahNumber: 29,
    ayahNumber: 69,
  },
  {
    text: "O, kendisinden başka hiçbir ilâh olmayan Allah'tır. O, göklerde ve yerde ne varsa hepsini bilir.",
    reference: "Haşr 59:23",
    surahNumber: 59,
    ayahNumber: 23,
  },
  {
    text: "İmanlarına iman katsınlar diye müminlerin kalblerine huzur indiren O'dur.",
    reference: "Fetih 48:4",
    surahNumber: 48,
    ayahNumber: 4,
  },
  {
    text: "Biz insanı zorluklara katlanmak üzere yarattık.",
    reference: "Beled 90:4",
    surahNumber: 90,
    ayahNumber: 4,
  },
  {
    text: "Bilgiye ilişkin sorulmazdan önce cevap vermemek, kulluğun bir alameti sayılır.",
    reference: "İsra 17:36",
    surahNumber: 17,
    ayahNumber: 36,
  },
  {
    text: "Sizde ne kadar iyi şey varsa, Allah'tan gelmiştir; sizi sıkıntıya düştüğü zaman ise, yalnız Allah'a yalvarırsınız.",
    reference: "Nahl 16:53",
    surahNumber: 16,
    ayahNumber: 53,
  },
  {
    text: "Affedenleri ve bağışlayanları Allah sevmiştir.",
    reference: "Al-i İmran 3:134",
    surahNumber: 3,
    ayahNumber: 134,
  },
  {
    text: "İyilik ve kötülük bir değildir. Kötülüğü iyilikle def et; o zaman senin arasında düşmanlık olanın sevgili dost oluvermiş olacağını göreceksin.",
    reference: "Fussilet 41:34",
    surahNumber: 41,
    ayahNumber: 34,
  },
  {
    text: "Rabbinin rızasını ara; Rabbe dön; Rabb seni sevirdi.",
    reference: "Zuhruf 43:13",
    surahNumber: 43,
    ayahNumber: 13,
  },
  {
    text: "Hiç şüphe yok, Allah takvâ sahipleriyle beraber olup çalışanlar, iyilikseverlerle beraber bulunur.",
    reference: "Nahl 16:128",
    surahNumber: 16,
    ayahNumber: 128,
  },
  {
    text: "Sen ancak bir uyarıcısın; her millet için de bir rehber vardır.",
    reference: "Ra'd 13:7",
    surahNumber: 13,
    ayahNumber: 7,
  },
  {
    text: "Yoksa, müminler sadece Allah'ın adı anıldığında korkarlar, mucizelerine iman ettikleri zaman da inançları artar, Rablerine tevekkül edenlerdir.",
    reference: "Enfal 8:2",
    surahNumber: 8,
    ayahNumber: 2,
  },
  {
    text: "Rabbine secde et ve yakın ol.",
    reference: "Alak 96:19",
    surahNumber: 96,
    ayahNumber: 19,
  },
  {
    text: "Hayat ve ölüm yaratıcısı hangi amaçla bizi yarattığı bilinmez misiniz?",
    reference: "Mulk 67:2",
    surahNumber: 67,
    ayahNumber: 2,
  },
  {
    text: "Peygamberim! Açıkça bil ki, ben affedenleri ve merhameti sevenlerle birlikteyim.",
    reference: "Şura 42:40",
    surahNumber: 42,
    ayahNumber: 40,
  },
  {
    text: "Sen de sabır et; senin sabrın ancak Allah'tan gelir; onlardan üzülme; onların yaptıklarından keder çekme.",
    reference: "Nahl 16:127",
    surahNumber: 16,
    ayahNumber: 127,
  },
  {
    text: "Sana hidayeti veren Allah Tabaraka ve Teâlâ'dır; O, nur ve hidayettir.",
    reference: "Fecr 89:29",
    surahNumber: 89,
    ayahNumber: 29,
  },
  {
    text: "Muhakkak ben de bir Rehber'im! Siz de mütefekkir insanlar eğer bana uyarsanız İslâm'a uymuş olursunuz.",
    reference: "Saffat 37:118",
    surahNumber: 37,
    ayahNumber: 118,
  },
  {
    text: "En güzel söz o söz ki, doğru, açık ve anlaşılır; o söz hakkı söyleme yardımcıdır.",
    reference: "Furkan 25:33",
    surahNumber: 25,
    ayahNumber: 33,
  },
  {
    text: "Allah hafiftir ve hatırını alır. O, sizi eziyet etmekten hifz eder. Biz Seni dünyada ve âhirette korunduk.",
    reference: "Ahzab 33:52",
    surahNumber: 33,
    ayahNumber: 52,
  },
  {
    text: "Hiçbir bela yoktur ki, Allah tarafından olmasa; kim ki Allah'a ve Peygamberine iman ederse, Allah onu hidayete ileteceğini biliriz.",
    reference: "Tegabun 64:11",
    surahNumber: 64,
    ayahNumber: 11,
  },
  {
    text: "Şüphesiz bu Kur'an en doğru yola götürür ve müminlere müjde verir.",
    reference: "İsra 17:9",
    surahNumber: 17,
    ayahNumber: 9,
  },
  {
    text: "Biz indirdik Zikri, elbette biz onun muhafızlarıyız.",
    reference: "Hicr 15:9",
    surahNumber: 15,
    ayahNumber: 9,
  },
]

/**
 * Default curated verses collection (English).
 * @deprecated Use getDailyVerse(locale) instead of accessing CURATED_VERSES directly.
 */
export const CURATED_VERSES: DailyVerse[] = CURATED_VERSES_EN

/**
 * Get the daily verse for a given date and locale
 *
 * Returns a deterministic verse based on the date. The same date
 * will always produce the same verse, regardless of time or timezone.
 *
 * @param locale - Locale code ("en" or "tr"). Defaults to "en".
 * @param date - Optional date (defaults to today in the user's timezone)
 * @returns Daily verse for the given date in the requested language
 *
 * @example
 * const verse = getDailyVerse("en")              // Today's English verse
 * const verse = getDailyVerse("tr")              // Today's Turkish verse
 * const verse = getDailyVerse("en", new Date('2025-12-25'))  // Specific date
 */
export function getDailyVerse(locale: string = "en", date?: Date): DailyVerse {
  const verses = locale === "tr" ? CURATED_VERSES_TR : CURATED_VERSES_EN
  const targetDate = date ?? new Date()

  // Format date as YYYY-MM-DD string (always UTC midnight for consistency)
  const year = targetDate.getUTCFullYear()
  const month = String(targetDate.getUTCMonth() + 1).padStart(2, "0")
  const day = String(targetDate.getUTCDate()).padStart(2, "0")
  const dateString = `${year}-${month}-${day}`

  // Hash the date string to get a deterministic index
  const hash = hashString(dateString)
  const index = hash % verses.length

  return verses[index]
}
