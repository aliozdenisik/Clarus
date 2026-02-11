"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { useQuery } from "@tanstack/react-query"
import { ChevronDown, ChevronRight, ExternalLink } from "lucide-react"
import { springPresets, tactileScale } from "@/lib/design-system"
import { GlowCard } from "@/components/ui/glow-card"
import { Skeleton } from "@/components/ui/skeleton"
import { getEtymologyApiEtymologyRootGet } from "@/lib/api/sdk.gen"
import { cn } from "@/lib/utils"

interface RichRootCardProps {
  root: string | null
  rootSource: string
  rootBuckwalter?: string | null
  query: string
  language?: "arabic" | "hebrew" | "greek"
}

export function RichRootCard({
  root,
  rootSource,
  rootBuckwalter,
  query,
  language = "arabic",
}: RichRootCardProps) {
  const [showAllForms, setShowAllForms] = useState(false)
  const isArabic = language === "arabic"

  const { data, isLoading, isError } = useQuery({
    queryKey: ["etymology", rootBuckwalter],
    queryFn: async () => {
      if (!rootBuckwalter) throw new Error("No root available")
      const response = await getEtymologyApiEtymologyRootGet({
        path: { root: rootBuckwalter },
      })
      if (response.error) {
        const errorMsg =
          typeof response.error.detail === "string"
            ? response.error.detail
            : "Failed to fetch etymology"
        throw new Error(errorMsg)
      }
      return response.data
    },
    enabled: !!rootBuckwalter && rootSource !== "not_found" && isArabic,
    staleTime: Infinity,
  })

  if (!isArabic) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={springPresets.fluid}
        data-testid="rich-root-card"
      >
        <GlowCard className="p-6">
          <div className="flex flex-col items-center gap-3">
            {root ? (
              <>
                <p
                  lang={language === "greek" ? "el" : "he"}
                  className={`${language === "greek" ? "font-greek" : "font-hebrew"} text-center text-4xl font-bold text-[var(--color-text-primary)]`}
                  dir={language === "greek" ? "ltr" : "rtl"}
                >
                  {language === "greek" ? root : <bdi>{root}</bdi>}
                </p>
                {rootBuckwalter && (
                  <p className="text-center text-sm tracking-wide text-[var(--color-text-muted)]">
                    {rootBuckwalter}
                  </p>
                )}
              </>
            ) : (
              <p className="text-center text-sm text-[var(--color-text-muted)]">
                No root found for this query
              </p>
            )}
          </div>
        </GlowCard>
      </motion.div>
    )
  }

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={springPresets.fluid}
        data-testid="rich-root-card"
      >
        <GlowCard className="p-6">
          <div className="space-y-4">
            <div className="flex flex-col items-center gap-3">
              <Skeleton className="h-12 w-32" />
              <Skeleton className="h-4 w-24" />
            </div>
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        </GlowCard>
      </motion.div>
    )
  }

  if (isError || !data) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={springPresets.fluid}
        data-testid="rich-root-card"
      >
        <GlowCard className="p-6">
          <div className="flex flex-col items-center gap-3">
            {root ? (
              <>
                <p
                  lang="ar"
                  className="font-arabic text-center text-4xl font-bold text-[var(--color-text-primary)]"
                  dir="rtl"
                >
                  <bdi>{root}</bdi>
                </p>
                {rootBuckwalter && (
                  <p className="text-center text-sm tracking-wide text-[var(--color-text-muted)]">
                    {rootBuckwalter}
                  </p>
                )}
              </>
            ) : (
              <p className="text-center text-sm text-[var(--color-text-muted)]">
                No root found for this query
              </p>
            )}
          </div>
        </GlowCard>
      </motion.div>
    )
  }

  const morphologicalForms = data.morphological_forms || []
  const displayedForms = showAllForms ? morphologicalForms : morphologicalForms.slice(0, 5)
  const hasMoreForms = morphologicalForms.length > 5

  const sourceColor =
    data.source === "lane"
      ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
      : "bg-blue-500/20 text-blue-300 border-blue-500/30"

  const confidenceColor =
    data.confidence === "high"
      ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
      : data.confidence === "medium"
        ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
        : "bg-red-500/20 text-red-300 border-red-500/30"

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={springPresets.fluid}
      data-testid="rich-root-card"
    >
      <GlowCard className="p-6">
        <div className="space-y-6">
          <div className="flex flex-col items-center gap-3">
            <p
              lang="ar"
              className="font-arabic text-center text-4xl font-bold text-[var(--color-text-primary)]"
              dir="rtl"
            >
              <bdi>{data.root}</bdi>
            </p>
            <p className="text-center text-sm tracking-wide text-[var(--color-text-muted)]">
              {data.root_buckwalter}
            </p>

            <div className="flex flex-wrap items-center justify-center gap-2">
              {data.quran_frequency !== undefined && (
                <span
                  className="rounded border border-indigo-500/30 bg-indigo-500/20 px-2 py-0.5 text-xs text-indigo-300"
                  data-testid="root-frequency"
                >
                  {data.quran_frequency} kullanım
                </span>
              )}
              <span className={cn("rounded border px-2 py-0.5 text-xs", sourceColor)}>
                {data.source === "lane" ? "Lane's Lexicon" : "Korpus"}
              </span>
              <span
                className={cn("rounded border px-2 py-0.5 text-xs capitalize", confidenceColor)}
              >
                {data.confidence}
              </span>
            </div>
          </div>

          {data.definition_tr && (
            <div className="space-y-2" data-testid="root-definition-tr">
              <h4 className="text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
                Türkçe Tanım
              </h4>
              <p className="text-sm leading-relaxed text-[var(--color-text-secondary)]">
                {data.definition_tr}
              </p>
            </div>
          )}

          {data.definition_en && (
            <div className="space-y-2" data-testid="root-definition-en">
              <h4 className="text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
                İngilizce Tanım
              </h4>
              <p className="text-sm leading-relaxed text-[var(--color-text-secondary)]">
                {data.definition_en}
              </p>
            </div>
          )}

          {!data.definition_tr && !data.definition_en && (
            <div className="rounded-md border border-amber-500/30 bg-amber-500/10 p-3">
              <p className="text-xs text-amber-300">
                Tanım mevcut değil. Daha fazla bilgi için kök kullanımlarına bakın.
              </p>
            </div>
          )}

          {morphologicalForms.length > 0 && (
            <div className="space-y-3" data-testid="morphological-forms">
              <div className="flex items-center justify-between">
                <h4 className="text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
                  Morfolojik Formlar
                </h4>
                {hasMoreForms && (
                  <motion.button
                    onClick={() => setShowAllForms(!showAllForms)}
                    whileTap={tactileScale.press}
                    className="flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300"
                  >
                    {showAllForms ? (
                      <>
                        <ChevronDown className="h-3 w-3" />
                        Daha az göster
                      </>
                    ) : (
                      <>
                        <ChevronRight className="h-3 w-3" />
                        Tümünü göster ({morphologicalForms.length})
                      </>
                    )}
                  </motion.button>
                )}
              </div>
              <div className="space-y-2">
                {displayedForms.map((form, idx) => (
                  <motion.div
                    key={`${form.form_arabic}-${idx}`}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ ...springPresets.snappy, delay: idx * 0.05 }}
                    className="flex items-baseline gap-2 rounded-md bg-[var(--color-bg-elevated)]/50 p-2"
                  >
                    {form.form_arabic && (
                      <span
                        lang="ar"
                        className="font-arabic text-sm text-[var(--color-text-primary)]"
                        dir="rtl"
                      >
                        <bdi>{form.form_arabic}</bdi>
                      </span>
                    )}
                    {form.form_category && (
                      <span className="text-xs text-[var(--color-text-muted)]">
                        ({form.form_category})
                      </span>
                    )}
                    {form.example_word && (
                      <span
                        lang="ar"
                        className="font-arabic ml-auto text-xs text-[var(--color-text-secondary)]"
                        dir="rtl"
                      >
                        <bdi>{form.example_word}</bdi>
                      </span>
                    )}
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          <motion.a
            href={`/keyword-search?q=${encodeURIComponent(query)}`}
            whileHover={tactileScale.hover}
            whileTap={tactileScale.press}
            className="flex items-center justify-center gap-2 rounded-md bg-indigo-500/20 px-4 py-2 text-sm font-medium text-indigo-300 transition-colors hover:bg-indigo-500/30"
          >
            Tüm kullanımları gör
            <ExternalLink className="h-3.5 w-3.5" />
          </motion.a>
        </div>
      </GlowCard>
    </motion.div>
  )
}
