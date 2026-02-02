"use client";

import { useState, useEffect, useCallback, Suspense, useMemo } from "react";
import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { SearchInput } from "@/components/keyword-search/search-input";
import { RootCard } from "@/components/keyword-search/root-card";
import { StatsBar } from "@/components/keyword-search/stats-bar";
import { DerivedWords } from "@/components/keyword-search/derived-words";
import { SurahChart } from "@/components/keyword-search/surah-chart";
import { VerseCard } from "@/components/keyword-search/verse-card";
import { Pagination } from "@/components/keyword-search/pagination";
import { stripArabicDiacritics } from "@/lib/utils/arabic";
import { RootBrowser } from "@/components/keyword-search/root-browser";
import { Skeleton } from "@/components/ui/skeleton";
import { searchKeywordApiSearchKeywordPost, getSurahDetailApiMetadataQuranSurahsSurahIdGet, getQuranSurahsApiMetadataQuranSurahsGet } from "@/lib/api/sdk.gen";
import type { KeywordSearchResponse } from "@/lib/api/types.gen";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type TabType = "results" | "browser";

function KeywordSearchContent() {
  const [query, setQuery] = useState("");
  const [searchResult, setSearchResult] = useState<KeywordSearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>("results");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedWord, setSelectedWord] = useState<string | null>(null);
  const [translations, setTranslations] = useState<Map<string, string>>(new Map());
  const [translationsLoading, setTranslationsLoading] = useState(false);
  const [surahTransliterations, setSurahTransliterations] = useState<Map<number, string>>(new Map());

  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();

  // Fetch surah Latin transliterations on mount
  useEffect(() => {
    const fetchSurahNames = async () => {
       try {
         const response = await getQuranSurahsApiMetadataQuranSurahsGet();
         const body = response.data as { data?: { surahs?: Array<{ id: number; transliteration: string }> } } | undefined;
         const surahs = body?.data?.surahs || [];
        const map = new Map<number, string>();
        surahs.forEach(s => map.set(s.id, s.transliteration));
        setSurahTransliterations(map);
      } catch { /* ignore */ }
    };
    fetchSurahNames();
  }, []);

  // Helper: get Latin surah name, fallback to Arabic
  const getSurahName = useCallback((surahId: number, arabicFallback: string) =>
    surahTransliterations.get(surahId) || arabicFallback, [surahTransliterations]);

  // Auth guard
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  const handleSearch = useCallback(async (searchQuery: string, page: number = 1) => {
    if (!searchQuery.trim()) {
      setError("Please enter an Arabic word or Buckwalter root");
      return;
    }

    setIsLoading(true);
    setError(null);
    setSelectedWord(null);

    try {
      const response = await searchKeywordApiSearchKeywordPost({
        body: {
          query: searchQuery.trim(),
          page,
          per_page: 50,
        },
      });

      if (response.data) {
        setSearchResult(response.data as KeywordSearchResponse);
        setCurrentPage(page);
      }
    } catch (err: unknown) {
      const error = err as { status?: number };
      if (error.status === 429) {
        toast.error("Daily search limit reached. Please try again tomorrow.");
      } else {
        toast.error("Search failed. Please try again.");
      }
      setError("Search failed");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handlePageChange = useCallback((newPage: number) => {
    if (query.trim()) {
      handleSearch(query, newPage);
    }
  }, [query, handleSearch]);

  const handleWordFilter = useCallback((word: string | null) => {
    setSelectedWord(word);
  }, []);

  const handleRootSelect = useCallback((root: string) => {
    setQuery(root);
    handleSearch(root, 1);
    setActiveTab("results");
  }, [handleSearch]);

  // Fetch Turkish translations after search results arrive
  useEffect(() => {
    if (!searchResult?.verses?.length) return;

    const fetchTranslations = async () => {
      setTranslationsLoading(true);
      const translationMap = new Map<string, string>();

      // Group verses by surah_id
      const surahIds = [...new Set(searchResult.verses!.map((v) => v.surah_id))];

      // Fetch each surah's data
      await Promise.all(
        surahIds.map(async (surahId) => {
           try {
             const response = await getSurahDetailApiMetadataQuranSurahsSurahIdGet({
               path: { surah_id: surahId },
             });
             // API returns { success, data: { surah: { verses: [...] } } }
             const body = response.data as { data?: { surah?: { verses?: Array<{ text: string; translation: string }> } } } | undefined;
             const verses = body?.data?.surah?.verses;
             if (verses) {
               verses.forEach(
                 (
                   verse: { text: string; translation: string },
                   index: number
                 ) => {
                   const key = `${surahId}:${index + 1}`;
                   translationMap.set(key, verse.translation);
                 }
               );
             }
          } catch {
            // Silently fail for individual surahs
          }
        })
      );

      setTranslations(translationMap);
      setTranslationsLoading(false);
    };

    fetchTranslations();
  }, [searchResult?.verses]);

  // Helper to get translation
  const getTranslation = useCallback(
    (surahId: number, ayahNumber: number): string | undefined => {
      return translations.get(`${surahId}:${ayahNumber}`);
    },
    [translations]
  );

  // Filter verses by selected word
  const filteredVerses = useMemo(() => {
    if (!searchResult?.verses) return [];
    if (!selectedWord) return searchResult.verses;
    const normalizedSelected = stripArabicDiacritics(selectedWord);
    return searchResult.verses.filter((v) =>
      v.matched_words.some(
        (w) => stripArabicDiacritics(w) === normalizedSelected
      )
    );
  }, [searchResult?.verses, selectedWord]);

  // Compute chart data based on selected word (client-side)
  const chartData = useMemo(() => {
    // If no word selected, show full root distribution
    if (!selectedWord || !searchResult?.surah_distribution) {
      return searchResult?.surah_distribution || [];
    }

    // If word selected, compute distribution from filtered verses
    if (!searchResult?.verses) return [];

    const normalizedSelected = stripArabicDiacritics(selectedWord);
    const wordFilteredVerses = searchResult.verses.filter((v) =>
      v.matched_words.some(
        (w) => stripArabicDiacritics(w) === normalizedSelected
      )
    );

    // Aggregate by surah
    const surahMap = new Map<number, { surah_id: number; surah_name: string; count: number }>();
    for (const verse of wordFilteredVerses) {
      const existing = surahMap.get(verse.surah_id);
      if (existing) {
        existing.count += 1;
      } else {
        surahMap.set(verse.surah_id, {
          surah_id: verse.surah_id,
          surah_name: verse.surah_name,
          count: 1,
        });
      }
    }

    return Array.from(surahMap.values());
  }, [selectedWord, searchResult]);

  // Compute filtered stats based on selected word
  const filteredStats = useMemo(() => {
    if (!selectedWord || !searchResult) {
      return {
        totalOccurrences: searchResult?.total_occurrences || 0,
        uniqueWords: (searchResult?.unique_words || []).length,
        surahCount: (searchResult?.surah_distribution || []).length,
      };
    }

    // When word selected, compute from filtered data
    return {
      totalOccurrences: filteredVerses.length,
      uniqueWords: 1,
      surahCount: chartData.length,
    };
  }, [selectedWord, searchResult, filteredVerses, chartData]);

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-[var(--color-bg-app)]">
      {/* Ambient teal gradient background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-teal-950/20 via-transparent to-transparent" />
      </div>

      {/* Header */}
      <div className="relative pt-12 pb-2 px-6">
        <div className="mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={springPresets.fluid}
          >
            {/* Ornamental divider */}
            <div className="text-center text-[var(--color-text-muted)] text-xs tracking-widest mb-4">
              ◆
            </div>

            {/* Title */}
            <h1 className="font-display text-4xl font-normal tracking-tight text-center text-[var(--color-text-primary)] mb-2">
              Word Search
            </h1>
            <p className="text-sm text-[var(--color-text-secondary)] text-center mb-8">
              Explore Arabic roots and their Quranic footprint
            </p>

            {/* Search Input */}
            <SearchInput
              value={query}
              onChange={setQuery}
              onSearch={handleSearch}
              isLoading={isLoading}
              placeholder="Search for Arabic roots (e.g., كتب or ktb)..."
            />
          </motion.div>
        </div>
      </div>

      {/* Content */}
      <div className="relative px-6 pb-16">
        <div className="mx-auto max-w-4xl">
          {/* Tab Navigation */}
          <div className="flex flex-wrap gap-1 p-1 bg-[var(--color-bg-surface)] rounded-lg border border-[var(--color-border-subtle)] w-fit mb-6">
            {[
              { id: "results" as const, label: "Search Results" },
              { id: "browser" as const, label: "Root Browser" },
            ].map((tab) => {
              const isActive = activeTab === tab.id;
              return (
                <div key={tab.id} className="relative">
                  {isActive && (
                    <motion.div
                      layoutId="activeKeywordTab"
                      className="absolute inset-0 bg-[var(--color-bg-elevated)] rounded-md border border-[var(--color-border-subtle)] shadow-sm"
                      initial={false}
                      transition={springPresets.snappy}
                    />
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setActiveTab(tab.id)}
                    className={cn(
                      "relative z-10 hover:bg-transparent transition-colors duration-200",
                      isActive
                        ? "text-[var(--color-accent-primary)] font-medium"
                        : "text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
                    )}
                    data-state={isActive ? "active" : "inactive"}
                  >
                    {tab.label}
                  </Button>
                </div>
              );
            })}
          </div>

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
                    {[1, 2, 3].map((i) => (
                      <Skeleton key={i} className="h-20" />
                    ))}
                  </div>
                  {/* Verse skeletons */}
                  <div className="space-y-4">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <Skeleton key={i} className="h-40" />
                    ))}
                  </div>
                </div>
              ) : error ? (
                // Error state
                <div className="text-center py-12">
                  <p className="text-[var(--color-text-muted)]">{error}</p>
                </div>
              ) : searchResult ? (
                // Full results
                <div className="space-y-8">
                  {/* Buckwalter feedback */}
                  {searchResult.root_source?.includes("buckwalter") &&
                    searchResult.root && (
                      <div className="text-center text-sm text-[var(--color-text-secondary)]">
                        Detected: Buckwalter Latin → Arabic:{" "}
                        <span className="font-arabic" lang="ar">
                          {searchResult.root}
                        </span>
                      </div>
                    )}

                  {/* Root not found */}
                  {searchResult.root_source === "not_found" ? (
                    <div className="text-center py-12">
                      <p className="text-lg text-[var(--color-text-muted)]">
                        No root found for &quot;{searchResult.query}&quot;
                      </p>
                      <p className="text-sm text-[var(--color-text-secondary)] mt-2">
                        Try a different Arabic word or Buckwalter
                        transliteration.
                      </p>
                    </div>
                  ) : (
                    <>
                      <RootCard
                        root={searchResult.root || null}
                        rootSource={searchResult.root_source || ""}
                        rootBuckwalter={searchResult.root_buckwalter}
                      />
                      <StatsBar
                        totalOccurrences={filteredStats.totalOccurrences}
                        uniqueWords={filteredStats.uniqueWords}
                        surahCount={filteredStats.surahCount}
                      />
                      <DerivedWords
                        words={searchResult.unique_words || []}
                        selectedWord={selectedWord}
                        onWordSelect={handleWordFilter}
                        transliterations={searchResult.word_transliterations || {}}
                      />
                      <SurahChart
                        data={chartData.map(d => ({
                          ...d,
                          surah_name: getSurahName(d.surah_id, d.surah_name)
                        }))}
                        selectedWord={selectedWord}
                      />

                      {/* Verse Cards */}
                      <div className="space-y-4">
                        <div className="text-center text-[var(--color-text-muted)] text-xs tracking-widest">
                          ◆
                        </div>
                        <h3 className="text-lg font-medium text-[var(--color-text-primary)] text-center">
                          Verse Results
                        </h3>
                        {filteredVerses.map((verse, i) => (
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
                            index={i}
                          />
                        ))}
                      </div>

                      {/* Pagination */}
                      {searchResult.pagination && (
                        <Pagination
                          page={searchResult.pagination.page}
                          totalPages={searchResult.pagination.total_pages}
                          totalVerses={searchResult.pagination.total_verses}
                          hasNext={searchResult.pagination.has_next}
                          hasPrev={searchResult.pagination.has_prev}
                          onPageChange={handlePageChange}
                        />
                      )}
                    </>
                  )}
                </div>
              ) : (
                // Empty state (before any search)
                <div className="text-center py-12 space-y-4">
                  <div className="text-[var(--color-text-muted)] text-xs tracking-widest">
                    ◆
                  </div>
                  <p className="text-lg text-[var(--color-text-secondary)]">
                    Search for any Arabic root or word to explore its Quranic
                    footprint
                  </p>
                  <p
                    className="font-arabic text-3xl text-[var(--color-text-muted)]"
                    lang="ar"
                  >
                    بِسۡمِ ٱللَّهِ ٱلرَّحۡمَٰنِ ٱلرَّحِيمِ
                  </p>
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
  );
}

export default function KeywordSearchPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
          <div className="text-[var(--color-text-secondary)]">Loading...</div>
        </div>
      }
    >
      <KeywordSearchContent />
    </Suspense>
  );
}
