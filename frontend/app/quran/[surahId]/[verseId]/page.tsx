"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { useSession } from "@/lib/auth-client"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"
import { ArrowLeft, ChevronLeft, ChevronRight } from "lucide-react"
import { API_BASE } from "@/lib/config"
import { ClickableVerse } from "@/components/quran/clickable-verse"
import { TranslationBlock } from "@/components/quran/translation-block"

interface TranslationItem {
  translator: string
  translator_display: string
  text: string
}

interface VerseTranslationsData {
  success: boolean
  surah_id: number
  verse_id: number
  surah_name: string
  arabic_text: string
  translations: TranslationItem[]
}

const SURAH_VERSE_COUNTS: Record<number, number> = {
  1: 7,
  2: 286,
  3: 200,
  4: 176,
  5: 120,
  6: 165,
  7: 206,
  8: 75,
  9: 129,
  10: 109,
  11: 123,
  12: 111,
  13: 43,
  14: 52,
  15: 99,
  16: 128,
  17: 111,
  18: 110,
  19: 98,
  20: 135,
  21: 112,
  22: 78,
  23: 118,
  24: 64,
  25: 77,
  26: 227,
  27: 93,
  28: 88,
  29: 69,
  30: 60,
  31: 34,
  32: 30,
  33: 73,
  34: 54,
  35: 45,
  36: 83,
  37: 182,
  38: 88,
  39: 75,
  40: 85,
  41: 54,
  42: 53,
  43: 89,
  44: 59,
  45: 37,
  46: 35,
  47: 38,
  48: 29,
  49: 18,
  50: 45,
  51: 60,
  52: 49,
  53: 62,
  54: 55,
  55: 78,
  56: 96,
  57: 29,
  58: 22,
  59: 24,
  60: 13,
  61: 14,
  62: 11,
  63: 11,
  64: 18,
  65: 12,
  66: 12,
  67: 30,
  68: 52,
  69: 52,
  70: 44,
  71: 28,
  72: 28,
  73: 20,
  74: 56,
  75: 40,
  76: 31,
  77: 50,
  78: 40,
  79: 46,
  80: 42,
  81: 29,
  82: 19,
  83: 36,
  84: 25,
  85: 22,
  86: 17,
  87: 19,
  88: 26,
  89: 30,
  90: 20,
  91: 15,
  92: 21,
  93: 11,
  94: 8,
  95: 8,
  96: 19,
  97: 5,
  98: 8,
  99: 8,
  100: 11,
  101: 11,
  102: 8,
  103: 3,
  104: 9,
  105: 5,
  106: 4,
  107: 7,
  108: 3,
  109: 6,
  110: 3,
  111: 5,
  112: 4,
  113: 5,
  114: 6,
}

