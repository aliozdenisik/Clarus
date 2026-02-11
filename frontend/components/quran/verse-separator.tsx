export function VerseSeparator() {
  return (
    <div
      data-testid="verse-separator"
      className="h-px w-full"
      style={{
        background:
          "linear-gradient(to right, transparent, var(--color-border-subtle), transparent)",
      }}
    />
  )
}
