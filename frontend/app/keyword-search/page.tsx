"use client";

import { useState, useEffect, useCallback, Suspense } from "react";
import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { SearchInput } from "@/components/keyword-search/search-input";
import { searchKeywordApiSearchKeywordPost } from "@/lib/api/sdk.gen";
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

  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();

  // Auth guard
  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  const handleSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await searchKeywordApiSearchKeywordPost({
        body: {
          query: searchQuery,
          page: currentPage,
          per_page: 50,
        },
      });

      setSearchResult(response.data as KeywordSearchResponse);
      toast.success(`Found ${response.data?.total_occurrences || 0} occurrences`);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Search failed";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [currentPage]);

  const handlePageChange = useCallback((newPage: number) => {
    setCurrentPage(newPage);
    if (query.trim()) {
      handleSearch(query);
    }
  }, [query, handleSearch]);

  const handleWordFilter = useCallback((word: string) => {
    setSelectedWord(word);
  }, []);

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
              {!searchResult && !isLoading && (
                <div className="text-center py-16">
                  <p className="text-[var(--color-text-muted)] text-sm">
                    Search for a root to see results
                  </p>
                </div>
              )}

              {/* Placeholder for search results components (Tasks 2-5) */}
              {searchResult && (
                <div className="space-y-6">
                  {/* Root card will go here (Task 2) */}
                  {/* Stats bar will go here (Task 3) */}
                  {/* Derived words will go here (Task 4) */}
                  {/* Chart will go here (Task 4) */}
                  {/* Verse cards will go here (Task 5) */}
                  {/* Pagination will go here (Task 5) */}
                  
                  <div className="text-center py-8 text-[var(--color-text-muted)] text-sm">
                    Results display components will be integrated in Tasks 2-5
                  </div>
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
              <div className="text-center py-16">
                <p className="text-[var(--color-text-muted)] text-sm">
                  Root browser will appear here (Task 6)
                </p>
              </div>
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
