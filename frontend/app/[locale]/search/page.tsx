"use client"

import { useState, useEffect, Suspense, useRef, useCallback } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { useSession } from "@/lib/auth-client"
import { DotPattern } from "@/components/ui/dot-pattern"
import { AuroraSectionBackground } from "@/components/ui/aurora-background"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"
import { useRouter, useSearchParams } from "next/navigation"
import { ExternalLink, Search } from "lucide-react"
import { useTranslations } from "next-intl"
import { SearchTabs, SearchSource } from "@/components/search/search-tabs"
import { RateLimitBanner } from "@/components/search/rate-limit-banner"
import { useSSE } from "@/lib/hooks/use-sse"
import { usePreferencesStore } from "@/lib/stores/preferences-store"
import { parseCitations } from "@/lib/utils/parse-citations"
import { InlineCitation } from "@/components/compare/inline-citation"
import { VerseDetail } from "@/components/search/verse-tooltip"
import { SourceBadge, SourceType } from "@/components/compare/source-badge"
import { useLogger } from "@/lib/logger"
import { LanguageSelector } from "@/components/search/language-selector"
import { TranslatorSelector } from "@/components/search/translator-selector"
import { useKeywordStore, KeywordSuggestion } from "@/lib/stores/keyword-store"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { searchQuranApiSearchQuranPost, searchBibleApiSearchBiblePost } from "@/lib/api/sdk.gen"
import { API_BASE } from "@/lib/config"

interface SearchResult {
  source: string
  reference: string
  text: string
  score: number
}

interface SearchCompletePayload {
  results?: SearchResult[]
  detected_language?: string
}

interface SearchSSEMessage {
  type?: string
  content?: string
  verse_details?: Record<string, VerseDetail>
  error?: string
  message?: string
  result?: SearchCompletePayload
  detected_language?: string
}

interface SearchSSEAggregate {
  tokens: string
  verseDetails?: Record<string, VerseDetail>
  error?: string
  noResultsMessage?: string
  completeMessage?: SearchSSEMessage
}

const isAbortError = (error: unknown): boolean =>
  error instanceof DOMException
    ? error.name === "AbortError"
    : error instanceof Error && error.name === "AbortError"

