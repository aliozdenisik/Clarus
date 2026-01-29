"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { Button } from "@/components/ui/button";
import { GlowCard } from "@/components/ui/glow-card";
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
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center py-20 text-[var(--color-text-muted)]"
          >
            <HistoryIcon className="mb-4 h-16 w-16 opacity-20" />
            <p className="text-lg font-medium">No search history found</p>
            <p className="text-sm">Your search history will appear here</p>
            <Button
              variant="outline"
              className="mt-6"
              onClick={() => router.push("/search")}
            >
              Start Searching
            </Button>
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
                        onClick={() => handleDelete(item.id)}
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
