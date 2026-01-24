// Spring animation presets (Framer Motion)
export const springPresets = {
  snappy: { type: "spring" as const, stiffness: 300, damping: 30 },
  fluid: { type: "spring" as const, stiffness: 170, damping: 26 },
  gentle: { type: "spring" as const, stiffness: 120, damping: 14 },
} as const;

export const defaultTransition = springPresets.snappy;

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
} as const;
