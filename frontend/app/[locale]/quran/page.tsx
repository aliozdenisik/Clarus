"use client"

import { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { useSession, signOut } from "@/lib/auth-client"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { MagicCard } from "@/components/ui/magic-card"
import { Skeleton } from "@/components/ui/skeleton"
import { VerseLookupInput } from "@/components/verse-lookup"
import { toast } from "sonner"
import { useRouter } from "next/navigation"
import { useTranslations } from "next-intl"
import { BookOpen, Search, User, LogOut } from "lucide-react"
import { getQuranSurahsApiMetadataQuranSurahsGet } from "@/lib/api/sdk.gen"

interface Surah {
  id: number
  name: string
  name_transliterated: string
  verse_count: number
  revelation_type: string
}

// API response format (may vary)
interface ApiSurah {
  id: number
  name?: string
  name_arabic?: string
  transliteration?: string
  name_transliterated?: string
  total_verses?: number
  verse_count?: number
  type?: string
  revelation_type?: string
}

export default function QuranPage() {
  const [surahs, setSurahs] = useState<Surah[]>([])
  const [filter, setFilter] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const { data: session } = useSession()
  const user = session?.user
  const router = useRouter()
  const t = useTranslations("QuranBrowse")
  const tCommon = useTranslations("Common")

  useEffect(() => {
    const controller = new AbortController()

    const fetchSurahs = async () => {
      try {
        const response = await getQuranSurahsApiMetadataQuranSurahsGet({
          signal: controller.signal,
        })

        if (controller.signal.aborted) {
          return
        }

        const data = response.data as
          | { data?: { surahs?: ApiSurah[] }; surahs?: ApiSurah[] }
          | ApiSurah[]
          | undefined
        const surahList: ApiSurah[] = Array.isArray(data)
          ? data
          : data?.data?.surahs || data?.surahs || []
        const mappedSurahs: Surah[] = surahList.map((s: ApiSurah) => ({
          id: s.id,
          name: s.name_arabic || s.name || "",
          name_transliterated: s.transliteration || s.name_transliterated || s.name || "",
          verse_count: s.total_verses || s.verse_count || 0,
          revelation_type: s.type || s.revelation_type || "",
        }))

        if (controller.signal.aborted) {
          return
        }

        setSurahs(mappedSurahs)
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
          setIsLoading(false)
        }
      }
    }

    fetchSurahs()

    return () => {
      controller.abort()
    }
  }, [t])

  const handleLogout = async () => {
    await signOut()
    router.push("/sign-in")
    toast.success("Logged out successfully")
  }

  const filteredSurahs = surahs.filter(
    (surah) =>
      surah.name_transliterated.toLowerCase().includes(filter.toLowerCase()) ||
      surah.id.toString().includes(filter)
  )

  return (
    <div className="min-h-screen bg-[var(--color-bg-app)] px-6 py-8 md:px-8">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.snappy}
          className="mb-6 flex items-center justify-between"
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
              Search
            </Button>
            {user && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
              >
                <LogOut className="h-4 w-4" />
                Logout
              </Button>
            )}
          </div>
        </motion.div>

        {/* Verse Lookup Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
          className="mb-4"
        >
          <div className="mb-3">
            <h2 className="text-sm font-medium tracking-wide text-[var(--color-text-secondary)] uppercase">
              Ayet Ara
            </h2>
            <p className="mt-1 text-xs text-[var(--color-text-muted)]">
              Doğrudan bir ayete git (örn: Bakara 183 veya 2:183)
            </p>
          </div>
          <VerseLookupInput placeholder="Bakara 183 veya 2:183" />
        </motion.div>

        {/* Divider */}
        <div className="mb-6 border-t border-[var(--color-border)]" />

        {/* Title & Filter */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springPresets.fluid, delay: 0.1 }}
          className="mb-6"
        >
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="mb-2 flex items-center gap-3 text-3xl font-bold text-[var(--color-text-primary)]">
                <BookOpen className="h-8 w-8 text-[var(--color-accent-primary)]" />
                {t("title")}
              </h1>
              <p className="text-[var(--color-text-muted)]">{t("description")}</p>
            </div>
            <div className="w-full md:w-72">
              <div className="relative">
                <Search className="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-[var(--color-text-muted)]" />
                <Input
                  type="text"
                  placeholder={t("searchPlaceholder")}
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Content */}
        {isLoading ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {Array.from({ length: 12 }, (_, slot) => slot + 1).map((slot) => (
              <Skeleton key={`quran-page-skeleton-${slot}`} className="h-32 w-full" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            <AnimatePresence mode="popLayout">
              {filteredSurahs.map((surah, i) => (
                <motion.div
                  key={surah.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  layout
                  transition={{ ...springPresets.snappy, delay: i * 0.02 }}
                >
                  <button
                    type="button"
                    onClick={() => router.push(`/quran/${surah.id}`)}
                    className="w-full text-left"
                  >
                    <MagicCard className="h-full transition-all duration-300 hover:-translate-y-0.5 hover:border-[var(--color-accent-primary)] hover:shadow-[0_8px_24px_rgba(99,102,241,0.15)] rounded-lg border border-[var(--color-border-subtle)] p-6" gradientSize={200} gradientColor="#1a1a2e" gradientFrom="#7c3aed" gradientTo="#4f46e5">
                      <div className="flex h-full flex-col gap-4">
                        <div className="flex items-center justify-between gap-3">
                          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-indigo-500/35 bg-indigo-500/15 text-sm font-bold text-indigo-200">
                            {surah.id}
                          </div>
                          <span
                            className="font-arabic text-2xl leading-relaxed font-semibold text-[var(--color-text-primary)]"
                            lang="ar"
                            dir="rtl"
                          >
                            {surah.name}
                          </span>
                        </div>

                        <div className="mt-auto">
                          <h3 className="text-base font-semibold text-[var(--color-text-primary)]">
                            {surah.name_transliterated}
                          </h3>
                          <div className="mt-1 flex items-center gap-2 text-xs font-medium tracking-wide text-[var(--color-text-secondary)] uppercase">
                            <span>{surah.revelation_type}</span>
                            <span aria-hidden="true">•</span>
                            <span>{tCommon("verses", { count: surah.verse_count })}</span>
                          </div>
                        </div>
                      </div>
                    </MagicCard>
                  </button>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}

        {!isLoading && filteredSurahs.length === 0 && (
          <div className="py-20 text-center text-[var(--color-text-muted)]">
            {t("noSurahs", { filter })}
          </div>
        )}
      </div>
    </div>
  )
}
