"use client"

import * as React from "react"
import { motion, AnimatePresence } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { Sparkles, Command, ArrowRight } from "lucide-react"
import { cn } from "@/lib/utils"

import { LanguageSelector } from "@/components/search/language-selector"
import { TranslatorSelector } from "@/components/search/translator-selector"
import { CollectionSelector } from "@/components/compare/collection-selector"

function useAutoResizeTextarea(ref: React.RefObject<HTMLTextAreaElement | null>) {
  return React.useCallback(() => {
    const element = ref.current
    if (!element) return

    element.style.height = "auto"
    const minHeight = 48
    const maxHeight = 200
    const nextHeight = Math.min(Math.max(element.scrollHeight, minHeight), maxHeight)
    element.style.height = `${nextHeight}px`
    element.style.overflowY = element.scrollHeight > maxHeight ? "auto" : "hidden"
  }, [ref])
}

function TypingDots() {
  return (
    <div className="flex items-center gap-0.5">
      {[0, 1, 2].map((i) => (
        <motion.div
          key={i}
          className="h-1 w-1 rounded-full bg-white/50"
          animate={{ opacity: [0.4, 1, 0.4] }}
          transition={{
            duration: 1.4,
            repeat: Infinity,
            delay: i * 0.2,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  )
}

export interface AnimatedSearchInputProps {
  value: string
  onChange: (value: string) => void
  onSubmit: (e: React.FormEvent) => void
  placeholder: string
  isLoading: boolean
  disabled?: boolean
  selectedLanguage: string | null
  onLanguageChange: (lang: string | null) => void
  detectedLanguage?: string
  selectedTranslator: string
  onTranslatorChange: (translator: string) => void
  selectedCollections: string[]
  onCollectionsChange: (collections: string[]) => void
  showTranslatorSelector: boolean
  suggestedTopics: string[]
  onTopicSelect: (topic: string) => void
  submitLabel: string
  loadingLabel: string
  textareaRef: React.RefObject<HTMLTextAreaElement | null>
}

export function AnimatedSearchInput({
  value,
  onChange,
  onSubmit,
  placeholder,
  isLoading,
  disabled,
  selectedLanguage,
  onLanguageChange,
  detectedLanguage,
  selectedTranslator,
  onTranslatorChange,
  selectedCollections,
  onCollectionsChange,
  showTranslatorSelector,
  suggestedTopics,
  onTopicSelect,
  submitLabel,
  loadingLabel,
  textareaRef,
}: AnimatedSearchInputProps) {
  const [isFocused, setIsFocused] = React.useState(false)
  const [selectedIndex, setSelectedIndex] = React.useState(0)

  const adjustHeight = useAutoResizeTextarea(textareaRef)

  const showCommandPalette = value.startsWith("/") && !isLoading

  const filteredTopics = React.useMemo(() => {
    if (!showCommandPalette) return []
    const search = value.slice(1).toLowerCase()
    return suggestedTopics.filter((t) => t.toLowerCase().includes(search))
  }, [value, showCommandPalette, suggestedTopics])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (showCommandPalette && filteredTopics.length > 0) {
      if (e.key === "ArrowDown") {
        e.preventDefault()
        setSelectedIndex((i) => (i + 1) % filteredTopics.length)
      } else if (e.key === "ArrowUp") {
        e.preventDefault()
        setSelectedIndex((i) => (i - 1 + filteredTopics.length) % filteredTopics.length)
      } else if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault()
        onTopicSelect(filteredTopics[selectedIndex])
      }
    } else if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      if (value.trim() && !isLoading) {
        onSubmit(e)
      }
    }
  }

  return (
    <div className="relative mx-auto w-full max-w-2xl">
      <AnimatePresence>
        {showCommandPalette && filteredTopics.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 10, scale: 0.95 }}
            transition={springPresets.snappy}
            className="absolute bottom-full z-20 mb-2 w-full overflow-hidden rounded-xl border border-white/10 bg-[var(--color-bg-surface)] shadow-2xl backdrop-blur-xl"
          >
            <div className="p-1">
              <div className="flex items-center gap-2 px-2 py-1.5 text-xs font-medium text-[var(--color-text-muted)]">
                <Command className="h-3 w-3" />
                Suggested Topics
              </div>
              {filteredTopics.map((topic, index) => (
                <button
                  key={topic}
                  type="button"
                  onClick={() => onTopicSelect(topic)}
                  className={cn(
                    "flex w-full items-center gap-2 rounded-lg px-2 py-2 text-left text-sm transition-colors",
                    index === selectedIndex
                      ? "bg-white/10 text-[var(--color-text-primary)]"
                      : "text-[var(--color-text-secondary)] hover:bg-white/5"
                  )}
                >
                  <Sparkles
                    className={cn(
                      "h-4 w-4",
                      index === selectedIndex ? "text-violet-400" : "text-[var(--color-text-muted)]"
                    )}
                  />
                  {topic}
                </button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={springPresets.fluid}
        className={cn(
          "relative rounded-2xl border border-white/10 bg-[var(--color-bg-surface)]/80 shadow-2xl backdrop-blur-2xl transition-all duration-300",
          isFocused ? "border-violet-500/30 shadow-violet-500/10" : "hover:border-white/20"
        )}
      >
        <AnimatePresence>
          {isFocused && (
            <motion.span
              layoutId="focus-ring"
              className="pointer-events-none absolute -inset-px z-10 rounded-2xl border-2 border-violet-500/30"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />
          )}
        </AnimatePresence>

        <div className="relative z-10 px-4 pt-4 pb-2">
          <textarea
            ref={textareaRef}
            data-testid="compare-topic-input"
            value={value}
            onChange={(e) => {
              onChange(e.target.value)
              adjustHeight()
              setSelectedIndex(0)
            }}
            onKeyDown={handleKeyDown}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            rows={1}
            disabled={disabled || isLoading}
            className="w-full resize-none bg-transparent text-base leading-relaxed text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)] focus:outline-none disabled:opacity-50"
            style={{ minHeight: "48px" }}
          />
        </div>

        <div className="relative z-10 flex flex-wrap items-center justify-between gap-3 border-t border-white/5 bg-white/[0.02] px-2 py-2 sm:px-3">
          <div className="flex flex-wrap items-center gap-2">
            <LanguageSelector
              value={selectedLanguage}
              onChange={onLanguageChange}
              detectedLanguage={detectedLanguage}
            />

            {showTranslatorSelector && (
              <TranslatorSelector value={selectedTranslator} onChange={onTranslatorChange} />
            )}

            <div className="mx-1 hidden h-4 w-px bg-white/10 sm:block" />

            <div className="flex items-center gap-2">
              <span className="hidden text-xs text-[var(--color-text-muted)] sm:inline-block">
                Sources:
              </span>
              <CollectionSelector
                selected={selectedCollections}
                onChange={onCollectionsChange}
                disabled={isLoading}
              />
            </div>
          </div>

          <div className="ml-auto flex items-center gap-2">
            <motion.button
              type="button"
              onClick={(e) => {
                if (value.trim() && !isLoading) onSubmit(e)
              }}
              data-testid="compare-analyze-button"
              disabled={!value.trim() || isLoading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                "group relative flex h-9 items-center gap-2 rounded-lg px-4 text-sm font-medium text-white transition-all disabled:cursor-not-allowed disabled:opacity-50",
                value.trim()
                  ? "bg-gradient-to-r from-violet-500 to-indigo-500 shadow-lg shadow-violet-500/25 hover:from-violet-600 hover:to-indigo-600"
                  : "cursor-not-allowed bg-zinc-800 text-zinc-500"
              )}
            >
              {isLoading ? (
                <>
                  <TypingDots />
                  <span className="ml-1">{loadingLabel}</span>
                </>
              ) : (
                <>
                  <span>{submitLabel}</span>
                  <div className="relative flex h-5 w-5 items-center justify-center overflow-hidden">
                    <motion.div
                      initial={{ x: 0 }}
                      animate={{ x: isFocused && value.trim() ? 3 : 0 }}
                      transition={{
                        repeat: isFocused && value.trim() ? Infinity : 0,
                        repeatType: "reverse",
                        duration: 0.8,
                      }}
                    >
                      <ArrowRight size={16} />
                    </motion.div>
                  </div>
                </>
              )}
            </motion.button>
          </div>
        </div>
      </motion.div>


    </div>
  )
}
