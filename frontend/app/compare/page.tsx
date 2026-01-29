"use client";

import { useState, useEffect, useCallback, useRef, useMemo, Suspense } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { GlowCard } from "@/components/ui/glow-card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { useSSE } from "@/lib/hooks/use-sse";
import {
  LogOut,
  User,
  BookOpen,
  Clock,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Quote,
  Search,
} from "lucide-react";
import { usePreferencesStore } from "@/lib/stores/preferences-store";
import { FilterTabs, FilterType } from "@/components/compare/filter-tabs";
import { SourceReferenceCard } from "@/components/compare/source-reference-card";
import { InlineCitation } from "@/components/compare/inline-citation";
import { parseCitations } from "@/lib/utils/parse-citations";
import { useLogger } from "@/lib/logger";

interface ParagraphData {
  title: string;
  content: string;
  citations: string[];
}

interface CompareResult {
  topic: string;
  essay: string;
  paragraphs: ParagraphData[];
  citations: Record<string, string[]>;
  confidence: number;
  total_verses: number;
  total_citations: number;
  latency_ms: number;
  verse_details?: Record<string, {
    text: string;
    book_name: string;
    chapter: number;
    verse: number;
    source: string;
    translation: string;
    book_nr?: number;  // Bible book number (null for Quran)
  }>;
}

const FILTER_TO_SOURCE: Record<string, string[]> = {
  'all': ['quran_tr', 'bible_ot', 'bible_nt', 'bible_apocrypha'],
  'quran': ['quran_tr'],
  'old_testament': ['bible_ot'],
  'new_testament': ['bible_nt'],
  'apocrypha': ['bible_apocrypha']
};

