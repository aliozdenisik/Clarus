"use client"

import { forwardRef, useCallback, useEffect, useImperativeHandle, useMemo, useState } from "react"
import {
  AnimatePresence,
  AnimatePresenceProps,
  motion,
  MotionProps,
  Transition,
} from "framer-motion"

import { cn } from "@/lib/utils"

interface TextRotateProps {
  texts: string[]
  rotationInterval?: number
  initial?: MotionProps["initial"]
  animate?: MotionProps["animate"]
  exit?: MotionProps["exit"]
  animatePresenceMode?: AnimatePresenceProps["mode"]
  animatePresenceInitial?: boolean
  staggerDuration?: number
  staggerFrom?: "first" | "last" | "center" | number | "random"
  transition?: Transition
  loop?: boolean
  auto?: boolean
  splitBy?: "words" | "characters" | "lines" | string
  onNext?: (index: number) => void
  mainClassName?: string
  splitLevelClassName?: string
  elementLevelClassName?: string
}

export interface TextRotateRef {
  next: () => void
  previous: () => void
  jumpTo: (index: number) => void
  reset: () => void
}

interface WordObject {
  characters: string[]
  needsSpace: boolean
}

const TextRotate = forwardRef<TextRotateRef, TextRotateProps>(
  (
    {
      texts,
      transition = { type: "spring", damping: 30, stiffness: 400 },
      initial = { y: "100%", opacity: 0 },
      animate = { y: 0, opacity: 1 },
      exit = { y: "-120%", opacity: 0 },
      animatePresenceMode = "wait",
      animatePresenceInitial = false,
      rotationInterval = 3000,
      staggerDuration = 0.025,
      staggerFrom = "first",
      loop = true,
      auto = true,
      splitBy = "characters",
      onNext,
      mainClassName,
      splitLevelClassName,
      elementLevelClassName,
    },
    ref
  ) => {
    const [currentTextIndex, setCurrentTextIndex] = useState(0)

    const splitIntoCharacters = (text: string): string[] => {
      if (typeof Intl !== "undefined" && "Segmenter" in Intl) {
        const segmenter = new Intl.Segmenter("en", { granularity: "grapheme" })
        return Array.from(segmenter.segment(text), ({ segment }) => segment)
      }
      return Array.from(text)
    }

    const elements = useMemo(() => {
      const currentText = texts[currentTextIndex]
      if (splitBy === "characters") {
        const text = currentText.split(" ")
        return text.map((word, i) => ({
          characters: splitIntoCharacters(word),
          needsSpace: i !== text.length - 1,
        }))
      }
      return splitBy === "words"
        ? currentText.split(" ")
        : splitBy === "lines"
          ? currentText.split("\n")
          : currentText.split(splitBy)
    }, [texts, currentTextIndex, splitBy])

    const getStaggerDelay = useCallback(
      (index: number, totalChars: number) => {
        const total = totalChars
        if (staggerFrom === "first") return index * staggerDuration
        if (staggerFrom === "last") return (total - 1 - index) * staggerDuration
        if (staggerFrom === "center") {
          const center = Math.floor(total / 2)
          return Math.abs(center - index) * staggerDuration
        }
        if (staggerFrom === "random") {
          const randomIndex = Math.floor(Math.random() * total)
          return Math.abs(randomIndex - index) * staggerDuration
        }
        return Math.abs(staggerFrom - index) * staggerDuration
      },
      [staggerFrom, staggerDuration]
    )

    const handleIndexChange = useCallback(
      (newIndex: number) => {
        setCurrentTextIndex(newIndex)
        onNext?.(newIndex)
      },
      [onNext]
    )

    const next = useCallback(() => {
      const nextIndex =
        currentTextIndex === texts.length - 1 ? (loop ? 0 : currentTextIndex) : currentTextIndex + 1

      if (nextIndex !== currentTextIndex) {
        handleIndexChange(nextIndex)
      }
    }, [currentTextIndex, texts.length, loop, handleIndexChange])

    const previous = useCallback(() => {
      const prevIndex =
        currentTextIndex === 0 ? (loop ? texts.length - 1 : currentTextIndex) : currentTextIndex - 1

      if (prevIndex !== currentTextIndex) {
        handleIndexChange(prevIndex)
      }
    }, [currentTextIndex, texts.length, loop, handleIndexChange])

    const jumpTo = useCallback(
      (index: number) => {
        const validIndex = Math.max(0, Math.min(index, texts.length - 1))
        if (validIndex !== currentTextIndex) {
          handleIndexChange(validIndex)
        }
      },
      [texts.length, currentTextIndex, handleIndexChange]
    )

    const reset = useCallback(() => {
      if (currentTextIndex !== 0) {
        handleIndexChange(0)
      }
    }, [currentTextIndex, handleIndexChange])

    useImperativeHandle(
      ref,
      () => ({
        next,
        previous,
        jumpTo,
        reset,
      }),
      [next, previous, jumpTo, reset]
    )

    useEffect(() => {
      if (!auto) return
      const intervalId = setInterval(next, rotationInterval)
      return () => clearInterval(intervalId)
    }, [next, rotationInterval, auto])

    return (
      <motion.span
        className={cn("flex flex-wrap whitespace-pre-wrap", mainClassName)}
        layout
        transition={transition}
      >
        <span className="sr-only">{texts[currentTextIndex]}</span>

        <AnimatePresence mode={animatePresenceMode} initial={animatePresenceInitial}>
          <motion.div
            key={currentTextIndex}
            className={cn("flex flex-wrap", splitBy === "lines" && "w-full flex-col")}
            layout
            aria-hidden="true"
          >
            {(() => {
              const wordOccurrences = new Map<string, number>()

              return (
                splitBy === "characters"
                  ? (elements as WordObject[])
                  : (elements as string[]).map((el, i) => ({
                      characters: [el],
                      needsSpace: i !== elements.length - 1,
                    }))
              ).map((wordObj, wordIndex, array) => {
                const wordToken = wordObj.characters.join("")
                const wordOccurrence = (wordOccurrences.get(wordToken) ?? 0) + 1
                wordOccurrences.set(wordToken, wordOccurrence)
                const wordKey = `${wordToken}-${wordOccurrence}`
                const previousCharsCount = array
                  .slice(0, wordIndex)
                  .reduce((sum, word) => sum + word.characters.length, 0)
                const charOccurrences = new Map<string, number>()

                return (
                  <span key={wordKey} className={cn("inline-flex", splitLevelClassName)}>
                    {wordObj.characters.map((char, charIndex) => {
                      const charOccurrence = (charOccurrences.get(char) ?? 0) + 1
                      charOccurrences.set(char, charOccurrence)
                      const charKey = `${char}-${charOccurrence}`

                      return (
                        <motion.span
                          initial={initial}
                          animate={animate}
                          exit={exit}
                          key={charKey}
                          transition={{
                            ...transition,
                            delay: getStaggerDelay(
                              previousCharsCount + charIndex,
                              array.reduce((sum, word) => sum + word.characters.length, 0)
                            ),
                          }}
                          className={cn("inline-block", elementLevelClassName)}
                        >
                          {char}
                        </motion.span>
                      )
                    })}
                    {wordObj.needsSpace && <span className="whitespace-pre"> </span>}
                  </span>
                )
              })
            })()}
          </motion.div>
        </AnimatePresence>
      </motion.span>
    )
  }
)

