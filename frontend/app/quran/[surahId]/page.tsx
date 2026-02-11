"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter, useSearchParams } from "next/navigation"
import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { useSession, signOut } from "@/lib/auth-client"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"
import { User, LogOut } from "lucide-react"
import { API_BASE } from "@/lib/config"
import { SurahHeader } from "@/components/quran/surah-header"
import { VerseBlock } from "@/components/quran/verse-block"
import { VerseSeparator } from "@/components/quran/verse-separator"
import { TranslationSelector } from "@/components/quran/translation-selector"

interface Verse {
  id: number
  text: string
  translation: string
}

interface SurahDetail {
  id: number
  name: string
  name_arabic: string
  transliteration: string
  type: string
  total_verses: number
  verses: Verse[]
}

export default function SurahDetailPage() {
  const params = useParams()
  const surahId = params.surahId as string
  const searchParams = useSearchParams()
  const [surah, setSurah] = useState<SurahDetail | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [highlightedVerse, setHighlightedVerse] = useState<number | null>(null)
  const { data: session, isPending: authLoading } = useSession()
  const user = session?.user
  const router = useRouter()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in")
    }
  }, [user, authLoading, router])

  useEffect(() => {
    const verseParam = searchParams.get("verse")
    if (verseParam) {
      const verseId = parseInt(verseParam, 10)
      if (!isNaN(verseId)) {
        setHighlightedVerse(verseId)
      }
    }
  }, [searchParams])

  useEffect(() => {
    if (highlightedVerse && surah) {
      const timer = setTimeout(() => {
        const element = document.querySelector(`[data-verse-id="${highlightedVerse}"]`)
        if (element) {
          element.scrollIntoView({ behavior: "smooth", block: "center" })
          setTimeout(() => setHighlightedVerse(null), 2000)
        }
      }, 100)
      return () => clearTimeout(timer)
    }
  }, [highlightedVerse, surah])

  useEffect(() => {
    const controller = new AbortController()

    const fetchSurah = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/metadata/quran/surahs/${surahId}`, {
          credentials: "include",
          signal: controller.signal,
        })

        if (controller.signal.aborted) {
          return
        }

        if (!response.ok) {
          throw new Error("Failed to fetch surah")
        }

        const data = await response.json()

        if (controller.signal.aborted) {
          return
        }

        setSurah(data.data?.surah || null)
      } catch (error) {
        if (
          (error instanceof DOMException && error.name === "AbortError") ||
          (error instanceof Error && error.name === "AbortError")
        ) {
          return
        }

        toast.error("Failed to load surah")
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      }
    }

    if (user && surahId) {
      fetchSurah()
    }

    return () => {
      controller.abort()
    }
  }, [user, surahId])

  const handleLogout = async () => {
    await signOut()
    router.push("/sign-in")
    toast.success("Logged out successfully")
  }

  const handleVerseClick = (verseId: number) => {
    router.push(`/quran/${surahId}/${verseId}`)
  }

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-[var(--color-bg-app)] p-8">
        <div className="mx-auto max-w-4xl">
          <Skeleton className="mb-4 h-12 w-64" />
          <Skeleton className="mb-8 h-6 w-48" />
          <div className="space-y-4">
            {[...Array(10)].map((_, i) => (
              <Skeleton key={`surah-detail-skeleton-${i}`} className="h-24 w-full" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!surah) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)] p-8">
        <div className="text-center">
          <p className="mb-4 text-[var(--color-text-muted)]">Surah not found</p>
          <Button onClick={() => router.push("/quran")}>Back to Quran</Button>
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
          className="mb-6 flex items-center justify-end gap-4"
        >
          <TranslationSelector />
          <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
            <User className="h-4 w-4" />
            <span className="text-sm">{user?.name || user?.email}</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleLogout}
            className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </motion.div>

        <SurahHeader
          id={surah.id}
          nameArabic={surah.name_arabic}
          transliteration={surah.transliteration}
          type={surah.type}
          totalVerses={surah.total_verses}
        />

        <div className="space-y-1">
          {surah.verses.map((verse, i) => (
            <div key={verse.id}>
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ ...springPresets.gentle, delay: i * 0.02 }}
              >
                <VerseBlock
                  surahId={Number(surahId)}
                  verse={verse}
                  isHighlighted={highlightedVerse === verse.id}
                  onClick={() => handleVerseClick(verse.id)}
                />
              </motion.div>
              {i < surah.verses.length - 1 && <VerseSeparator />}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
