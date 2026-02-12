"use client"

import React, { useState } from "react"
import { Popover, PopoverTrigger, PopoverContent } from "@/components/ui/popover"
import { motion, AnimatePresence } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { useQuery } from "@tanstack/react-query"
import { getEtymologyApiEtymologyRootGet } from "@/lib/api"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { ChevronDown, ChevronUp, AlertCircle, ArrowRight } from "lucide-react"
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
    retry: false,
  })

  if (!hasEtymology) {
    return <>{children}</>
  }

  const morphologicalForms = data?.morphological_forms || []

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>{children}</PopoverTrigger>
      <PopoverContent
        side="top"
        sideOffset={8}
        align="center"
        className="z-50 max-w-[min(400px,calc(100vw-2rem))] min-w-[min(280px,calc(100vw-2rem))] p-0"
      >
        <AnimatePresence>
          {isOpen && (
            <motion.div
              data-testid="etymology-popover"
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
                  <motion.div
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ ...springPresets.gentle, delay: 0 }}
                    className="flex items-center justify-between border-b border-[var(--color-border-subtle)] pb-3"
                  >
                    <div className="flex flex-col gap-1">
                      <p
                        data-testid="root-text"
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
                    {/* Confidence Badge with Color Coding */}
                    {data.confidence && (
                      <span
                        data-testid="confidence-badge"
                        className={cn(
                          "rounded-full border px-2.5 py-1 text-xs font-medium",
                          data.confidence === "high" &&
                            "border-emerald-500/30 bg-emerald-500/20 text-emerald-300",
                          data.confidence === "medium" &&
                            "border-amber-500/30 bg-amber-500/20 text-amber-300",
                          data.confidence === "low" &&
                            "border-zinc-500/30 bg-zinc-500/20 text-zinc-300"
                        )}
                      >
                        {data.confidence === "high" && "Yüksek"}
                        {data.confidence === "medium" && "Orta"}
                        {data.confidence === "low" && "Düşük"}
                      </span>
                    )}
                  </motion.div>

                  {/* Definitions */}
                  <motion.div
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ ...springPresets.gentle, delay: 0.05 }}
                    className="space-y-2"
                  >
                    {data.summary_tr || data.summary_en ? (
                      <>
                        {data.summary_tr && (
                          <p
                            data-testid="root-meaning"
                            className="text-sm text-[var(--color-text-primary)]"
                          >
                            <span className="font-medium text-[var(--color-text-muted)]">
                              Anlam:
                            </span>{" "}
                            {data.summary_tr}
                          </p>
                        )}
                        {data.summary_en && (
                          <p className="text-sm text-[var(--color-text-secondary)] italic">
                            {data.summary_en}
                          </p>
                        )}
                      </>
                    ) : data.definition_tr ? (
                      <p
                        data-testid="root-meaning"
                        className="text-sm text-[var(--color-text-primary)]"
                      >
                        <span className="font-medium text-[var(--color-text-muted)]">Anlam:</span>{" "}
                        {data.definition_tr}
                      </p>
                    ) : (
                      <p
                        data-testid="root-meaning"
                        className="text-sm text-[var(--color-text-muted)] italic"
                      >
                        <span className="font-medium">Anlam:</span> Tanım mevcut değil
                      </p>
                    )}
                  </motion.div>

                  {/* Morphological Forms - Collapsible Section */}
                  {morphologicalForms.length > 0 && (
                    <motion.div
                      initial={{ opacity: 0, y: -4 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ ...springPresets.gentle, delay: 0.1 }}
                      className="space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-[var(--color-text-primary)]">
                          Morfolojik Formlar:
                        </span>
                        {morphologicalForms.length > 5 && (
                          <button
                            type="button"
                            onClick={() => setShowAllForms(!showAllForms)}
                            className="flex items-center gap-1 text-xs text-[var(--color-accent-primary)] transition-colors duration-200 hover:text-[var(--color-accent-hover)]"
                          >
                            <motion.span
                              whileTap={{ scale: 0.95 }}
                              transition={springPresets.bouncy}
                            >
                              {showAllForms ? (
                                <>
                                  <span>Daha Az</span>
                                  <ChevronUp className="inline h-3 w-3" />
                                </>
                              ) : (
                                <>
                                  <span>Tümünü Gör ({morphologicalForms.length})</span>
                                  <ChevronDown className="inline h-3 w-3" />
                                </>
                              )}
                            </motion.span>
                          </button>
                        )}
                      </div>

                      <AnimatePresence mode="wait">
                        <motion.ul
                          key={showAllForms ? "all" : "partial"}
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={springPresets.gentle}
                          className="space-y-1.5 overflow-hidden"
                        >
                          {(showAllForms ? morphologicalForms : morphologicalForms.slice(0, 5)).map(
                            (form, idx) => (
                              <motion.li
                                key={`${form.form_pattern}-${idx}`}
                                initial={{ opacity: 0, x: -8 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ ...springPresets.gentle, delay: idx * 0.02 }}
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
                              </motion.li>
                            )
                          )}
                        </motion.ul>
                      </AnimatePresence>
                    </motion.div>
                  )}

                  {/* Frequency & Source */}
                  <motion.div
                    initial={{ opacity: 0, y: -4 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ ...springPresets.gentle, delay: 0.15 }}
                    className="space-y-1 border-t border-[var(--color-border-subtle)] pt-3 text-sm"
                  >
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
                  </motion.div>

                  {/* Deep Link to Keyword Search */}
                  {data.root_buckwalter && (
                    <motion.div
                      initial={{ opacity: 0, y: -4 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ ...springPresets.gentle, delay: 0.2 }}
                    >
                      <Link
                        data-testid="detail-link"
                        href={`/keyword-search/root/${encodeURIComponent(data.root_buckwalter)}`}
                        onClick={() => setIsOpen(false)}
                      >
                        <motion.div
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.97 }}
                          transition={springPresets.bouncy}
                          className="flex items-center justify-center gap-2 rounded-lg border border-[var(--color-accent-primary)]/30 bg-[var(--color-accent-primary)]/10 px-4 py-2.5 text-sm font-medium text-[var(--color-accent-primary)] transition-colors hover:bg-[var(--color-accent-primary)]/20"
                        >
                          <span>Detaylı Analiz</span>
                          <ArrowRight className="h-4 w-4" />
                        </motion.div>
                      </Link>
                    </motion.div>
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
