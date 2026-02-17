import { ReactNode } from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { ArrowRight, type LucideIcon } from "lucide-react"

interface BentoGridProps {
  children: ReactNode
  className?: string
}

/**
 * BentoGrid - Responsive grid container for BentoCard components
 *
 * Default: 1 column mobile, 3 columns on md+
 * Add `auto-rows-[22rem]` to className for fixed row heights
 * Add `lg:grid-rows-3` for explicit row control
 */
export const BentoGrid = ({ children, className }: BentoGridProps) => {
  return (
    <div
      className={cn("grid w-full auto-rows-[22rem] grid-cols-1 gap-6 md:grid-cols-3", className)}
    >
      {children}
    </div>
  )
}

interface BentoCardProps {
  name: string
  className?: string
  background: ReactNode
  Icon: LucideIcon
  description: string
  href: string
  cta: string
  isPrimary?: boolean
}

/**
 * BentoCard - Feature card with hover animations
 *
 * Hover effects:
 * - Content shifts up (-translate-y-10)
 * - Icon scales down (scale-75)
 * - CTA button reveals from bottom
 * - Subtle overlay appears
 */
export const BentoCard = ({
  name,
  className,
  background,
  Icon,
  description,
  href,
  cta,
  isPrimary,
}: BentoCardProps) => (
  <div
    className={cn(
      "group relative col-span-3 flex flex-col justify-between overflow-hidden rounded-xl md:col-span-1",
      // Glassmorphism styling
      "border border-white/[0.10] bg-white/[0.03] backdrop-blur-xl",
      "shadow-inner-[inset_0_1px_0_rgba(255,255,255,0.05)] shadow-[0_8px_32px_rgba(0,0,0,0.4)]",
      // Hover state
      "transform-gpu transition-all duration-500 ease-out",
      "hover:-translate-y-1 hover:border-white/[0.18] hover:shadow-[0_12px_48px_rgba(0,0,0,0.5)]",
      // Primary card emphasis
      isPrimary && "border-[var(--color-accent-primary)]/30 shadow-[0_0_24px_rgba(79,70,229,0.12)]",
      className
    )}
  >
    {/* Background element (images, patterns, etc.) */}
    <div>{background}</div>

    {/* Content section - shifts up on hover */}
    <div
      className={cn(
        "pointer-events-none z-10 flex transform-gpu flex-col gap-1 p-8",
        "transition-all duration-300 group-hover:-translate-y-10"
      )}
    >
      <Icon
        className={cn(
          "h-12 w-12 origin-left transform-gpu text-[var(--color-accent-primary)]",
          "transition-all duration-300 ease-in-out group-hover:scale-75"
        )}
      />
      <h3 className="text-xl font-semibold text-[var(--color-text-primary)]">{name}</h3>
      <p className="max-w-lg text-[var(--color-text-secondary)]">
        {description.split(/(\d[\d.,]*\d)/g).map((part) =>
          /^\d[\d.,]*\d$/.test(part) ? (
            <span key={`num-${part}`} className="font-semibold text-[var(--color-text-primary)]">
              {part}
            </span>
          ) : (
            part
          )
        )}
      </p>
    </div>

    {/* CTA button - reveals on hover */}
    <div
      className={cn(
        "pointer-events-none absolute bottom-0 flex w-full translate-y-10 transform-gpu flex-row items-center p-4",
        "opacity-0 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100"
      )}
    >
      <Button variant="ghost" asChild size="sm" className="pointer-events-auto">
        <a href={href}>
          {cta}
          <ArrowRight className="ml-2 h-4 w-4" />
        </a>
      </Button>
    </div>

    {/* Hover overlay */}
    <div
      className={cn(
        "pointer-events-none absolute inset-0 transform-gpu transition-all duration-300",
        "group-hover:bg-[var(--color-accent-primary)]/[.03]"
      )}
    />
  </div>
)
