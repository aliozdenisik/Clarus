"use client";

import { useState, useEffect, Suspense, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useSession, signOut } from "@/lib/auth-client";
import { DotPattern } from "@/components/ui/dot-pattern";
import { AuroraSectionBackground } from "@/components/ui/aurora-background";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { ExternalLink, Search } from "lucide-react";
import { SearchTabs, SearchSource } from "@/components/search/search-tabs";
import { useSSE } from "@/lib/hooks/use-sse";
import { usePreferencesStore } from "@/lib/stores/preferences-store";
import { parseCitations, CitationPart } from "@/lib/utils/parse-citations";
import { InlineCitation } from "@/components/compare/inline-citation";
import { VerseDetail } from "@/components/search/verse-tooltip";
import { SourceBadge, SourceType } from "@/components/compare/source-badge";
import { useLogger } from "@/lib/logger";
import { LanguageSelector } from "@/components/search/language-selector";
import { KeywordSelector } from "@/components/search/keyword-selector";
import { useKeywordStore, KeywordSuggestion } from "@/lib/stores/keyword-store";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";

interface SearchResult {
  source: string;
  reference: string;
  text: string;
  score: number;
}

function SearchContent() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeTab, setActiveTab] = useState<SearchSource>("quran");
  const [streamedAnswer, setStreamedAnswer] = useState("");
  const [verseDetails, setVerseDetails] = useState<Record<string, VerseDetail>>({});
  const [highlightedVerse, setHighlightedVerse] = useState<string | null>(null);
  const [openPopover, setOpenPopover] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState<string | null>(null);
  const [detectedLanguage, setDetectedLanguage] = useState<string | undefined>(undefined);
  const [isEnhancing, setIsEnhancing] = useState(false);
   const resultsContainerRef = useRef<HTMLDivElement>(null);
   const hasHandledSSEError = useRef(false);
   const hasAutoExecuted = useRef(false);

  const keywordStore = useKeywordStore();

  const log = useLogger("SearchPage");
  const { data: session, isPending } = useSession();
  const user = session?.user;
  const isLoading = isPending;
  const router = useRouter();
  const searchParams = useSearchParams();

  const { data: sseData, isStreaming, error: sseError, startStream } = useSSE();
  const { enable_streaming } = usePreferencesStore();

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);

   useEffect(() => {
     const source = searchParams?.get("source") as SearchSource;
     if (source && ["quran", "ot", "nt", "apocrypha"].includes(source)) {
       setActiveTab(source);
     }

     const advanced = searchParams?.get("advanced");
     if (advanced === "true") {
       keywordStore.setAdvancedMode(true);
     }
   }, [searchParams, keywordStore]);

   useEffect(() => {
    const tokens = sseData
      .filter((m) => m.type === "token")
      .map((m) => m.content)
      .join("");
    setStreamedAnswer(tokens);

    const verseDetailsMsg = sseData.find((m) => m.verse_details);
    if (verseDetailsMsg?.verse_details) {
      setVerseDetails(verseDetailsMsg.verse_details as Record<string, VerseDetail>);
    }

    const errorMsg = sseData.find((m) => m.error);
    if (errorMsg?.error) {
      log.error("SSE server error", { error: errorMsg.error });
    }

    const noResultsMsg = sseData.find((m) => m.type === "no_results");
    if (noResultsMsg) {
      setStreamedAnswer("");
      setIsSearching(false);
      toast.info(
        (noResultsMsg as { message?: string }).message ||
          "No results found for your query."
      );
    }

    const completeMsg = sseData.find((m) => m.type === "complete");
    if (completeMsg) {
      const result = (completeMsg as { result?: { results?: SearchResult[] } }).result;
      if (result?.results) {
        setResults(result.results);

        if (result.results.length === 0) {
          setStreamedAnswer("");
        }
      }
      const completeResult = completeMsg as any;
      if (completeResult.result?.detected_language || completeResult.detected_language) {
        setDetectedLanguage(completeResult.result?.detected_language || completeResult.detected_language);
      }
      setIsSearching(false);
    }
  }, [sseData]);

  const handleLogout = async () => {
    await signOut();
    router.push("/login");
    toast.success("Logged out successfully");
  };

  const handleTabChange = (tab: SearchSource) => {
    setActiveTab(tab);
    setResults([]);
    setStreamedAnswer("");
    setVerseDetails({});
    setHighlightedVerse(null);
    setOpenPopover(null);
    keywordStore.reset();
    const params = new URLSearchParams();
    params.set("source", tab);
    if (keywordStore.advancedMode) {
      params.set("advanced", "true");
    }
    router.push(`/search?${params.toString()}`);
  };

  const mapSourceToType = useCallback((source: string): SourceType => {
    switch (source) {
      case "quran":
        return "quran";
      case "bible_ot":
      case "ot":
        return "old_testament";
      case "bible_nt":
      case "nt":
        return "new_testament";
      case "bible_apocrypha":
      case "apocrypha":
        return "apocrypha";
      default:
        return "quran";
    }
  }, []);

  const scrollToVerse = useCallback((reference: string) => {
    const element = document.querySelector(`[data-verse-id="${reference}"]`);
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "center" });
      setHighlightedVerse(reference);
      setTimeout(() => setHighlightedVerse(null), 2000);
    }
  }, []);

  const navigateToVerse = useCallback((reference: string) => {
    const verse = verseDetails[reference];
    if (!verse) {
      log.warn("No verse details for reference, falling back to scroll", {
        action: "navigateToVerse",
        reference,
      });
      scrollToVerse(reference);
      return;
    }

    let url = "";
    if (verse.source === "quran_tr" || verse.source === "quran") {
      const surahId = verse.surah_id || verse.chapter;
      const verseId = verse.verse_id || verse.verse;
      url = `/quran/${surahId}?verse=${verseId}`;
    } else if (verse.source.startsWith("bible_")) {
      const bookNr = verse.book_nr || 1;
      url = `/bible/${bookNr}?chapter=${verse.chapter}&verse=${verse.verse}`;
    } else {
      log.warn("Unknown source format, falling back to scroll", {
        action: "navigateToVerse",
        reference,
        source: verse.source,
      });
      scrollToVerse(reference);
      return;
    }

    window.open(url, "_blank");
  }, [verseDetails, scrollToVerse, log]);

  /** Strip redundant metadata prefix like "[38:29] Sâd (Sad) - Score: 0.060 " from verse text */
  const extractVerseText = (text: string): string => {
    return text.replace(/^\[[\d:]+\]\s+.*?-\s*Score:\s*[\d.]+\s*/, "");
  };

  const getPlaceholder = () => {
    switch (activeTab) {
      case "quran":
        return "Search Quran...";
      case "ot":
        return "Search Old Testament...";
      case "nt":
        return "Search New Testament...";
      case "apocrypha":
        return "Search Apocrypha...";
      default:
        return "Search...";
    }
  };

  const enhanceQuery = async (searchQuery: string) => {
    setIsEnhancing(true);
    try {
      const token = localStorage.getItem("access_token");
      const corpus = activeTab === "quran" ? "quran" : "bible";

      const response = await fetch("http://localhost:8000/api/search/enhance", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ query: searchQuery, corpus }),
      });

      if (!response.ok) {
        throw new Error("Enhancement failed");
      }

      const data = await response.json();
      if (data.keywords && Array.isArray(data.keywords)) {
        const keywordSuggestions: KeywordSuggestion[] = data.keywords.map(
          (kw: any) => ({
            text: kw.text || kw,
            language: kw.language || "unknown",
            confidence: kw.confidence || 1.0,
            selected: true,
            source: kw.source || corpus,
          })
        );
        keywordStore.setKeywords(keywordSuggestions);
      }
    } catch (error) {
      log.error("Query enhancement failed", { error });
      toast.error("Failed to extract keywords");
    } finally {
      setIsEnhancing(false);
    }
  };

  const handleKeywordSearch = () => {
    if (keywordStore.selectedKeywords.length === 0) {
      toast.error("Please select at least one keyword");
      return;
    }

    // Perform search with selected keywords
    if (enable_streaming) {
      setIsSearching(true);
      const baseUrl = "http://localhost:8000";
      const token = localStorage.getItem("access_token");
      if (!token) {
        toast.error("Authentication required");
        performBatchSearch();
        return;
      }
      let url = `${baseUrl}/api/stream/search?q=${encodeURIComponent(query)}&source=${activeTab}&token=${encodeURIComponent(token)}`;
      if (selectedLanguage) {
        url += `&language=${encodeURIComponent(selectedLanguage)}`;
      }
      // Add keywords to URL
      const keywordTexts = keywordStore.selectedKeywords.map((k) => k.text).join(",");
      url += `&keywords=${encodeURIComponent(keywordTexts)}`;
      startStream(url);
    } else {
      performBatchSearch();
    }
  };

  const handleAdvancedModeToggle = (checked: boolean) => {
    keywordStore.setAdvancedMode(checked);
    const params = new URLSearchParams(window.location.search);
    if (checked) {
      params.set("advanced", "true");
    } else {
      params.delete("advanced");
      keywordStore.reset();
    }
    router.push(`/search?${params.toString()}`);
  };

   const performBatchSearch = useCallback(async (queryOverride?: string) => {
     const searchQuery = queryOverride ?? query;
     if (!searchQuery.trim()) return;

     setIsSearching(true);
     setResults([]);

     try {
       const token = localStorage.getItem("access_token");

       let url = "http://localhost:8000/api/search/quran";
       let body: any = { query: searchQuery, mode: "semantic", top_k: 10 };
       if (selectedLanguage) {
         body.language = selectedLanguage;
       }

       // Add keywords if advanced mode is ON and keywords are selected
       if (keywordStore.advancedMode && keywordStore.selectedKeywords.length > 0) {
         body.keywords = keywordStore.selectedKeywords.map((k) => k.text);
       }

      if (activeTab !== "quran") {
        url = "http://localhost:8000/api/search/bible";
        body = { ...body, testament: activeTab };
      }

      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();
      setResults(data.results);

      if (data.verse_details) {
        setVerseDetails(data.verse_details);
      }

      if (data.detected_language) {
        setDetectedLanguage(data.detected_language);
      }

      toast.success(`Found ${data.results.length} results`);
    } catch (error) {
      toast.error("Search failed. Please try again.");
     } finally {
       setIsSearching(false);
     }
   }, [query, activeTab, selectedLanguage, keywordStore.advancedMode, keywordStore.selectedKeywords]);

  useEffect(() => {
    if (sseError && !hasHandledSSEError.current) {
      hasHandledSSEError.current = true;
      toast.error("Streaming failed. Switching to standard search.");
      performBatchSearch();
    }
   }, [sseError, performBatchSearch]);

   // Auto-execute search from URL q param (history re-run)
   useEffect(() => {
     const q = searchParams?.get("q");
     if (q && q.trim() && !hasAutoExecuted.current) {
       hasAutoExecuted.current = true;
       setQuery(q);          // Populate input field for display

       // Reset state for fresh search
       setResults([]);
       setStreamedAnswer("");
       setVerseDetails({});
       hasHandledSSEError.current = false;

       if (enable_streaming) {
         setIsSearching(true);
         const baseUrl = "http://localhost:8000";
         const token = localStorage.getItem("access_token");
         if (token) {
           let url = `${baseUrl}/api/stream/search?q=${encodeURIComponent(q)}&source=${activeTab}&token=${encodeURIComponent(token)}`;
           if (selectedLanguage) {
             url += `&language=${encodeURIComponent(selectedLanguage)}`;
           }
           startStream(url);
         } else {
           performBatchSearch(q);
         }
       } else {
         performBatchSearch(q);    // Pass q directly — state may not be updated yet
       }
     }
   }, [searchParams, activeTab, enable_streaming, startStream, performBatchSearch, selectedLanguage]);

   const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setResults([]);
    setStreamedAnswer("");
    setVerseDetails({});
    setHighlightedVerse(null);
    setOpenPopover(null);
    hasHandledSSEError.current = false;

    // If keywords are selected, perform keyword-based search
    if (keywordStore.selectedKeywords.length > 0) {
      handleKeywordSearch();
      return;
    }

    // If advanced mode is ON and no keywords yet, enhance first
    // (This happens on first submit after toggling advanced mode ON)
    if (keywordStore.advancedMode && keywordStore.keywords.length === 0) {
      await enhanceQuery(query);
      toast.info("Keywords extracted. Adjust selection and search again.");
      return;
    }

    // Normal search flow
    if (enable_streaming) {
      setIsSearching(true);
      const baseUrl = "http://localhost:8000";
      const token = localStorage.getItem("access_token");
      if (!token) {
        toast.error("Authentication required");
        performBatchSearch();
        return;
      }
      let url = `${baseUrl}/api/stream/search?q=${encodeURIComponent(query)}&source=${activeTab}&token=${encodeURIComponent(token)}`;
      if (selectedLanguage) {
        url += `&language=${encodeURIComponent(selectedLanguage)}`;
      }
      startStream(url);
    } else {
      performBatchSearch();
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-muted)] text-sm tracking-wide">Loading...</div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-[var(--color-bg-app)] overflow-hidden">
      {/* Subtle ambient texture */}
      <div className="fixed inset-0 pointer-events-none">
        <DotPattern width={40} height={40} cr={0.4} className="opacity-[0.015]" />
      </div>

      {/* Search Hero */}
      <AuroraSectionBackground className="pt-20 pb-12 px-6">
        <div className="mx-auto max-w-3xl">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.fluid, duration: 0.6 }}
            className="text-center mb-10"
          >
            {/* Decorative badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1, duration: 0.4 }}
              className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm mb-6"
            >
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500" />
              </span>
              <span className="text-xs font-medium text-[var(--color-text-secondary)] tracking-wide">
                AI-Powered Semantic Search
              </span>
            </motion.div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl font-bold text-[var(--color-text-primary)] mb-4 tracking-tight">
              <span className="bg-gradient-to-r from-white via-white to-white/70 bg-clip-text text-transparent">
                Search
              </span>
            </h1>
            
            {/* Subtitle with dynamic verse count */}
            <p className="text-base md:text-lg text-[var(--color-text-muted)] max-w-md mx-auto leading-relaxed">
              Explore sacred texts with semantic search across{" "}
              <motion.span 
                key={activeTab}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="text-[var(--color-text-secondary)] font-medium inline-block"
              >
                {activeTab === "quran" && "6,236 verses"}
                {activeTab === "ot" && "23,145 verses"}
                {activeTab === "nt" && "7,957 verses"}
                {activeTab === "apocrypha" && "5,717 verses"}
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
            <form onSubmit={handleSearch} className="relative mb-6 w-full max-w-2xl">
              <div className="relative flex gap-2 items-center justify-center">
                <div className="relative flex-1 group">
                  {/* Glow effect on focus */}
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500/20 via-violet-500/20 to-indigo-500/20 rounded-xl opacity-0 group-focus-within:opacity-100 blur transition-opacity duration-300" />
                  
                  <Input 
                    id="search-input"
                    type="search"
                    data-testid="search-input"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={getPlaceholder()}
                    className="relative peer pe-24 ps-12 h-12 bg-[var(--color-bg-surface)]/80 backdrop-blur-sm border-white/10 hover:border-white/20 focus:border-indigo-500/50 transition-colors text-base"
                  />
                  <div className="pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-4 text-muted-foreground/60 peer-disabled:opacity-50">
                    <Search size={20} strokeWidth={1.5} />
                  </div>
                  <button
                    type="submit"
                    data-testid="search-submit-button"
                    disabled={(isSearching && !isStreaming) || !query.trim() || isEnhancing}
                    className="absolute inset-y-0 end-1.5 flex h-[calc(100%-12px)] my-auto items-center justify-center rounded-lg px-4 text-sm font-medium bg-gradient-to-r from-indigo-500 to-violet-500 text-white transition-all hover:from-indigo-600 hover:to-violet-600 focus:z-10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring/70 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 shadow-lg shadow-indigo-500/25"
                    aria-label="Submit search"
                  >
                    {isEnhancing ? "Extracting..." : isSearching || isStreaming ? "Searching..." : "Search"}
                  </button>
                </div>
                <LanguageSelector
                  value={selectedLanguage}
                  onChange={setSelectedLanguage}
                  detectedLanguage={detectedLanguage}
                />
              </div>
            </form>

            {/* Keyword Selector */}
            <div className="w-full max-w-2xl space-y-3">
              <KeywordSelector
                keywords={keywordStore.keywords}
                onSelectionChange={(selected) => {
                  keywordStore.setKeywords(
                    keywordStore.keywords.map((k) => ({
                      ...k,
                      selected: selected.some((s) => s.text === k.text),
                    }))
                  );
                }}
                isLoading={isEnhancing}
                onSearch={handleKeywordSearch}
              />
              
              {/* Action buttons */}
              <div className="flex justify-between items-center">
                {/* Extract keywords button - shown when no keywords and query exists */}
                {keywordStore.keywords.length === 0 && query.trim() && (
                  <button
                    type="button"
                    onClick={() => enhanceQuery(query)}
                    disabled={isEnhancing}
                    className="text-xs text-[var(--color-accent-primary)] hover:text-[var(--color-accent-primary)]/80 transition-colors disabled:opacity-50"
                  >
                    {isEnhancing ? "Extracting keywords..." : "Extract keywords for advanced search"}
                  </button>
                )}
                
                {/* Clear keywords button - shown when keywords exist */}
                {keywordStore.keywords.length > 0 && (
                  <button
                    type="button"
                    onClick={() => {
                      keywordStore.reset();
                      toast.info("Switched to normal search");
                    }}
                    className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors ml-auto"
                  >
                    Clear keywords & use normal search
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </AuroraSectionBackground>

      {/* Content */}
      <div className="relative px-6 pb-16">
        <div className="mx-auto max-w-3xl">
          {/* AI Answer */}
          <AnimatePresence>
            {streamedAnswer && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="mb-12"
              >
                <div className="relative pl-5 border-l border-[var(--color-accent-primary)]/40 py-1">
                  <span className="text-[10px] font-medium uppercase tracking-wider text-[var(--color-text-muted)] mb-3 block">
                    AI Interpretation
                  </span>
                  <div className="text-[var(--color-text-secondary)] leading-[1.75] text-[15px]">
                    {parseCitations(streamedAnswer).map((part, i) => {
                      if (typeof part === "string") {
                        return <span key={i}>{part}</span>;
                      }

                      const verse = verseDetails[part.reference];

                      return (
                        <InlineCitation
                          key={i}
                          reference={part.reference}
                          verseDetail={verse}
                          onNavigate={navigateToVerse}
                        />
                      );
                    })}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Loading skeletons - no answer yet */}
          {isSearching && !results.length && !streamedAnswer && (
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-24 w-full rounded-lg" />
              ))}
            </div>
          )}

          {/* Loading skeletons - answer streaming, waiting for sources */}
          {isSearching && !results.length && streamedAnswer && (
            <div className="space-y-3">
              <div className="h-px bg-[var(--color-border-subtle)] mb-6" />
              <p className="text-xs text-[var(--color-text-muted)] tracking-wide uppercase mb-4">
                Retrieving sources...
              </p>
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-24 w-full rounded-lg" />
              ))}
            </div>
          )}

          {/* Divider between AI answer and results */}
          {results.length > 0 && streamedAnswer && (
            <div className="h-px bg-[var(--color-border-subtle)] mb-8" />
          )}

          {/* Results */}
          <div ref={resultsContainerRef}>
            <AnimatePresence mode="popLayout">
              {results.map((result, i) => (
                <motion.div
                  key={`${result.reference}-${i}`}
                  data-verse-id={result.reference}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{
                    opacity: 1,
                    y: 0,
                  }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  transition={{ ...springPresets.snappy, delay: i * 0.03 }}
                  className="mb-3"
                >
                  <div
                    className={cn(
                      "p-4 rounded-lg bg-[var(--color-bg-surface)] border border-[var(--color-border-subtle)] hover:border-[var(--color-border-glow)] transition-colors duration-200",
                      highlightedVerse === result.reference && "border-[var(--color-accent-primary)]/40"
                    )}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-[var(--color-accent-primary)]">
                          {result.reference || "Unknown Reference"}
                        </span>
                        <SourceBadge source={mapSourceToType(result.source)} />
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[11px] text-[var(--color-text-muted)] tabular-nums font-mono">
                          {(result.score * 100).toFixed(1)}%
                        </span>
                        <button
                          type="button"
                          onClick={() => navigateToVerse(result.reference)}
                          aria-label="Go to verse"
                          className="text-[var(--color-text-muted)] hover:text-[var(--color-accent-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent-primary)]/50 rounded transition-colors duration-200"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                    <p className="text-[var(--color-text-secondary)] leading-[1.7] text-[15px]">
                      {extractVerseText(result.text)}
                    </p>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
          <div className="text-[var(--color-text-muted)] text-sm tracking-wide">Loading...</div>
        </div>
      }
    >
      <SearchContent />
    </Suspense>
  );
}
