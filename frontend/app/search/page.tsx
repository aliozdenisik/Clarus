"use client";

import { useState, useEffect, Suspense, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { GlowCard } from "@/components/ui/glow-card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { LogOut, User, GitCompare } from "lucide-react";
import { SearchTabs, SearchSource } from "@/components/search/search-tabs";
import { useSSE } from "@/lib/hooks/use-sse";
import { usePreferencesStore } from "@/lib/stores/preferences-store";
import { parseCitations, CitationPart } from "@/lib/utils/parse-citations";
import { InlineCitation } from "@/components/compare/inline-citation";
import { VerseTooltip, VerseDetail } from "@/components/search/verse-tooltip";
import { SourceBadge, SourceType } from "@/components/compare/source-badge";

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

    // Handle verse_details message
    const verseDetailsMsg = sseData.find((m) => m.verse_details);
    if (verseDetailsMsg?.verse_details) {
      setVerseDetails(verseDetailsMsg.verse_details as Record<string, VerseDetail>);
    }

    const completeMsg = sseData.find((m) => m.type === "complete");
    if (completeMsg?.result) {
      const data = completeMsg.result as { results?: SearchResult[] };
      if (data.results) {
        setResults(data.results);
        setIsSearching(false);
      }
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
      console.warn(`No verse details for ${reference}, falling back to scroll`);
      scrollToVerse(reference);  // Fallback: scroll instead of navigate
      return;
    }

    let url = "";
    if (verse.source === "quran_tr" || verse.source === "quran") {
      // Use surah_id and verse_id for Quran (handle both source formats)
      const surahId = verse.surah_id || verse.chapter;
      const verseId = verse.verse_id || verse.verse;
      url = `/quran/${surahId}?verse=${verseId}`;
    } else if (verse.source.startsWith("bible_")) {
      // Use book_nr for Bible
      const bookNr = verse.book_nr || 1;
      url = `/bible/${bookNr}?chapter=${verse.chapter}&verse=${verse.verse}`;
    } else {
      console.warn(`Unknown source format: ${verse.source}`);
      scrollToVerse(reference);
      return;
    }

    window.open(url, "_blank");
  }, [verseDetails, scrollToVerse]);

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

  const performBatchSearch = useCallback(async () => {
    setIsSearching(true);
    setResults([]);

    try {
      const token = localStorage.getItem("access_token");

      let url = "http://localhost:8000/api/search/quran";
      let body: any = { query, mode: "semantic", top_k: 10 };

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

      // NEW: Store verse_details if available
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

  // Handle SSE errors by falling back to batch search
  useEffect(() => {
    if (sseError && !hasHandledSSEError.current) {
      hasHandledSSEError.current = true;
      toast.error("Streaming failed. Switching to standard search.");
      performBatchSearch();
    }
  }, [sseError, performBatchSearch]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setResults([]);
    setStreamedAnswer("");
    setVerseDetails({});
    setHighlightedVerse(null);
    setOpenPopover(null);
    hasHandledSSEError.current = false;  // Reset error handler flag

    if (enable_streaming) {
      setIsSearching(true);
      const baseUrl = "http://localhost:8000";
      const token = localStorage.getItem("access_token");
      if (!token) {
        toast.error("Authentication required");
        performBatchSearch();
        return;
      }
      // SSE/EventSource doesn't support custom headers, so pass token as query param
      const url = `${baseUrl}/api/stream/search?q=${encodeURIComponent(query)}&source=${activeTab}&token=${encodeURIComponent(token)}`;
      startStream(url);
    } else {
      performBatchSearch();
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--color-bg-app)] p-8">
      <div className="mx-auto max-w-4xl">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.snappy}
          className="mb-6 flex items-center justify-between"
        >
          <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
            <User className="h-4 w-4" />
            <span className="text-sm">{user?.name || user?.email}</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/compare")}
              className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
            >
              <GitCompare className="h-4 w-4" />
              Compare
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
        >
          <h1 className="mb-8 text-3xl font-bold text-[var(--color-text-primary)]">
            Search
          </h1>

          <SearchTabs activeTab={activeTab} onTabChange={handleTabChange} />

          <form onSubmit={handleSearch} className="mb-8 flex gap-4">
            <Input
              type="text"
              data-testid="search-input"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={getPlaceholder()}
              className="flex-1"
            />
            <Button
              type="submit"
              data-testid="search-submit-button"
              disabled={(isSearching && !isStreaming) || !query.trim()}
              className="bg-[var(--color-accent-primary)]"
            >
              {isSearching || isStreaming ? "Searching..." : "Search"}
            </Button>
          </form>
        </motion.div>

        <AnimatePresence>
          {streamedAnswer && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-8"
            >
              <GlowCard className="bg-[var(--color-bg-secondary)]">
                <h3 className="mb-2 text-sm font-medium text-[var(--color-accent-primary)]">AI Answer</h3>
                <div className="whitespace-pre-wrap text-[var(--color-text-primary)] leading-relaxed">
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
              </GlowCard>
            </motion.div>
          )}
        </AnimatePresence>

        {isSearching && !results.length && !streamedAnswer && (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-32 w-full" />
            ))}
          </div>
        )}

        {isSearching && !results.length && streamedAnswer && (
          <div className="space-y-4 mt-8">
             <p className="text-sm text-[var(--color-text-muted)]">Fetching source verses...</p>
             {[...Array(3)].map((_, i) => (
               <Skeleton key={i} className="h-32 w-full" />
             ))}
          </div>
        )}

        <div ref={resultsContainerRef}>
          <AnimatePresence mode="popLayout">
            {results.map((result, i) => (
              <motion.div
                key={`${result.reference}-${i}`}
                data-verse-id={result.reference}
                initial={{ opacity: 0, y: 20 }}
                animate={{
                  opacity: 1,
                  y: 0,
                  scale: highlightedVerse === result.reference ? 1.02 : 1,
                }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ ...springPresets.snappy, delay: i * 0.05 }}
                className="mb-4"
              >
                <GlowCard
                  className={
                    highlightedVerse === result.reference
                      ? "ring-2 ring-[var(--color-accent-primary)] transition-all duration-300"
                      : ""
                  }
                >
                  <div className="mb-2 flex items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-[var(--color-accent-primary)]">
                        {result.reference || "Unknown Reference"}
                      </span>
                      <SourceBadge source={mapSourceToType(result.source)} />
                    </div>
                    <span className="text-xs text-[var(--color-text-muted)]">
                      {(result.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-[var(--color-text-primary)] leading-relaxed">{result.text}</p>
                </GlowCard>
              </motion.div>
            ))}
          </AnimatePresence>
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
          <div className="text-[var(--color-text-secondary)]">Loading...</div>
        </div>
      }
    >
      <SearchContent />
    </Suspense>
  );
}
