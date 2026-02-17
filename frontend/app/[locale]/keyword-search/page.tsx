"use client"

import { useState, useEffect, useCallback, Suspense, useMemo, useRef } from "react"
import dynamic from "next/dynamic"
import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { useTranslations } from "next-intl"
import { toast } from "sonner"
import { SearchInput } from "@/components/keyword-search/search-input"
import { RichRootCard } from "@/components/keyword-search/rich-root-card"
import { StatsBar } from "@/components/keyword-search/stats-bar"
import { DerivedWords } from "@/components/keyword-search/derived-words"
// Lazy-load recharts (~200KB) — only needed when chart is visible
const SurahChart = dynamic(
  () =>
    import("@/components/keyword-search/surah-chart").then((mod) => ({ default: mod.SurahChart })),
  {
    ssr: false,
    loading: () => (
      <div className="w-full animate-pulse rounded-lg bg-zinc-800/50" style={{ height: "400px" }} />
    ),
  }
)
import { VerseCard } from "@/components/keyword-search/verse-card"
import { Pagination } from "@/components/keyword-search/pagination"
import { stripArabicDiacritics } from "@/lib/utils/arabic"
import { stripHebrewDiacritics } from "@/lib/utils/hebrew"
import { stripGreekDiacritics } from "@/lib/utils/greek"
import { RootBrowser } from "@/components/keyword-search/root-browser"
import { Skeleton } from "@/components/ui/skeleton"
import {
  searchKeywordApiSearchKeywordPost,
  getSurahDetailApiMetadataQuranSurahsSurahIdGet,
  getQuranSurahsApiMetadataQuranSurahsGet,
} from "@/lib/api/sdk.gen"
import type { KeywordSearchResponse, VerseMatchItem } from "@/lib/api/types.gen"
import { Tabs as VercelTabs } from "@/components/ui/vercel-tabs"
import { LanguageTabs, type LanguageTab } from "@/components/keyword-search/language-tabs"
import {
  BibleCategoryTabs,
  type BibleCategoryFilter,
} from "@/components/keyword-search/bible-category-tabs"
import { AccuracyDisclaimer } from "@/components/keyword-search/accuracy-disclaimer"
import { ExperimentalDisclaimer } from "@/components/keyword-search/experimental-disclaimer"
import { API_BASE } from "@/lib/config"

type TabType = "results" | "browser"

const QURAN_VERSES_PER_PAGE = 30
const BIBLE_VERSES_PER_PAGE = 12

const EMPTY_STATE_SUGGESTIONS: Record<LanguageTab, string[]> = {
  quran: ["كتب", "صبر", "علم"],
  hebrew_ot: ["H3789", "H2617", "H430"],
  greek_nt: ["G3056", "G26", "G4102"],
}

// Bible search response type (not in generated types yet)
interface BibleSearchResult {
  success: boolean
  query: string
  root: string | null
  root_source: string
  strong_number: string | null
  total_occurrences: number
  unique_words: string[]
  book_distribution: { book_id: number; book_name: string; count: number }[]
  verses: {
    book_id: number
    book_name: string
    chapter: number
    verse: number
    text_original: string | null
    text_english: string | null
    matched_words: string[]
    reference: string
  }[]
  pagination: {
    page: number
    per_page: number
    total_verses: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
  transliteration: string | null
  word_transliterations: Record<string, string>
}

type BibleVerseMatch = BibleSearchResult["verses"][number]

const isQuranVerseMatch = (verse: VerseMatchItem | BibleVerseMatch): verse is VerseMatchItem =>
  "surah_id" in verse

const isBibleVerseMatch = (verse: VerseMatchItem | BibleVerseMatch): verse is BibleVerseMatch =>
  "book_id" in verse

const isAbortError = (error: unknown): boolean =>
  error instanceof DOMException
    ? error.name === "AbortError"
    : error instanceof Error && error.name === "AbortError"

function KeywordSearchContent() {
  const t = useTranslations("KeywordSearch")
  const [query, setQuery] = useState("")
  const [activeLanguage, setActiveLanguage] = useState<LanguageTab>("quran")
  const [bibleCategoryFilter, setBibleCategoryFilter] = useState<BibleCategoryFilter>("all")
  const [searchResult, setSearchResult] = useState<KeywordSearchResponse | null>(null)
  const [bibleSearchResult, setBibleSearchResult] = useState<BibleSearchResult | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>("results")
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedWord, setSelectedWord] = useState<string | null>(null)
  const [translations, setTranslations] = useState<Map<string, string>>(new Map())
  const [translationsLoading, setTranslationsLoading] = useState(false)
  const [surahTransliterations, setSurahTransliterations] = useState<Map<number, string>>(new Map())
  const searchAbortControllerRef = useRef<AbortController | null>(null)
  const versesPerPage = activeLanguage === "quran" ? QURAN_VERSES_PER_PAGE : BIBLE_VERSES_PER_PAGE

