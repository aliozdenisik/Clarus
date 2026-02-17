"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { MagicCard } from "@/components/ui/magic-card"
import { Input } from "@/components/ui/input"
import { useRouter } from "next/navigation"
import { Search, BookOpen, User, LogOut } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { useSession, signOut } from "@/lib/auth-client"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import { logger } from "@/lib/logger"
import { getBibleBooksApiMetadataBibleBooksGet } from "@/lib/api/sdk.gen"
import { useTranslations } from "next-intl"

interface Book {
  nr: number
  name: string
  chapters_count: number
  testament: string
}

const HEBREW_NAMES: Record<string, string> = {
  Genesis: "Bereshit",
  Exodus: "Shemot",
  Leviticus: "Vayikra",
  Numbers: "Bamidbar",
  Deuteronomy: "Devarim",
  Joshua: "Yehoshua",
  Judges: "Shoftim",
  Ruth: "Rut",
  "1 Samuel": "Shmuel Alef",
  "2 Samuel": "Shmuel Bet",
  "1 Kings": "Melachim Alef",
  "2 Kings": "Melachim Bet",
  "1 Chronicles": "Divrei HaYamim Alef",
  "2 Chronicles": "Divrei HaYamim Bet",
  Ezra: "Ezra",
  Nehemiah: "Nechemyah",
  Esther: "Esther",
  Job: "Iyov",
  Psalms: "Tehillim",
  Proverbs: "Mishlei",
  Ecclesiastes: "Kohelet",
  "Song of Solomon": "Shir HaShirim",
  "Song of Songs": "Shir HaShirim", // Handle variation
  Isaiah: "Yeshayahu",
  Jeremiah: "Yirmeyahu",
  Lamentations: "Eichah",
  Ezekiel: "Yechezkel",
  Daniel: "Daniel",
  Hosea: "Hoshea",
  Joel: "Yoel",
  Amos: "Amos",
  Obadiah: "Ovadyah",
  Jonah: "Yonah",
  Micah: "Michah",
  Nahum: "Nachum",
  Habakkuk: "Chavakuk",
  Zephaniah: "Tzefanyah",
  Haggai: "Chaggai",
  Zechariah: "Zecharyah",
  Malachi: "Malachi",
}

export default function OldTestamentPage() {
  const t = useTranslations("BibleBrowse")
  const tCommon = useTranslations("Common")
  const [books, setBooks] = useState<Book[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const { data: session } = useSession()
  const user = session?.user
  const router = useRouter()

  useEffect(() => {
    const controller = new AbortController()

    const fetchBooks = async () => {
      try {
        const response = await getBibleBooksApiMetadataBibleBooksGet({
          query: { testament: "old_testament" },
          signal: controller.signal,
        })

        if (controller.signal.aborted) {
          return
        }

        const data = response.data as { data?: { books?: Book[] } } | undefined
        setBooks(data?.data?.books || [])
      } catch (error) {
        if (
          (error instanceof DOMException && error.name === "AbortError") ||
          (error instanceof Error && error.name === "AbortError")
        ) {
          return
        }

        logger.error("Failed to load books", error, { component: "OldTestamentPage" })
        toast.error(t("failedToLoad"))
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      }
    }

    fetchBooks()

    return () => {
      controller.abort()
    }
  }, [t])

  const handleLogout = async () => {
    await signOut()
    router.push("/sign-in")
    toast.success(tCommon("logoutSuccess"))
  }

  const filteredBooks = books.filter(
    (book) =>
      book.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (HEBREW_NAMES[book.name] || "").toLowerCase().includes(searchQuery.toLowerCase())
  )

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
          {user && (
            <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
              <User className="h-4 w-4" />
              <span className="text-sm">{user?.name || user?.email}</span>
            </div>
          )}
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
            {user && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
              >
                <LogOut className="h-4 w-4" />
                {tCommon("logout")}
              </Button>
            )}
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
            {t("oldTestamentTitle")}
          </h1>
          <p className="text-[var(--color-text-secondary)]">{t("oldTestamentDescription")}</p>
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
            placeholder={t("searchPlaceholderOT")}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] pl-10"
          />
        </motion.div>

        {/* Grid */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {isLoading
            ? [...Array(12)].map((_, i) => (
                <Skeleton key={`old-testament-skeleton-${i}`} className="h-32 w-full rounded-xl" />
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
                  <MagicCard
                    className="group h-full rounded-lg border border-[var(--color-border-subtle)] p-6 transition-colors hover:border-[var(--color-accent-glow)]"
                    gradientSize={200}
                    gradientColor="#1a1a2e"
                    gradientFrom="#7c3aed"
                    gradientTo="#4f46e5"
                  >
                    <div className="flex h-full flex-col justify-between">
                      <div>
                        <h3 className="text-xl font-bold text-[var(--color-text-primary)] transition-colors group-hover:text-[var(--color-accent-primary)]">
                          {book.name}
                        </h3>
                        <p className="mt-1 text-sm text-[var(--color-text-secondary)] italic">
                          {HEBREW_NAMES[book.name] || book.name}
                        </p>
                      </div>
                      <div className="mt-4 flex items-center justify-between border-t border-[var(--color-border-subtle)] pt-4 text-xs text-[var(--color-text-muted)]">
                        <span>{tCommon("chapters", { count: book.chapters_count })}</span>
                        <span className="font-medium text-[var(--color-accent-primary)] opacity-0 transition-opacity group-hover:opacity-100">
                          {tCommon("read")} &rarr;
                        </span>
                      </div>
                    </div>
                  </MagicCard>
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
