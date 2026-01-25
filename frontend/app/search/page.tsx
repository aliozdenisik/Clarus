"use client";

import { useState, useEffect, Suspense } from "react";
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

    const completeMsg = sseData.find((m) => m.type === "complete");
    if (completeMsg?.result) {
      const data = completeMsg.result as any;
      if (data.results) {
        setResults(data.results);
        setIsSearching(false);
      }
    }
  }, [sseData]);

  useEffect(() => {
    if (sseError) {
      toast.error("Streaming failed. Switching to standard search.");
      performBatchSearch();
    }
  }, [sseError]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
    toast.success("Logged out successfully");
  };

  const handleTabChange = (tab: SearchSource) => {
    setActiveTab(tab);
    setResults([]);
    setStreamedAnswer("");
    router.push(`/search?source=${tab}`);
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

  const performBatchSearch = async () => {
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
      toast.success(`Found ${data.results.length} results`);
    } catch (error) {
      toast.error("Search failed. Please try again.");
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setResults([]);
    setStreamedAnswer("");

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
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={getPlaceholder()}
              className="flex-1"
            />
            <Button
              type="submit"
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
                <p className="whitespace-pre-wrap text-[var(--color-text-primary)]">{streamedAnswer}</p>
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

        <AnimatePresence mode="popLayout">
          {results.map((result, i) => (
            <motion.div
              key={`${result.reference}-${i}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ ...springPresets.snappy, delay: i * 0.05 }}
              className="mb-4"
            >
              <GlowCard>
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-sm font-medium text-[var(--color-accent-primary)]">
                    {result.reference}
                  </span>
                  <span className="text-xs text-[var(--color-text-muted)]">
                    Score: {(result.score * 100).toFixed(1)}%
                  </span>
                </div>
                <p className="text-[var(--color-text-primary)]">{result.text}</p>
              </GlowCard>
            </motion.div>
          ))}
        </AnimatePresence>
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
