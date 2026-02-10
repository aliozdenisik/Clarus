"use client"

import { Search, X, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  onSearch: (query: string) => void
  isLoading: boolean
  placeholder?: string
}

export function SearchInput({
  value,
  onChange,
  onSearch,
  isLoading,
  placeholder = "Search for Arabic roots...",
}: SearchInputProps) {
  const handleClear = () => {
    onChange("")
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && value.trim()) {
      e.preventDefault()
      onSearch(value)
    }
  }

  return (
    <div className="space-y-2">
      <div className="relative">
        <Search className="absolute top-1/2 left-4 h-[18px] w-[18px] -translate-y-1/2 text-[var(--color-text-muted)]" />
        <input
          type="text"
          dir="auto"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          className={cn(
            "h-12 w-full rounded-xl bg-[var(--color-bg-surface)] pr-24 pl-12",
            "text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]",
            "border border-[var(--color-border-subtle)]",
            "focus:border-[var(--color-border-glow)] focus:outline-none",
            "text-[15px] transition-all duration-300",
            "disabled:cursor-not-allowed disabled:opacity-50"
          )}
        />

        {/* Clear button */}
        {value && !isLoading && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute top-1/2 right-20 -translate-y-1/2 text-[var(--color-text-muted)] transition-colors hover:text-[var(--color-text-primary)]"
            aria-label="Clear search"
          >
            <X className="h-4 w-4" />
          </button>
        )}

        {/* Loading spinner */}
        {isLoading && (
          <div className="absolute top-1/2 right-20 -translate-y-1/2">
            <Loader2 className="h-4 w-4 animate-spin text-[var(--color-accent-primary)]" />
          </div>
        )}

        {/* Search button */}
        <Button
          type="button"
          onClick={() => value.trim() && onSearch(value)}
          disabled={isLoading || !value.trim()}
          className="absolute top-1/2 right-2 h-8 -translate-y-1/2 rounded-lg bg-[var(--color-accent-primary)] px-5 text-sm font-medium tracking-wide text-[#09090b] hover:bg-[var(--color-accent-hover)] disabled:opacity-40"
        >
          {isLoading ? "Searching..." : "Search"}
        </Button>
      </div>

      {/* Helper text */}
      <p className="pl-1 text-xs text-[var(--color-text-muted)]">
        Supports Arabic (كتب) and Buckwalter Latin (ktb)
      </p>
    </div>
  )
}
