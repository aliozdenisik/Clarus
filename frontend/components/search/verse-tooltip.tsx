"use client"

import * as Popover from "@radix-ui/react-popover"
import { SourceBadge, SourceType } from "@/components/compare/source-badge"
import { Button } from "@/components/ui/button"
import { ExternalLink } from "lucide-react"

export interface VerseDetail {
  text: string
  book_name?: string
  chapter?: number
  verse?: number
  source: string
  translation?: string
  book_nr?: number
  surah_id?: number
  surah_name?: string
  verse_id?: number
}

interface VerseTooltipProps {
  reference: string
  verseDetail?: VerseDetail
  children: React.ReactNode
  onNavigate?: (reference: string) => void
  isOpen?: boolean
  onOpenChange?: (open: boolean) => void
}

function mapSourceToType(source: string): SourceType {
  switch (source) {
    case "quran":
      return "quran"
    case "bible_ot":
    case "old_testament":
      return "old_testament"
    case "bible_nt":
    case "new_testament":
      return "new_testament"
    case "bible_apocrypha":
    case "apocrypha":
      return "apocrypha"
    default:
      return "quran"
  }
}

function truncateText(text: string, maxLength: number = 200): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength).trim() + "..."
}

export function VerseTooltip({
  reference,
  verseDetail,
  children,
  onNavigate,
  isOpen,
  onOpenChange,
}: VerseTooltipProps) {
  if (!verseDetail) {
    return <>{children}</>
  }

  const sourceType = mapSourceToType(verseDetail.source)
  const displayText = truncateText(verseDetail.text)

  return (
    <Popover.Root open={isOpen} onOpenChange={onOpenChange}>
      <Popover.Trigger asChild>{children}</Popover.Trigger>
      <Popover.Portal>
        <Popover.Content
          className="animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 z-50 w-80 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-elevated)] p-4 shadow-xl backdrop-blur-sm"
          sideOffset={8}
          align="start"
        >
          <div className="space-y-3">
            <div className="flex items-start justify-between gap-2">
              <h4 className="text-sm font-semibold text-[var(--color-text-primary)]">
                {reference}
              </h4>
              <SourceBadge source={sourceType} />
            </div>

            <p className="text-sm leading-relaxed text-[var(--color-text-secondary)]">
              &ldquo;{displayText}&rdquo;
            </p>

            {verseDetail.translation && (
              <p className="text-xs text-[var(--color-text-muted)]">{verseDetail.translation}</p>
            )}

            {onNavigate && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onNavigate(reference)}
                className="w-full justify-center gap-2 text-[var(--color-accent-primary)] hover:bg-[var(--color-bg-tertiary)]"
              >
                <ExternalLink className="h-3 w-3" />
                Go to verse
              </Button>
            )}
          </div>

          <Popover.Arrow className="fill-[var(--color-bg-elevated)]" />
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  )
}