function CompareContent() {
  const [topic, setTopic] = useState("");
  const [result, setResult] = useState<CompareResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [expandedParagraphs, setExpandedParagraphs] = useState<Set<number>>(
    new Set()
  );
  const [activeFilter, setActiveFilter] = useState<FilterType>('all');
  const [highlightedVerse, setHighlightedVerse] = useState<string | null>(null);
  const highlightTimerRef = useRef<NodeJS.Timeout | null>(null);
  const hasAutoExecuted = useRef(false);
  const log = useLogger("ComparePage");
  const { user, isLoading: authLoading, logout } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const { data: sseData, isStreaming, error: sseError, startStream } = useSSE();
  const { enable_streaming } = usePreferencesStore();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
    toast.success("Logged out successfully");
  };

  const toggleParagraph = (index: number) => {
    setExpandedParagraphs((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const scrollToVerse = useCallback((reference: string) => {
    const element = document.querySelector(`[data-verse-id="${reference}"]`);

    if (!element) {
      log.warn("Verse card not found for scroll", {
        action: "scrollToVerse",
        reference,
      });
      return;
    }

    // Cancel previous timer
    if (highlightTimerRef.current) {
      clearTimeout(highlightTimerRef.current);
    }

    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setHighlightedVerse(reference);

    highlightTimerRef.current = setTimeout(() => {
      setHighlightedVerse(null);
    }, 2000);
  }, [log]);

  // Navigate to verse page (opens in new tab)
  const navigateToVerse = useCallback((reference: string) => {
    if (!result?.verse_details) {
      log.warn("No verse_details available for navigation", {
        action: "navigateToVerse",
        reference,
      });
      scrollToVerse(reference);
      return;
    }

    const verse = result.verse_details[reference];
    if (!verse) {
      log.warn("Verse details not found for reference", {
        action: "navigateToVerse",
        reference,
      });
      scrollToVerse(reference);
      return;
    }

    let url: string;
    if (verse.source === 'quran_tr') {
      // Quran: /quran/{surahId}?verse={verseId}
      url = `/quran/${verse.chapter}?verse=${verse.verse}`;
    } else {
      // Bible: /bible/{bookNr}?chapter={chapter}&verse={verse}
      if (!verse.book_nr) {
        log.warn("Bible book_nr not available for reference", {
          action: "navigateToVerse",
          reference,
          source: verse.source,
        });
        scrollToVerse(reference);
        return;
      }
      url = `/bible/${verse.book_nr}?chapter=${verse.chapter}&verse=${verse.verse}`;
    }

    // Open in new tab
    window.open(url, '_blank');
  }, [result?.verse_details, scrollToVerse, log]);

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (highlightTimerRef.current) {
        clearTimeout(highlightTimerRef.current);
      }
    };
  }, []);

  const filteredVerses = useMemo(() => {
    if (!result?.verse_details) return [];
    const entries = Object.entries(result.verse_details);
    if (activeFilter === 'all') return entries;
    return entries.filter(([_, verse]) => 
      FILTER_TO_SOURCE[activeFilter].includes(verse.source)
    );
  }, [result?.verse_details, activeFilter]);

  const counts = useMemo(() => {
    if (!result?.verse_details) return { all: 0, quran: 0, old_testament: 0, new_testament: 0, apocrypha: 0 };
    const verses = Object.values(result.verse_details);
    return {
      all: verses.length,
      quran: verses.filter(v => v.source === 'quran_tr').length,
      old_testament: verses.filter(v => v.source === 'bible_ot').length,
      new_testament: verses.filter(v => v.source === 'bible_nt').length,
      apocrypha: verses.filter(v => v.source === 'bible_apocrypha').length,
    };
  }, [result?.verse_details]);

  const performBatchCompare = async (topicToCompare: string) => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("http://localhost:8000/api/compare/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ topic: topicToCompare, use_multi_agent: true }),
      });

      if (!response.ok) {
        throw new Error("Compare failed");
      }

      const data = await response.json();
      setResult(data);
      toast.success(
        `Analysis complete in ${(data.latency_ms / 1000).toFixed(1)}s`
      );
    } catch (error) {
      toast.error("Analysis failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
   };

  // Auto-execute comparison from URL q param (history re-run)
  useEffect(() => {
    const q = searchParams?.get("q");
    if (q && q.trim() && !hasAutoExecuted.current) {
      hasAutoExecuted.current = true;
      setTopic(q);           // Populate input field for display
      setIsLoading(true);
      setResult(null);
      setExpandedParagraphs(new Set());

      if (enable_streaming) {
        try {
          const baseUrl = "http://localhost:8000";
          const token = localStorage.getItem("access_token");
          if (!token) {
            toast.error("Authentication required");
            performBatchCompare(q);  // Fallback to batch
            return;
          }
          // Build SSE URL using q directly (NOT topic state, which may not be updated yet)
          const url = `${baseUrl}/api/stream/compare?topic=${encodeURIComponent(q)}&token=${encodeURIComponent(token)}`;
          startStream(url);
        } catch (err) {
          performBatchCompare(q);    // Fallback to batch
        }
      } else {
        performBatchCompare(q);      // q passed directly as topicToCompare parameter
      }
    }
  }, [searchParams, enable_streaming, startStream, performBatchCompare]);

  // Handle SSE Data updates
  useEffect(() => {
    if (sseData.length === 0) return;

    // Check for complete message
    const completeMsg = sseData.findLast((m) => m.type === "complete");
    if (completeMsg?.result) {
      setResult(completeMsg.result as CompareResult);
      setIsLoading(false);
      return;
    }

    // Handle verse_details from streaming (sent before text)
    const verseDetailsMsg = sseData.findLast((m: any) => m.verse_details);
    if (verseDetailsMsg?.verse_details) {
      setResult((prev) => {
        const base = prev || {
          topic,
          essay: "",
          paragraphs: [],
          citations: {},
          confidence: 0,
          total_verses: 0,
          total_citations: 0,
          latency_ms: 0,
        };
        return {
          ...base,
          verse_details: verseDetailsMsg.verse_details,
        };
      });
    }

    // Extract stats from most recent SSE messages
    const statsMsg = sseData.findLast((m: any) => m.stats);
    if (statsMsg?.stats) {
      setResult((prev) => {
        const base = prev || {
          topic,
          essay: "",
          paragraphs: [],
          citations: {},
          confidence: 0,
          total_verses: 0,
          total_citations: 0,
          latency_ms: 0,
        };
        return {
          ...base,
          confidence: statsMsg.stats.confidence || base.confidence,
          latency_ms: statsMsg.stats.latency_ms || base.latency_ms,
          total_verses: statsMsg.stats.total_verses || base.total_verses,
        };
      });
    }

    // Handle progressive updates
    const paragraphs = sseData
      .filter((m: any) => m.type === "section" || m.type === "paragraph")
      .map((m: any) => m.data || m.result || m.content)
      .filter(Boolean);

    if (paragraphs.length > 0) {
      setResult((prev) => {
        const base = prev || {
          topic,
          essay: "",
          paragraphs: [],
          citations: {},
          confidence: 0,
          total_verses: 0,
          total_citations: 0,
          latency_ms: 0,
        };
        
        // Auto-expand new paragraphs
        setExpandedParagraphs((prevSet) => {
          const newSet = new Set(prevSet);
          paragraphs.forEach((_, idx) => newSet.add(idx));
          return newSet;
        });

        return {
          ...base,
          paragraphs: paragraphs as ParagraphData[],
          total_citations: paragraphs.reduce((acc: number, p: any) => acc + (p.citations?.length || 0), 0)
        };
      });
      setIsLoading(false);
    }
  }, [sseData, topic]);

  // Handle SSE Errors
  useEffect(() => {
    if (sseError) {
      toast.error("Streaming connection lost. Falling back to standard analysis...");
      performBatchCompare(topic);
    }
  }, [sseError]);

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsLoading(true);
    setResult(null);
    setExpandedParagraphs(new Set()); 

    // Check streaming preference
    if (enable_streaming) {
      // Start SSE Stream
      try {
        const baseUrl = "http://localhost:8000";
        const token = localStorage.getItem("access_token");
        if (!token) {
          toast.error("Authentication required");
          performBatchCompare(topic);
          return;
        }
        // SSE/EventSource doesn't support custom headers, so pass token as query param
        const url = `${baseUrl}/api/stream/compare?topic=${encodeURIComponent(topic)}&token=${encodeURIComponent(token)}`;
        startStream(url);
      } catch (err) {
        // Fallback
        performBatchCompare(topic);
      }
    } else {
      // Use batch API directly
      performBatchCompare(topic);
    }
  };

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    );
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
              Search
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

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
        >
          <h1 className="mb-2 text-3xl font-bold text-[var(--color-text-primary)]">
            Comparative Scripture Analysis
          </h1>
          <p className="mb-8 text-[var(--color-text-muted)]">
            Multi-agent analysis across Quran, Old Testament, New Testament, and
            Apocrypha
          </p>

          {/* Search Form */}
          <form onSubmit={handleCompare} className="mb-8 flex gap-4">
            <Input
              type="text"
              data-testid="compare-topic-input"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="Enter a topic (e.g., patience, forgiveness, creation)..."
              className="flex-1"
            />
            <Button
              type="submit"
              data-testid="compare-analyze-button"
              disabled={isLoading || !topic.trim()}
              className="bg-[var(--color-accent-primary)] min-w-[120px]"
            >
              {isLoading ? "Analyzing..." : "Analyze"}
            </Button>
          </form>
        </motion.div>

        {/* Loading State & Streaming Progress */}
        {(isLoading || isStreaming) && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4 mb-8"
          >
            <div className="flex items-center gap-2 text-[var(--color-text-muted)] mb-4">
              <Sparkles className="h-4 w-4 animate-pulse" />
              <span>
                {result?.paragraphs?.length 
                  ? `Analyzing... (${result.paragraphs.length}/5 agents completed)`
                  : "Initializing multi-agent analysis..."}
              </span>
            </div>
            
            {/* Show remaining skeletons */}
            {[...Array(Math.max(0, 5 - (result?.paragraphs?.length || 0)))].map((_, i) => (
              <Skeleton key={i} className="h-32 w-full" />
            ))}
          </motion.div>
        )}

        {/* Results */}
        <AnimatePresence mode="wait">
          {result && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={springPresets.fluid}
            >
              {/* Stats Header */}
              <GlowCard className="mb-6">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div className="flex items-center gap-2">
                    <Sparkles className="h-5 w-5 text-[var(--color-accent-primary)]" />
                    <span className="font-semibold text-[var(--color-text-primary)]">
                      Analysis Complete
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-4 text-sm text-[var(--color-text-muted)]">
                    <div className="flex items-center gap-1">
                      <BookOpen className="h-4 w-4" />
                      <span>{result.total_verses} verses</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Quote className="h-4 w-4" />
                      <span>{result.total_citations} citations</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      <span>{(result.latency_ms / 1000).toFixed(1)}s</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <span
                        className={`font-medium ${
                          result.confidence >= 0.8
                            ? "text-green-400"
                            : result.confidence >= 0.6
                              ? "text-yellow-400"
                              : "text-red-400"
                        }`}
                      >
                        {(result.confidence * 100).toFixed(0)}% confidence
                      </span>
                    </div>
                  </div>
                </div>
              </GlowCard>

              {/* Paragraphs */}
              <div className="space-y-4">
                {result.paragraphs.map((paragraph, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{
                      ...springPresets.snappy,
                      delay: index * 0.1,
                    }}
                  >
                    <GlowCard>
                      {/* Paragraph Header */}
                      <button
                        onClick={() => toggleParagraph(index)}
                        className="flex w-full items-center justify-between text-left"
                      >
                        <h3 className="text-lg font-semibold text-[var(--color-accent-primary)]">
                          {paragraph.title}
                        </h3>
                        {expandedParagraphs.has(index) ? (
                          <ChevronUp className="h-5 w-5 text-[var(--color-text-muted)]" />
                        ) : (
                          <ChevronDown className="h-5 w-5 text-[var(--color-text-muted)]" />
                        )}
                      </button>

                      {/* Paragraph Content */}
                      <AnimatePresence>
                        {expandedParagraphs.has(index) && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: "auto", opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            transition={springPresets.snappy}
                            className="overflow-hidden"
                          >
                            <div className="mt-4 border-t border-[var(--color-border-subtle)] pt-4">
                              <p className="text-[var(--color-text-primary)] leading-relaxed whitespace-pre-wrap">
                                {parseCitations(paragraph.content).map((part, i) => {
                                  if (typeof part === 'string') {
                                    return <span key={i}>{part}</span>;
                                  }
                                  
                                  const verse = result.verse_details?.[part.reference];
                                  if (!verse) {
                                    return (
                                      <span key={i} className="text-[var(--color-text-muted)]">
                                        [{part.reference}]
                                      </span>
                                    );
                                  }
                                  
                                  return (
                                    <InlineCitation
                                      key={i}
                                      reference={part.reference}
                                      onClick={() => navigateToVerse(part.reference)}
                                    />
                                  );
                                })}
                              </p>

                              {/* Citations */}
                              {paragraph.citations.length > 0 && (
                                <div className="mt-4 pt-4 border-t border-[var(--color-border-subtle)]">
                                  <p className="text-xs font-medium text-[var(--color-text-muted)] mb-2">
                                    Citations:
                                  </p>
                                  <div className="flex flex-wrap gap-2">
                                    {paragraph.citations.map((citation, i) => (
                                      <span
                                        key={i}
                                        className="inline-block px-2 py-1 text-xs rounded-md bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)] border border-[var(--color-border-subtle)]"
                                      >
                                        {citation}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </GlowCard>
                  </motion.div>
                ))}
              </div>

              {/* Kaynak Referanslari */}
              {result.verse_details && Object.keys(result.verse_details).length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{
                    ...springPresets.snappy,
                    delay: result.paragraphs.length * 0.1 + 0.1,
                  }}
                  className="mt-6"
                  data-testid="verse-references-section"
                >
                  <GlowCard>
                    <h3
                      className="text-lg font-semibold text-[var(--color-text-primary)] mb-4"
                      data-testid="verse-references-heading"
                    >
                      Kaynak Referanslari
                    </h3>
                    
                    <FilterTabs
                      activeFilter={activeFilter}
                      onFilterChange={setActiveFilter}
                      counts={counts}
                    />
                    
                    <div className="space-y-4 mt-4">
                      {filteredVerses.length > 0 ? (
                        filteredVerses.map(([reference, verse], index) => (
                          <SourceReferenceCard
                            key={reference}
                            reference={reference}
                            verse={verse}
                            isHighlighted={highlightedVerse === reference}
                            index={index}
                          />
                        ))
                      ) : (
                        <p className="text-[var(--color-text-muted)] text-center py-8">
                          Bu kategori icin sonuc bulunamadi.
                          {activeFilter !== 'all' && (
                            <span> Tum sonuclari gormek icin "Tumu" sekmesine tiklayin.</span>
                          )}
                        </p>
                      )}
                    </div>
                  </GlowCard>
                </motion.div>
              )}

              {/* All Citations Summary */}
              {Object.keys(result.citations).length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{
                    ...springPresets.snappy,
                    delay: result.paragraphs.length * 0.1,
                  }}
                  className="mt-6"
                >
                  <GlowCard>
                    <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">
                      All Citations by Source
                    </h3>
                    <div className="space-y-4">
                      {Object.entries(result.citations).map(
                        ([source, citations]) =>
                          citations.length > 0 && (
                            <div key={source}>
                              <p className="text-sm font-medium text-[var(--color-accent-primary)] mb-2 capitalize">
                                {source.replace("_", " ")}
                              </p>
                              <div className="flex flex-wrap gap-2">
                                {citations.map((citation, i) => (
                                  <span
                                    key={i}
                                    className="inline-block px-2 py-1 text-xs rounded-md bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)] border border-[var(--color-border-subtle)]"
                                  >
                                    {citation}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )
                      )}
                    </div>
                  </GlowCard>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    }>
      <CompareContent />
    </Suspense>
  );
}