  useEffect(() => {
    return () => {
      if (searchAbortControllerRef.current) {
        searchAbortControllerRef.current.abort()
        searchAbortControllerRef.current = null
      }
    }
  }, [])

  // Fetch surah Latin transliterations on mount
  useEffect(() => {
    const controller = new AbortController()

    const fetchSurahNames = async () => {
      try {
        const response = await getQuranSurahsApiMetadataQuranSurahsGet({
          signal: controller.signal,
        })

        if (controller.signal.aborted) {
          return
        }

        const body = response.data as
          | { data?: { surahs?: Array<{ id: number; transliteration: string }> } }
          | undefined
        const surahs = body?.data?.surahs || []
        const map = new Map<number, string>()
        surahs.forEach((s) => {
          map.set(s.id, s.transliteration)
        })
        setSurahTransliterations(map)
      } catch (error) {
        if (isAbortError(error)) {
          return
        }
      }
    }
    fetchSurahNames()

    return () => {
      controller.abort()
    }
  }, [])

  // Helper: get Latin surah name, fallback to Arabic
  const getSurahName = useCallback(
    (surahId: number, arabicFallback: string) =>
      surahTransliterations.get(surahId) || arabicFallback,
    [surahTransliterations]
  )

  const handleSearch = useCallback(
    async (searchQuery: string) => {
      if (!searchQuery.trim()) {
        setError(
          activeLanguage === "quran"
            ? t("errorQuran")
            : activeLanguage === "hebrew_ot"
              ? t("errorHebrew")
              : t("errorGreek")
        )
        return
      }

      if (searchAbortControllerRef.current) {
        searchAbortControllerRef.current.abort()
      }

      const controller = new AbortController()
      searchAbortControllerRef.current = controller

      setIsLoading(true)
      setError(null)
      setSelectedWord(null)
      setCurrentPage(1)

      try {
        if (activeLanguage === "quran") {
          const response = await searchKeywordApiSearchKeywordPost({
            body: {
              query: searchQuery.trim(),
              page: 1,
              per_page: 0, // 0 = return ALL verses in one call
            },
            signal: controller.signal,
          })

          if (controller.signal.aborted) {
            return
          }

          if (response.data) {
            setSearchResult(response.data as KeywordSearchResponse)
            setBibleSearchResult(null)
          }
        } else {
          // Bible search via raw fetch (Hebrew OT or Greek NT)
          const languageFilter = activeLanguage === "hebrew_ot" ? "hebrew" : "greek"

          // Build request body with optional category filter
          const requestBody: Record<string, unknown> = {
            query: searchQuery.trim(),
            page: 1,
            per_page: 0,
            language_filter: languageFilter,
          }

          // Add category filter if not "all"
          if (bibleCategoryFilter !== "all") {
            requestBody.category_filter = bibleCategoryFilter
          }

          const res = await fetch(`${API_BASE}/api/keyword-search/bible/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            signal: controller.signal,
            body: JSON.stringify(requestBody),
          })

          if (controller.signal.aborted) {
            return
          }

          if (!res.ok) {
            if (res.status === 429) {
              toast.error(t("rateLimited"))
            } else {
              toast.error(t("searchFailed"))
            }
            setError(t("searchFailed"))
            return
          }

          const data = (await res.json()) as BibleSearchResult
          if (controller.signal.aborted) {
            return
          }

          setBibleSearchResult(data)
          setSearchResult(null)
        }
      } catch (err: unknown) {
        if (isAbortError(err)) {
          return
        }

        const error = err as { status?: number }
        if (error.status === 429) {
          toast.error(t("rateLimited"))
        } else {
          toast.error(t("searchFailed"))
        }
        setError(t("searchFailed"))
      } finally {
        if (searchAbortControllerRef.current === controller) {
          searchAbortControllerRef.current = null
        }

        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      }
    },
    [activeLanguage, bibleCategoryFilter, t]
  )

  // All pagination is client-side — no API calls needed
  const handlePageChange = useCallback((newPage: number) => {
    setCurrentPage(newPage)
    // Scroll to top of verse results
    window.scrollTo({ top: 0, behavior: "smooth" })
  }, [])

  // All word filtering is client-side — no API calls needed
  const handleWordFilter = useCallback((word: string | null) => {
    setSelectedWord(word)
    setCurrentPage(1) // Reset to page 1 when filtering
  }, [])

  const handleRootSelect = useCallback(
    (root: string) => {
      setQuery(root)
      handleSearch(root)
      setActiveTab("results")
    },
    [handleSearch]
  )

  const handleSuggestionSearch = useCallback(
    (suggestion: string) => {
      setQuery(suggestion)
      void handleSearch(suggestion)
    },
    [handleSearch]
  )

  const handleLanguageChange = useCallback((language: LanguageTab) => {
    setActiveLanguage(language)
    setBibleCategoryFilter("all") // Reset category filter when changing language
    setSearchResult(null)
    setBibleSearchResult(null)
    setSelectedWord(null)
    setCurrentPage(1)
    setError(null)
  }, [])

  // Track if category change should trigger re-search
  const [shouldResearch, setShouldResearch] = useState(false)

  const handleCategoryChange = useCallback(
    (category: BibleCategoryFilter) => {
      setBibleCategoryFilter(category)
      // Mark that we should re-search if we have results
      if (bibleSearchResult && query.trim()) {
        setShouldResearch(true)
      }
    },
    [bibleSearchResult, query]
  )

  // Effect to trigger re-search when category changes
  useEffect(() => {
    if (
      shouldResearch &&
      query.trim() &&
      (activeLanguage === "hebrew_ot" || activeLanguage === "greek_nt")
    ) {
      setShouldResearch(false)
      handleSearch(query)
    }
  }, [shouldResearch, query, activeLanguage, handleSearch])

  // Fetch Turkish translations after search results arrive
  useEffect(() => {
    if (!searchResult?.verses?.length) {
      setTranslationsLoading(false)
      return
    }

    const controller = new AbortController()

    const fetchTranslations = async () => {
      setTranslationsLoading(true)
      const translationMap = new Map<string, string>()

      // Group verses by surah_id
      const surahIds = [...new Set(searchResult.verses!.map((v) => v.surah_id))]

      // Fetch each surah's data
      await Promise.all(
        surahIds.map(async (surahId) => {
          try {
            const response = await getSurahDetailApiMetadataQuranSurahsSurahIdGet({
              path: { surah_id: surahId },
              signal: controller.signal,
            })

            if (controller.signal.aborted) {
              return
            }

            // API returns { success, data: { surah: { verses: [...] } } }
            const body = response.data as
              | { data?: { surah?: { verses?: Array<{ text: string; translation: string }> } } }
              | undefined
            const verses = body?.data?.surah?.verses
            if (verses) {
              verses.forEach((verse: { text: string; translation: string }, index: number) => {
                const key = `${surahId}:${index + 1}`
                translationMap.set(key, verse.translation)
              })
            }
          } catch (error) {
            if (isAbortError(error)) {
              return
            }

            // Silently fail for individual surahs
          }
        })
      )

      if (controller.signal.aborted) {
        return
      }

      setTranslations(translationMap)
      setTranslationsLoading(false)
    }

    fetchTranslations()

    return () => {
      controller.abort()
    }
  }, [searchResult?.verses])

  // Helper to get translation
  const getTranslation = useCallback(
    (surahId: number, ayahNumber: number): string | undefined => {
      return translations.get(`${surahId}:${ayahNumber}`)
    },
    [translations]
  )

  // Filter verses by selected word (all data is in memory — instant)
  const filteredVerses = useMemo(() => {
    if (activeLanguage === "quran") {
      if (!searchResult?.verses) return []
      if (!selectedWord) return searchResult.verses
      const normalizedSelected = stripArabicDiacritics(selectedWord)
      return searchResult.verses.filter((v) =>
        v.matched_words.some((w) => stripArabicDiacritics(w) === normalizedSelected)
      )
    } else {
      if (!bibleSearchResult?.verses) return []
      if (!selectedWord) return bibleSearchResult.verses
      const stripFn = activeLanguage === "hebrew_ot" ? stripHebrewDiacritics : stripGreekDiacritics
      const normalizedSelected = stripFn(selectedWord)
      return bibleSearchResult.verses.filter((v) =>
        v.matched_words.some((w) => stripFn(w) === normalizedSelected)
      )
    }
  }, [activeLanguage, searchResult?.verses, bibleSearchResult?.verses, selectedWord])

  const totalFilteredPages = useMemo(
    () => Math.max(1, Math.ceil(filteredVerses.length / versesPerPage)),
    [filteredVerses.length, versesPerPage]
  )

  const paginatedVerses = useMemo(
    () => filteredVerses.slice((currentPage - 1) * versesPerPage, currentPage * versesPerPage),
    [filteredVerses, currentPage, versesPerPage]
  )

  // Compute chart data based on selected word (client-side)
  const chartData = useMemo(() => {
    if (activeLanguage === "quran") {
      // If no word selected, show full root distribution
      if (!selectedWord || !searchResult?.surah_distribution) {
        return searchResult?.surah_distribution || []
      }

      // If word selected, compute distribution from filtered verses
      if (!searchResult?.verses) return []

      const normalizedSelected = stripArabicDiacritics(selectedWord)
      const wordFilteredVerses = searchResult.verses.filter((v) =>
        v.matched_words.some((w) => stripArabicDiacritics(w) === normalizedSelected)
      )

      // Aggregate by surah
      const surahMap = new Map<number, { surah_id: number; surah_name: string; count: number }>()
      for (const verse of wordFilteredVerses) {
        const existing = surahMap.get(verse.surah_id)
        if (existing) {
          existing.count += 1
        } else {
          surahMap.set(verse.surah_id, {
            surah_id: verse.surah_id,
            surah_name: verse.surah_name,
            count: 1,
          })
        }
      }

      return Array.from(surahMap.values())
    } else {
      // Bible: book distribution
      if (!selectedWord || !bibleSearchResult?.book_distribution) {
        return (
          bibleSearchResult?.book_distribution?.map((b) => ({
            surah_id: b.book_id,
            surah_name: b.book_name,
            count: b.count,
          })) || []
        )
      }

      // If word selected, compute distribution from filtered verses
      if (!bibleSearchResult?.verses) return []

      const stripFn = activeLanguage === "hebrew_ot" ? stripHebrewDiacritics : stripGreekDiacritics
      const normalizedSelected = stripFn(selectedWord)
      const wordFilteredVerses = bibleSearchResult.verses.filter((v) =>
        v.matched_words.some((w) => stripFn(w) === normalizedSelected)
      )

      // Aggregate by book
      const bookMap = new Map<number, { surah_id: number; surah_name: string; count: number }>()
      for (const verse of wordFilteredVerses) {
        const existing = bookMap.get(verse.book_id)
        if (existing) {
          existing.count += 1
        } else {
          bookMap.set(verse.book_id, {
            surah_id: verse.book_id,
            surah_name: verse.book_name,
            count: 1,
          })
        }
      }

      return Array.from(bookMap.values())
    }
  }, [activeLanguage, selectedWord, searchResult, bibleSearchResult])

  // Compute filtered stats based on selected word
  const filteredStats = useMemo(() => {
    const currentResult = activeLanguage === "quran" ? searchResult : bibleSearchResult

    if (!selectedWord || !currentResult) {
      return {
        totalOccurrences: currentResult?.total_occurrences || 0,
        uniqueWords: (currentResult?.unique_words || []).length,
        surahCount:
          activeLanguage === "quran"
            ? (searchResult?.surah_distribution || []).length
            : (bibleSearchResult?.book_distribution || []).length,
      }
    }

    // When word selected, compute from filtered data
    return {
      totalOccurrences: filteredVerses.length,
      uniqueWords: 1,
      surahCount: chartData.length,
    }
  }, [activeLanguage, selectedWord, searchResult, bibleSearchResult, filteredVerses, chartData])

  const emptyStateHint =
    activeLanguage === "quran"
      ? t("emptyStateHintQuran")
      : activeLanguage === "hebrew_ot"
        ? t("emptyStateHintHebrew")
        : t("emptyStateHintGreek")

  const emptyStateSuggestions = EMPTY_STATE_SUGGESTIONS[activeLanguage]

  return (
    <div className="relative min-h-screen bg-[var(--color-bg-app)]">
      {/* Ambient teal gradient background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-teal-950/20 via-transparent to-transparent" />
      </div>

      {/* Header */}
      <div className="relative px-6 pt-10 pb-3">
        <div className="mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={springPresets.fluid}
          >
            {/* Ornamental divider */}
            <div className="mb-4 text-center text-xs tracking-widest text-[var(--color-text-muted)]">
              ◆
            </div>

            {/* Title */}
            <h1 className="font-display mb-2 text-center text-4xl font-semibold tracking-tight text-[var(--color-text-primary)]">
              {t("pageTitle")}
            </h1>
            <p className="mb-6 text-center text-base text-[var(--color-text-secondary)]">
              {activeLanguage === "quran"
                ? t("subtitleQuran")
                : activeLanguage === "hebrew_ot"
                  ? t("subtitleHebrew")
                  : t("subtitleGreek")}
            </p>

            {/* Language Tabs */}
            <div className="mb-6 flex justify-center border-b border-[var(--color-border-subtle)] pb-4">
              <LanguageTabs activeTab={activeLanguage} onTabChange={handleLanguageChange} />
            </div>

            {/* Bible Category Filter (only for Bible modes) */}
            {(activeLanguage === "hebrew_ot" || activeLanguage === "greek_nt") && (
              <div className="mb-6 flex justify-center">
                <BibleCategoryTabs
                  activeCategory={bibleCategoryFilter}
                  onCategoryChange={handleCategoryChange}
                  languageMode={activeLanguage}
                />
              </div>
            )}

            {/* Search Input */}
            <SearchInput
              value={query}
              onChange={setQuery}
              onSearch={handleSearch}
              isLoading={isLoading}
              placeholder={
                activeLanguage === "quran"
                  ? t("placeholderQuran")
                  : activeLanguage === "hebrew_ot"
                    ? t("placeholderHebrew")
                    : t("placeholderGreek")
              }
            />

            {/* Experimental Disclaimer */}
            <ExperimentalDisclaimer className="mt-4" />
          </motion.div>
        </div>
      </div>

      {/* Content */}
      <div className="relative px-6 pb-16">
        <div className="mx-auto max-w-4xl">
          {/* Tab Navigation */}
          <VercelTabs
            tabs={[
              { id: "results", label: t("tabs.results") },
              ...(activeLanguage === "quran" ? [{ id: "browser", label: t("tabs.browser") }] : []),
            ]}
            activeTab={activeTab}
            onTabChange={(tabId) => setActiveTab(tabId as TabType)}
            className="mb-8 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/60 p-1"
          />

          {/* Tab Content */}
          {activeTab === "results" && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={springPresets.snappy}
            >
              {/* Loading skeletons */}
              {isLoading ? (
                <div className="space-y-6">
                  {/* Root card skeleton */}
                  <div className="flex flex-col items-center gap-3 py-6">
                    <Skeleton className="h-16 w-32" />
                    <Skeleton className="h-6 w-24" />
                  </div>
                  {/* Stats skeleton */}
                  <div className="grid grid-cols-3 gap-4">
                    {[1, 2, 3].map((slot) => (
                      <Skeleton key={`keyword-stats-skeleton-${slot}`} className="h-20" />
                    ))}
                  </div>
                  {/* Verse skeletons */}
                  <div className="space-y-4">
                    {[1, 2, 3, 4, 5].map((slot) => (
                      <Skeleton key={`keyword-verse-skeleton-${slot}`} className="h-40" />
                    ))}
                  </div>
                </div>
              ) : error ? (
                // Error state
                <div className="rounded-xl border border-red-500/30 bg-red-500/5 px-4 py-8 text-center">
                  <p className="text-sm font-medium text-red-300">{error}</p>
                </div>
              ) : searchResult || bibleSearchResult ? (
                <div className="space-y-8">
                  {/* Buckwalter/Strong's feedback */}
                  {activeLanguage === "quran" &&
                    searchResult?.root_source?.includes("buckwalter") &&
                    searchResult.root && (
                      <div className="text-center text-sm text-[var(--color-text-secondary)]">
                        {t("detectedBuckwalter")}{" "}
                        <span className="font-arabic" lang="ar">
                          {searchResult.root}
                        </span>
                      </div>
                    )}

                  {/* Root not found */}
                  {(activeLanguage === "quran" && searchResult?.root_source === "not_found") ||
                  (activeLanguage !== "quran" && bibleSearchResult?.root_source === "not_found") ? (
                    <div className="space-y-4 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/40 px-6 py-10 text-center">
                      <div
                        className="text-xs tracking-widest text-[var(--color-text-muted)]"
                        aria-hidden="true"
                      >
                        ◆
                      </div>
                      <p className="text-lg font-semibold text-[var(--color-text-primary)]">
                        {t("noRootFound", {
                          query:
                            activeLanguage === "quran"
                              ? searchResult?.query || ""
                              : bibleSearchResult?.query || "",
                        })}
                      </p>
                      <p className="mt-2 text-sm text-[var(--color-text-secondary)]">
                        {activeLanguage === "quran"
                          ? t("tryDifferentQuran")
                          : activeLanguage === "hebrew_ot"
                            ? t("tryDifferentHebrew")
                            : t("tryDifferentGreek")}
                      </p>

                      <div className="space-y-2">
                        <p className="text-xs font-medium tracking-wide text-[var(--color-text-secondary)] uppercase">
                          {t("emptyStateExamples")}
                        </p>
                        <div className="flex flex-wrap justify-center gap-2">
                          {emptyStateSuggestions.map((suggestion) => (
                            <button
                              key={`keyword-empty-retry-${suggestion}`}
                              type="button"
                              onClick={() => handleSuggestionSearch(suggestion)}
                              className="rounded-full border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] px-3 py-1.5 text-sm text-[var(--color-text-secondary)] transition-colors hover:border-[var(--color-border-glow)] hover:text-[var(--color-text-primary)]"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      </div>

                      {activeLanguage === "quran" && (
                        <div>
                          <button
                            type="button"
                            onClick={() => setActiveTab("browser")}
                            className="rounded-lg bg-[var(--color-accent-primary)] px-4 py-2 text-sm font-medium text-[#09090b] transition-colors hover:bg-[var(--color-accent-hover)]"
                          >
                            {t("browseRoots")}
                          </button>
                        </div>
                      )}
                    </div>
                  ) : (
                    <>
                      <div className="flex flex-col gap-8 lg:flex-row lg:items-start">
                        <motion.div
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={springPresets.fluid}
                          className="lg:sticky lg:top-20 lg:max-h-[calc(100vh-6rem)] lg:w-80 lg:shrink-0 lg:overflow-y-auto lg:pe-3 lg:[scrollbar-color:#3f3f46_transparent] lg:[scrollbar-width:thin] lg:[&::-webkit-scrollbar]:w-2 lg:[&::-webkit-scrollbar-thumb]:rounded lg:[&::-webkit-scrollbar-thumb]:bg-zinc-700 lg:[&::-webkit-scrollbar-thumb:hover]:bg-zinc-600"
                          data-testid="root-card-panel"
                        >
                          <div className="space-y-6">
                            <RichRootCard
                              root={
                                activeLanguage === "quran"
                                  ? searchResult?.root || null
                                  : bibleSearchResult?.root || null
                              }
                              rootSource={
                                activeLanguage === "quran"
                                  ? searchResult?.root_source || ""
                                  : bibleSearchResult?.root_source || ""
                              }
                              rootBuckwalter={
                                activeLanguage === "quran"
                                  ? searchResult?.root_buckwalter
                                  : bibleSearchResult?.transliteration
                              }
                              query={query}
                              language={
                                activeLanguage === "quran"
                                  ? "arabic"
                                  : activeLanguage === "hebrew_ot"
                                    ? "hebrew"
                                    : "greek"
                              }
                            />
                            <StatsBar
                              totalOccurrences={filteredStats.totalOccurrences}
                              uniqueWords={filteredStats.uniqueWords}
                              surahCount={filteredStats.surahCount}
                              language={activeLanguage}
                            />
                            <DerivedWords
                              words={
                                activeLanguage === "quran"
                                  ? searchResult?.unique_words || []
                                  : bibleSearchResult?.unique_words || []
                              }
                              selectedWord={selectedWord}
                              onWordSelect={handleWordFilter}
                              transliterations={
                                activeLanguage === "quran"
                                  ? searchResult?.word_transliterations || {}
                                  : bibleSearchResult?.word_transliterations || {}
                              }
                              language={
                                activeLanguage === "quran"
                                  ? "arabic"
                                  : activeLanguage === "hebrew_ot"
                                    ? "hebrew"
                                    : "greek"
                              }
                            />
                          </div>
                        </motion.div>

                        <motion.div
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={springPresets.fluid}
                          className="min-w-0 flex-1 space-y-8"
                          data-testid="results-panel"
                        >
                          <SurahChart
                            data={
                              activeLanguage === "quran"
                                ? chartData.map((d) => ({
                                    ...d,
                                    surah_name: getSurahName(d.surah_id, d.surah_name),
                                  }))
                                : chartData
                            }
                            language={activeLanguage}
                          />

                          <div className="space-y-4">
                            <div className="text-center text-xs tracking-widest text-[var(--color-text-muted)]">
                              ◆
                            </div>
                            <h3 className="text-center text-lg font-medium text-[var(--color-text-primary)]">
                              {t("verseResults")}
                            </h3>
                            {activeLanguage === "quran"
                              ? paginatedVerses.map((verse) => {
                                  if (!isQuranVerseMatch(verse)) {
                                    return null
                                  }

                                  return (
                                    <VerseCard
                                      key={`${verse.surah_id}-${verse.ayah_number}`}
                                      surahId={verse.surah_id}
                                      surahName={getSurahName(verse.surah_id, verse.surah_name)}
                                      ayahNumber={verse.ayah_number}
                                      textUthmani={verse.text_uthmani}
                                      textClean={verse.text_clean}
                                      matchedWords={verse.matched_words}
                                      turkishTranslation={getTranslation(
                                        verse.surah_id,
                                        verse.ayah_number
                                      )}
                                      isTranslationLoading={translationsLoading}
                                      language="arabic"
                                    />
                                  )
                                })
                              : paginatedVerses.map((verse) => {
                                  if (!isBibleVerseMatch(verse)) {
                                    return null
                                  }

                                  return (
                                    <VerseCard
                                      key={`${verse.book_id}-${verse.chapter}-${verse.verse}`}
                                      surahId={verse.book_id}
                                      surahName={verse.book_name}
                                      ayahNumber={verse.verse}
                                      textUthmani={verse.text_original || ""}
                                      textClean={verse.text_original || ""}
                                      matchedWords={verse.matched_words}
                                      englishTranslation={verse.text_english}
                                      chapter={verse.chapter}
                                      language={activeLanguage === "hebrew_ot" ? "hebrew" : "greek"}
                                    />
                                  )
                                })}
                          </div>

                          {filteredVerses.length > versesPerPage && (
                            <Pagination
                              page={currentPage}
                              totalPages={totalFilteredPages}
                              totalVerses={filteredVerses.length}
                              hasNext={currentPage < totalFilteredPages}
                              hasPrev={currentPage > 1}
                              onPageChange={handlePageChange}
                            />
                          )}

                          {(activeLanguage === "hebrew_ot" || activeLanguage === "greek_nt") && (
                            <div className="mt-8 border-t border-[var(--color-border-subtle)] pt-6">
                              <AccuracyDisclaimer />
                            </div>
                          )}
                        </motion.div>
                      </div>
                    </>
                  )}
                </div>
              ) : (
                // Empty state (before any search)
                <div className="flex min-h-[45vh] flex-col items-center justify-center gap-5 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/40 px-6 py-10 text-center">
                  <div
                    className="text-xs tracking-widest text-[var(--color-text-muted)]"
                    aria-hidden="true"
                  >
                    ◆
                  </div>
                  <p className="text-xl font-semibold text-[var(--color-text-primary)]">
                    {activeLanguage === "quran"
                      ? t("emptyStateQuran")
                      : activeLanguage === "hebrew_ot"
                        ? t("emptyStateHebrew")
                        : t("emptyStateGreek")}
                  </p>
                  <p className="max-w-2xl text-sm text-[var(--color-text-secondary)]">
                    {emptyStateHint}
                  </p>

                  <div className="space-y-2">
                    <p className="text-xs font-medium tracking-wide text-[var(--color-text-secondary)] uppercase">
                      {t("emptyStateExamples")}
                    </p>
                    <div className="flex flex-wrap justify-center gap-2">
                      {emptyStateSuggestions.map((suggestion) => (
                        <button
                          key={`keyword-empty-suggestion-${suggestion}`}
                          type="button"
                          onClick={() => handleSuggestionSearch(suggestion)}
                          className="rounded-full border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] px-3 py-1.5 text-sm text-[var(--color-text-secondary)] transition-colors hover:border-[var(--color-border-glow)] hover:text-[var(--color-text-primary)]"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>

                  {activeLanguage === "quran" && (
                    <button
                      type="button"
                      onClick={() => setActiveTab("browser")}
                      className="rounded-lg bg-[var(--color-accent-primary)] px-4 py-2 text-sm font-medium text-[#09090b] transition-colors hover:bg-[var(--color-accent-hover)]"
                    >
                      {t("browseRoots")}
                    </button>
                  )}
                </div>
              )}
            </motion.div>
          )}

          {activeTab === "browser" && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={springPresets.snappy}
            >
              <RootBrowser onRootSelect={handleRootSelect} />
            </motion.div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function KeywordSearchPage() {
  const tCommon = useTranslations("Common")

  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
          <div className="text-[var(--color-text-secondary)]">{tCommon("loading")}</div>
        </div>
      }
    >
      <KeywordSearchContent />
    </Suspense>
  )
}
