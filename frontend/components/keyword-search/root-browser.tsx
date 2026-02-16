"use client"

import React, { useState, useEffect, useMemo, useCallback } from "react"
import { motion } from "framer-motion"
import { List, type RowComponentProps, useListRef } from "react-window"
import { springPresets } from "@/lib/design-system"
import { Skeleton } from "@/components/ui/skeleton"
import { Search } from "lucide-react"
import { toast } from "sonner"
import { listRootsApiSearchKeywordRootsGet } from "@/lib/api/sdk.gen"
import type { RootListItem } from "@/lib/api/types.gen"
import { cn } from "@/lib/utils"
import { useTranslations } from "next-intl"

interface RootBrowserProps {
  onRootSelect: (root: string) => void
}

type SortMode = "frequency" | "alphabetical"

const ROOT_ROW_HEIGHT = 56
const ROOT_LIST_MAX_HEIGHT = 560
const ROOT_LIST_OVERSCAN = 8

interface RootListData {
  roots: RootListItem[]
  onSelect: (root: string) => void
}

const RootRow = React.memo(function RootRow({
  root,
  count,
  onSelect,
}: {
  root: string
  count: number
  onSelect: (root: string) => void
}) {
  const handleClick = useCallback(() => {
    onSelect(root)
  }, [onSelect, root])

  return (
    <motion.button
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={springPresets.snappy}
      onClick={handleClick}
      className="group flex w-full items-center justify-between rounded-lg px-4 py-3 transition-colors hover:bg-[var(--color-bg-elevated)]"
    >
      <span
        className="font-arabic text-xl text-[var(--color-text-primary)] transition-colors group-hover:text-[var(--color-accent-primary)]"
        lang="ar"
      >
        {root}
      </span>
      <span className="text-sm text-[var(--color-text-muted)] tabular-nums">
        {count.toLocaleString()}
      </span>
    </motion.button>
  )
})

function VirtualizedRootRow({
  index,
  style,
  roots,
  onSelect,
  ariaAttributes,
}: RowComponentProps<RootListData>) {
  const rootItem = roots[index]

  if (!rootItem) {
    return null
  }

  return (
    <div style={style} className="px-1" {...ariaAttributes}>
      <RootRow root={rootItem.root} count={rootItem.count} onSelect={onSelect} />
    </div>
  )
}

