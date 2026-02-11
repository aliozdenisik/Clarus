"use client"

import React, { useState } from "react"
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover"
import { motion, AnimatePresence } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { useQuery } from "@tanstack/react-query"
import { getEtymologyApiEtymologyRootGet } from "@/lib/api"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { ExternalLink, ChevronDown, ChevronUp, AlertCircle } from "lucide-react"
import { cn } from "@/lib/utils"
import Link from "next/link"

interface EtymologyPopupProps {
  word?: {
    token?: string | null
    root?: string | null
    root_buckwalter?: string | null
    has_etymology: boolean
  }
  root?: string
  rootBuckwalter?: string
  open?: boolean
  onOpenChange?: (open: boolean) => void
  children: React.ReactNode
}

export function EtymologyPopup({
  word,
  root: rootProp,
  rootBuckwalter: rootBuckwalterProp,
  open: openProp,
  onOpenChange,
  children,
}: EtymologyPopupProps) {
  const [isOpenInternal, setIsOpenInternal] = useState(false)
  const [showAllForms, setShowAllForms] = useState(false)

  const isControlled = openProp !== undefined
  const isOpen = isControlled ? openProp : isOpenInternal

  const setIsOpen = (value: boolean) => {
    if (!isControlled) {
      setIsOpenInternal(value)
    }
    onOpenChange?.(value)
  }

  const root = rootProp || word?.root
  const rootBuckwalter = rootBuckwalterProp || word?.root_buckwalter
  const hasEtymology = word?.has_etymology ?? (!!root || !!rootBuckwalter)

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["etymology", root],
    queryFn: async () => {
      if (!root) throw new Error("No root available")
      const response = await getEtymologyApiEtymologyRootGet({
        path: { root: root },
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
    enabled: isOpen && !!root && hasEtymology,
    staleTime: Infinity, // Etymology data never changes
  })

  if (!hasEtymology) {
    return <>{children}</>
  }

  const morphologicalForms = data?.morphological_forms || []
  const displayedForms = showAllForms ? morphologicalForms : morphologicalForms.slice(0, 5)
  const hasMoreForms = morphologicalForms.length > 5

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>{children}</PopoverTrigger>
      <PopoverContent
        side="top"
        sideOffset={8}
        align="center"
        className="z-50 max-w-[400px] min-w-[280px] p-0"
      >
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={springPresets.snappy}
              className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-elevated)] shadow-lg"
            >
              {/* Loading State */}
              {isLoading && (
                <div className="space-y-3 p-4">
                  <Skeleton className="h-8 w-32" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                  <div className="space-y-2 pt-2">
                    <Skeleton className="h-3 w-full" />
                    <Skeleton className="h-3 w-full" />
                    <Skeleton className="h-3 w-2/3" />
                  </div>
                </div>
              )}

              {/* Error State */}
              {isError && !isLoading && (
                <div className="space-y-3 p-4">
                  <div className="flex items-center gap-2 text-red-400">
                    <AlertCircle className="h-5 w-5" />
                    <span className="text-sm font-medium">Etimoloji bilgisi yüklenemedi</span>
                  </div>
                  <Button variant="outline" size="sm" onClick={() => refetch()} className="w-full">
                    Tekrar Dene
                  </Button>
                </div>
              )}

              {/* No Root State */}
              {!root && !isLoading && (
                <div className="p-4">
                  <p className="text-sm text-[var(--color-text-muted)]">
                    Bu kelime için kök bilgisi mevcut değil
                  </p>
                </div>
              )}

              {/* Success State */}
              {data && !isLoading && !isError && (
                <div className="space-y-4 p-4">
                  {/* Header: Root Arabic + Buckwalter */}
                  <div className="flex items-center justify-between border-b border-[var(--color-border-subtle)] pb-3">
                    <div className="flex flex-col gap-1">
                      <p
                        lang="ar"
                        className="font-arabic text-2xl font-bold text-[var(--color-text-primary)]"
                        dir="rtl"
                      >
                        <bdi>{data.root}</bdi>
                      </p>
                      <p className="text-sm tracking-wide text-[var(--color-text-muted)]">
                        ({data.root_buckwalter})
                      </p>
                    </div>
                    {/* Confidence Badge */}
                    <span
                      className={cn(
                        "rounded-full px-2.5 py-1 text-xs font-medium",
                        data.confidence === "high" &&
                          "border border-green-500/30 bg-green-500/20 text-green-300",
                        data.confidence === "medium" &&
                          "border border-yellow-500/30 bg-yellow-500/20 text-yellow-300",
                        data.confidence === "low" &&
                          "border border-red-500/30 bg-red-500/20 text-red-300"
                      )}
                    >
                      {data.confidence === "high" && "Yüksek"}
                      {data.confidence === "medium" && "Orta"}
                      {data.confidence === "low" && "Düşük"}
                    </span>
                  </div>

                  {/* Definitions */}
                  <div className="space-y-2">
                    {data.definition_tr && (
                      <p className="text-sm text-[var(--color-text-primary)]">
                        <span className="font-medium text-[var(--color-text-muted)]">Anlam:</span>{" "}
                        {data.definition_tr}
                      </p>
                    )}
                    {data.definition_en && (
                      <p className="text-sm text-[var(--color-text-secondary)]">
                        <span className="font-medium text-[var(--color-text-muted)]">English:</span>{" "}
                        {data.definition_en}
                      </p>
                    )}
                  </div>

                  {/* Morphological Forms */}
                  {morphologicalForms.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-[var(--color-text-primary)]">
                          Morfolojik Formlar:
                        </span>
                        {hasMoreForms && (
                          <button
                            type="button"
                            onClick={() => setShowAllForms(!showAllForms)}
                            className="flex items-center gap-1 text-xs text-[var(--color-accent-primary)] transition-colors duration-200 hover:text-[var(--color-accent-hover)]"
                          >
                            {showAllForms ? (
                              <>
                                <span>Daha Az</span>
                                <ChevronUp className="h-3 w-3" />
                              </>
                            ) : (
                              <>
                                <span>Tümünü Gör ({morphologicalForms.length})</span>
                                <ChevronDown className="h-3 w-3" />
                              </>
                            )}
                          </button>
                        )}
                      </div>
                      <ul className="space-y-1.5">
                        {displayedForms.map((form, idx) => (
                          <li
                            key={`${form.form_pattern}-${idx}`}
                            className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]"
                          >
                            {form.form_arabic && (
                              <span lang="ar" className="font-arabic text-base" dir="rtl">
                                <bdi>{form.form_arabic}</bdi>
                              </span>
                            )}
                            {form.form_pattern && (
                              <span className="text-xs text-[var(--color-text-muted)]">
                                ({form.form_pattern})
                              </span>
                            )}
                            {form.occurrences !== null && form.occurrences !== undefined && (
                              <span className="ml-auto text-xs text-[var(--color-text-muted)]">
                                {form.occurrences} kez
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Frequency & Source */}
                  <div className="space-y-1 border-t border-[var(--color-border-subtle)] pt-3 text-sm">
                    {data.quran_frequency !== null && data.quran_frequency !== undefined && (
                      <p className="text-[var(--color-text-secondary)]">
                        <span className="font-medium text-[var(--color-text-muted)]">
                          Kuran&apos;da:
                        </span>{" "}
                        {data.quran_frequency} kez
                      </p>
                    )}
                    {data.source && (
                      <p className="text-[var(--color-text-secondary)]">
                        <span className="font-medium text-[var(--color-text-muted)]">Kaynak:</span>{" "}
                        {data.source === "lane" && "Lane's Lexicon"}
                        {data.source === "corpus_only" && "Quranic Arabic Corpus"}
                        {data.source !== "lane" && data.source !== "corpus_only" && data.source}
                        {data.lane_match_type === "exact" && " ✓"}
                      </p>
                    )}
                  </div>

                  {/* Keyword Search Link */}
                  {data.root_buckwalter && (
                    <Link
                      href={`/keyword-search?q=${encodeURIComponent(data.root_buckwalter)}`}
                      className="flex items-center justify-center gap-1.5 rounded-md bg-[var(--color-accent-primary)] px-4 py-2 text-sm font-medium text-white transition-all duration-200 hover:bg-[var(--color-accent-hover)]"
                      onClick={() => setIsOpen(false)}
                    >
                      <span>Kelime Aramasına Git</span>
                      <ExternalLink className="h-4 w-4" />
                    </Link>
                  )}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </PopoverContent>
    </Popover>
  )
}
