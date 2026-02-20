"use client"

import { Search, X, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { useTranslations } from "next-intl"

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  onSearch: (query: string) => void
  isLoading: boolean
  placeholder?: string
  helperText?: string
}

export function SearchInput({
  value,
  onChange,
  onSearch,
  isLoading,
  placeholder,
  helperText,
}: SearchInputProps) {
  const t = useTranslations("KeywordSearch")

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
          aria-label={t("searchInputLabel")}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder ?? t("placeholderQuran")}
          disabled={isLoading}
          className={cn(
            "h-12 w-full rounded-xl bg-[var(--color-bg-surface)] pr-24 pl-12",
            "text-[var(--color-text-primary)] placeholder:text-[var(--color-text-secondary)]/80",
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
            className="absolute top-1/2 right-20 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-md text-[var(--color-text-muted)] transition-colors hover:text-[var(--color-text-primary)] focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:outline-none"
            aria-label={t("clearSearch")}
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
          className="absolute top-1/2 right-2 h-8 -translate-y-1/2 rounded-lg bg-gradient-to-r from-[var(--color-accent-primary)] to-indigo-500 px-5 text-sm font-medium tracking-wide text-[#09090b] shadow-[0_0_16px_rgba(79,70,229,0.28)] transition-all hover:to-indigo-400 hover:shadow-[0_0_24px_rgba(99,102,241,0.4)] disabled:opacity-40"
        >
          {isLoading ? t("searching") : t("searchButton")}
        </Button>
      </div>

      {/* Helper text */}
      <p className="pl-1 text-xs text-[var(--color-text-secondary)]">
        {helperText ?? t("helperText")}
      </p>
    </div>
  )
}