export function RootBrowser({ onRootSelect }: RootBrowserProps) {
  const t = useTranslations("KeywordSearch")
  const [roots, setRoots] = useState<RootListItem[]>([])
  const [totalCount, setTotalCount] = useState<number>(0)
  const [isLoading, setIsLoading] = useState(false)
  const [filterText, setFilterText] = useState("")
  const [sortBy, setSortBy] = useState<SortMode>("frequency")
  const listRef = useListRef(null)

  // Fetch all roots on mount
  useEffect(() => {
    const fetchAllRoots = async () => {
      setIsLoading(true)
      try {
        const allRoots: RootListItem[] = []
        let page = 1
        let hasMore = true

        while (hasMore) {
          const response = await listRootsApiSearchKeywordRootsGet({
            query: { page, per_page: 200 },
          })

          if (response.data) {
            allRoots.push(...(response.data.roots || []))
            hasMore = allRoots.length < (response.data.total || 0)
            page++
          } else {
            hasMore = false
          }
        }

        // Deduplicate roots by merging counts for identical root strings
        // (Arabic Unicode normalization can cause GROUP BY to return
        //  roots that are byte-different but render-identical)
        const rootMap = new Map<string, number>()
        for (const item of allRoots) {
          rootMap.set(item.root, (rootMap.get(item.root) || 0) + item.count)
        }
        const dedupedRoots: RootListItem[] = Array.from(rootMap.entries()).map(([root, count]) => ({
          root,
          count,
        }))

        setRoots(dedupedRoots)
        setTotalCount(dedupedRoots.length)
      } catch {
        toast.error(t("browser.loading"))
      } finally {
        setIsLoading(false)
      }
    }

    fetchAllRoots()
  }, [t])

  // Filter and sort roots
  const sortedRoots = useMemo(() => {
    // Filter by search text (supports Arabic and Latin)
    const filtered = filterText ? roots.filter((r) => r.root.includes(filterText)) : roots

    // Sort by selected mode
    return [...filtered].sort((a, b) => {
      if (sortBy === "frequency") {
        return b.count - a.count
      }
      return a.root.localeCompare(b.root, "ar")
    })
  }, [roots, filterText, sortBy])

  // Featured roots (top 20 most frequent)
  const featuredRoots = useMemo(() => {
    return [...roots].sort((a, b) => b.count - a.count).slice(0, 20)
  }, [roots])

  // Show featured roots initially, all roots when filtering/sorting
  const displayRoots = filterText || sortBy === "alphabetical" ? sortedRoots : featuredRoots

  const listData = useMemo<RootListData>(
    () => ({ roots: displayRoots, onSelect: onRootSelect }),
    [displayRoots, onRootSelect]
  )

  const listHeight = Math.min(ROOT_LIST_MAX_HEIGHT, displayRoots.length * ROOT_ROW_HEIGHT)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-[var(--color-text-primary)]">
          {totalCount > 0
            ? t("browser.totalRoots", { count: totalCount.toLocaleString() })
            : t("browser.arabicRoots")}
        </h2>
      </div>

      {/* Filter input */}
      <div className="relative">
        <Search className="absolute top-1/2 left-4 h-[18px] w-[18px] -translate-y-1/2 text-[var(--color-text-muted)]" />
        <input
          type="text"
          dir="auto"
          value={filterText}
          onChange={(e) => setFilterText(e.target.value)}
          placeholder={t("browser.searchPlaceholder")}
          disabled={isLoading}
          className={cn(
            "h-12 w-full rounded-xl bg-[var(--color-bg-surface)] pr-4 pl-12",
            "text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]",
            "border border-[var(--color-border-subtle)]",
            "focus:border-[var(--color-border-glow)] focus:outline-none",
            "text-[15px] transition-all duration-300",
            "disabled:cursor-not-allowed disabled:opacity-50"
          )}
        />
      </div>

      {/* Sort toggle */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setSortBy("frequency")}
          className={cn(
            "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
            sortBy === "frequency"
              ? "bg-indigo-500 text-white"
              : "bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
          )}
        >
          {t("browser.byFrequency")}
        </button>
        <button
          onClick={() => setSortBy("alphabetical")}
          className={cn(
            "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
            sortBy === "alphabetical"
              ? "bg-indigo-500 text-white"
              : "bg-[var(--color-bg-elevated)] text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
          )}
        >
          {t("browser.alphabetical")}
        </button>
      </div>

      {/* Section header */}
      {!filterText && sortBy === "frequency" && (
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-medium tracking-widest text-[var(--color-text-secondary)] uppercase">
            {t("browser.featuredRoots")}
          </h3>
          <div className="h-px flex-1 bg-[var(--color-border-subtle)]" />
          <span className="text-xs text-[var(--color-text-muted)]">◆</span>
        </div>
      )}

      {/* Loading skeleton */}
      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 10 }).map((_, i) => (
            <div
              key={`root-browser-skeleton-${i}`}
              className="flex items-center justify-between px-4 py-3"
            >
              <Skeleton className="h-6 w-24" />
              <Skeleton className="h-4 w-12" />
            </div>
          ))}
        </div>
      )}

      {/* Root list */}
      {!isLoading && displayRoots.length > 0 && (
        <div className="overflow-hidden rounded-xl border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/40">
          <List
            listRef={listRef}
            defaultHeight={ROOT_LIST_MAX_HEIGHT}
            overscanCount={ROOT_LIST_OVERSCAN}
            rowComponent={VirtualizedRootRow}
            rowCount={displayRoots.length}
            rowHeight={ROOT_ROW_HEIGHT}
            rowProps={listData}
            style={{ height: listHeight, width: "100%" }}
          />
        </div>
      )}

      {/* Empty state */}
      {!isLoading && displayRoots.length === 0 && (
        <div className="py-12 text-center">
          <p className="text-[var(--color-text-muted)]">
            {filterText ? t("browser.noRootsMatch") : t("browser.noRootsAvailable")}
          </p>
        </div>
      )}
    </div>
  )
}
