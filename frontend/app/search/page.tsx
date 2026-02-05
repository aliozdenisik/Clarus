"use client";

import { useState, useEffect, Suspense, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { DotPattern } from "@/components/ui/dot-pattern";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { Search } from "lucide-react";
import { SlidingTabs, SearchSource } from "@/components/ui/sliding-tabs";
import { SearchResultCard } from "@/components/search/search-result-card";
import { AIInterpretation } from "@/components/search/ai-interpretation";
import { useSSE } from "@/lib/hooks/use-sse";
import { usePreferencesStore } from "@/lib/stores/preferences-store";
import { VerseDetail } from "@/components/search/verse-tooltip";
import { useLogger } from "@/lib/logger";
import { LanguageSelector } from "@/components/search/language-selector";
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
      const completeResult = completeMsg as any;
      if (completeResult.result?.detected_language || completeResult.detected_language) {
        setDetectedLanguage(completeResult.result?.detected_language || completeResult.detected_language);
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
       if (selectedLanguage) {
         body.language = selectedLanguage;
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
   }, [query, activeTab, selectedLanguage]);

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
      <div className="relative pt-16 pb-8 px-6">
        <div className="mx-auto max-w-3xl">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={springPresets.fluid}
          >
            <h1 className="text-2xl font-medium text-[var(--color-text-primary)] mb-2 tracking-tight">
              Search
            </h1>
            <p className="text-sm text-[var(--color-text-muted)] mb-8">
              Explore sacred texts with semantic search
            </p>

            <SlidingTabs activeTab={activeTab} onTabChange={handleTabChange} />

            <form onSubmit={handleSearch} className="relative mb-6">
              <div className="relative flex gap-2 items-center">
                <div className="relative flex-1">
                  <Input 
                    id="search-input"
                    type="search"
                    data-testid="search-input"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={getPlaceholder()}
                    className="peer pe-20 ps-10 h-11"
                  />
                  <div className="pointer-events-none absolute inset-y-0 start-0 flex items-center justify-center ps-3 text-muted-foreground/80 peer-disabled:opacity-50">
                    <Search size={18} strokeWidth={2} />
                  </div>
                  <button
                    type="submit"
                    data-testid="search-submit-button"
                    disabled={(isSearching && !isStreaming) || !query.trim()}
                    className="absolute inset-y-0 end-1 flex h-[calc(100%-8px)] my-auto items-center justify-center rounded-lg px-3 text-sm font-medium bg-[var(--color-accent-primary)] text-white transition-colors hover:bg-[var(--color-accent-primary)]/90 focus:z-10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring/70 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50"
                    aria-label="Submit search"
                  >
                    {isSearching || isStreaming ? "Searching..." : "Search"}
                  </button>
                </div>
                <LanguageSelector
                  value={selectedLanguage}
                  onChange={setSelectedLanguage}
                  detectedLanguage={detectedLanguage}
                />
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
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                className="mb-12"
              >
                <AIInterpretation
                  text={streamedAnswer}
                  verseDetails={verseDetails}
                  onNavigate={navigateToVerse}
                />
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
                  <SearchResultCard
                    source={result.source}
                    reference={result.reference}
                    text={extractVerseText(result.text)}
                    score={result.score}
                    onClick={() => navigateToVerse(result.reference)}
                    className={highlightedVerse === result.reference ? "ring-2 ring-[var(--color-accent-primary)]/40" : ""}
                  />
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
