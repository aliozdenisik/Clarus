"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Switch } from "@/components/ui/switch"
import { Skeleton } from "@/components/ui/skeleton"
import type { KeywordSuggestion } from "@/lib/stores/keyword-store"

export interface KeywordSelectorProps {
  keywords: KeywordSuggestion[]
  onSelectionChange: (selected: KeywordSuggestion[]) => void
  isLoading: boolean
  onSearch: () => void
}

export function KeywordSelector({
  keywords,
  onSelectionChange,
  isLoading,
  onSearch,
}: KeywordSelectorProps) {
  void onSearch
  const [advancedMode, setAdvancedMode] = React.useState(false)
  const [selectedKeywords, setSelectedKeywords] = React.useState<KeywordSuggestion[]>(
    keywords.filter((k) => k.selected)
  )

  React.useEffect(() => {
    setSelectedKeywords(keywords.filter((k) => k.selected))
  }, [keywords])

  const handleToggle = (checked: boolean) => {
    setAdvancedMode(checked)
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

  const handleSelectAll = () => {
    setSelectedKeywords(keywords)
    onSelectionChange(keywords)
  }

  const handleDeselectAll = () => {
    setSelectedKeywords([])
    onSelectionChange([])
  }

  const hasNoSelection = selectedKeywords.length === 0 && keywords.length > 0

  return (
    <div className="space-y-4">
      {/* Toggle Switch */}
      <div className="flex items-center justify-between">
        <Switch
          checked={advancedMode}
          onCheckedChange={handleToggle}
          label="Gelişmiş Arama"
          description="Anahtar kelime bazlı arama"
        />
      </div>

      {/* Keyword Chips Section */}
      <AnimatePresence>
        {advancedMode && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="space-y-3">
              {/* Action Buttons */}
              {!isLoading && keywords.length > 0 && (
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleSelectAll}
                    className={cn(
                      "rounded-lg px-3 py-1.5 text-xs font-medium transition-colors",
                      "bg-zinc-900/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-300",
                      "focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
                    )}
                  >
                    Tümünü Seç
                  </button>
                  <button
                    type="button"
                    onClick={handleDeselectAll}
                    className={cn(
                      "rounded-lg px-3 py-1.5 text-xs font-medium transition-colors",
                      "bg-zinc-900/50 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-300",
                      "focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40"
                    )}
                  >
                    Tümünü Kaldır
                  </button>
                </div>
              )}

              {/* Loading State */}
              {isLoading && (
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {[...Array(5)].map((_, i) => (
                    <Skeleton
                      key={`keyword-selector-skeleton-${i}`}
                      className="h-8 w-24 shrink-0 rounded-full"
                    />
                  ))}
                </div>
              )}

              {/* Keyword Chips */}
              {!isLoading && keywords.length > 0 && (
                <div className="scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent flex gap-2 overflow-x-auto pb-2">
                  {keywords.map((keyword) => {
                    const isSelected = selectedKeywords.some((k) => k.text === keyword.text)

                    return (
                      <motion.button
                        key={keyword.text}
                        type="button"
                        onClick={() => handleKeywordToggle(keyword)}
                        initial={false}
                        animate={{
                          backgroundColor: isSelected
                            ? "rgba(39, 39, 42, 1)"
                            : "rgba(39, 39, 42, 0.5)",
                          borderColor: isSelected
                            ? "rgba(79, 70, 229, 0.6)"
                            : "rgba(63, 63, 70, 0.4)",
                        }}
                        whileHover={{
                          backgroundColor: isSelected
                            ? "rgba(39, 39, 42, 1)"
                            : "rgba(39, 39, 42, 0.8)",
                        }}
                        whileTap={{ scale: 0.96 }}
                        transition={{ duration: 0.15 }}
                        className={cn(
                          "group relative flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium",
                          "focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500/40",
                          isSelected
                            ? "text-zinc-100 shadow-sm"
                            : "text-zinc-400 hover:text-zinc-300"
                        )}
                      >
                        <span>{keyword.text}</span>
                        <AnimatePresence>
                          {isSelected && (
                            <motion.div
                              initial={{ scale: 0, opacity: 0 }}
                              animate={{ scale: 1, opacity: 1 }}
                              exit={{ scale: 0, opacity: 0 }}
                              transition={{ duration: 0.15 }}
                              className="flex items-center"
                            >
                              <X className="h-3 w-3" />
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </motion.button>
                    )
                  })}
                </div>
              )}

              {/* Warning Message */}
              {hasNoSelection && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 rounded-lg border border-amber-500/20 bg-amber-500/10 px-3 py-2"
                >
                  <svg
                    className="h-4 w-4 shrink-0 text-amber-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  <span className="text-xs text-amber-500">En az 1 anahtar kelime seçin</span>
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default KeywordSelector
