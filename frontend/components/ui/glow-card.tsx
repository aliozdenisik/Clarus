"use client"

import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { cn } from "@/lib/utils"

interface GlowCardProps {
  children: React.ReactNode
  className?: string
}

export function GlowCard({ children, className }: GlowCardProps) {
  return (
    <motion.div
      className={cn(
        "relative rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] p-6",
        className
      )}
      whileHover={{
        borderColor: "var(--color-border-glow)",
      }}
      transition={springPresets.snappy}
    >
      {children}
    </motion.div>
  )
}