function SearchContent() {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchResult[]>([])
  const [hasSearched, setHasSearched] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [activeTab, setActiveTab] = useState<SearchSource>("quran")
  const [streamedAnswer, setStreamedAnswer] = useState("")
  const [verseDetails, setVerseDetails] = useState<Record<string, VerseDetail>>({})
  const [highlightedVerse, setHighlightedVerse] = useState<string | null>(null)
  const [selectedLanguage, setSelectedLanguage] = useState<string | null>(null)
  const [detectedLanguage, setDetectedLanguage] = useState<string | undefined>(undefined)
  const [selectedTranslator, setSelectedTranslator] = useState("diyanet")
  const [isEnhancing, setIsEnhancing] = useState(false)
  const [isRateLimited, setIsRateLimited] = useState(false)
  const resultsContainerRef = useRef<HTMLDivElement>(null)
  const hasHandledSSEError = useRef(false)
  const hasAutoExecuted = useRef(false)
  const enhanceAbortControllerRef = useRef<AbortController | null>(null)
  const batchSearchAbortControllerRef = useRef<AbortController | null>(null)

  // Zustand selectors — subscribe only to used fields, not the entire store
  const advancedMode = useKeywordStore((s) => s.advancedMode)
  const keywords = useKeywordStore((s) => s.keywords)
  const selectedKeywords = useKeywordStore((s) => s.selectedKeywords)
  const setAdvancedMode = useKeywordStore((s) => s.setAdvancedMode)
  const setKeywords = useKeywordStore((s) => s.setKeywords)
  const resetKeywordStore = useKeywordStore((s) => s.reset)

  const log = useLogger("SearchPage")
  const { data: session, isPending } = useSession()
  const user = session?.user
  const isLoading = isPending
  const router = useRouter()
  const searchParams = useSearchParams()

  const {
    data: sseData,
    isStreaming,
    error: sseError,
    errorCode: sseErrorCode,
    startStream,
  } = useSSE()
  const { enable_streaming } = usePreferencesStore()

  const t = useTranslations("Search")
  const tToast = useTranslations("Toast")

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/sign-in")
    }
  }, [user, isLoading, router])

  useEffect(() => {
    return () => {
      if (enhanceAbortControllerRef.current) {
        enhanceAbortControllerRef.current.abort()
        enhanceAbortControllerRef.current = null
      }

      if (batchSearchAbortControllerRef.current) {
        batchSearchAbortControllerRef.current.abort()
        batchSearchAbortControllerRef.current = null
      }
    }
  }, [])

  useEffect(() => {
    const source = searchParams?.get("source") as SearchSource
    if (source && ["quran", "ot", "nt", "apocrypha"].includes(source)) {
      setActiveTab(source)
    }

    const advanced = searchParams?.get("advanced")
    if (advanced === "true") {
      setAdvancedMode(true)
    }
  }, [searchParams, setAdvancedMode])

  const sseProcessedCount = useRef(0)

  useEffect(() => {
    if (sseData.length === 0) {
      sseProcessedCount.current = 0
      return
    }

    const newMessages = sseData.slice(sseProcessedCount.current)
    sseProcessedCount.current = sseData.length

    const streamState = newMessages.reduce<SearchSSEAggregate>(
      (acc, rawMessage) => {
        const message = rawMessage as SearchSSEMessage

        if (message.type === "token") {
          acc.tokens += message.content ?? ""
        }

        if (!acc.verseDetails && message.verse_details) {
          acc.verseDetails = message.verse_details
        }

        if (!acc.error && message.error) {
          acc.error = message.error
        }

        if (!acc.noResultsMessage && message.type === "no_results") {
          acc.noResultsMessage = message.message || "No results found for your query."
        }

        if (!acc.completeMessage && message.type === "complete") {
          acc.completeMessage = message
        }

        return acc
      },
      {
        tokens: "",
      }
    )

    if (streamState.tokens) {
      setStreamedAnswer((previousTokens) => previousTokens + streamState.tokens)
    }

    if (streamState.verseDetails) {
      setVerseDetails(streamState.verseDetails)
    }

    if (streamState.error) {
      log.error("SSE server error", { error: streamState.error })
    }

    if (streamState.noResultsMessage) {
      setStreamedAnswer("")
      setIsSearching(false)
      toast.info(streamState.noResultsMessage)
    }

    const completeMsg = streamState.completeMessage
    if (completeMsg) {
      const completeResult = completeMsg.result
      if (completeResult?.results) {
        setResults(completeResult.results)

        if (completeResult.results.length === 0) {
          setStreamedAnswer("")
        }
      }

      const detectedLanguage = completeResult?.detected_language || completeMsg.detected_language
      if (detectedLanguage) {
        setDetectedLanguage(detectedLanguage)
      }
      setIsSearching(false)
    }
  }, [log, sseData, sseData.length])

  const handleTabChange = (tab: SearchSource) => {
    setActiveTab(tab)
    setHasSearched(false)
    setResults([])
    setStreamedAnswer("")
    setVerseDetails({})
    setHighlightedVerse(null)
    setIsRateLimited(false)
    resetKeywordStore()
    const params = new URLSearchParams()
    params.set("source", tab)
    if (advancedMode) {
      params.set("advanced", "true")
    }
    router.push(`/search?${params.toString()}`)
  }

  const mapSourceToType = useCallback((source: string): SourceType => {
    switch (source) {
      case "quran":
        return "quran"
      case "bible_ot":
      case "ot":
        return "old_testament"
      case "bible_nt":
      case "nt":
        return "new_testament"
      case "bible_apocrypha":
      case "apocrypha":
        return "apocrypha"
      default:
        return "quran"
    }
  }, [])

  const scrollToVerse = useCallback((reference: string) => {
    const element = document.querySelector(`[data-verse-id="${reference}"]`)
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "center" })
      setHighlightedVerse(reference)
      setTimeout(() => setHighlightedVerse(null), 2000)
    }
  }, [])

  const navigateToVerse = useCallback(
    (reference: string) => {
      const verse = verseDetails[reference]
      if (!verse) {
        log.warn("No verse details for reference, falling back to scroll", {
          action: "navigateToVerse",
          reference,
        })
        scrollToVerse(reference)
        return
      }

      let url = ""
      if (verse.source === "quran_tr" || verse.source === "quran") {
        const surahId = verse.surah_id || verse.chapter
        const verseId = verse.verse_id || verse.verse
        url = `/quran/${surahId}?verse=${verseId}`
      } else if (verse.source.startsWith("bible_")) {
        const bookNr = verse.book_nr || 1
        url = `/bible/${bookNr}?chapter=${verse.chapter}&verse=${verse.verse}`
      } else {
        log.warn("Unknown source format, falling back to scroll", {
          action: "navigateToVerse",
          reference,
          source: verse.source,
        })
        scrollToVerse(reference)
        return
      }

      window.open(url, "_blank", "noopener,noreferrer")
    },
    [verseDetails, scrollToVerse, log]
  )

  /** Strip redundant metadata prefix like "[38:29] Sâd (Sad) - Score: 0.060 " from verse text */
  const extractVerseText = (text: string): string => {
    return text.replace(/^\[[\d:]+\]\s+.*?-\s*Score:\s*[\d.]+\s*/, "")
  }

  const getPlaceholder = () => {
    switch (activeTab) {
      case "quran":
        return t("placeholder")
      case "ot":
        return t("biblePlaceholder")
      case "nt":
        return t("biblePlaceholder")
      case "apocrypha":
        return t("biblePlaceholder")
      default:
        return t("placeholder")
    }
  }

  const suggestedQueries = [
    t("emptyState.suggestions.patience"),
    t("emptyState.suggestions.creation"),
    t("emptyState.suggestions.justice"),
  ]

  const quickTips = [
    {
      title: t("emptyState.tips.semantic.title"),
      description: t("emptyState.tips.semantic.description"),
    },
    {
      title: t("emptyState.tips.compare.title"),
      description: t("emptyState.tips.compare.description"),
    },
    {
      title: t("emptyState.tips.keyword.title"),
      description: t("emptyState.tips.keyword.description"),
    },
  ]

  const isPreSearchState =
    !query.trim() &&
    !hasSearched &&
    !isSearching &&
    !isStreaming &&
    results.length === 0 &&
    !streamedAnswer

  const isNoResultsState =
    hasSearched &&
    !isSearching &&
    !isStreaming &&
    results.length === 0 &&
    !streamedAnswer &&
    !isRateLimited

  const suspenseSkeletonKeys = [
    "search-suspense-skeleton-a",
    "search-suspense-skeleton-b",
    "search-suspense-skeleton-c",
  ]

  const loadingSkeletonKeys = [
    "search-loading-skeleton-a",
    "search-loading-skeleton-b",
    "search-loading-skeleton-c",
  ]

  const sourceSkeletonKeys = [
    "search-source-skeleton-a",
    "search-source-skeleton-b",
    "search-source-skeleton-c",
  ]

  const enhanceQuery = async (searchQuery: string): Promise<KeywordSuggestion[] | null> => {
    if (enhanceAbortControllerRef.current) {
      enhanceAbortControllerRef.current.abort()
    }

    const controller = new AbortController()
    enhanceAbortControllerRef.current = controller

    setIsEnhancing(true)
    try {
      const corpus = activeTab === "quran" ? "quran" : "bible"

      const response = await fetch(`${API_BASE}/api/search/enhance`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        signal: controller.signal,
        body: JSON.stringify({ query: searchQuery, corpus }),
      })

      if (!response.ok) {
        throw new Error("Enhancement failed")
      }

      const data = await response.json()
      if (controller.signal.aborted) {
        return null
      }

      if (data.keywords && Array.isArray(data.keywords)) {
        const keywordSuggestions: KeywordSuggestion[] = data.keywords.map(
          (
            kw: { text?: string; language?: string; confidence?: number; source?: string } | string
          ) => ({
            text: typeof kw === "string" ? kw : kw.text || "",
            language: typeof kw === "string" ? "unknown" : kw.language || "unknown",
            confidence: typeof kw === "string" ? 1.0 : kw.confidence || 1.0,
            selected: true,
            source: typeof kw === "string" ? corpus : kw.source || corpus,
          })
        )
        setKeywords(keywordSuggestions)
        return keywordSuggestions
      }

      return []
    } catch (error) {
      if (isAbortError(error)) {
        return null
      }

      log.error("Query enhancement failed", { error })
      toast.error(tToast("searchFailed"))
      return null
    } finally {
      if (enhanceAbortControllerRef.current === controller) {
        enhanceAbortControllerRef.current = null
      }

      if (!controller.signal.aborted) {
        setIsEnhancing(false)
      }
    }
  }

  const handleKeywordSearch = (keywordsOverride?: KeywordSuggestion[]) => {
    const effectiveKeywords = keywordsOverride ?? selectedKeywords

    if (effectiveKeywords.length === 0) {
      toast.error(tToast("searchFailed"))
      return
    }

    setHasSearched(true)

    // Perform search with selected keywords
    if (enable_streaming) {
      setIsSearching(true)
      let url = `/api/stream/search?q=${encodeURIComponent(query)}&source=${activeTab}`
      if (selectedLanguage) {
        url += `&language=${encodeURIComponent(selectedLanguage)}`
      }
      // Add translator if searching Quran
      if (activeTab === "quran") {
        url += `&translator=${encodeURIComponent(selectedTranslator)}`
      }
      // Add keywords to URL
      const keywordTexts = effectiveKeywords.map((k) => k.text).join(",")
      url += `&keywords=${encodeURIComponent(keywordTexts)}`
      startStream(url)
    } else {
      performBatchSearch(undefined, effectiveKeywords)
    }
  }

  const performBatchSearch = useCallback(
    async (queryOverride?: string, keywordsOverride?: KeywordSuggestion[]) => {
      const searchQuery = queryOverride ?? query
      if (!searchQuery.trim()) return

      if (batchSearchAbortControllerRef.current) {
        batchSearchAbortControllerRef.current.abort()
      }

      const controller = new AbortController()
      batchSearchAbortControllerRef.current = controller

      const keywordsToUse = keywordsOverride ?? selectedKeywords

      setIsSearching(true)
      setResults([])

      try {
        const body: Record<string, unknown> = { query: searchQuery, mode: "semantic", top_k: 10 }
        if (selectedLanguage) {
          body.language = selectedLanguage
        }

        if (activeTab === "quran") {
          body.translator = selectedTranslator
        }

        if (advancedMode && keywordsToUse.length > 0) {
          body.keywords = keywordsToUse.map((k) => k.text)
        }

        const response =
          activeTab === "quran"
            ? await searchQuranApiSearchQuranPost({
                body: body as never,
                signal: controller.signal,
              })
            : await searchBibleApiSearchBiblePost({
                body: { ...body, testament: activeTab } as never,
                signal: controller.signal,
              })

        if (controller.signal.aborted) {
          return
        }

        if (response.error) {
          const errorBody = response.error as { error?: { code?: string } }
          if (errorBody.error?.code === "RATE_LIMIT_EXCEEDED") {
            setIsRateLimited(true)
            setIsSearching(false)
            return
          }
          toast.error(tToast("searchFailed"))
          setIsSearching(false)
          return
        }

        const data = response.data as {
          results: SearchResult[]
          verse_details?: Record<string, VerseDetail>
          detected_language?: string
        }

        if (controller.signal.aborted) {
          return
        }

        setResults(data.results)

        if (data.verse_details) {
          setVerseDetails(data.verse_details)
        }

        if (data.detected_language) {
          setDetectedLanguage(data.detected_language)
        }

        toast.success(tToast("searchSuccess"))
      } catch (error) {
        if (isAbortError(error)) {
          return
        }

        toast.error(tToast("searchFailed"))
      } finally {
        if (batchSearchAbortControllerRef.current === controller) {
          batchSearchAbortControllerRef.current = null
        }

        if (!controller.signal.aborted) {
          setIsSearching(false)
        }
      }
    },
    [query, activeTab, selectedLanguage, selectedTranslator, advancedMode, selectedKeywords, tToast]
  )

  useEffect(() => {
    if (sseError && !hasHandledSSEError.current) {
      hasHandledSSEError.current = true
      if (sseErrorCode === "RATE_LIMIT_EXCEEDED") {
        setIsRateLimited(true)
        setIsSearching(false)
        return
      }
      toast.error(tToast("searchFailed"))
      performBatchSearch()
    }
  }, [sseError, sseErrorCode, performBatchSearch, tToast])

  // Auto-execute search from URL q param (history re-run)
  useEffect(() => {
    const q = searchParams?.get("q")
    if (q && q.trim() && !hasAutoExecuted.current) {
      hasAutoExecuted.current = true
      setHasSearched(true)
      setQuery(q) // Populate input field for display

      // Reset state for fresh search
      setResults([])
      setStreamedAnswer("")
      setVerseDetails({})
      setIsRateLimited(false)
      hasHandledSSEError.current = false

      if (enable_streaming) {
        setIsSearching(true)
        let url = `/api/stream/search?q=${encodeURIComponent(q)}&source=${activeTab}`
        if (selectedLanguage) {
          url += `&language=${encodeURIComponent(selectedLanguage)}`
        }
        // Add translator if searching Quran
        if (activeTab === "quran") {
          url += `&translator=${encodeURIComponent(selectedTranslator)}`
        }
        startStream(url)
      } else {
        performBatchSearch(q) // Pass q directly — state may not be updated yet
      }
    }
  }, [
    searchParams,
    activeTab,
    enable_streaming,
    startStream,
    performBatchSearch,
    selectedLanguage,
    selectedTranslator,
  ])

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setHasSearched(true)

    setResults([])
    setStreamedAnswer("")
    setVerseDetails({})
    setHighlightedVerse(null)
    setIsRateLimited(false)
    hasHandledSSEError.current = false

    // If keywords are selected, perform keyword-based search
    if (selectedKeywords.length > 0) {
      handleKeywordSearch()
      return
    }

    // If advanced mode is ON and no keywords yet, enhance first
    // (This happens on first submit after toggling advanced mode ON)
    if (advancedMode && keywords.length === 0) {
      const extractedKeywords = await enhanceQuery(query)
      if (extractedKeywords && extractedKeywords.length > 0) {
        handleKeywordSearch(extractedKeywords)
        return
      }
    }

    // Normal search flow
    if (enable_streaming) {
      setIsSearching(true)
      let url = `/api/stream/search?q=${encodeURIComponent(query)}&source=${activeTab}`
      if (selectedLanguage) {
        url += `&language=${encodeURIComponent(selectedLanguage)}`
      }
      // Add translator if searching Quran
      if (activeTab === "quran") {
        url += `&translator=${encodeURIComponent(selectedTranslator)}`
      }
      startStream(url)
    } else {
      performBatchSearch()
    }
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-sm tracking-wide text-[var(--color-text-muted)]">Loading...</div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[var(--color-bg-app)]">
      {/* Subtle ambient texture */}
      <div className="pointer-events-none fixed inset-0">
        <DotPattern width={40} height={40} cr={0.4} className="opacity-[0.015]" />
      </div>

      {/* Search Hero */}
      <AuroraSectionBackground className="px-6 pt-20 pb-12">
        <div className="mx-auto max-w-3xl">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.fluid, duration: 0.6 }}
            className="mb-10 text-center"
          >
            {/* Decorative badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1, duration: 0.4 }}
              className="mb-6 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 backdrop-blur-sm"
            >
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-indigo-400 opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-indigo-500" />
              </span>
              <span className="text-xs font-medium tracking-wide text-[var(--color-text-secondary)]">
                {t("title")}
              </span>
            </motion.div>

            {/* Title */}
            <h1 className="mb-4 text-4xl font-bold tracking-tight text-[var(--color-text-primary)] md:text-5xl">
              <span className="bg-gradient-to-r from-white via-white to-white/70 bg-clip-text text-transparent">
                {t("title")}
              </span>
            </h1>

            {/* Subtitle with dynamic verse count */}
            <p className="mx-auto max-w-xl text-base leading-relaxed text-[var(--color-text-secondary)] md:text-lg">
              {t("subtitlePrefix")}{" "}
              <motion.span
                key={activeTab}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="inline-block font-semibold text-[var(--color-text-secondary)]"
              >
                {activeTab === "quran" && t("verseCounts.quran")}
                {activeTab === "ot" && t("verseCounts.oldTestament")}
                {activeTab === "nt" && t("verseCounts.newTestament")}
                {activeTab === "apocrypha" && t("verseCounts.apocrypha")}
              </motion.span>
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.fluid, delay: 0.2, duration: 0.5 }}
            className="flex flex-col items-center"
          >
            <SearchTabs activeTab={activeTab} onTabChange={handleTabChange} />

            {/* Search form with glass effect */}
            <form onSubmit={handleSearch} className="relative mb-6 w-full max-w-3xl">
              <div className="relative flex items-center justify-center gap-2">
                <div className="group relative flex-1">
                  {/* Glow effect on focus */}
                  <div className="absolute -inset-0.5 rounded-xl bg-gradient-to-r from-indigo-500/20 via-violet-500/20 to-indigo-500/20 opacity-0 blur transition-opacity duration-300 group-focus-within:opacity-100" />

                  <Input
                    id="search-input"
                    type="search"
                    data-testid="search-input"
                    value={query}
                    onChange={(e) => {
                      setQuery(e.target.value)
                      if (!e.target.value.trim()) {
                        setHasSearched(false)
                      }
                    }}
                    placeholder={getPlaceholder()}
                    className="peer relative h-12 border-white/10 bg-[var(--color-bg-surface)]/80 ps-12 pe-24 text-base backdrop-blur-sm transition-colors hover:border-white/20 focus:border-indigo-500/50"
                  />
                  <div className="text-muted-foreground/60 pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-4 peer-disabled:opacity-50">
                    <Search size={20} strokeWidth={1.5} />
                  </div>
                  <button
                    type="submit"
                    data-testid="search-submit-button"
                    disabled={(isSearching && !isStreaming) || !query.trim() || isEnhancing}
                    className="focus-visible:outline-ring/70 absolute inset-y-0 end-1.5 my-auto flex h-[calc(100%-12px)] items-center justify-center rounded-lg bg-gradient-to-r from-indigo-500 to-violet-500 px-4 text-sm font-medium text-white shadow-lg shadow-indigo-500/25 transition-all hover:from-indigo-600 hover:to-violet-600 focus:z-10 focus-visible:outline focus-visible:outline-2 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50"
                    aria-label="Submit search"
                  >
                    {isEnhancing
                      ? t("enhancing")
                      : isSearching || isStreaming
                        ? t("searching")
                        : t("searchButton")}
                  </button>
                </div>
                <LanguageSelector
                  value={selectedLanguage}
                  onChange={setSelectedLanguage}
                  detectedLanguage={detectedLanguage}
                />
                {activeTab === "quran" && (
                  <TranslatorSelector value={selectedTranslator} onChange={setSelectedTranslator} />
                )}
              </div>
            </form>
          </motion.div>
        </div>
      </AuroraSectionBackground>

      {/* Content */}
      <div className="relative px-6 pb-16">
        <div className="mx-auto max-w-3xl">
          {isPreSearchState && (
            <motion.section
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ ...springPresets.gentle, duration: 0.45 }}
              className="mb-12 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/50 p-6 md:p-8"
            >
              <div className="mx-auto max-w-xl text-center">
                <h2 className="mb-3 text-xl font-semibold text-[var(--color-text-primary)] md:text-2xl">
                  {t("emptyState.title")}
                </h2>
                <p className="text-sm leading-relaxed text-[var(--color-text-secondary)] md:text-base">
                  {t("emptyState.description")}
                </p>
              </div>

              <div className="mt-6 grid grid-cols-1 gap-2.5 sm:grid-cols-3">
                {suggestedQueries.map((suggestion) => (
                  <button
                    key={suggestion}
                    type="button"
                    onClick={() => setQuery(suggestion)}
                    className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-elevated)] px-3 py-2.5 text-left text-sm text-[var(--color-text-secondary)] transition-colors hover:border-[var(--color-border-glow)] hover:text-[var(--color-text-primary)]"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>

              <div className="mt-6 grid grid-cols-1 gap-3 md:grid-cols-3">
                {quickTips.map((tip) => (
                  <div
                    key={tip.title}
                    className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-elevated)]/70 p-3"
                  >
                    <p className="mb-1 text-sm font-medium text-[var(--color-text-primary)]">
                      {tip.title}
                    </p>
                    <p className="text-xs leading-relaxed text-[var(--color-text-muted)]">
                      {tip.description}
                    </p>
                  </div>
                ))}
              </div>
            </motion.section>
          )}

          {isNoResultsState && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ ...springPresets.gentle, duration: 0.35 }}
              className="mb-10 rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/70 p-6 text-center"
            >
              <p className="text-lg font-semibold text-[var(--color-text-primary)]">
                {t("noResultsQuery", { query })}
              </p>
              <p className="mt-2 text-sm text-[var(--color-text-secondary)]">
                {t("noResultsHint")}
              </p>
              <button
                type="button"
                onClick={() => {
                  setQuery("")
                  setHasSearched(false)
                }}
                className="mt-4 text-sm font-medium text-[var(--color-accent-primary)] transition-colors hover:text-[var(--color-accent-primary)]/80"
              >
                {t("clearSearch")}
              </button>
            </motion.div>
          )}

          {isRateLimited && <RateLimitBanner />}

          {/* AI Answer Section - Outside Suspense (renders immediately) */}
          <AnimatePresence>
            {streamedAnswer && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="mb-12"
              >
                <div className="relative border-l border-[var(--color-accent-primary)]/40 py-1 pl-5">
                  <span className="mb-3 block text-[10px] font-medium tracking-wider text-[var(--color-text-muted)] uppercase">
                    {t("aiInterpretation")}
                  </span>
                  <div className="text-[15px] leading-[1.75] text-[var(--color-text-secondary)]">
                    {(() => {
                      let partCursor = 0

                      return parseCitations(streamedAnswer).map((part) => {
                        if (typeof part === "string") {
                          const key = `text-${partCursor}`
                          partCursor += part.length
                          return <span key={key}>{part}</span>
                        }

                        const verse = verseDetails[part.reference]
                        const key = `citation-${part.reference}-${partCursor}`
                        partCursor += part.reference.length

                        return (
                          <InlineCitation
                            key={key}
                            reference={part.reference}
                            verseDetail={verse}
                            onNavigate={navigateToVerse}
                          />
                        )
                      })
                    })()}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Results Section - Inside Suspense (progressive loading) */}
          <Suspense
            fallback={
              <div className="space-y-3">
                {suspenseSkeletonKeys.map((key) => (
                  <Skeleton key={key} className="h-24 w-full rounded-lg" />
                ))}
              </div>
            }
          >
            {/* Loading skeletons - no answer yet */}
            {isSearching && !results.length && !streamedAnswer && !isRateLimited && (
              <div className="space-y-3">
                {loadingSkeletonKeys.map((key) => (
                  <Skeleton key={key} className="h-24 w-full rounded-lg" />
                ))}
              </div>
            )}

            {/* Loading skeletons - answer streaming, waiting for sources */}
            {isSearching && !results.length && streamedAnswer && !isRateLimited && (
              <div className="space-y-3">
                <div className="mb-6 h-px bg-[var(--color-border-subtle)]" />
                <p className="mb-4 text-xs tracking-wide text-[var(--color-text-muted)] uppercase">
                  {t("retrievingSources")}
                </p>
                {sourceSkeletonKeys.map((key) => (
                  <Skeleton key={key} className="h-24 w-full rounded-lg" />
                ))}
              </div>
            )}

            {/* Divider between AI answer and results */}
            {results.length > 0 && streamedAnswer && (
              <div className="mb-8 h-px bg-[var(--color-border-subtle)]" />
            )}

            {/* Results */}
            <div ref={resultsContainerRef}>
              <AnimatePresence mode="popLayout">
                {(() => {
                  const seenResultKeys = new Map<string, number>()

                  return results.map((result) => {
                    const baseKey = `${result.source}-${result.reference}`
                    const occurrence = (seenResultKeys.get(baseKey) ?? 0) + 1
                    seenResultKeys.set(baseKey, occurrence)
                    const resultKey = `${baseKey}-${occurrence}`

                    return (
                      <div key={resultKey} data-verse-id={result.reference} className="mb-3">
                        <div
                          className={cn(
                            "rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-4 transition-colors duration-200 hover:border-[var(--color-border-glow)]",
                            highlightedVerse === result.reference &&
                              "border-[var(--color-accent-primary)]/40"
                          )}
                        >
                          <div className="mb-3 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <span className="text-sm font-medium text-white">
                                {result.reference || t("unknownReference")}
                              </span>
                              <SourceBadge source={mapSourceToType(result.source)} />
                            </div>
                            <div className="flex items-center gap-3">
                              <span className="font-mono text-[11px] text-[var(--color-text-muted)] tabular-nums">
                                {(result.score * 100).toFixed(1)}%
                              </span>
                              <button
                                type="button"
                                onClick={() => navigateToVerse(result.reference)}
                                aria-label={t("viewVerse")}
                                className="rounded text-[var(--color-text-muted)] transition-colors duration-200 hover:text-[var(--color-accent-primary)] focus:ring-2 focus:ring-[var(--color-accent-primary)]/50 focus:outline-none"
                              >
                                <ExternalLink className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          </div>
                          <p className="text-[15px] leading-[1.7] text-[var(--color-text-secondary)]">
                            {extractVerseText(result.text)}
                          </p>
                        </div>
                      </div>
                    )
                  })
                })()}
              </AnimatePresence>
            </div>
          </Suspense>
        </div>
      </div>
    </div>
  )
}

export default function SearchPage() {
  const tCommon = useTranslations("Common")

  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
          <div className="text-sm tracking-wide text-[var(--color-text-muted)]">
            {tCommon("loading")}
          </div>
        </div>
      }
    >
      <SearchContent />
    </Suspense>
  )
}
