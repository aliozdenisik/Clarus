"use client";

import { useState, useEffect, useCallback, useRef, useMemo, Suspense } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useSession, signOut } from "@/lib/auth-client";

import { GlowCard } from "@/components/ui/glow-card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { useSSE } from "@/lib/hooks/use-sse";
import {
  Clock,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Quote,
  Search,
} from "lucide-react";
import { usePreferencesStore } from "@/lib/stores/preferences-store";
import { AnimatedFilterTabs, FilterType } from "@/components/ui/animated-tabs";
import { TypingIndicator, AIResponse } from "@/components/ui/typewriter";
import { DotPattern } from "@/components/ui/dot-pattern";
import { AuroraSectionBackground } from "@/components/ui/aurora-background";

import { SourceReferenceCard } from "@/components/compare/source-reference-card";
import { InlineCitation } from "@/components/compare/inline-citation";
import { parseCitations, parseBareReferences, stripMarkdownHeaders } from "@/lib/utils/parse-citations";
import { useLogger } from "@/lib/logger";
import { LanguageSelector } from "@/components/search/language-selector";
import { TranslatorSelector } from "@/components/search/translator-selector";
import { CollectionSelector } from "@/components/compare/collection-selector";
import { AnalysisProgress } from "@/components/compare/analysis-progress";
import type { KeywordSuggestion } from "@/lib/stores/keyword-store";
import { compareScripturesApiComparePost } from "@/lib/api/sdk.gen";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

