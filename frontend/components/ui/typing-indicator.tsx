"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

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
