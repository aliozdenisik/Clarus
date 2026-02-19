/**
 * Daily Verse Utility
 *
 * Returns a deterministic daily verse based on the current date.
 * Uses a simple hash function to ensure the same verse is returned
 * for the same date, regardless of time or timezone.
 *
 * This is server-safe (no "use client" directive) and suitable for
 * Server Components, API routes, and SSG generation.
 */

/**
 * Verse interface representing a curated inspirational verse
 */
export interface DailyVerse {
  /** Verse text in Turkish (Diyanet translation) */
  text: string
  /** Verse reference, e.g., "Bakara 2:153" */
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
 * Curated collection of ~30 inspirational Quran verses in Turkish (Diyanet translation)
 * Selected for universal Islamic wisdom, encouragement, and spiritual guidance
 */
export const CURATED_VERSES: DailyVerse[] = [
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
    text: "Rabbine summa'n at! Ancak seni kendine davetin için başka yol açılmamıştır.",
    reference: "Tebbet 111:1",
    surahNumber: 111,
    ayahNumber: 1,
  },
  {
    text: "Biz indirdik Zikri, elbette biz onun muhafızlarıyız.",
    reference: "Hicr 15:9",
    surahNumber: 15,
    ayahNumber: 9,
  },
]

/**
 * Get the daily verse for a given date
 *
 * Returns a deterministic verse based on the date. The same date
 * will always produce the same verse, regardless of time or timezone.
 *
 * @param date - Optional date (defaults to today in the user's timezone)
 * @returns Daily verse for the given date
 *
 * @example
 * const verse = getDailyVerse()  // Today's verse
 * const verse = getDailyVerse(new Date('2025-12-25'))  // Specific date
 */
export function getDailyVerse(date?: Date): DailyVerse {
  const targetDate = date ?? new Date()

  // Format date as YYYY-MM-DD string (always UTC midnight for consistency)
  const year = targetDate.getUTCFullYear()
  const month = String(targetDate.getUTCMonth() + 1).padStart(2, "0")
  const day = String(targetDate.getUTCDate()).padStart(2, "0")
  const dateString = `${year}-${month}-${day}`

  // Hash the date string to get a deterministic index
  const hash = hashString(dateString)
  const index = hash % CURATED_VERSES.length

  return CURATED_VERSES[index]
}
