"use client"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"

export const TRANSLATORS = [
  { key: "diyanet", label: "Diyanet İşleri", shortLabel: "Diyanet" },
  { key: "yazir", label: "Elmalılı Hamdi Yazır", shortLabel: "Yazır" },
  { key: "ates", label: "Süleyman Ateş", shortLabel: "Ateş" },
  { key: "bulac", label: "Ali Bulaç", shortLabel: "Bulaç" },
  { key: "ozturk", label: "Yaşar Nuri Öztürk", shortLabel: "Öztürk" },
  { key: "vakfi", label: "Türk Vakfı", shortLabel: "Vakfı" },
  { key: "yildirim", label: "Suat Yıldırım", shortLabel: "Yıldırım" },
  { key: "yuksel", label: "Edip Yüksel", shortLabel: "Yüksel" },
] as const

export type TranslatorKey = (typeof TRANSLATORS)[number]["key"]

interface TranslatorSelectorProps {
  value: string
  onChange: (translator: TranslatorKey) => void
}

export function TranslatorSelector({ value, onChange }: TranslatorSelectorProps) {
  // Display logic for badge text
  const getBadgeText = () => {
    const selected = TRANSLATORS.find((t) => t.key === value)
    return `Translator: ${selected?.shortLabel ?? "Diyanet"}`
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className={cn(
            "h-11 shrink-0 rounded-lg px-3 text-sm font-medium",
            "bg-[var(--color-bg-surface)] text-[var(--color-text-secondary)]",
            "border border-[var(--color-border-subtle)]",
            "transition-colors duration-200 hover:border-[var(--color-border-glow)]",
            "focus:border-[var(--color-accent-primary)] focus:ring-1 focus:ring-[var(--color-accent-primary)]/20 focus:outline-none"
          )}
        >
          {getBadgeText()}
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuRadioGroup
          value={value}
          onValueChange={(val) => onChange(val as TranslatorKey)}
        >
          {TRANSLATORS.map((translator) => (
            <DropdownMenuRadioItem key={translator.key} value={translator.key}>
              <span className="flex w-full items-center justify-between">
                <span className="font-medium">{translator.label}</span>
                <span className="ml-3 text-xs font-normal text-[var(--color-text-muted)]">
                  {translator.shortLabel.toUpperCase()}
                </span>
              </span>
            </DropdownMenuRadioItem>
          ))}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
