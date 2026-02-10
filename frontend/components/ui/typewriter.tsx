"use client"

import { useEffect, useMemo, useState } from "react"
import { motion, Variants } from "framer-motion"

import { cn } from "@/lib/utils"

interface TypewriterProps {
  text: string | string[]
  speed?: number
  initialDelay?: number
  waitTime?: number
  deleteSpeed?: number
  loop?: boolean
  className?: string
  showCursor?: boolean
  hideCursorOnType?: boolean
  cursorChar?: string | React.ReactNode
  cursorAnimationVariants?: {
    initial: Variants["initial"]
    animate: Variants["animate"]
  }
  cursorClassName?: string
  onComplete?: () => void
}

const Typewriter = ({
  text,
  speed = 50,
  initialDelay = 0,
  waitTime = 2000,
  deleteSpeed = 30,
  loop = true,
  className,
  showCursor = true,
  hideCursorOnType = false,
  cursorChar = "▊",
  cursorClassName = "ml-0.5",
  cursorAnimationVariants = {
    initial: { opacity: 0 },
    animate: {
      opacity: 1,
      transition: {
        duration: 0.5,
        repeat: Infinity,
        repeatType: "reverse",
      },
    },
  },
  onComplete,
}: TypewriterProps) => {
  const [displayText, setDisplayText] = useState("")
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isDeleting, setIsDeleting] = useState(false)
  const [currentTextIndex, setCurrentTextIndex] = useState(0)

  const texts = useMemo(() => (Array.isArray(text) ? text : [text]), [text])

  useEffect(() => {
    let timeout: NodeJS.Timeout

    const currentText = texts[currentTextIndex]

    const startTyping = () => {
      if (isDeleting) {
        if (displayText === "") {
          setIsDeleting(false)
          if (currentTextIndex === texts.length - 1 && !loop) {
            onComplete?.()
            return
          }
          setCurrentTextIndex((prev) => (prev + 1) % texts.length)
          setCurrentIndex(0)
          timeout = setTimeout(() => {}, waitTime)
        } else {
          timeout = setTimeout(() => {
            setDisplayText((prev) => prev.slice(0, -1))
          }, deleteSpeed)
        }
      } else {
        if (currentIndex < currentText.length) {
          timeout = setTimeout(() => {
            setDisplayText((prev) => prev + currentText[currentIndex])
            setCurrentIndex((prev) => prev + 1)
          }, speed)
        } else if (texts.length > 1) {
          timeout = setTimeout(() => {
            setIsDeleting(true)
          }, waitTime)
        } else if (!loop) {
          onComplete?.()
        }
      }
    }

    if (currentIndex === 0 && !isDeleting && displayText === "") {
      timeout = setTimeout(startTyping, initialDelay)
    } else {
      startTyping()
    }

    return () => clearTimeout(timeout)
  }, [
    currentIndex,
    displayText,
    isDeleting,
    speed,
    deleteSpeed,
    waitTime,
    texts,
    currentTextIndex,
    loop,
    initialDelay,
    onComplete,
  ])

  return (
    <span className={cn("inline whitespace-pre-wrap", className)}>
      <span>{displayText}</span>
      {showCursor && (
        <motion.span
          variants={cursorAnimationVariants}
          className={cn(
            cursorClassName,
            "text-[var(--color-accent-primary)]",
            hideCursorOnType && (currentIndex < texts[currentTextIndex].length || isDeleting)
              ? "opacity-0"
              : ""
          )}
          initial="initial"
          animate="animate"
        >
          {cursorChar}
        </motion.span>
      )}
    </span>
  )
}

export { Typewriter }

// Streaming Text for AI responses - luxury feel
interface StreamingTextProps {
  text: string
  speed?: number
  className?: string
  onComplete?: () => void
}

export function StreamingText({ text, speed = 20, className, onComplete }: StreamingTextProps) {
  const [displayedText, setDisplayedText] = useState("")
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    setDisplayedText("")
    setIsComplete(false)
    let index = 0

    const interval = setInterval(() => {
      if (index < text.length) {
        setDisplayedText(text.slice(0, index + 1))
        index++
      } else {
        clearInterval(interval)
        setIsComplete(true)
        onComplete?.()
      }
    }, speed)

    return () => clearInterval(interval)
  }, [text, speed, onComplete])

  return (
    <div className={cn("relative", className)}>
      <span className="whitespace-pre-wrap">{displayedText}</span>
      {!isComplete && (
        <motion.span
          className="ml-0.5 inline-block h-5 w-2 rounded-sm bg-[var(--color-accent-primary)]"
          animate={{ opacity: [1, 0.3, 1] }}
          transition={{ duration: 0.8, repeat: Infinity }}
        />
      )}
    </div>
  )
}

// Typing Indicator for loading states
interface TypingIndicatorProps {
  className?: string
  dotClassName?: string
}

export function TypingIndicator({ className, dotClassName }: TypingIndicatorProps) {
  return (
    <div className={cn("flex items-center gap-1", className)}>
      {[0, 1, 2].map((i) => (
        <motion.div
          key={`typing-dot-${i}`}
          className={cn("h-2 w-2 rounded-full bg-[var(--color-accent-primary)]", dotClassName)}
          animate={{
            y: [0, -6, 0],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 0.8,
            repeat: Infinity,
            delay: i * 0.15,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  )
}

// Luxury AI Response Container
interface AIResponseProps {
  content: string
  isStreaming?: boolean
  className?: string
}

export function AIResponse({ content, isStreaming = false, className }: AIResponseProps) {
  return (
    <div
      className={cn(
        "relative rounded-2xl p-6",
        "bg-gradient-to-br from-[var(--color-bg-secondary)] to-[var(--color-bg-tertiary)]",
        "border border-white/5",
        "shadow-xl shadow-black/20",
        className
      )}
    >
      {/* Subtle glow effect */}
      <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-[var(--color-accent-primary)]/5 to-transparent" />

      <div className="relative">
        {isStreaming ? (
          <StreamingText
            text={content}
            className="leading-relaxed text-[var(--color-text-primary)]"
          />
        ) : (
          <p className="leading-relaxed whitespace-pre-wrap text-[var(--color-text-primary)]">
            {content}
          </p>
        )}
      </div>
    </div>
  )
}
