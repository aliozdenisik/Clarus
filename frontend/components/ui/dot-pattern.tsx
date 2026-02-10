"use client"

import { useId } from "react"
import { cn } from "@/lib/utils"

interface DotPatternProps {
  width?: number
  height?: number
  x?: number
  y?: number
  cx?: number
  cy?: number
  cr?: number
  className?: string
}

export function DotPattern({
  width = 24,
  height = 24,
  x = 0,
  y = 0,
  cx = 1,
  cy = 0.5,
  cr = 0.5,
  className,
  ...props
}: DotPatternProps) {
  const id = useId()

  return (
    <svg
      aria-hidden="true"
      className={cn(
        "pointer-events-none absolute inset-0 h-full w-full fill-white/[0.03]",
        className
      )}
      {...props}
    >
      <defs>
        <pattern
          id={id}
          width={width}
          height={height}
          patternUnits="userSpaceOnUse"
          patternContentUnits="userSpaceOnUse"
          x={x}
          y={y}
        >
          <circle id="pattern-circle" cx={cx} cy={cy} r={cr} />
        </pattern>
      </defs>
      <rect width="100%" height="100%" strokeWidth={0} fill={`url(#${id})`} />
    </svg>
  )
}

// Grid pattern for backgrounds
interface GridPatternProps {
  size?: number
  className?: string
}

export function GridPattern({ size = 60, className }: GridPatternProps) {
  return (
    <div
      className={cn("pointer-events-none absolute inset-0 opacity-[0.02]", className)}
      style={{
        backgroundImage: `
          linear-gradient(to right, currentColor 1px, transparent 1px),
          linear-gradient(to bottom, currentColor 1px, transparent 1px)
        `,
        backgroundSize: `${size}px ${size}px`,
      }}
    />
  )
}

// Radial gradient overlay
interface RadialGradientProps {
  className?: string
  color?: string
  size?: string
  position?: string
  opacity?: number
}

export function RadialGradient({
  className,
  color = "var(--color-accent-primary)",
  size = "600px",
  position = "center",
  opacity = 0.15,
}: RadialGradientProps) {
  return (
    <div
      className={cn("pointer-events-none absolute", className)}
      style={{
        background: `radial-gradient(${size} circle at ${position}, ${color}, transparent)`,
        opacity,
      }}
    />
  )
}

// Noise texture overlay
export function NoiseTexture({ className }: { className?: string }) {
  return (
    <div
      className={cn("pointer-events-none absolute inset-0 opacity-[0.015]", className)}
      style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E")`,
      }}
    />
  )
}

// Luxury card with decorative elements
interface LuxuryCardProps {
  children: React.ReactNode
  className?: string
  variant?: "default" | "elevated" | "glowing"
  accentColor?: string
}

export function LuxuryCard({
  children,
  className,
  variant = "default",
  accentColor = "var(--color-accent-primary)",
}: LuxuryCardProps) {
  const variants = {
    default: "bg-[var(--color-bg-secondary)] border-white/5",
    elevated: "bg-[var(--color-bg-elevated)] border-white/10 shadow-xl shadow-black/20",
    glowing: "bg-[var(--color-bg-secondary)] border-white/10",
  }

  return (
    <div
      className={cn("relative overflow-hidden rounded-2xl border", variants[variant], className)}
    >
      {/* Corner accents for luxury feel */}
      {variant === "glowing" && (
        <>
          <div
            className="absolute -top-1 -left-1 h-3 w-3"
            style={{ backgroundColor: accentColor }}
          />
          <div
            className="absolute -top-1 -right-1 h-3 w-3"
            style={{ backgroundColor: accentColor }}
          />
          <div
            className="absolute -bottom-1 -left-1 h-3 w-3"
            style={{ backgroundColor: accentColor }}
          />
          <div
            className="absolute -right-1 -bottom-1 h-3 w-3"
            style={{ backgroundColor: accentColor }}
          />
        </>
      )}

      {/* Dot pattern background */}
      <DotPattern width={8} height={8} cr={0.3} className="z-0" />

      {/* Gradient overlay */}
      {variant === "glowing" && (
        <div
          className="pointer-events-none absolute inset-0 opacity-10"
          style={{
            background: `radial-gradient(circle at 50% 0%, ${accentColor}, transparent 50%)`,
          }}
        />
      )}

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </div>
  )
}

// Quote card with luxury styling
interface LuxuryQuoteCardProps {
  quote: string
  source: string
  sourceDetail?: string
  accentColor?: string
  className?: string
}

export function LuxuryQuoteCard({
  quote,
  source,
  sourceDetail,
  accentColor = "var(--color-accent-primary)",
  className,
}: LuxuryQuoteCardProps) {
  return (
    <LuxuryCard variant="glowing" accentColor={accentColor} className={className}>
      <div className="p-6 md:p-8">
        {/* Quote mark */}
        <div
          className="mb-4 font-serif text-6xl leading-none opacity-20"
          style={{ color: accentColor }}
        >
          &quot;
        </div>

        {/* Quote text */}
        <blockquote className="mb-6 text-lg leading-relaxed font-light text-[var(--color-text-primary)] italic md:text-xl">
          {quote}
        </blockquote>

        {/* Divider */}
        <div className="mb-4 flex items-center gap-3">
          <div
            className="h-px flex-1"
            style={{
              background: `linear-gradient(to right, transparent, ${accentColor}40, transparent)`,
            }}
          />
        </div>

        {/* Source */}
        <div className="text-right">
          <cite className="not-italic">
            <span className="font-medium text-[var(--color-text-primary)]">{source}</span>
            {sourceDetail && (
              <span className="ml-2 text-sm text-[var(--color-text-secondary)]">
                — {sourceDetail}
              </span>
            )}
          </cite>
        </div>
      </div>
    </LuxuryCard>
  )
}
