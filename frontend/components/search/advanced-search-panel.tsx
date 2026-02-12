"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { X, AlertTriangle } from "lucide-react"
import { cn } from "@/lib/utils"
import { springPresets } from "@/lib/design-system"
import { Switch } from "@/components/ui/switch"
import { Skeleton } from "@/components/ui/skeleton"
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/ui/tooltip"
import type { KeywordSuggestion } from "@/lib/stores/keyword-store"

export interface AdvancedSearchPanelProps {
  keywords: KeywordSuggestion[]
  onSelectionChange: (selected: KeywordSuggestion[]) => void
  isLoading: boolean
  onExtractKeywords?: () => void
  groupLabel?: string
  open?: boolean
  onOpenChange?: (open: boolean) => void
  showToggle?: boolean
  showDivider?: boolean
  className?: string
}

export function AdvancedSearchPanel({
  keywords,
  onSelectionChange,
  isLoading,
  onExtractKeywords,
  groupLabel,
  open,
  onOpenChange,
  showToggle = true,
  showDivider = true,
  className,
}: AdvancedSearchPanelProps) {
  const [internalOpen, setInternalOpen] = React.useState(false)
  const [selectedKeywords, setSelectedKeywords] = React.useState<KeywordSuggestion[]>([])

  const isControlled = open !== undefined
  const expanded = isControlled ? open : internalOpen

  React.useEffect(() => {
    setSelectedKeywords(keywords.filter((k) => k.selected))
  }, [keywords])

  const handleToggle = (checked: boolean) => {
    if (isControlled) {
      onOpenChange?.(checked)
    } else {
      setInternalOpen(checked)
    }

    if (checked && keywords.length === 0 && onExtractKeywords) {
      onExtractKeywords()
    }
  }

  const handleKeywordToggle = (keyword: KeywordSuggestion) => {
    const isSelected = selectedKeywords.some((k) => k.text === keyword.text)
    let newSelected: KeywordSuggestion[]

    if (isSelected) {
      newSelected = selectedKeywords.filter((k) => k.text !== keyword.text)
    } else {
      newSelected = [...selectedKeywords, keyword]
    }

    setSelectedKeywords(newSelected)
    onSelectionChange(newSelected)
  }

  const selectAll = () => {
    setSelectedKeywords(keywords)
    onSelectionChange(keywords)
  }

  const deselectAll = () => {
    setSelectedKeywords([])
    onSelectionChange([])
  }

  const hasNoSelection = expanded && keywords.length > 0 && selectedKeywords.length === 0

  return (
    <div className={cn("space-y-0", className)}>
      {showDivider && <div className="h-px bg-[var(--color-border-subtle)]" />}

      {showToggle && (
        <div className="pt-4">
          <Switch
            checked={expanded}
            onCheckedChange={handleToggle}
            label="Advanced Search"
            description="Keyword-based search"
          />
        </div>
      )}

      {groupLabel && expanded && (
        <p className="pt-3 text-xs font-medium text-[var(--color-text-muted)]">{groupLabel}</p>
      )}

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={springPresets.fluid}
            className="overflow-hidden"
          >
            <div className="space-y-3 pt-4">
              {isLoading && (
                <div className="flex flex-wrap gap-2">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton
                      key={`advanced-search-skeleton-${i}`}
                      className="h-7 w-20 shrink-0 rounded-full"
                    />
                  ))}
                </div>
              )}

              {!isLoading && keywords.length > 0 && (
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={selectAll}
                      className={cn(
                        "rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
                        "border border-[var(--color-border-subtle)] bg-transparent",
                        "text-[var(--color-text-secondary)]",
                        "hover:border-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]",
                        "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-primary)]/40"
                      )}
                    >
                      Select All
                    </button>
                    <button
                      type="button"
                      onClick={deselectAll}
                      className={cn(
                        "rounded-md px-2.5 py-1 text-xs font-medium transition-colors",
                        "border border-[var(--color-border-subtle)] bg-transparent",
                        "text-[var(--color-text-secondary)]",
                        "hover:border-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]",
                        "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-primary)]/40"
                      )}
                    >
                      Deselect All
                    </button>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {keywords.map((keyword) => {
                      const isSelected = selectedKeywords.some((k) => k.text === keyword.text)

                      return (
                        <Tooltip key={keyword.text}>
                          <TooltipTrigger asChild>
                            <motion.button
                              type="button"
                              onClick={() => handleKeywordToggle(keyword)}
                              whileHover={{ scale: 1.02 }}
                              whileTap={{ scale: 0.98 }}
                              transition={springPresets.snappy}
                              className={cn(
                                "group relative flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-all duration-200",
                                "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-primary)]/40",
                                isSelected
                                  ? "border-[var(--color-accent-primary)]/50 bg-[var(--color-accent-primary)]/10 text-[var(--color-text-primary)] shadow-sm"
                                  : "border-zinc-700/40 bg-transparent text-zinc-500 hover:border-zinc-600/60 hover:text-zinc-400"
                              )}
                            >
                              <span>{keyword.text}</span>
                              <AnimatePresence>
                                {isSelected && (
                                  <motion.div
                                    initial={{ scale: 0, opacity: 0 }}
                                    animate={{ scale: 1, opacity: 1 }}
                                    exit={{ scale: 0, opacity: 0 }}
                                    transition={springPresets.snappy}
                                    className="flex items-center"
                                  >
                                    <X className="h-3 w-3" />
                                  </motion.div>
                                )}
                              </AnimatePresence>
                            </motion.button>
                          </TooltipTrigger>
                          <TooltipContent side="top" sideOffset={8}>
                            <div className="space-y-0.5 text-left">
                              <div className="text-xs font-medium">
                                {keyword.language === "ar" ? "Arabic" : keyword.language}
                              </div>
                              <div className="text-xs opacity-80">
                                Confidence: {Math.round(keyword.confidence * 100)}%
                              </div>
                              {keyword.source && (
                                <div className="text-xs opacity-80">Source: {keyword.source}</div>
                              )}
                            </div>
                          </TooltipContent>
                        </Tooltip>
                      )
                    })}
                  </div>
                </div>
              )}

              {hasNoSelection && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={springPresets.gentle}
                  className="flex items-center gap-2 rounded-lg border border-amber-500/20 bg-amber-500/5 px-3 py-2"
                >
                  <AlertTriangle className="h-4 w-4 shrink-0 text-amber-500" />
                  <span className="text-xs text-amber-500">Select at least 1 keyword</span>
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default AdvancedSearchPanel
