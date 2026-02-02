"use client";

import { useState, useRef, useEffect } from "react";
import { Search, X, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: (query: string) => void;
  isLoading: boolean;
  placeholder?: string;
}

export function SearchInput({
  value,
  onChange,
  onSearch,
  isLoading,
  placeholder = "Search for Arabic roots...",
}: SearchInputProps) {
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);

  const handleInputChange = (newValue: string) => {
    onChange(newValue);
    
    // Clear existing timer
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    // Debounce search with 300ms delay
    if (newValue.trim()) {
      debounceTimer.current = setTimeout(() => {
        onSearch(newValue);
      }, 300);
    }
  };

  const handleClear = () => {
    onChange("");
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && value.trim()) {
      e.preventDefault();
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
      onSearch(value);
    }
  };

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, []);

  return (
    <div className="space-y-2">
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-[18px] w-[18px] text-[var(--color-text-muted)]" />
        <input
          type="text"
          dir="auto"
          value={value}
          onChange={(e) => handleInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading}
          className={cn(
            "w-full h-12 pl-12 pr-24 bg-[var(--color-bg-surface)] rounded-xl",
            "text-[var(--color-text-primary)] placeholder:text-[var(--color-text-muted)]",
            "border border-[var(--color-border-subtle)]",
            "focus:border-[var(--color-border-glow)] focus:outline-none",
            "transition-all duration-300 text-[15px]",
            "disabled:opacity-50 disabled:cursor-not-allowed"
          )}
        />
        
        {/* Clear button */}
        {value && !isLoading && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute right-20 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors"
            aria-label="Clear search"
          >
            <X className="h-4 w-4" />
          </button>
        )}

        {/* Loading spinner */}
        {isLoading && (
          <div className="absolute right-20 top-1/2 -translate-y-1/2">
            <Loader2 className="h-4 w-4 text-[var(--color-accent-primary)] animate-spin" />
          </div>
        )}

        {/* Search button */}
        <Button
          type="button"
          onClick={() => value.trim() && onSearch(value)}
          disabled={isLoading || !value.trim()}
          className="absolute right-2 top-1/2 -translate-y-1/2 bg-[var(--color-accent-primary)] text-[#09090b] hover:bg-[var(--color-accent-hover)] font-medium rounded-lg px-5 h-8 text-sm tracking-wide disabled:opacity-40"
        >
          {isLoading ? "Searching..." : "Search"}
        </Button>
      </div>

      {/* Helper text */}
      <p className="text-xs text-[var(--color-text-muted)] pl-1">
        Supports Arabic (كتب) and Buckwalter Latin (ktb)
      </p>
    </div>
  );
}
