"use client"

import { useState } from "react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import { Languages } from "lucide-react"

const TRANSLATORS = [
  { key: "diyanet", label: "Diyanet İşleri" },
  { key: "yazir", label: "Elmalılı Yazır" },
  { key: "ates", label: "Süleyman Ateş" },
  { key: "bulac", label: "Ali Bulaç" },
  { key: "ozturk", label: "Yaşar Nuri Öztürk" },
  { key: "vakfi", label: "Diyanet Vakfı" },
  { key: "yildirim", label: "Suat Yıldırım" },
  { key: "yuksel", label: "Edip Yüksel" },
] as const

export type TranslatorKey = (typeof TRANSLATORS)[number]["key"]

const STORAGE_KEY = "clarus:default-translator"

interface TranslationSelectorProps {
  value?: TranslatorKey
  onChange?: (translator: TranslatorKey) => void
}

export function TranslationSelector({ value, onChange }: TranslationSelectorProps) {
  const [selectedTranslator, setSelectedTranslator] = useState<TranslatorKey>(() => {
    if (typeof window !== "undefined") {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored && TRANSLATORS.some((t) => t.key === stored)) {
        return stored as TranslatorKey
      }
    }
    return "diyanet"
  })

  const handleChange = (translator: TranslatorKey) => {
    setSelectedTranslator(translator)
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEY, translator)
    }
    onChange?.(translator)
  }

  const currentTranslator = value ?? selectedTranslator
  const selected = TRANSLATORS.find((t) => t.key === currentTranslator)

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className={cn(
            "flex h-9 items-center gap-2 rounded-lg px-3 text-sm font-medium",
            "bg-[var(--color-bg-surface)] text-[var(--color-text-secondary)]",
            "border border-[var(--color-border-subtle)]",
            "transition-colors duration-200 hover:border-[var(--color-border-glow)]",
            "focus:border-[var(--color-accent-primary)] focus:ring-1 focus:ring-[var(--color-accent-primary)]/20 focus:outline-none"
          )}
        >
          <Languages className="h-4 w-4" />
          <span>{selected?.label ?? "Diyanet İşleri"}</span>
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuRadioGroup
          value={currentTranslator}
          onValueChange={(value) => handleChange(value as TranslatorKey)}
        >
          {TRANSLATORS.map((translator) => (
            <DropdownMenuRadioItem key={translator.key} value={translator.key}>
              {translator.label}
            </DropdownMenuRadioItem>
          ))}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
