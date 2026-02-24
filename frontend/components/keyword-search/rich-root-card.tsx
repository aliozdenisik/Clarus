"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { useQuery } from "@tanstack/react-query"
import Link from "next/link"
import { ChevronDown, ChevronRight, ExternalLink, BookOpen } from "lucide-react"
import { springPresets, tactileScale } from "@/lib/design-system"
import { MagicCard } from "@/components/ui/magic-card"
import { Skeleton } from "@/components/ui/skeleton"
import { getEtymologyApiEtymologyRootGet } from "@/lib/api/sdk.gen"
import { cn } from "@/lib/utils"
import { useTranslations } from "next-intl"
import { UpgradeGate } from "@/components/keyword-search/upgrade-gate"

interface RichRootCardProps {
  root: string | null
  rootSource: string
  rootBuckwalter?: string | null
  query: string
  language?: "arabic" | "hebrew" | "greek"
  showEtymology?: boolean
}

export function RichRootCard({
  root,
  rootSource,
  rootBuckwalter,
  query,
  language = "arabic",
  showEtymology = true,
}: RichRootCardProps) {
  const t = useTranslations("KeywordSearch")
  const [showAllForms, setShowAllForms] = useState(false)
  const isArabic = language === "arabic"

  const { data, isLoading, isError } = useQuery({
    queryKey: ["etymology", rootBuckwalter],
    queryFn: async () => {
      if (!rootBuckwalter) throw new Error(t("noResults"))
      const response = await getEtymologyApiEtymologyRootGet({
        path: { root: rootBuckwalter },
      })
      if (response.error) {
        const errorMsg =
          typeof response.error.detail === "string" ? response.error.detail : t("searchFailed")
        throw new Error(errorMsg)
      }
      return response.data
    },
    enabled: !!rootBuckwalter && rootSource !== "not_found" && isArabic,
    staleTime: Infinity,
    retry: false,
  })

  if (!isArabic) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={springPresets.fluid}
        data-testid="rich-root-card"
      >
        <MagicCard className="p-8">
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
                {t("noRootFound", { query })}
              </p>
            )}
          </div>
        </MagicCard>
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
        <MagicCard className="p-8">
          <div className="space-y-4">
            <div className="flex flex-col items-center gap-3">
              <Skeleton className="h-12 w-32" />
              <Skeleton className="h-4 w-24" />
            </div>
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        </MagicCard>
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
        <MagicCard className="p-8">
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
                {t("noRootFound", { query })}
              </p>
            )}
          </div>
        </MagicCard>
      </motion.div>
    )
  }

  const morphologicalForms = data.morphological_forms || []
  const displayedForms = showAllForms ? morphologicalForms : morphologicalForms.slice(0, 5)
  const hasMoreForms = morphologicalForms.length > 5

  const sourceColor =
    data.source === "lane"
      ? "border-indigo-500/30 bg-indigo-500/20 text-indigo-200"
      : "border-zinc-700 bg-zinc-800/70 text-zinc-300"

  const confidenceColor =
    data.confidence === "high"
      ? "border-indigo-500/30 bg-indigo-500/20 text-indigo-200"
      : data.confidence === "medium"
        ? "border-indigo-500/25 bg-indigo-500/15 text-indigo-200"
        : "border-zinc-700 bg-zinc-800/70 text-zinc-300"

  const actionLinkClassName =
    "group flex w-full items-center justify-center gap-2 rounded-md border border-[var(--color-border-subtle)] bg-[var(--color-bg-elevated)]/40 px-3 py-2 text-xs font-medium text-[var(--color-text-secondary)] transition-colors hover:border-[var(--color-border-glow)] hover:text-[var(--color-text-primary)]"

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={springPresets.fluid}
      data-testid="rich-root-card"
    >
      <MagicCard className="p-8">
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
                  {data.quran_frequency} {t("stats.occurrences")}
                </span>
              )}
              <span className={cn("rounded border px-2 py-0.5 text-xs", sourceColor)}>
                {data.source === "lane" ? t("rootInfo.definition") : t("rootInfo.title")}
              </span>
              <span
                className={cn("rounded border px-2 py-0.5 text-xs capitalize", confidenceColor)}
              >
                {data.confidence}
              </span>
            </div>
          </div>

          {showEtymology ? (
            <>
              {(data.summary_tr || data.summary_en) && (
                <div className="space-y-2" data-testid="root-summary">
                  <h4 className="text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
                    {t("rootInfo.title")}
                  </h4>
                  <p className="text-center text-sm leading-relaxed text-[var(--color-text-secondary)]">
                    {data.summary_tr || data.summary_en}
                  </p>
                </div>
              )}
              {!data.summary_tr && !data.summary_en && data.definition_tr && (
                <div className="space-y-2" data-testid="root-definition-tr">
                  <h4 className="text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
                    {t("rootInfo.definition")}
                  </h4>
                  <p className="line-clamp-3 text-center text-sm leading-relaxed text-[var(--color-text-secondary)]">
                    {data.definition_tr}
                  </p>
                </div>
              )}
              {!data.summary_tr &&
                !data.summary_en &&
                !data.definition_tr &&
                !data.definition_en && (
                  <div className="rounded-md border border-amber-500/30 bg-amber-500/10 p-3">
                    <p className="text-xs text-amber-300">{t("translationNotAvailable")}</p>
                  </div>
                )}
              {morphologicalForms.length > 0 && (
                <div className="space-y-3" data-testid="morphological-forms">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-semibold tracking-wide text-[var(--color-text-muted)] uppercase">
                      {t("rootInfo.forms")}
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
                            {t("pagination.previous")}
                          </>
                        ) : (
                          <>
                            <ChevronRight className="h-3 w-3" />
                            {t("chart.showAll", {
                              count: morphologicalForms.length,
                              type: t("derivedWords.title"),
                            })}
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
                        className="flex items-baseline gap-3 rounded-md border border-[var(--color-border-subtle)] bg-[var(--color-bg-elevated)]/40 px-3 py-3"
                      >
                        {form.form_arabic && (
                          <span
                            lang="ar"
                            className="font-arabic text-base leading-loose text-[var(--color-text-primary)]"
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
                            className="font-arabic ml-auto pr-1 text-sm leading-loose text-[var(--color-text-secondary)]"
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
              <div className="space-y-2 pt-1">
                {data.root_buckwalter && (
                  <Link
                    href={`/keyword-search/root/${data.root_buckwalter}`}
                    className={actionLinkClassName}
                    data-testid="root-detail-link"
                  >
                    <BookOpen className="h-3.5 w-3.5" />
                    <span>{t("accuracy.verificationTitle")}</span>
                  </Link>
                )}

                {data.root_buckwalter && (
                  <Link
                    href={`/keyword-search/root/${data.root_buckwalter}`}
                    className={actionLinkClassName}
                    data-testid="root-dictionary-link"
                  >
                    {t("rootInfo.dictionaryMeanings")}
                    <ExternalLink className="h-3.5 w-3.5" />
                  </Link>
                )}
              </div>
            </>
          ) : (
            <UpgradeGate locked>
              <div className="h-32 rounded-md bg-zinc-800/50" />
            </UpgradeGate>
          )}
        </div>
      </MagicCard>
    </motion.div>
  )
}
