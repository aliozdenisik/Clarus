"use client";

import { useState, useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { Skeleton } from "@/components/ui/skeleton";
import { Search } from "lucide-react";
import { toast } from "sonner";
import { listRootsApiSearchKeywordRootsGet } from "@/lib/api/sdk.gen";
import type { RootListItem } from "@/lib/api/types.gen";
import { cn } from "@/lib/utils";

interface RootBrowserProps {
  onRootSelect: (root: string) => void;
}

type SortMode = "frequency" | "alphabetical";

function RootRow({
  root,
  count,
  index,
  onClick,
}: {
  root: string;
  count: number;
  index: number;
  onClick: () => void;
}) {
  return (
    <motion.button
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ ...springPresets.snappy, delay: Math.min(index * 0.02, 0.5) }}
      onClick={onClick}
      className="w-full flex items-center justify-between px-4 py-3 rounded-lg hover:bg-[var(--color-bg-elevated)] transition-colors group"
    >
      <span
        className="font-arabic text-xl text-[var(--color-text-primary)] group-hover:text-[var(--color-accent-primary)] transition-colors"
        lang="ar"
      >
        {root}
      </span>
      <span className="text-sm text-[var(--color-text-muted)] tabular-nums">
        {count.toLocaleString()}
      </span>
    </motion.button>
  );
}

export function RootBrowser({ onRootSelect }: RootBrowserProps) {
  const [roots, setRoots] = useState<RootListItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  const [filterText, setFilterText] = useState("");
  const [sortBy, setSortBy] = useState<SortMode>("frequency");

  // Fetch all roots on mount
  useEffect(() => {
    const fetchAllRoots = async () => {
      setIsLoading(true);
      try {
        const allRoots: RootListItem[] = [];
        let page = 1;
        let hasMore = true;

        while (hasMore) {
          const response = await listRootsApiSearchKeywordRootsGet({
            query: { page, per_page: 200 },
          });

          if (response.data) {
            allRoots.push(...(response.data.roots || []));
            hasMore = allRoots.length < (response.data.total || 0);
            page++;
          } else {
            hasMore = false;
          }
        }

        // Deduplicate roots by merging counts for identical root strings
        // (Arabic Unicode normalization can cause GROUP BY to return
        //  roots that are byte-different but render-identical)
        const rootMap = new Map<string, number>();
        for (const item of allRoots) {
          rootMap.set(item.root, (rootMap.get(item.root) || 0) + item.count);
        }
        const dedupedRoots: RootListItem[] = Array.from(rootMap.entries()).map(
          ([root, count]) => ({ root, count })
        );

        setRoots(dedupedRoots);
        setTotalCount(dedupedRoots.length);
      } catch (err) {
        toast.error("Failed to load roots");
      } finally {
        setIsLoading(false);
      }
    };

    fetchAllRoots();
  }, []);

  // Filter and sort roots
  const sortedRoots = useMemo(() => {
    // Filter by search text (supports Arabic and Latin)
    const filtered = filterText
      ? roots.filter((r) => r.root.includes(filterText))
      : roots;

    // Sort by selected mode
    return [...filtered].sort((a, b) => {
      if (sortBy === "frequency") {
        return b.count - a.count;
      }
      return a.root.localeCompare(b.root, "ar");
    });
  }, [roots, filterText, sortBy]);

  // Featured roots (top 20 most frequent)
  const featuredRoots = useMemo(() => {
    return [...roots]
      .sort((a, b) => b.count - a.count)
      .slice(0, 20);
  }, [roots]);

  // Show featured roots initially, all roots when filtering/sorting
  const displayRoots = filterText || sortBy === "alphabetical" ? sortedRoots : featuredRoots;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-[var(--color-text-primary)]">
          {totalCount > 0 ? `${totalCount.toLocaleString()} Arabic Roots` : "Arabic Roots"}
        </h2>
      </div>

      {/* Filter input */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-[18px] w-[18px] text-[var(--color-text-muted)]" />
        <input
          type="text"
          dir="auto"
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
          placeholder="Filter roots..."
          disabled={isLoading}
          className={cn(
            "w-full h-12 pl-12 pr-4 bg-[var(--color-bg-surface)] rounded-xl",
            "text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]",
            "border border-[var(--color-border-subtle)]",
            "focus:border-[var(--color-border-glow)] focus:outline-none",
            "transition-all duration-300 text-[15px]",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        />
      </div>

      {/* Sort toggle */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setSortBy("frequency")}
          className={cn(
            "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
            sortBy === "frequency"
              ? "bg-indigo-500 text-white"
              : "bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
          )}
        >
          By Frequency
        </button>
        <button
          onClick={() => setSortBy("alphabetical")}
          className={cn(
            "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
            sortBy === "alphabetical"
              ? "bg-indigo-500 text-white"
              : "bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
          )}
        >
          Alphabetical
        </button>
      </div>

      {/* Section header */}
      {!filterText && sortBy === "frequency" && (
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-medium text-[var(--color-text-secondary)] uppercase tracking-widest">
            Featured / Most Frequent Roots
          </h3>
          <div className="flex-1 h-px bg-[var(--color-border-subtle)]" />
          <span className="text-[var(--color-text-muted)] text-xs">◆</span>
        </div>
      )}

      {/* Loading skeleton */}
      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="flex items-center justify-between px-4 py-3">
              <Skeleton className="h-6 w-24" />
              <Skeleton className="h-4 w-12" />
            </div>
          ))}
        </div>
      )}

      {/* Root list */}
      {!isLoading && displayRoots.length > 0 && (
        <div className="space-y-1">
          {displayRoots.map((rootItem, index) => (
            <RootRow
              key={`${rootItem.root}-${index}`}
              root={rootItem.root}
              count={rootItem.count}
              index={index}
              onClick={() => onRootSelect(rootItem.root)}
            />
          ))}
        </div>
      )}

      {/* Empty state */}
      {!isLoading && displayRoots.length === 0 && (
        <div className="text-center py-12">
          <p className="text-[var(--color-text-muted)]">
            {filterText ? "No roots match your filter" : "No roots available"}
          </p>
        </div>
      )}
    </div>
  );
}