export default function VerseDetailPage() {
  const params = useParams()
  const surahId = parseInt(params.surahId as string, 10)
  const verseId = parseInt(params.verseId as string, 10)
  const router = useRouter()
  const [verseData, setVerseData] = useState<VerseTranslationsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const { data: session, isPending: authLoading } = useSession()
  const user = session?.user

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in")
    }
  }, [user, authLoading, router])

  useEffect(() => {
    const controller = new AbortController()

    const fetchVerseTranslations = async () => {
      if (isNaN(surahId) || isNaN(verseId) || surahId < 1 || surahId > 114 || verseId < 1) {
        router.replace(`/quran/${surahId}`)
        return
      }

      const maxVerses = SURAH_VERSE_COUNTS[surahId]
      if (verseId > maxVerses) {
        router.replace(`/quran/${surahId}`)
        return
      }

      try {
        const response = await fetch(
          `${API_BASE}/api/metadata/quran/verses/${surahId}/${verseId}/translations`,
          {
            credentials: "include",
            signal: controller.signal,
          }
        )

        if (controller.signal.aborted) {
          return
        }

        if (!response.ok) {
          throw new Error("Failed to fetch verse translations")
        }

        const data = await response.json()

        if (controller.signal.aborted) {
          return
        }

        setVerseData(data)
      } catch (error) {
        if (
          (error instanceof DOMException && error.name === "AbortError") ||
          (error instanceof Error && error.name === "AbortError")
        ) {
          return
        }

        toast.error("Failed to load verse translations")
        router.replace(`/quran/${surahId}`)
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      }
    }

    if (user && !isNaN(surahId) && !isNaN(verseId)) {
      fetchVerseTranslations()
    }

    return () => {
      controller.abort()
    }
  }, [user, surahId, verseId, router])

  const getPrevVerse = (): { surahId: number; verseId: number } | null => {
    if (surahId === 1 && verseId === 1) {
      return null
    }

    if (verseId === 1) {
      const prevSurahId = surahId - 1
      return {
        surahId: prevSurahId,
        verseId: SURAH_VERSE_COUNTS[prevSurahId],
      }
    }

    return { surahId, verseId: verseId - 1 }
  }

  const getNextVerse = (): { surahId: number; verseId: number } | null => {
    const maxVerses = SURAH_VERSE_COUNTS[surahId]

    if (surahId === 114 && verseId === maxVerses) {
      return null
    }

    if (verseId === maxVerses) {
      return {
        surahId: surahId + 1,
        verseId: 1,
      }
    }

    return { surahId, verseId: verseId + 1 }
  }

  const prevVerse = getPrevVerse()
  const nextVerse = getNextVerse()

  const handleNavigation = (targetSurahId: number, targetVerseId: number) => {
    router.push(`/quran/${targetSurahId}/${targetVerseId}`)
  }

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-[var(--color-bg-app)] p-8">
        <div className="mx-auto max-w-4xl">
          <Skeleton className="mb-6 h-10 w-48" />
          <Skeleton className="mb-4 h-8 w-64" />
          <Skeleton className="mb-8 h-24 w-full" />
          <div className="space-y-4">
            {[...Array(8)].map((_, i) => (
              <Skeleton key={`verse-detail-skeleton-${i}`} className="h-32 w-full" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!verseData) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)] p-8">
        <div className="text-center">
          <p className="mb-4 text-[var(--color-text-muted)]">Ayet bulunamadı</p>
          <Button onClick={() => router.push(`/quran/${surahId}`)}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Sure sayfasına dön
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--color-bg-app)] p-8">
      <div className="mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.snappy}
          className="sticky top-0 z-10 mb-8 flex items-center justify-between border-b border-[var(--color-border-subtle)] bg-[var(--color-bg-app)]/80 pb-4 backdrop-blur-sm"
        >
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push(`/quran/${surahId}`)}
              className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
            >
              <ArrowLeft className="h-4 w-4" />
              Geri
            </Button>
            <div className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
              <button
                onClick={() => router.push("/quran")}
                className="transition-colors hover:text-[var(--color-accent-primary)]"
              >
                Kuran
              </button>
              <span>/</span>
              <button
                data-testid="breadcrumb-surah"
                onClick={() => router.push(`/quran/${surahId}`)}
                className="transition-colors hover:text-[var(--color-accent-primary)]"
              >
                {verseData.surah_name}
              </button>
              <span>/</span>
              <span className="font-medium text-[var(--color-text-primary)]">Ayet {verseId}</span>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
          className="mb-8 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-elevated)] p-8 text-center"
        >
          <div data-testid="arabic-text" className="flex items-center justify-center py-8">
            <ClickableVerse
              surahId={surahId}
              ayahNumber={verseId}
              arabicText={verseData.arabic_text}
            />
          </div>
        </motion.div>

        <div className="mb-8 space-y-4">
          {verseData.translations.length > 0 ? (
            verseData.translations.map((translation, index) => (
              <TranslationBlock
                key={`translation-${translation.translator}`}
                translator={translation.translator}
                translatorDisplay={translation.translator_display}
                text={translation.text || "Çeviri mevcut değil"}
                index={index}
              />
            ))
          ) : (
            <div className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-8 text-center">
              <p className="text-[var(--color-text-muted)]">Çeviri mevcut değil</p>
            </div>
          )}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ ...springPresets.fluid, delay: 0.2 }}
          className="flex items-center justify-between"
        >
          <Button
            variant="outline"
            size="lg"
            disabled={!prevVerse}
            onClick={() => prevVerse && handleNavigation(prevVerse.surahId, prevVerse.verseId)}
            data-testid="prev-verse-button"
            className="flex items-center gap-2"
          >
            <motion.div
              whileTap={prevVerse ? { scale: 0.97 } : {}}
              transition={springPresets.bouncy}
            >
              <ChevronLeft className="h-5 w-5" />
              Önceki Ayet
            </motion.div>
          </Button>

          <div className="text-center">
            <div className="text-sm text-[var(--color-text-muted)]">
              {surahId}:{verseId}
            </div>
          </div>

          <Button
            variant="outline"
            size="lg"
            disabled={!nextVerse}
            onClick={() => nextVerse && handleNavigation(nextVerse.surahId, nextVerse.verseId)}
            data-testid="next-verse-button"
            className="flex items-center gap-2"
          >
            <motion.div
              whileTap={nextVerse ? { scale: 0.97 } : {}}
              transition={springPresets.bouncy}
            >
              Sonraki Ayet
              <ChevronRight className="h-5 w-5" />
            </motion.div>
          </Button>
        </motion.div>
      </div>
    </div>
  )
}
