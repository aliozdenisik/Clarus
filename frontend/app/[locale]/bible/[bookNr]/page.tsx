"use client"

import { useState, useEffect, useRef } from "react"
import { useParams, useRouter, useSearchParams } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { useSession, signOut } from "@/lib/auth-client"
import { Button } from "@/components/ui/button"
import { GlowCard } from "@/components/ui/glow-card"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"
import { ArrowLeft, BookOpen, User, LogOut } from "lucide-react"
import { cn } from "@/lib/utils"
import { API_BASE } from "@/lib/config"
import { useTranslations } from "next-intl"

interface ChapterSummary {
  chapter: number
  verses_count: number
}

interface BookDetail {
  nr: number
  name: string
  testament: string
  chapters: ChapterSummary[]
}

interface Verse {
  verse: number
  text: string
}

interface ChapterContent {
  book_name: string
  chapter: number
  verses: Verse[]
}

export default function BookDetailPage() {
  const t = useTranslations("BibleBrowse")
  const tCommon = useTranslations("Common")
  const params = useParams()
  const bookNr = params.bookNr as string
  const searchParams = useSearchParams()
  const [book, setBook] = useState<BookDetail | null>(null)
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null)
  const [chapterContent, setChapterContent] = useState<ChapterContent | null>(null)
  const [isLoadingBook, setIsLoadingBook] = useState(true)
  const [isLoadingChapter, setIsLoadingChapter] = useState(false)
  const [highlightedVerse, setHighlightedVerse] = useState<number | null>(null)
  const { data: session, isPending: authLoading } = useSession()
  const user = session?.user
  const router = useRouter()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in")
    }
  }, [user, authLoading, router])

  // Read URL params on mount
  useEffect(() => {
    const chapterParam = searchParams.get("chapter")
    const verseParam = searchParams.get("verse")

    if (chapterParam) {
      const chapterNum = parseInt(chapterParam, 10)
      if (!isNaN(chapterNum)) {
        setSelectedChapter(chapterNum)
      }
    }
    if (verseParam) {
      const verseNum = parseInt(verseParam, 10)
      if (!isNaN(verseNum)) {
        setHighlightedVerse(verseNum)
      }
    }
  }, [searchParams])

  // Fetch book details + initial chapter in parallel (eliminates sequential waterfall)
  useEffect(() => {
    const controller = new AbortController()

    const fetchInitialData = async () => {
      const chapterParam = searchParams.get("chapter")
      const targetChapter = chapterParam ? Number(chapterParam) : 1

      try {
        const [bookRes, chapterRes] = await Promise.all([
          fetch(`${API_BASE}/api/metadata/bible/books/${bookNr}`, {
            credentials: "include",
            signal: controller.signal,
          }),
          fetch(`${API_BASE}/api/metadata/bible/books/${bookNr}/chapters/${targetChapter}`, {
            credentials: "include",
            signal: controller.signal,
          }),
        ])

        if (controller.signal.aborted) {
          return
        }

        if (!bookRes.ok) throw new Error("Failed to fetch book")

        const bookData = await bookRes.json()

        if (controller.signal.aborted) {
          return
        }

        setBook(bookData.data?.book || null)

        if (bookData.data?.book?.chapters?.length > 0) {
          setSelectedChapter(targetChapter)
        }

        if (chapterRes.ok) {
          const chapterData = await chapterRes.json()
          if (!controller.signal.aborted) {
            setChapterContent(chapterData.data || null)
          }
        }
      } catch (error) {
        if (
          (error instanceof DOMException && error.name === "AbortError") ||
          (error instanceof Error && error.name === "AbortError")
        ) {
          return
        }

        toast.error(t("failedToLoad"))
      } finally {
        if (!controller.signal.aborted) {
          setIsLoadingBook(false)
          setIsLoadingChapter(false)
        }
      }
    }

    if (user && bookNr) {
      setIsLoadingBook(true)
      setIsLoadingChapter(true)
      fetchInitialData()
    }

    return () => {
      controller.abort()
    }
  }, [user, bookNr, searchParams, t])

  // Fetch chapter content when user switches chapters (after initial load)
  const initialChapterRef = useRef<number | null>(null)

  useEffect(() => {
    // Skip fetch if this is the initial chapter (already fetched in parallel above)
    if (selectedChapter === null) return
    if (initialChapterRef.current === null) {
      initialChapterRef.current = selectedChapter
      return
    }
    if (
      selectedChapter === initialChapterRef.current &&
      chapterContent?.chapter === selectedChapter
    ) {
      return
    }

    const controller = new AbortController()

    const fetchChapter = async () => {
      setIsLoadingChapter(true)
      try {
        const response = await fetch(
          `${API_BASE}/api/metadata/bible/books/${bookNr}/chapters/${selectedChapter}`,
          { credentials: "include", signal: controller.signal }
        )

        if (controller.signal.aborted) {
          return
        }

        if (!response.ok) throw new Error("Failed to fetch chapter")

        const data = await response.json()
        if (!controller.signal.aborted) {
          setChapterContent(data.data || null)
        }
      } catch (error) {
        if (
          (error instanceof DOMException && error.name === "AbortError") ||
          (error instanceof Error && error.name === "AbortError")
        ) {
          return
        }

        toast.error(t("failedToLoadChapter"))
      } finally {
        if (!controller.signal.aborted) {
          setIsLoadingChapter(false)
        }
      }
    }

    if (user && selectedChapter) {
      fetchChapter()
    }

    return () => {
      controller.abort()
    }
  }, [user, bookNr, selectedChapter, chapterContent?.chapter, t])

  // Scroll to verse when chapter content loads and highlightedVerse is set.
  // Uses polling because AnimatePresence mode="wait" delays DOM mounting
  // until the loading skeleton's exit animation completes (~300-600ms).
  useEffect(() => {
    if (!highlightedVerse || !chapterContent) return

    let cancelled = false

    const tryScroll = () => {
      const element = document.querySelector(`[data-verse-id="${highlightedVerse}"]`)
      if (!element) return false
      element.scrollIntoView({ behavior: "smooth", block: "center" })
      setTimeout(() => {
        if (!cancelled) setHighlightedVerse(null)
      }, 2000)
      return true
    }

    let attempts = 0
    const interval = setInterval(() => {
      if (cancelled || tryScroll() || ++attempts >= 15) {
        clearInterval(interval)
      }
    }, 100)

    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }, [highlightedVerse, chapterContent])

  const handleLogout = async () => {
    await signOut()
    router.push("/sign-in")
    toast.success(tCommon("logoutSuccess"))
  }

  const getBackRoute = () => {
    if (!book) return "/old-testament"
    switch (book.testament) {
      case "old_testament":
        return "/old-testament"
      case "new_testament":
        return "/new-testament"
      case "apocrypha":
        return "/apocrypha"
      default:
        return "/old-testament"
    }
  }

  const getTestamentLabel = () => {
    if (!book) return ""
    switch (book.testament) {
      case "old_testament":
        return t("oldTestamentTitle")
      case "new_testament":
        return t("newTestamentTitle")
      case "apocrypha":
        return t("apocryphaTitle")
      default:
        return ""
    }
  }

  if (authLoading || isLoadingBook) {
    return (
      <div className="min-h-screen bg-[var(--color-bg-app)] p-8">
        <div className="mx-auto max-w-4xl">
          <Skeleton className="mb-4 h-12 w-64" />
          <Skeleton className="mb-8 h-6 w-48" />
          <Skeleton className="mb-4 h-12 w-full" />
          <div className="space-y-4">
            {[...Array(10)].map((_, i) => (
              <Skeleton key={`book-detail-page-skeleton-${i}`} className="h-20 w-full" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!book) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)] p-8">
        <div className="text-center">
          <p className="mb-4 text-[var(--color-text-muted)]">{t("bookNotFound")}</p>
          <Button onClick={() => router.push("/old-testament")}>{t("backToBooks")}</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--color-bg-app)] p-8">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.snappy}
          className="mb-6 flex items-center justify-between"
        >
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push(getBackRoute())}
            className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
          >
            <ArrowLeft className="h-4 w-4" />
            {book?.testament === "old_testament" && t("backToOldTestament")}
            {book?.testament === "new_testament" && t("backToNewTestament")}
            {book?.testament === "apocrypha" && t("backToApocrypha")}
          </Button>
          <div className="flex items-center gap-4">
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
              {tCommon("logout")}
            </Button>
          </div>
        </motion.div>

        {/* Book Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
          className="mb-8"
        >
          <div className="mb-2 flex items-center gap-3">
            <BookOpen className="h-8 w-8 text-[var(--color-accent-primary)]" />
            <h1 className="text-3xl font-bold text-[var(--color-text-primary)]">{book.name}</h1>
          </div>
          <p className="text-[var(--color-text-muted)]">
            {getTestamentLabel()} • {book.chapters.length} chapters
          </p>
        </motion.div>

        {/* Chapter Selector */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <p className="mb-3 text-sm text-[var(--color-text-muted)]">{t("selectChapter")}</p>
          <div className="flex flex-wrap gap-2">
            {book.chapters.map((ch) => (
              <button
                key={ch.chapter}
                onClick={() => setSelectedChapter(ch.chapter)}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                  selectedChapter === ch.chapter
                    ? "bg-[var(--color-accent-primary)] text-white"
                    : "bg-[var(--color-bg-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-elevated)] hover:text-[var(--color-text-primary)]"
                }`}
              >
                {ch.chapter}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Chapter Content */}
        <AnimatePresence mode="wait">
          {isLoadingChapter ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-4"
            >
              {[...Array(10)].map((_, i) => (
                <Skeleton key={`book-chapter-skeleton-${i}`} className="h-16 w-full" />
              ))}
            </motion.div>
          ) : chapterContent ? (
            <motion.div
              key={`chapter-${selectedChapter}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={springPresets.fluid}
            >
              <GlowCard className="p-6">
                <h3 className="mb-4 text-lg font-bold text-[var(--color-text-primary)]">
                  {t("chapterTitle", { chapter: chapterContent.chapter })}
                </h3>
                <div className="space-y-3">
                  {chapterContent.verses.map((verse) => (
                    <p
                      key={verse.verse}
                      data-verse-id={verse.verse}
                      className={cn(
                        "leading-relaxed text-[var(--color-text-primary)]",
                        highlightedVerse === verse.verse &&
                          "rounded-lg p-2 shadow-[var(--color-accent-primary)]/20 shadow-lg ring-2 ring-[var(--color-accent-primary)] transition-all duration-500"
                      )}
                    >
                      <span className="mr-2 text-sm font-bold text-[var(--color-accent-primary)]">
                        {verse.verse}
                      </span>
                      {verse.text}
                    </p>
                  ))}
                </div>
              </GlowCard>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="py-12 text-center text-[var(--color-text-muted)]"
            >
              {t("selectChapterPrompt")}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
