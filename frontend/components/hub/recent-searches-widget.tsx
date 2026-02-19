"use client"

import { useState, useEffect } from "react"
import { useTranslations } from "next-intl"
import { useSession } from "@/lib/auth-client"
import { MagicCard } from "@/components/ui/magic-card"
import { Skeleton } from "@/components/ui/skeleton"
import { Search } from "lucide-react"
import { formatDistanceToNow } from "date-fns/formatDistanceToNow"
import Link from "next/link"
import { cn } from "@/lib/utils"
import { getSearchHistoryApiSearchHistoryGet } from "@/lib/api/sdk.gen"

interface HistoryItem {
  id: number
  query: string
  search_type: string
  created_at: string
  result_count: number | null
}

const SKELETON_KEYS = [
  "recent-search-skeleton-a",
  "recent-search-skeleton-b",
  "recent-search-skeleton-c",
  "recent-search-skeleton-d",
  "recent-search-skeleton-e",
]

function getSearchTypeDot(searchType: string): { color: string; label: string } {
  if (searchType.includes("quran")) {
    return { color: "bg-emerald-500", label: "Quran" }
  }
  if (searchType.includes("compare")) {
    return { color: "bg-violet-500", label: "Compare" }
  }
  return { color: "bg-amber-500", label: "Bible" }
}

function getItemUrl(item: HistoryItem): string {
  const q = encodeURIComponent(item.query)
  if (item.search_type.includes("quran")) return `/search?source=quran&q=${q}`
  if (item.search_type.includes("compare")) return `/compare?q=${q}`
  if (item.search_type.includes("ot")) return `/search?source=ot&q=${q}`
  if (item.search_type.includes("nt")) return `/search?source=nt&q=${q}`
  if (item.search_type.includes("apocrypha")) return `/search?source=apocrypha&q=${q}`
  return `/search?q=${q}`
}

export function RecentSearchesWidget() {
  const t = useTranslations("Hub")
  const { data: session } = useSession()
  const [loading, setLoading] = useState(true)
  const [items, setItems] = useState<HistoryItem[]>([])

  useEffect(() => {
    if (!session?.user) {
      setLoading(false)
      return
    }

    let cancelled = false

    async function fetchRecent() {
      setLoading(true)
      try {
        const response = await getSearchHistoryApiSearchHistoryGet({
          query: { page: 1, limit: 5 },
        })

        if (cancelled) return

        if (response.data) {
          const body = response.data as {
            success: boolean
            data: HistoryItem[]
          }
          setItems((body.data ?? []).slice(0, 5))
        }
      } catch {
        if (!cancelled) setItems([])
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    fetchRecent()

    return () => {
      cancelled = true
    }
  }, [session?.user])

  return (
    <MagicCard className="rounded-xl border border-white/[0.06] p-4 md:p-5">
      <p className="text-muted-foreground mb-4 text-xs font-medium tracking-wider uppercase">
        {t("recentSearches")}
      </p>

      {loading && (
        <ul aria-label="Loading recent searches">
          {SKELETON_KEYS.map((key) => (
            <li
              key={key}
              className="flex min-h-[44px] items-center gap-3 border-b border-white/[0.04] py-3 last:border-0"
            >
              <Skeleton className="h-2 w-2 shrink-0 rounded-full" />
              <Skeleton className="h-4 w-40" />
              <Skeleton className="ml-auto h-3 w-20" />
            </li>
          ))}
        </ul>
      )}

      {!loading && items.length === 0 && (
        <div className="flex flex-col items-center justify-center gap-3 py-6 text-center">
          <Search className="text-muted-foreground/40 h-8 w-8" aria-hidden="true" />
          <p className="text-muted-foreground text-sm">{t("noRecentSearches")}</p>
          <Link
            href="/search"
            className="text-muted-foreground hover:text-foreground text-xs underline underline-offset-2 transition-colors"
          >
            {t("searchNow")}
          </Link>
        </div>
      )}

      {!loading && items.length > 0 && (
        <ul>
          {items.map((item) => {
            const dot = getSearchTypeDot(item.search_type)
            const url = getItemUrl(item)

            return (
              <li key={`${item.id}-${item.created_at}`}>
                <Link
                  href={url}
                  className={cn(
                    "flex min-h-[44px] items-center gap-3 py-3",
                    "border-b border-white/[0.04] last:border-0",
                    "rounded-sm transition-colors hover:bg-white/[0.03]",
                    "-mx-1 px-1"
                  )}
                >
                  <span
                    className={cn("h-2 w-2 shrink-0 rounded-full", dot.color)}
                    title={dot.label}
                  />

                  <span className="min-w-0 flex-1 truncate text-sm font-medium">{item.query}</span>

                  <span className="text-muted-foreground shrink-0 font-mono text-xs">
                    {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                  </span>
                </Link>
              </li>
            )
          })}
        </ul>
      )}

      {!loading && (
        <div className="mt-4 flex justify-end">
          <Link
            href="/history"
            className="text-muted-foreground hover:text-foreground text-xs transition-colors"
          >
            {t("viewAll")} →
          </Link>
        </div>
      )}
    </MagicCard>
  )
}
