// Spring animation presets (Framer Motion)
export const springPresets = {
  snappy: { type: "spring" as const, stiffness: 300, damping: 30 },
  fluid: { type: "spring" as const, stiffness: 170, damping: 26 },
  gentle: { type: "spring" as const, stiffness: 120, damping: 14 },
  bouncy: { type: "spring" as const, stiffness: 400, damping: 10 },
  heavy: { type: "spring" as const, stiffness: 80, damping: 20 },
} as const

export const defaultTransition = springPresets.snappy

// Color tokens (matching CSS variables)
export const colors = {
  bgApp: "var(--color-bg-app)",
  bgSurface: "var(--color-bg-surface)",
  bgElevated: "var(--color-bg-elevated)",
  borderSubtle: "var(--color-border-subtle)",
  borderGlow: "var(--color-border-glow)",
  textPrimary: "var(--color-text-primary)",
  textSecondary: "var(--color-text-secondary)",
  textMuted: "var(--color-text-muted)",
  accentPrimary: "var(--color-accent-primary)",
  accentGlow: "var(--color-accent-glow)",
} as const

// Tactile interaction tokens (scale/position for press/hover states)
export const tactileScale = {
  press: { scale: 0.98 },
  release: { scale: 1.0 },
  hover: { y: -2 },
} as const
