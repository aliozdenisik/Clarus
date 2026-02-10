"use client"

import { cn } from "@/lib/utils"
import { motion } from "framer-motion"
import { Search, Sparkles, BookOpen, ArrowRight } from "lucide-react"
import { ReactNode } from "react"

interface HeroSectionProps {
  title: string
  subtitle: string
  ctaText?: string
  onCtaClick?: () => void
  searchPlaceholder?: string
  onSearch?: (query: string) => void
  className?: string
  children?: ReactNode
}

export function HeroSection({
  title,
  subtitle,
  ctaText = "Get Started",
  onCtaClick,
  searchPlaceholder = "Search sacred texts...",
  onSearch,
  className,
  children,
}: HeroSectionProps) {
  return (
    <section
      className={cn(
        "relative flex min-h-[80vh] flex-col items-center justify-center overflow-hidden",
        "px-4 py-20",
        className
      )}
    >
      {/* Background gradient effects */}
      <div className="pointer-events-none absolute inset-0">
        {/* Top right gradient */}
        <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-[var(--color-accent-primary)]/20 blur-3xl" />
        {/* Bottom left gradient */}
        <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-[var(--color-accent-secondary)]/20 blur-3xl" />
        {/* Center subtle glow */}
        <div className="absolute top-1/2 left-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[var(--color-accent-primary)]/5 blur-3xl" />
      </div>

      {/* Animated grid pattern */}
      <div className="absolute inset-0 opacity-[0.02]">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `
              linear-gradient(to right, white 1px, transparent 1px),
              linear-gradient(to bottom, white 1px, transparent 1px)
            `,
            backgroundSize: "60px 60px",
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 mx-auto max-w-4xl text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2"
        >
          <Sparkles className="h-4 w-4 text-[var(--color-accent-primary)]" />
          <span className="text-sm text-[var(--color-text-secondary)]">
            AI-Powered Sacred Text Analysis
          </span>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mb-6 text-4xl leading-tight font-bold text-white md:text-5xl lg:text-6xl xl:text-7xl"
        >
          <span className="bg-gradient-to-r from-white via-white to-white/60 bg-clip-text text-transparent">
            {title}
          </span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mx-auto mb-10 max-w-2xl text-lg leading-relaxed text-[var(--color-text-secondary)] md:text-xl"
        >
          {subtitle}
        </motion.p>

        {/* Search bar */}
        {onSearch && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="relative mx-auto mb-8 max-w-xl"
          >
            <div className="group relative">
              {/* Glow effect on focus */}
              <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-[var(--color-accent-primary)]/20 to-[var(--color-accent-secondary)]/20 opacity-0 blur-xl transition-opacity duration-500 group-focus-within:opacity-100" />

              <div className="relative flex items-center overflow-hidden rounded-2xl border border-white/10 bg-[var(--color-bg-secondary)]">
                <div className="pl-5">
                  <BookOpen className="h-5 w-5 text-[var(--color-text-tertiary)]" />
                </div>
                <input
                  type="text"
                  placeholder={searchPlaceholder}
                  className="flex-1 bg-transparent px-4 py-4 text-[var(--color-text-primary)] placeholder:text-[var(--color-text-tertiary)] focus:outline-none"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      onSearch((e.target as HTMLInputElement).value)
                    }
                  }}
                />
                <button
                  onClick={() => {
                    const input = document.querySelector("input") as HTMLInputElement
                    onSearch(input?.value || "")
                  }}
                  className="m-2 rounded-xl bg-[var(--color-accent-primary)] p-3 text-white transition-colors hover:bg-[var(--color-accent-primary)]/90"
                >
                  <Search className="h-5 w-5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* CTA Button */}
        {onCtaClick && (
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            onClick={onCtaClick}
            className="group inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[var(--color-accent-primary)] to-[var(--color-accent-secondary)] px-8 py-4 font-semibold text-white shadow-[var(--color-accent-primary)]/25 shadow-lg transition-all duration-300 hover:opacity-90"
          >
            {ctaText}
            <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
          </motion.button>
        )}

        {/* Quick suggestion pills */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="mt-10 flex flex-wrap justify-center gap-2"
        >
          {["Creation story", "Love and forgiveness", "Patience", "Prayer"].map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => onSearch?.(suggestion)}
              className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-[var(--color-text-secondary)] transition-all duration-300 hover:border-white/20 hover:bg-white/10"
            >
              {suggestion}
            </button>
          ))}
        </motion.div>

        {children}
      </div>
    </section>
  )
}

// Minimal Hero for inner pages
interface MinimalHeroProps {
  title: string
  subtitle?: string
  className?: string
}

export function MinimalHero({ title, subtitle, className }: MinimalHeroProps) {
  return (
    <section className={cn("relative py-16 text-center", className)}>
      {/* Subtle background gradient */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-0 left-1/2 h-[200px] w-[600px] -translate-x-1/2 rounded-full bg-[var(--color-accent-primary)]/10 blur-3xl" />
      </div>

      <div className="relative z-10">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 text-3xl font-bold text-white md:text-4xl"
        >
          {title}
        </motion.h1>
        {subtitle && (
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mx-auto max-w-xl text-[var(--color-text-secondary)]"
          >
            {subtitle}
          </motion.p>
        )}
      </div>
    </section>
  )
}