// Verse counts per collection (from Qdrant)
const COLLECTION_VERSE_COUNTS: Record<string, number> = {
  'quran_tr': 6236,
  'bible_ot': 23145,
  'bible_nt': 7957,
  'bible_apocrypha': 5717,
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
  const [selectedLanguage, setSelectedLanguage] = useState<string | null>(null);
  const [detectedLanguage, setDetectedLanguage] = useState<string | undefined>(undefined);
  const [selectedTranslator, setSelectedTranslator] = useState("diyanet");
  const [selectedCollections, setSelectedCollections] = useState<string[]>([
    "quran_tr", "bible_ot", "bible_nt", "bible_apocrypha"
  ]);
  
  // Keyword state
  const [advancedMode, setAdvancedMode] = useState(false);
  const [quranKeywords, setQuranKeywords] = useState<KeywordSuggestion[]>([]);
  const [bibleKeywords, setBibleKeywords] = useState<KeywordSuggestion[]>([]);
  const [isExtractingKeywords, setIsExtractingKeywords] = useState(false);
  
  // Dynamic verse count based on selected collections
  const selectedVerseCount = useMemo(() => {
    return selectedCollections.reduce(
      (total, col) => total + (COLLECTION_VERSE_COUNTS[col] || 0),
      0
    );
  }, [selectedCollections]);
  
  const highlightTimerRef = useRef<NodeJS.Timeout | null>(null);
  const hasAutoExecuted = useRef(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const lastHandledSseError = useRef<Error | null>(null);
  const log = useLogger("ComparePage");
  const { data: session, isPending: authLoading } = useSession();
  const user = session?.user;
  const router = useRouter();
  const searchParams = useSearchParams();

  const { data: sseData, isStreaming, error: sseError, startStream } = useSSE();
  const { enable_streaming } = usePreferencesStore();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in");
    }
  }, [user, authLoading, router]);

  const handleLogout = async () => {
    await signOut();
    router.push("/sign-in");
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

   const extractKeywords = async (query: string, corpus: "quran" | "bible") => {
     const response = await fetch(`${API_BASE_URL}/api/search/enhance`, {
       method: "POST",
       headers: {
         "Content-Type": "application/json",
       },
       credentials: "include",
       body: JSON.stringify({ query, corpus }),
     });

    if (!response.ok) {
      throw new Error(`Keyword extraction failed for ${corpus}`);
    }

    const data = await response.json();
    return data.keywords || [];
  };

  const performBatchCompare = async (topicToCompare: string) => {
    setIsLoading(true);
    try {
      const requestBody: any = {
        topic: topicToCompare,
        use_multi_agent: true,
        collections: selectedCollections,
        ...(selectedLanguage && { language: selectedLanguage }),
        translator: selectedTranslator,
      };
      
      if (advancedMode) {
        const selectedQuranKeywords = quranKeywords
          .filter((k) => k.selected)
          .map((k) => k.text);
        const selectedBibleKeywords = bibleKeywords
          .filter((k) => k.selected)
          .map((k) => k.text);
        
        if (selectedQuranKeywords.length > 0) {
          requestBody.quran_keywords = selectedQuranKeywords;
        }
        if (selectedBibleKeywords.length > 0) {
          requestBody.bible_keywords = selectedBibleKeywords;
        }
      }
      
      const response = await compareScripturesApiComparePost({
        body: requestBody,
      });

      const data = response.data as any;
      setResult(data);
      if (data.detected_language) {
        setDetectedLanguage(data.detected_language);
      }
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
           // Build SSE URL using q directly (NOT topic state, which may not be updated yet)
           let url = `${API_BASE_URL}/api/stream/compare?topic=${encodeURIComponent(q)}`;
          url += `&collections=${encodeURIComponent(selectedCollections.join(','))}`;
          if (selectedLanguage) {
            url += `&language=${encodeURIComponent(selectedLanguage)}`;
          }
          url += `&translator=${encodeURIComponent(selectedTranslator)}`;
          startStream(url);
        } catch (err) {
          performBatchCompare(q);    // Fallback to batch
        }
      } else {
        performBatchCompare(q);      // q passed directly as topicToCompare parameter
      }
    }
  }, [searchParams, enable_streaming, startStream, performBatchCompare, selectedLanguage]);

  // Handle SSE Data updates
  useEffect(() => {
    if (sseData.length === 0) return;

    // Check for complete message
    const completeMsg = sseData.findLast((m) => m.type === "complete");
    if (completeMsg?.result) {
      setResult(completeMsg.result as CompareResult);
      if ((completeMsg.result as any).detected_language) {
        setDetectedLanguage((completeMsg.result as any).detected_language);
      }
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
    // Backend sends: {"type": "stats", "data": {confidence, latency_ms, total_verses, total_citations}}
    const statsMsg = sseData.findLast((m: any) => m.type === "stats");
    if (statsMsg?.data) {
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
          confidence: statsMsg.data.confidence || base.confidence,
          latency_ms: statsMsg.data.latency_ms || base.latency_ms,
          total_verses: statsMsg.data.total_verses || base.total_verses,
          total_citations: statsMsg.data.total_citations || base.total_citations,
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
    if (sseError && sseError !== lastHandledSseError.current) {
      lastHandledSseError.current = sseError;
      toast.error("Streaming connection lost. Falling back to standard analysis...");
      performBatchCompare(topic);
    }
  }, [sseError, topic, performBatchCompare]);

  const handleCompare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    // Less than 2 collections → redirect to Search page
    if (selectedCollections.length < 2) {
      const sourceMap: Record<string, string> = {
        'quran_tr': 'quran',
        'bible_ot': 'old_testament',
        'bible_nt': 'new_testament',
        'bible_apocrypha': 'apocrypha',
      };
      // Default to quran if nothing selected, otherwise use the single selected source
      const source = selectedCollections.length === 1 
        ? (sourceMap[selectedCollections[0]] || 'quran')
        : 'quran';
      router.push(`/search?source=${source}&q=${encodeURIComponent(topic)}`);
      toast.info("Karşılaştırma için en az 2 kaynak gerekli. Arama sayfasına yönlendiriliyorsunuz.");
      return;
    }

    setIsLoading(true);
    setResult(null);
    setExpandedParagraphs(new Set());

    // If advanced mode is ON, extract keywords first
    if (advancedMode) {
      setIsExtractingKeywords(true);
      try {
        // Extract keywords in parallel for both corpora
        const [quranKw, bibleKw] = await Promise.all([
          selectedCollections.includes("quran_tr")
            ? extractKeywords(topic, "quran")
            : Promise.resolve([]),
          selectedCollections.some((c) =>
              ["bible_ot", "bible_nt", "bible_apocrypha"].includes(c)
            )
            ? extractKeywords(topic, "bible")
            : Promise.resolve([]),
        ]);

        setQuranKeywords(quranKw);
        setBibleKeywords(bibleKw);
        setIsExtractingKeywords(false);

        // Wait for user to select keywords before proceeding
        // User will click "Analyze" again after selecting keywords
        setIsLoading(false);
        return;
      } catch (error) {
        toast.error("Keyword extraction failed. Proceeding with normal search.");
        setIsExtractingKeywords(false);
        // Fall through to normal compare
      }
    }

     // Check streaming preference
     if (enable_streaming) {
       // Start SSE Stream — uses cookie auth via withCredentials
       try {
         let url = `${API_BASE_URL}/api/stream/compare?topic=${encodeURIComponent(topic)}`;
        url += `&collections=${encodeURIComponent(selectedCollections.join(','))}`;
        if (selectedLanguage) {
          url += `&language=${encodeURIComponent(selectedLanguage)}`;
        }
        url += `&translator=${encodeURIComponent(selectedTranslator)}`;
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
    <div className="relative min-h-screen bg-[var(--color-bg-app)] overflow-hidden">
      {/* Subtle ambient texture */}
      <div className="fixed inset-0 pointer-events-none">
        <DotPattern width={40} height={40} cr={0.4} className="opacity-[0.015]" />
      </div>

      {/* Compare Hero */}
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
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-violet-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-2 w-2 bg-violet-500" />
              </span>
              <span className="text-xs font-medium text-[var(--color-text-secondary)] tracking-wide">
                5-Agent Multi-Scripture Analysis
              </span>
            </motion.div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl font-bold text-[var(--color-text-primary)] mb-4 tracking-tight">
              <span className="bg-gradient-to-r from-white via-white to-white/70 bg-clip-text text-transparent">
                Compare
              </span>
            </h1>
            
            {/* Subtitle with dynamic verse count */}
            <p className="text-base md:text-lg text-[var(--color-text-muted)] max-w-md mx-auto leading-relaxed">
              Comparative analysis across{" "}
              <span className="text-[var(--color-text-secondary)] font-medium tabular-nums">
                {selectedVerseCount.toLocaleString()}
              </span>
              {" "}verses from{" "}
              <span className="text-[var(--color-text-secondary)] font-medium">
                {selectedCollections.length}
              </span>
              {" "}sources
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.fluid, delay: 0.2, duration: 0.5 }}
            className="flex flex-col items-center"
          >
            {/* Search form with glass effect */}
            <form onSubmit={handleCompare} className="relative mb-6 w-full max-w-2xl">
              <div className="relative flex gap-2 items-center justify-center">
                <div className="relative flex-1 group">
                  {/* Glow effect on focus */}
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-violet-500/20 via-indigo-500/20 to-violet-500/20 rounded-xl opacity-0 group-focus-within:opacity-100 blur transition-opacity duration-300" />
                  
                  <textarea
                    ref={textareaRef}
                    data-testid="compare-topic-input"
                    value={topic}
                    onChange={(e) => {
                      setTopic(e.target.value);
                      // Auto-resize: reset to auto then set to scrollHeight
                      const ta = e.target;
                      ta.style.height = 'auto';
                      ta.style.height = `${ta.scrollHeight}px`;
                    }}
                    onKeyDown={(e) => {
                      // Submit on Enter (without Shift)
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        if (topic.trim() && !isLoading) {
                          handleCompare(e as unknown as React.FormEvent);
                        }
                      }
                    }}
                    placeholder="Enter a topic to compare..."
                    rows={1}
                    className="relative peer pe-28 ps-12 min-h-12 py-3 bg-[var(--color-bg-surface)]/80 backdrop-blur-sm border-white/10 hover:border-white/20 focus:border-violet-500/50 transition-colors text-base w-full rounded-lg border border-input shadow-sm shadow-black/5 placeholder:text-muted-foreground/70 focus-visible:border-ring focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring/20 disabled:cursor-not-allowed disabled:opacity-50 resize-none overflow-hidden"
                  />
                  <div className="pointer-events-none absolute top-0 start-0 flex h-12 items-center justify-center ps-4 text-muted-foreground/60 peer-disabled:opacity-50">
                    <Search size={20} strokeWidth={1.5} />
                  </div>
                  <button
                    type="submit"
                    data-testid="compare-analyze-button"
                    disabled={isLoading || !topic.trim()}
                    className="absolute top-1.5 end-1.5 flex h-9 items-center justify-center rounded-lg px-4 text-sm font-medium bg-gradient-to-r from-violet-500 to-indigo-500 text-white transition-all hover:from-violet-600 hover:to-indigo-600 focus:z-10 focus-visible:outline focus-visible:outline-2 focus-visible:outline-ring/70 disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 shadow-lg shadow-violet-500/25"
                    aria-label="Submit analysis"
                  >
                    {isLoading ? "Analyzing..." : "Analyze"}
                  </button>
                </div>
                <LanguageSelector
                  value={selectedLanguage}
                  onChange={setSelectedLanguage}
                  detectedLanguage={detectedLanguage}
                />
                {selectedCollections.includes("quran_tr") && (
                  <TranslatorSelector
                    value={selectedTranslator}
                    onChange={setSelectedTranslator}
                  />
                )}
              </div>
              
              {/* Collection Selector - compact inline */}
              <div className="w-full mt-3 flex items-center justify-center gap-2">
                <span className="text-xs text-[var(--color-text-muted)]">Kaynaklar:</span>
                <CollectionSelector
                  selected={selectedCollections}
                  onChange={setSelectedCollections}
                  disabled={isLoading}
                />
              </div>
              
              {/* Keyword Selector - Advanced Mode Toggle */}
              <div className="w-full mt-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="advanced-mode"
                      checked={advancedMode}
                      onChange={(e) => setAdvancedMode(e.target.checked)}
                      disabled={isLoading || isExtractingKeywords}
                      className="w-4 h-4 rounded border-zinc-700 bg-zinc-900 text-indigo-500 focus:ring-2 focus:ring-indigo-500/40"
                    />
                    <label
                      htmlFor="advanced-mode"
                      className="text-sm font-medium text-[var(--color-text-secondary)] cursor-pointer"
                    >
                      Gelişmiş Arama
                    </label>
                  </div>
                  <span className="text-xs text-[var(--color-text-muted)]">
                    Anahtar kelime bazlı arama
                  </span>
                </div>
                
                {/* Show keywords after extraction */}
                {advancedMode && (quranKeywords.length > 0 || bibleKeywords.length > 0) && (
                  <div className="space-y-3 p-4 rounded-lg bg-[var(--color-bg-surface)]/50 border border-[var(--color-border-subtle)]">
                    {/* Quran Keywords */}
                    {quranKeywords.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-[var(--color-text-muted)] mb-2">
                          Kuran Anahtar Kelimeleri:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {quranKeywords.map((kw) => (
                            <button
                              key={kw.text}
                              type="button"
                              onClick={() => {
                                setQuranKeywords((prev) =>
                                  prev.map((k) =>
                                    k.text === kw.text ? { ...k, selected: !k.selected } : k
                                  )
                                );
                              }}
                              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                                kw.selected
                                  ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40"
                                  : "bg-zinc-800/50 text-zinc-400 border border-zinc-700/40 hover:bg-zinc-800"
                              }`}
                            >
                              {kw.text}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Bible Keywords */}
                    {bibleKeywords.length > 0 && (
                      <div>
                        <p className="text-xs font-medium text-[var(--color-text-muted)] mb-2">
                          İncil Anahtar Kelimeleri:
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {bibleKeywords.map((kw) => (
                            <button
                              key={kw.text}
                              type="button"
                              onClick={() => {
                                setBibleKeywords((prev) =>
                                  prev.map((k) =>
                                    k.text === kw.text ? { ...k, selected: !k.selected } : k
                                  )
                                );
                              }}
                              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                                kw.selected
                                  ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/40"
                                  : "bg-zinc-800/50 text-zinc-400 border border-zinc-700/40 hover:bg-zinc-800"
                              }`}
                            >
                              {kw.text}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Loading state for keyword extraction */}
                {isExtractingKeywords && (
                  <div className="flex items-center gap-2 text-[var(--color-text-muted)] text-sm">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-indigo-500 border-t-transparent" />
                    <span>Anahtar kelimeler çıkarılıyor...</span>
                  </div>
                )}
              </div>
            </form>
          </motion.div>
        </div>
      </AuroraSectionBackground>

       {/* Content */}
       <div className="relative px-6 pb-16">
         <div className="mx-auto max-w-3xl">
         {/* Loading State & Streaming Progress - Outside Suspense (renders immediately) */}
         {(isLoading || isStreaming) && (
           <motion.div
             initial={{ opacity: 0 }}
             animate={{ opacity: 1 }}
             className="space-y-4 mb-8"
           >
             {/* Granular pipeline progress (streaming mode) */}
             {(() => {
               const progressEvents = sseData
                 .filter((m) => m.type === "progress" && m.step && m.message)
                 .map((m) => ({ step: m.step as string, message: m.message as string }));
               
               if (progressEvents.length > 0) {
                 return (
                   <AnalysisProgress
                     progressEvents={progressEvents}
                     hasParagraphs={(result?.paragraphs?.length ?? 0) > 0}
                     className="mb-4"
                   />
                 );
               }

               // Fallback for batch mode (no SSE progress events)
               return (
                 <div className="flex items-center gap-3 text-[var(--color-text-muted)] mb-4">
                   <TypingIndicator />
                   <span className="text-sm">
                     {result?.paragraphs?.length 
                       ? `Analyzing... (${result.paragraphs.length}/5 agents completed)`
                       : "Initializing multi-agent analysis..."}
                   </span>
                 </div>
               );
             })()}
             
             {/* Show remaining skeletons */}
             {[...Array(Math.max(0, 5 - (result?.paragraphs?.length || 0)))].map((_, i) => (
               <Skeleton key={i} className="h-32 w-full" />
             ))}
           </motion.div>
         )}

         {/* Analysis & Essay Section - Inside Suspense (progressive loading) */}
         <Suspense
           fallback={
             <div className="space-y-4">
               {[...Array(5)].map((_, i) => (
                 <Skeleton key={i} className="h-32 w-full" />
               ))}
             </div>
           }
         >
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
                             {stripMarkdownHeaders(paragraph.title)}
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
                               <div className="mt-4 pt-4">
                                 <div className="relative pl-6 border-l-2 border-[var(--color-accent-primary)] py-1">
                                   <span className="text-[11px] font-medium uppercase tracking-[0.15em] text-[var(--color-accent-primary)] mb-3 block opacity-70">
                                     AI Interpretation
                                   </span>
                                   <p className="text-[var(--color-text-primary)] leading-[1.85] text-[15px] whitespace-pre-wrap">
                                     {parseBareReferences(parseCitations(stripMarkdownHeaders(paragraph.content)), paragraph.citations).map((part, i) => {
                                       if (typeof part === 'string') {
                                         return <span key={i}>{part}</span>;
                                       }
                                       
                                       const verse = result.verse_details?.[part.reference];
                                       
                                       return (
                                         <InlineCitation
                                           key={i}
                                           reference={part.reference}
                                           verseDetail={verse}
                                           onNavigate={navigateToVerse}
                                         />
                                       );
                                     })}
                                   </p>
                                 </div>

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

                 {/* Ornamental divider */}
                 {result.paragraphs.length > 0 && result.verse_details && (
                   <div className="flex items-center gap-4 my-8">
                     <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[var(--color-border-subtle)] to-transparent" />
                     <div className="w-1 h-1 rotate-45 bg-[var(--color-accent-primary)] opacity-30" />
                     <div className="flex-1 h-px bg-gradient-to-r from-transparent via-[var(--color-border-subtle)] to-transparent" />
                   </div>
                 )}

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
                       
                       <AnimatedFilterTabs
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
         </Suspense>
         </div>
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
