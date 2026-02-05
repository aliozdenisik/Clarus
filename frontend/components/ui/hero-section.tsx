"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { Search, Sparkles, BookOpen, ArrowRight } from "lucide-react";
import { ReactNode } from "react";

interface HeroSectionProps {
  title: string;
  subtitle: string;
  ctaText?: string;
  onCtaClick?: () => void;
  searchPlaceholder?: string;
  onSearch?: (query: string) => void;
  className?: string;
  children?: ReactNode;
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
        "relative min-h-[80vh] flex flex-col items-center justify-center overflow-hidden",
        "px-4 py-20",
        className
      )}
    >
      {/* Background gradient effects */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Top right gradient */}
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-[var(--color-accent-primary)]/20 rounded-full blur-3xl" />
        {/* Bottom left gradient */}
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-[var(--color-accent-secondary)]/20 rounded-full blur-3xl" />
        {/* Center subtle glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[var(--color-accent-primary)]/5 rounded-full blur-3xl" />
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
      <div className="relative z-10 max-w-4xl mx-auto text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8"
        >
          <Sparkles className="w-4 h-4 text-[var(--color-accent-primary)]" />
          <span className="text-sm text-[var(--color-text-secondary)]">
            AI-Powered Sacred Text Analysis
          </span>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold text-white leading-tight mb-6"
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
          className="text-lg md:text-xl text-[var(--color-text-secondary)] max-w-2xl mx-auto mb-10 leading-relaxed"
        >
          {subtitle}
        </motion.p>

        {/* Search bar */}
        {onSearch && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="relative max-w-xl mx-auto mb-8"
          >
            <div className="relative group">
              {/* Glow effect on focus */}
              <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-[var(--color-accent-primary)]/20 to-[var(--color-accent-secondary)]/20 opacity-0 group-focus-within:opacity-100 blur-xl transition-opacity duration-500" />

              <div className="relative flex items-center bg-[var(--color-bg-secondary)] border border-white/10 rounded-2xl overflow-hidden">
                <div className="pl-5">
                  <BookOpen className="w-5 h-5 text-[var(--color-text-tertiary)]" />
                </div>
                <input
                  type="text"
                  placeholder={searchPlaceholder}
                  className="flex-1 px-4 py-4 bg-transparent text-[var(--color-text-primary)] placeholder:text-[var(--color-text-tertiary)] focus:outline-none"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      onSearch((e.target as HTMLInputElement).value);
                    }
                  }}
                />
                <button
                  onClick={() => {
                    const input = document.querySelector("input") as HTMLInputElement;
                    onSearch(input?.value || "");
                  }}
                  className="m-2 p-3 rounded-xl bg-[var(--color-accent-primary)] text-white hover:bg-[var(--color-accent-primary)]/90 transition-colors"
                >
                  <Search className="w-5 h-5" />
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
            className="group inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-[var(--color-accent-primary)] to-[var(--color-accent-secondary)] text-white font-semibold hover:opacity-90 transition-all duration-300 shadow-lg shadow-[var(--color-accent-primary)]/25"
          >
            {ctaText}
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </motion.button>
        )}

        {/* Quick suggestion pills */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.5 }}
          className="flex flex-wrap justify-center gap-2 mt-10"
        >
          {["Creation story", "Love and forgiveness", "Patience", "Prayer"].map(
            (suggestion) => (
              <button
                key={suggestion}
                onClick={() => onSearch?.(suggestion)}
                className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-[var(--color-text-secondary)] hover:bg-white/10 hover:border-white/20 transition-all duration-300"
              >
                {suggestion}
              </button>
            )
          )}
        </motion.div>

        {children}
      </div>
    </section>
  );
}

// Minimal Hero for inner pages
interface MinimalHeroProps {
  title: string;
  subtitle?: string;
  className?: string;
}

export function MinimalHero({ title, subtitle, className }: MinimalHeroProps) {
  return (
    <section className={cn("relative py-16 text-center", className)}>
      {/* Subtle background gradient */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[200px] bg-[var(--color-accent-primary)]/10 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10">
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-3xl md:text-4xl font-bold text-white mb-4"
        >
          {title}
        </motion.h1>
        {subtitle && (
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-[var(--color-text-secondary)] max-w-xl mx-auto"
          >
            {subtitle}
          </motion.p>
        )}
      </div>
    </section>
  );
}
