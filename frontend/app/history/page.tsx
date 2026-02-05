"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { Button } from "@/components/ui/button";
import { GlowCard } from "@/components/ui/glow-card";
import { GlowingButton } from "@/components/ui/glowing-button";
import { DotPattern, RadialGradient } from "@/components/ui/dot-pattern";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import {
  LogOut,
  User,
  Clock,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Search,
  History as HistoryIcon,
  BookOpen,
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import {
  getSearchHistoryApiSearchHistoryGet,
  deleteHistoryItemApiSearchHistoryHistoryIdDelete,
  clearHistoryApiSearchHistoryDelete,
} from '@/lib/api/sdk.gen';

interface HistoryItem {
  id: number;
  query: string;
  search_type: string;
  created_at: string;
  result_count: number | null;
}

interface PaginationData {
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

const SEARCH_TYPE_LABELS: Record<string, string> = {
  // Standard search
  search_quran: "Quran",
  search_bible_all: "Bible",
  search_bible_ot: "Old Testament",
  search_bible_nt: "New Testament",
  search_bible_apocrypha: "Apocrypha",
  // Streaming search
  stream_search_quran: "Quran",
  stream_search_bible: "Bible",
  stream_search_ot: "Old Testament",
  stream_search_nt: "New Testament",
  stream_search_apocrypha: "Apocrypha",
  // Compare
  compare: "Compare",
  compare_multi_agent: "Multi-Agent",
  stream_compare: "Compare",
};

function getSearchTypeLabel(searchType: string): string {
  return SEARCH_TYPE_LABELS[searchType] || "Search";
}

function getHistoryItemUrl(item: HistoryItem): string {
  const encodedQuery = encodeURIComponent(item.query);
  
  switch (item.search_type) {
    // Quran search
    case "search_quran":
    case "stream_search_quran":
      return `/search?source=quran&q=${encodedQuery}`;
    
    // Bible search (all / OT)
    case "search_bible_all":
    case "stream_search_bible":
    case "search_bible_ot":
    case "stream_search_ot":
      return `/search?source=ot&q=${encodedQuery}`;
    
    // Bible NT
    case "search_bible_nt":
    case "stream_search_nt":
      return `/search?source=nt&q=${encodedQuery}`;
    
    // Bible Apocrypha
    case "search_bible_apocrypha":
    case "stream_search_apocrypha":
      return `/search?source=apocrypha&q=${encodedQuery}`;
    
    // Compare
    case "compare":
    case "compare_multi_agent":
    case "stream_compare":
      return `/compare?q=${encodedQuery}`;
    
    // Fallback for unknown types
    default:
      return `/search?q=${encodedQuery}`;
  }
}

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [pagination, setPagination] = useState<PaginationData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isClearing, setIsClearing] = useState(false);
  const { user, isLoading: authLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  const fetchHistory = async (page = 1) => {
    try {
      setIsLoading(true);
      const response = await getSearchHistoryApiSearchHistoryGet({
        query: { page, limit: 20 },
      });

      // ACTUAL backend response structure (from backend/app/api/search.py:262-273):
      // { success: true, data: [...], pagination: { page, limit, total_items, total_pages, has_next, has_prev } }
      if (response.data) {
        const body = response.data as {
          success: boolean;
          data: HistoryItem[];
          pagination: {
            page: number;
            limit: number;
            total_items: number;
            total_pages: number;
            has_next: boolean;
            has_prev: boolean;
          };
        };
        setItems(body.data);
        setPagination({
          total: body.pagination.total_items,
          page: body.pagination.page,
          per_page: body.pagination.limit,
          pages: body.pagination.total_pages,
        });
      }
    } catch (error) {
      toast.error("Failed to load history");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      fetchHistory();
    }
  }, [user]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
    toast.success("Logged out successfully");
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteHistoryItemApiSearchHistoryHistoryIdDelete({
        path: { history_id: id },
      });

      setItems((prev) => prev.filter((item) => item.id !== id));
      toast.success("Item deleted");

      if (items.length === 1 && pagination && pagination.page > 1) {
        fetchHistory(pagination.page - 1);
      } else if (items.length === 1) {
        fetchHistory(1);
      }
    } catch (error) {
      toast.error("Failed to delete item");
    }
  };

  const handleClearAll = async () => {
    if (!confirm("Are you sure you want to clear all history?")) return;

    try {
      setIsClearing(true);
      await clearHistoryApiSearchHistoryDelete();

      setItems([]);
      setPagination(null);
      toast.success("History cleared");
    } catch (error) {
      toast.error("Failed to clear history");
    } finally {
      setIsClearing(false);
    }
  };

  const handlePageChange = (newPage: number) => {
    if (pagination && newPage >= 1 && newPage <= pagination.pages) {
      fetchHistory(newPage);
    }
  };

  const handleHistoryClick = (item: HistoryItem) => {
    router.push(getHistoryItemUrl(item));
  };

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    );
  }

  return (
    <div className="relative min-h-screen bg-[var(--color-bg-app)] p-8 overflow-hidden">
      {/* Premium ambient effects */}
      <div className="fixed inset-0 pointer-events-none">
        <DotPattern width={40} height={40} cr={0.4} className="opacity-[0.025]" />
        <RadialGradient 
          className="inset-0" 
          color="var(--color-accent-primary)" 
          size="900px" 
          position="30% 10%" 
          opacity={0.04}
        />
        <RadialGradient 
          className="inset-0" 
          color="var(--color-accent-secondary)" 
          size="600px" 
          position="70% 60%" 
          opacity={0.03}
        />
      </div>
      
      <div className="relative mx-auto max-w-4xl z-10">
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

        {/* Title & Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
          className="mb-8 flex items-center justify-between"
        >
          <div>
            <h1 className="mb-2 text-3xl font-bold text-[var(--color-text-primary)] flex items-center gap-3">
              <HistoryIcon className="h-8 w-8 text-[var(--color-accent-primary)]" />
              Search History
            </h1>
            <p className="text-[var(--color-text-muted)]">
              View and manage your past search queries
            </p>
          </div>
          {items && items.length > 0 && (
            <Button
              variant="destructive"
              size="sm"
              onClick={handleClearAll}
              disabled={isClearing}
              className="flex items-center gap-2"
            >
              <Trash2 className="h-4 w-4" />
              Clear All
            </Button>
          )}
        </motion.div>

        {/* Content */}
        {isLoading ? (
          <div className="space-y-4">
             <div className="text-[var(--color-text-secondary)] mb-4">Loading history...</div>
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        ) : !items || items.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={springPresets.gentle}
            className="flex flex-col items-center justify-center py-24"
          >
            {/* Illustrated empty state */}
            <div className="relative mb-8">
              <div className="absolute inset-0 blur-2xl bg-[var(--color-accent-primary)] opacity-10 rounded-full scale-150" />
              <div className="relative w-24 h-24 rounded-2xl bg-gradient-to-br from-[var(--color-bg-surface)] to-[var(--color-bg-elevated)] border border-[var(--color-border-subtle)] flex items-center justify-center">
                <BookOpen className="w-10 h-10 text-[var(--color-accent-primary)] opacity-60" />
              </div>
            </div>
            <h3 className="text-xl font-medium text-[var(--color-text-primary)] mb-2">
              No search history yet
            </h3>
            <p className="text-sm text-[var(--color-text-muted)] mb-8 text-center max-w-sm">
              Your searches will appear here. Start exploring sacred texts to build your history.
            </p>
            <GlowingButton
              onClick={() => router.push("/search")}
              glowColor="#6366f1"
              className="px-8"
            >
              <span className="flex items-center gap-2">
                <Search className="w-4 h-4" />
                Start Searching
              </span>
            </GlowingButton>
          </motion.div>
        ) : (
          <div className="space-y-4">
            <AnimatePresence mode="popLayout">
               {items.map((item, i) => (
                 <motion.div
                   key={item.id}
                   initial={{ opacity: 0, y: 20 }}
                   animate={{ opacity: 1, y: 0 }}
                   exit={{ opacity: 0, scale: 0.95 }}
                   transition={{ ...springPresets.snappy, delay: i * 0.05 }}
                   layout
                   onClick={() => handleHistoryClick(item)}
                   className="cursor-pointer"
                 >
                  <GlowCard className="group relative overflow-hidden">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="mb-1 flex items-center gap-3">
                          <span className="text-sm font-medium uppercase text-[var(--color-accent-primary)]">
                            {getSearchTypeLabel(item.search_type)}
                          </span>
                          <span className="flex items-center gap-1 text-xs text-[var(--color-text-muted)]">
                            <Clock className="h-3 w-3" />
                            {formatDistanceToNow(new Date(item.created_at), {
                              addSuffix: true,
                            })}
                          </span>
                        </div>
                        <p className="text-lg font-medium text-[var(--color-text-primary)]">
                          {item.query}
                        </p>
                        {item.result_count != null && item.result_count > 0 && (
                          <p className="mt-1 text-sm text-[var(--color-text-muted)]">
                            {item.result_count} {item.result_count === 1 ? 'result' : 'results'}
                          </p>
                        )}
                      </div>
                       <Button
                         variant="ghost"
                         size="icon"
                         onClick={(e) => {
                           e.stopPropagation();
                           handleDelete(item.id);
                         }}
                         className="opacity-0 transition-opacity group-hover:opacity-100 text-[var(--color-text-muted)] hover:text-red-500 hover:bg-red-500/10"
                         aria-label="Delete item"
                       >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </GlowCard>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Pagination */}
            {pagination && pagination.pages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(pagination.page - 1)}
                  disabled={pagination.page === 1}
                  className="flex items-center gap-2"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <span className="text-sm text-[var(--color-text-secondary)]">
                  Page {pagination.page} of {pagination.pages}
                </span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(pagination.page + 1)}
                  disabled={pagination.page === pagination.pages}
                  className="flex items-center gap-2"
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
