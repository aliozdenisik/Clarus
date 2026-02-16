"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { GlowCard } from "@/components/ui/glow-card"
import { Input } from "@/components/ui/input"
import { useRouter } from "next/navigation"
import { Search, BookOpen, User, LogOut } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { useSession, signOut } from "@/lib/auth-client"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import { logger } from "@/lib/logger"
import { API_BASE } from "@/lib/config"
import { useTranslations } from "next-intl"

interface Book {
  nr: number
  name: string
  chapters_count: number
  testament: string
}

const GREEK_NAMES: Record<string, string> = {
  Matthew: "Kata Matthaion",
  Mark: "Kata Markon",
  Luke: "Kata Loukan",
  John: "Kata Ioannen",
  Acts: "Praxeis Apostolon",
  Romans: "Pros Romaious",
  "1 Corinthians": "Pros Korinthious A",
  "2 Corinthians": "Pros Korinthious B",
  Galatians: "Pros Galatas",
  Ephesians: "Pros Ephesious",
  Philippians: "Pros Philippesious",
  Colossians: "Pros Kolossaeis",
  "1 Thessalonians": "Pros Thessalonikeis A",
  "2 Thessalonians": "Pros Thessalonikeis B",
  "1 Timothy": "Pros Timotheon A",
  "2 Timothy": "Pros Timotheon B",
  Titus: "Pros Titon",
  Philemon: "Pros Philemona",
  Hebrews: "Pros Hebraious",
  James: "Iakobou",
  "1 Peter": "Petrou A",
  "2 Peter": "Petrou B",
  "1 John": "Ioannou A",
  "2 John": "Ioannou B",
  "3 John": "Ioannou G",
  Jude: "Iouda",
  Revelation: "Apokalypsis",
}

export default function NewTestamentPage() {
  const t = useTranslations("BibleBrowse")
  const tCommon = useTranslations("Common")
  const [books, setBooks] = useState<Book[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const { data: session, isPending: authLoading } = useSession()
  const user = session?.user
  const router = useRouter()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in")
    }
  }, [user, authLoading, router])

  useEffect(() => {
    const controller = new AbortController()

    const fetchBooks = async () => {
      try {
        const response = await fetch(
          `${API_BASE}/api/metadata/bible/books?testament=new_testament`,
          {
            credentials: "include",
            signal: controller.signal,
          }
        )

        if (controller.signal.aborted) {
          return
        }

        if (!response.ok) throw new Error("Failed to fetch books")
        const data = await response.json()

        if (controller.signal.aborted) {
          return
        }

        setBooks(data.data?.books || [])
      } catch (error) {
        if (
          (error instanceof DOMException && error.name === "AbortError") ||
          (error instanceof Error && error.name === "AbortError")
        ) {
          return
        }

        logger.error("Failed to load books", error, { component: "NewTestamentPage" })
        toast.error(t("failedToLoad"))
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      }
    }

    if (user) {
      fetchBooks()
    }

    return () => {
      controller.abort()
    }
  }, [user, t])

  const handleLogout = async () => {
    await signOut()
    router.push("/sign-in")
    toast.success(tCommon("logoutSuccess"))
  }

  const filteredBooks = books.filter(
    (book) =>
      book.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (GREEK_NAMES[book.name] || "").toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-secondary)]">{tCommon("loading")}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--color-bg-app)] p-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.snappy}
          className="mb-8 flex items-center justify-between"
        >
          <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
            <User className="h-4 w-4" />
            <span className="text-sm">{user?.name || user?.email}</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/search")}
              className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
            >
              <Search className="h-4 w-4" />
              {tCommon("search")}
            </Button>
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

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
          className="mb-8"
        >
          <h1 className="mb-2 flex items-center gap-3 text-3xl font-bold text-[var(--color-text-primary)]">
            <BookOpen className="h-8 w-8 text-[var(--color-accent-primary)]" />
            {t("newTestamentTitle")}
          </h1>
          <p className="text-[var(--color-text-secondary)]">{t("newTestamentDescription")}</p>
        </motion.div>

        {/* Search */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="relative mb-8 max-w-md"
        >
          <Search className="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-[var(--color-text-muted)]" />
          <Input
            placeholder={t("searchPlaceholderNT")}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] pl-10"
          />
        </motion.div>

        {/* Grid */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {isLoading
            ? [...Array(12)].map((_, i) => (
                <Skeleton key={`new-testament-skeleton-${i}`} className="h-32 w-full rounded-xl" />
              ))
            : filteredBooks.map((book, i) => (
                <motion.div
                  key={book.nr}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{
                    ...springPresets.snappy,
                    delay: i * 0.03, // Stagger effect
                  }}
                  onClick={() => router.push(`/bible/${book.nr}`)}
                  className="cursor-pointer"
                >
                  <GlowCard className="group h-full transition-colors hover:border-[var(--color-accent-glow)]">
                    <div className="flex h-full flex-col justify-between">
                      <div>
                        <h3 className="text-xl font-bold text-[var(--color-text-primary)] transition-colors group-hover:text-[var(--color-accent-primary)]">
                          {book.name}
                        </h3>
                        <p className="mt-1 text-sm text-[var(--color-text-secondary)] italic">
                          {GREEK_NAMES[book.name] || book.name}
                        </p>
                      </div>
                      <div className="mt-4 flex items-center justify-between border-t border-[var(--color-border-subtle)] pt-4 text-xs text-[var(--color-text-muted)]">
                        <span>{tCommon("chapters", { count: book.chapters_count })}</span>
                        <span className="font-medium text-[var(--color-accent-primary)] opacity-0 transition-opacity group-hover:opacity-100">
                          {tCommon("read")} &rarr;
                        </span>
                      </div>
                    </div>
                  </GlowCard>
                </motion.div>
              ))}
        </div>

        {!isLoading && filteredBooks.length === 0 && (
          <div className="py-20 text-center text-[var(--color-text-muted)]">
            <p>{t("noBooks", { query: searchQuery })}</p>
          </div>
        )}
      </div>
    </div>
  )
}
