"use client"

import type { ReactNode } from "react"

import { MagicCard } from "@/components/ui/magic-card"
import { cn } from "@/lib/utils"

interface GlowCardProps {
  children?: ReactNode
  className?: string
}

export function GlowCard({ children, className }: GlowCardProps) {
  return (
    <MagicCard
      className={cn(
        "rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/60 p-6",
        className
      )}
      gradientSize={200}
      gradientColor="#1a1a2e"
      gradientFrom="#7c3aed"
      gradientTo="#4f46e5"
    >
      {children}
    </MagicCard>
  )
}
