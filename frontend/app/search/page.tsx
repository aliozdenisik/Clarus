"use client";

import { useState, useEffect, Suspense, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { Button } from "@/components/ui/button";
import { GlowCard } from "@/components/ui/glow-card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { ExternalLink, Search } from "lucide-react";
import { SearchTabs, SearchSource } from "@/components/search/search-tabs";
import { useSSE } from "@/lib/hooks/use-sse";
import { usePreferencesStore } from "@/lib/stores/preferences-store";
import { parseCitations, CitationPart } from "@/lib/utils/parse-citations";
import { InlineCitation } from "@/components/compare/inline-citation";
import { VerseTooltip, VerseDetail } from "@/components/search/verse-tooltip";
import { SourceBadge, SourceType } from "@/components/compare/source-badge";
import { useLogger } from "@/lib/logger";

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
   const resultsContainerRef = useRef<HTMLDivElement>(null);
   const hasHandledSSEError = useRef(false);
   const hasAutoExecuted = useRef(false);

  const log = useLogger("SearchPage");
  const { user, isLoading, logout } = useAuth();
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
   }, [searchParams]);

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
      setIsSearching(false);
    }
  }, [sseData]);

  const handleLogout = async () => {
    await logout();
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
    router.push(`/search?source=${tab}`);
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

   const performBatchSearch = useCallback(async (queryOverride?: string) => {
     const searchQuery = queryOverride ?? query;
     if (!searchQuery.trim()) return;

     setIsSearching(true);
     setResults([]);

     try {
       const token = localStorage.getItem("access_token");

       let url = "http://localhost:8000/api/search/quran";
       let body: any = { query: searchQuery, mode: "semantic", top_k: 10 };

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

      toast.success(`Found ${data.results.length} results`);
    } catch (error) {
      toast.error("Search failed. Please try again.");
    } finally {
      setIsSearching(false);
    }
  }, [query, activeTab]);

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
           const url = `${baseUrl}/api/stream/search?q=${encodeURIComponent(q)}&source=${activeTab}&token=${encodeURIComponent(token)}`;
           startStream(url);
         } else {
           performBatchSearch(q);
         }
       } else {
         performBatchSearch(q);    // Pass q directly — state may not be updated yet
       }
     }
   }, [searchParams, activeTab, enable_streaming, startStream, performBatchSearch]);

   const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setResults([]);
    setStreamedAnswer("");
    setVerseDetails({});
    setHighlightedVerse(null);
    setOpenPopover(null);
    hasHandledSSEError.current = false;

    if (enable_streaming) {
      setIsSearching(true);
      const baseUrl = "http://localhost:8000";
      const token = localStorage.getItem("access_token");
      if (!token) {
        toast.error("Authentication required");
        performBatchSearch();
        return;
      }
      const url = `${baseUrl}/api/stream/search?q=${encodeURIComponent(query)}&source=${activeTab}&token=${encodeURIComponent(token)}`;
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
    <div className="relative min-h-screen bg-[var(--color-bg-app)]">
      {/* Ambient warm gradient */}
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-[500px]"
        style={{
          background: "radial-gradient(ellipse 80% 50% at 50% -10%, rgba(91, 168, 181, 0.04), transparent 70%)",
        }}
      />

      {/* Search Hero */}
      <div className="relative pt-12 pb-2 px-6">
        <div className="mx-auto max-w-3xl">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={springPresets.fluid}
          >
            <h1 className="font-display text-4xl font-normal text-[var(--color-text-primary)] mb-1 tracking-tight">
              Search
            </h1>
            <p className="text-sm text-[var(--color-text-muted)] mb-8">
              Explore sacred texts with semantic search
            </p>

            <SearchTabs activeTab={activeTab} onTabChange={handleTabChange} />

            <form onSubmit={handleSearch} className="relative mb-4">
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-[18px] w-[18px] text-[var(--color-text-muted)]" />
                <input
                  type="text"
                  data-testid="search-input"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={getPlaceholder()}
                  className="w-full h-12 pl-12 pr-32 bg-[var(--color-bg-surface)] rounded-xl text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] border border-[var(--color-border-subtle)] focus:border-[var(--color-border-glow)] focus:outline-none transition-all duration-300 text-[15px]"
                />
                <Button
                  type="submit"
                  data-testid="search-submit-button"
                  disabled={(isSearching && !isStreaming) || !query.trim()}
                  className="absolute right-2 top-1/2 -translate-y-1/2 bg-[var(--color-accent-primary)] text-[#09090b] hover:bg-[var(--color-accent-hover)] font-medium rounded-lg px-5 h-8 text-sm tracking-wide disabled:opacity-40"
                >
                  {isSearching || isStreaming ? "Searching..." : "Search"}
                </Button>
              </div>
            </form>
          </motion.div>
        </div>
      </div>

      {/* Content */}
      <div className="relative px-6 pb-16">
        <div className="mx-auto max-w-3xl">
          {/* AI Answer */}
          <AnimatePresence>
            {streamedAnswer && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mb-10"
              >
                <div className="relative pl-6 border-l-2 border-[var(--color-accent-primary)] py-1">
                  <span className="text-[11px] font-medium uppercase tracking-[0.15em] text-[var(--color-accent-primary)] mb-3 block opacity-70">
                    AI Interpretation
                  </span>
                  <div className="text-[var(--color-text-primary)] leading-[1.85] text-[15px]">
                    {parseCitations(streamedAnswer).map((part, i) => {
                      if (typeof part === "string") {
                        return <span key={i}>{part}</span>;
                      }

                      const verse = verseDetails[part.reference];
                      if (!verse) {
                        return (
                          <span
                            key={i}
                            className="text-[var(--color-text-muted)]"
                          >
                            {part.reference}
                          </span>
                        );
                      }

                      return (
                        <VerseTooltip
                          key={i}
                          reference={part.reference}
                          verseDetail={verse}
                          onNavigate={navigateToVerse}
                          isOpen={openPopover === part.reference}
                          onOpenChange={(open) => {
                            setOpenPopover(open ? part.reference : null);
                          }}
                        >
                          <InlineCitation
                            reference={part.reference}
                            onClick={() => navigateToVerse(part.reference)}
                          />
                        </VerseTooltip>
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
                <Skeleton key={i} className="h-28 w-full rounded-xl" />
              ))}
            </div>
          )}

          {/* Loading skeletons - answer streaming, waiting for sources */}
          {isSearching && !results.length && streamedAnswer && (
            <div className="space-y-3">
              {/* Ornamental divider */}
              <div className="flex items-center gap-4 mb-6">
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[var(--color-border-subtle)] to-transparent" />
                <div className="w-1 h-1 rotate-45 bg-[var(--color-accent-primary)] opacity-30" />
                <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[var(--color-border-subtle)] to-transparent" />
              </div>
              <p className="text-xs text-[var(--color-text-muted)] tracking-wide uppercase mb-4">
                Retrieving sources...
              </p>
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-28 w-full rounded-xl" />
              ))}
            </div>
          )}

          {/* Ornamental divider between AI answer and results */}
          {results.length > 0 && streamedAnswer && (
            <div className="flex items-center gap-4 mb-8">
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[var(--color-border-subtle)] to-transparent" />
              <div className="w-1 h-1 rotate-45 bg-[var(--color-accent-primary)] opacity-30" />
              <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[var(--color-border-subtle)] to-transparent" />
            </div>
          )}

          {/* Results */}
          <div ref={resultsContainerRef}>
            <AnimatePresence mode="popLayout">
              {results.map((result, i) => (
                <motion.div
                  key={`${result.reference}-${i}`}
                  data-verse-id={result.reference}
                  initial={{ opacity: 0, y: 16 }}
                  animate={{
                    opacity: 1,
                    y: 0,
                    scale: highlightedVerse === result.reference ? 1.01 : 1,
                  }}
                  exit={{ opacity: 0, scale: 0.97 }}
                  transition={{ ...springPresets.snappy, delay: i * 0.04 }}
                  className="mb-3"
                >
                  <GlowCard
                    className={
                      highlightedVerse === result.reference
                        ? "ring-1 ring-[var(--color-accent-primary)]/40 transition-all duration-500"
                        : ""
                    }
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="font-display text-base text-[var(--color-accent-primary)]">
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
                          className="text-[var(--color-text-muted)] hover:text-[var(--color-accent-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent-primary)] rounded transition-colors duration-200"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                    <p className="text-[var(--color-text-secondary)] leading-[1.75] text-[15px]">
                      {extractVerseText(result.text)}
                    </p>
                  </GlowCard>
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
