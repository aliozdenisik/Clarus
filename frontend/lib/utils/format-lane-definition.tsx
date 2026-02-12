import type { ReactNode } from "react"

interface LaneSection {
  code: string
  label: string
  variant: "entry" | "sub" | "main"
}

function parseSectionCode(code: string): LaneSection | null {
  const subMatch = code.match(/^-b(\d+)[.-]$/)
  if (subMatch) {
    return { code, label: `Yakın Anlam`, variant: "sub" }
  }

  const mainMatch = code.match(/^-A(\d+)[.-]$/)
  if (mainMatch) {
    return { code, label: `Farklı Anlam`, variant: "main" }
  }

  return null
}

const VARIANT_STYLES: Record<LaneSection["variant"], string> = {
  entry:
    "inline-flex items-center rounded-md bg-zinc-700/50 px-1.5 py-0.5 text-[10px] font-semibold tabular-nums text-zinc-300",
  sub: "inline-flex items-center rounded-md border border-sky-500/30 bg-sky-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-sky-400",
  main: "inline-flex items-center rounded-md border border-amber-500/30 bg-amber-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-amber-400",
}

/**
 * Replaces Lane's Lexicon section codes (-b2-, -A3-) and entry numbers (1., 2.)
 * with styled badges. Required because Lane's 1863 reference codes are opaque
 * to non-specialist readers.
 */
export function formatLaneDefinition(text: string): ReactNode[] {
  // (-[bA]\d+[.-]) captures EN (-b2-) and TR (-b2.) section codes
  const pattern = /(-[bA]\d+[.-])|(?:^|\n)(\d+)\.\s/gm
  const parts: ReactNode[] = []
  let lastIndex = 0
  let key = 0

  let match: RegExpExecArray | null
  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      const beforeText = text.slice(lastIndex, match.index)
      if (beforeText) {
        parts.push(beforeText)
      }
    }

    if (match[1]) {
      const section = parseSectionCode(match[1])
      if (section) {
        parts.push(
          <span key={`lane-section-${key++}`} className="block pt-3 pb-1">
            <span
              className={VARIANT_STYLES[section.variant]}
              title={`Lane's Lexicon: ${section.code}`}
            >
              {section.label}
            </span>
          </span>
        )
      } else {
        parts.push(match[1])
      }
    } else if (match[2]) {
      const num = match[2]
      const startsWithNewline = match[0].startsWith("\n")
      if (startsWithNewline) {
        parts.push(
          <span key={`lane-break-${key++}`} className="block pt-4 pb-1">
            <span className={VARIANT_STYLES.entry} title={`Madde ${num}`}>
              {num}
            </span>
          </span>
        )
      } else {
        parts.push(
          <span key={`lane-entry-${key++}`} className="inline-block pr-1 pb-1">
            <span className={VARIANT_STYLES.entry} title={`Madde ${num}`}>
              {num}
            </span>
          </span>
        )
      }
    }

    lastIndex = match.index + match[0].length
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex))
  }

  return parts
}
