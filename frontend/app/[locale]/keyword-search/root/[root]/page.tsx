"use client"

import { useEffect, useRef, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowLeft } from "lucide-react"
import { springPresets } from "@/lib/design-system"
import { MagicCard } from "@/components/ui/magic-card"
import { Skeleton } from "@/components/ui/skeleton"
import { logger } from "@/lib/logger"
import { API_BASE } from "@/lib/config"
import { cn } from "@/lib/utils"
import { getAbbreviationsByCategory } from "@/lib/constants/lane-abbreviations"
import { formatLaneDefinition } from "@/lib/utils/format-lane-definition"

interface EtymologyData {
  id: number
  root: string
  root_buckwalter: string
  definition_en: string | null
  definition_tr: string | null
  summary_tr: string | null
  summary_en: string | null
  semantic_field: string | null
  morphological_forms: MorphForm[]
  related_roots: RelatedRoot[]
  quran_frequency: number
  source: string
  lane_match_type: string | null
  lane_volume: number | null
  confidence: string
  keyword_search_url: string
}

interface MorphForm {
  form_pattern: string | null
  form_arabic: string | null
  form_name: string | null
  form_category: string | null
  example_word: string | null
  occurrences: number | null
}

interface RelatedRoot {
  root: string
  root_buckwalter: string | null
  meaning_hint: string | null
}