TextRotate.displayName = "TextRotate"

export { TextRotate }

// Luxury Quote Display Component
interface LuxuryQuoteProps {
  quotes: { text: string; source: string }[]
  rotationInterval?: number
  className?: string
}

export function LuxuryQuote({ quotes, rotationInterval = 5000, className }: LuxuryQuoteProps) {
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % quotes.length)
    }, rotationInterval)
    return () => clearInterval(interval)
  }, [quotes.length, rotationInterval])

  return (
    <div className={cn("relative overflow-hidden", className)}>
      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className="text-center"
        >
          <blockquote className="text-xl leading-relaxed font-light text-[var(--color-text-primary)] italic md:text-2xl lg:text-3xl">
            &quot;{quotes[currentIndex].text}&quot;
          </blockquote>
          <motion.div
            className="mt-4 flex items-center justify-center gap-2"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <div className="h-px w-8 bg-gradient-to-r from-transparent via-[var(--color-accent-primary)] to-transparent" />
            <cite className="text-sm font-medium text-[var(--color-text-secondary)] not-italic">
              {quotes[currentIndex].source}
            </cite>
            <div className="h-px w-8 bg-gradient-to-r from-transparent via-[var(--color-accent-primary)] to-transparent" />
          </motion.div>
        </motion.div>
      </AnimatePresence>

      {/* Progress indicators */}
      <div className="mt-6 flex justify-center gap-1.5">
        {quotes.map((quote, index) => (
          <button
            key={`${quote.source}-${quote.text}`}
            onClick={() => setCurrentIndex(index)}
            className={cn(
              "h-1.5 w-1.5 rounded-full transition-all duration-300",
              index === currentIndex
                ? "w-6 bg-[var(--color-accent-primary)]"
                : "bg-white/20 hover:bg-white/40"
            )}
            aria-label={`Go to quote ${index + 1}`}
          />
        ))}
      </div>
    </div>
  )
}
