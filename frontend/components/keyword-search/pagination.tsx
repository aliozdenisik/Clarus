"use client"

import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

interface PaginationProps {
  page: number
  totalPages: number
  totalVerses: number
  hasNext: boolean
  hasPrev: boolean
  onPageChange: (page: number) => void
}

export function Pagination({
  page,
  totalPages,
  totalVerses,
  hasNext,
  hasPrev,
  onPageChange,
}: PaginationProps) {
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-center gap-4 py-4">
      <Button
        variant="ghost"
        size="sm"
        disabled={!hasPrev}
        onClick={() => onPageChange(page - 1)}
        className="text-[var(--color-text-secondary)]"
      >
        <ChevronLeft className="mr-1 h-4 w-4" />
        Previous
      </Button>

      <span className="text-sm text-[var(--color-text-muted)]">
        Page {page} of {totalPages} ({totalVerses} verses)
      </span>

      <Button
        variant="ghost"
        size="sm"
        disabled={!hasNext}
        onClick={() => onPageChange(page + 1)}
        className="text-[var(--color-text-secondary)]"
      >
        Next
        <ChevronRight className="ml-1 h-4 w-4" />
      </Button>
    </div>
  )
}