export default function RootDetailPage() {
  const params = useParams()
  const rootParam = params.root as string

  const [data, setData] = useState<EtymologyData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const controllerRef = useRef<AbortController | null>(null)

  useEffect(() => {
    if (!rootParam) return

    controllerRef.current?.abort()
    const controller = new AbortController()
    controllerRef.current = controller

    const fetchData = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const res = await fetch(`${API_BASE}/api/etymology/${encodeURIComponent(rootParam)}`, {
          signal: controller.signal,
        })
        if (!res.ok) {
          if (res.status === 404) {
            setError("Kök bulunamadı")
          } else {
            setError("Veri yüklenirken hata oluştu")
          }
          return
        }
        const json = await res.json()
        setData(json)
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") return
        logger.error(
          "Failed to fetch etymology",
          err instanceof Error ? err : new Error(String(err))
        )
        setError("Bağlantı hatası")
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      }
    }

    fetchData()
    return () => controller.abort()
  }, [rootParam])

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl space-y-6 px-4 py-12">
        <Skeleton className="h-6 w-40" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[var(--color-bg-app)]">
        <p className="text-lg text-zinc-400">{error}</p>
        <Link href="/keyword-search" className="text-sm text-indigo-400 hover:text-indigo-300">
          ← Kelime Aramasına Dön
        </Link>
      </div>
    )
  }

  if (!data) return null

  const sourceColor =
    data.source === "lane"
      ? "border-emerald-500/30 bg-emerald-500/20 text-emerald-300"
      : "border-amber-500/30 bg-amber-500/20 text-amber-300"

  const confidenceColor =
    data.confidence === "high"
      ? "border-emerald-500/30 bg-emerald-500/20 text-emerald-300"
      : data.confidence === "medium"
        ? "border-amber-500/30 bg-amber-500/20 text-amber-300"
        : "border-zinc-500/30 bg-zinc-500/20 text-zinc-300"

  return (
    <div className="mx-auto max-w-6xl space-y-8 px-4 py-12">
      <div className="mx-auto max-w-3xl">
        <Link
          href="/keyword-search"
          className="inline-flex items-center gap-2 text-sm text-zinc-400 transition-colors hover:text-zinc-200"
          data-testid="back-link"
        >
          <ArrowLeft className="h-4 w-4" />
          Kelime Aramasına Dön
        </Link>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={springPresets.fluid}
        className="mx-auto max-w-3xl"
      >
        <MagicCard className="space-y-6 p-8 rounded-lg border border-[var(--color-border-subtle)]" gradientSize={200} gradientColor="#1a1a2e" gradientFrom="#7c3aed" gradientTo="#4f46e5">
          <div className="space-y-3 text-center">
            <h1
              lang="ar"
              className="font-arabic text-5xl font-bold text-[var(--color-text-primary)]"
              data-testid="root-arabic"
            >
              {data.root}
            </h1>
            <p className="text-lg text-[var(--color-text-muted)]" data-testid="root-buckwalter">
              {data.root_buckwalter}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-2">
              <span className="rounded border border-indigo-500/30 bg-indigo-500/20 px-2 py-0.5 text-xs text-indigo-300">
                {data.quran_frequency} kullanım
              </span>
              <span className={cn("rounded border px-2 py-0.5 text-xs", sourceColor)}>
                {data.source === "lane" ? "Lane's Lexicon" : "Korpus"}
              </span>
              <span
                className={cn("rounded border px-2 py-0.5 text-xs capitalize", confidenceColor)}
              >
                {data.confidence}
              </span>
              {data.semantic_field && (
                <span className="rounded border border-purple-500/30 bg-purple-500/20 px-2 py-0.5 text-xs text-purple-300">
                  {data.semantic_field}
                </span>
              )}
            </div>
          </div>
        </MagicCard>
      </motion.div>

      {data.definition_tr && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springPresets.fluid, delay: 0.1 }}
        >
          <MagicCard className="space-y-3 p-6 rounded-lg border border-[var(--color-border-subtle)]" data-testid="definition-tr-section" gradientSize={200} gradientColor="#1a1a2e" gradientFrom="#7c3aed" gradientTo="#4f46e5">
            <h2 className="text-sm font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
              Lane&apos;s Lexicon &mdash; Akademik Türkçe Tercüme
            </h2>
            <p className="text-sm leading-relaxed whitespace-pre-line text-zinc-200">
              {formatLaneDefinition(data.definition_tr)}
            </p>
            <p className="mt-2 text-[10px] leading-relaxed text-zinc-600">
              Bu tercüme, orijinal İngilizce Lane&apos;s Lexicon metninden yapay zeka (LLM)
              aracılığıyla üretilmiştir. Akademik çalışmalarda orijinal İngilizce metni referans
              almanız önerilir.
            </p>
          </MagicCard>
        </motion.div>
      )}

      {data.definition_en && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springPresets.fluid, delay: 0.2 }}
        >
          <div className="grid gap-4 lg:grid-cols-[240px_1fr]" data-testid="definition-en-section">
            <aside
              className="top-6 self-start rounded-lg border border-zinc-800/60 bg-zinc-900/40 p-3 lg:sticky"
              data-testid="legend-en-panel"
            >
              <h3 className="mb-3 text-[10px] font-semibold tracking-widest text-zinc-500 uppercase">
                Abbreviations
              </h3>
              <div className="space-y-3">
                {getAbbreviationsByCategory("en").map((group) => (
                  <div key={group.category}>
                    <p className="mb-1 text-[9px] font-medium tracking-wider text-indigo-400/70 uppercase">
                      {group.label}
                    </p>
                    {group.items.map((item) => (
                      <div
                        key={item.abbreviation}
                        className="flex items-baseline gap-2 py-[2px] text-[11px]"
                      >
                        <span className="w-14 shrink-0 font-mono font-semibold text-amber-400/80">
                          {item.abbreviation}
                        </span>
                        <span className="leading-tight text-zinc-400">{item.meaning_en}</span>
                      </div>
                    ))}
                  </div>
                ))}
              </div>
            </aside>
            <MagicCard className="space-y-3 p-6 rounded-lg border border-[var(--color-border-subtle)]" gradientSize={200} gradientColor="#1a1a2e" gradientFrom="#7c3aed" gradientTo="#4f46e5">
              <h2 className="text-sm font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
                Lane&apos;s Lexicon &mdash; Original English
              </h2>
              <p className="text-sm leading-relaxed whitespace-pre-line text-zinc-200">
                {formatLaneDefinition(data.definition_en)}
              </p>
            </MagicCard>
          </div>
        </motion.div>
      )}

      {data.morphological_forms.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springPresets.fluid, delay: 0.3 }}
          className="mx-auto max-w-3xl"
        >
          <MagicCard className="space-y-4 p-6 rounded-lg border border-[var(--color-border-subtle)]" data-testid="morphological-section" gradientSize={200} gradientColor="#1a1a2e" gradientFrom="#7c3aed" gradientTo="#4f46e5">
            <h2 className="text-sm font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
              Morfolojik Formlar ({data.morphological_forms.length})
            </h2>
            <div className="space-y-2">
              {data.morphological_forms.map((form, idx) => (
                <div
                  key={`${form.form_pattern || ""}-${form.form_arabic || ""}-${idx}`}
                  className="flex items-center justify-between rounded-md border border-zinc-800 bg-zinc-900/50 px-3 py-2"
                >
                  <div className="flex items-center gap-3">
                    {form.form_arabic && (
                      <span
                        lang="ar"
                        className="font-arabic text-base text-[var(--color-text-primary)]"
                      >
                        {form.form_arabic}
                      </span>
                    )}
                    <div className="flex flex-col">
                      {form.form_pattern && (
                        <span className="text-xs text-zinc-400">{form.form_pattern}</span>
                      )}
                      {form.form_name && (
                        <span className="text-xs text-zinc-500">{form.form_name}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {form.form_category && (
                      <span className="rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] text-zinc-400">
                        {form.form_category}
                      </span>
                    )}
                    {form.occurrences != null && (
                      <span className="text-xs text-zinc-500">{form.occurrences}×</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </MagicCard>
        </motion.div>
      )}

      {data.related_roots.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ ...springPresets.fluid, delay: 0.4 }}
          className="mx-auto max-w-3xl"
        >
          <MagicCard className="space-y-4 p-6 rounded-lg border border-[var(--color-border-subtle)]" data-testid="related-roots-section" gradientSize={200} gradientColor="#1a1a2e" gradientFrom="#7c3aed" gradientTo="#4f46e5">
            <h2 className="text-sm font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
              İlgili Kökler ({data.related_roots.length})
            </h2>
            <div className="flex flex-wrap gap-2">
              {data.related_roots.map((rel) => (
                <Link
                  key={rel.root}
                  href={`/keyword-search/root/${rel.root_buckwalter || rel.root}`}
                  className="group rounded-md border border-zinc-800 bg-zinc-900/50 px-3 py-1.5 transition-colors hover:border-indigo-500/30 hover:bg-indigo-500/5"
                >
                  <span
                    lang="ar"
                    className="font-arabic text-sm text-[var(--color-text-primary)] group-hover:text-indigo-300"
                  >
                    {rel.root}
                  </span>
                  {rel.meaning_hint && (
                    <span className="ml-2 text-xs text-zinc-500">{rel.meaning_hint}</span>
                  )}
                </Link>
              ))}
            </div>
          </MagicCard>
        </motion.div>
      )}
    </div>
  )
}
