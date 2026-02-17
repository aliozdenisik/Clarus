"use client"

import { useState, useEffect } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { cn } from "@/lib/utils"

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
          <blockquote className="font-[family-name:var(--font-display)] text-2xl leading-[1.5] font-medium tracking-[0.01em] text-[#FAFAFA] md:text-3xl lg:text-[32px]">
            &quot;{quotes[currentIndex].text}&quot;
          </blockquote>
          <motion.div
            className="mt-12 flex items-center justify-center gap-4"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <div className="h-px w-10 bg-white/[0.15]" />
            <cite className="text-[13px] font-medium tracking-[0.08em] text-[#D1D5DB] uppercase not-italic">
              {quotes[currentIndex].source}
            </cite>
            <div className="h-px w-10 bg-white/[0.15]" />
          </motion.div>
        </motion.div>
      </AnimatePresence>

      <div className="mt-14 flex justify-center gap-2">
        {quotes.map((quote, index) => (
          <button
            type="button"
            key={`${quote.source}-${quote.text}`}
            onClick={() => setCurrentIndex(index)}
            className={cn(
              "h-2 w-2 rounded-full transition-all duration-300",
              index === currentIndex ? "w-8 bg-amber-500" : "bg-[#6B7280] hover:bg-[#9CA3AF]"
            )}
            aria-label={`Go to quote ${index + 1}`}
          />
        ))}
      </div>
    </div>
  )
}
