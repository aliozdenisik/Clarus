"use client";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

export const TRANSLATORS = [
  { key: "diyanet", label: "Diyanet İşleri", shortLabel: "Diyanet" },
  { key: "yazir", label: "Elmalılı Hamdi Yazır", shortLabel: "Yazır" },
  { key: "ates", label: "Süleyman Ateş", shortLabel: "Ateş" },
  { key: "bulac", label: "Ali Bulaç", shortLabel: "Bulaç" },
  { key: "ozturk", label: "Yaşar Nuri Öztürk", shortLabel: "Öztürk" },
  { key: "vakfi", label: "Türk Vakfı", shortLabel: "Vakfı" },
  { key: "yildirim", label: "Suat Yıldırım", shortLabel: "Yıldırım" },
  { key: "yuksel", label: "Edip Yüksel", shortLabel: "Yüksel" },
] as const;

interface TranslatorSelectorProps {
  value: string;
  onChange: (translator: string) => void;
}

export function TranslatorSelector({
  value,
  onChange,
}: TranslatorSelectorProps) {
  // Display logic for badge text
  const getBadgeText = () => {
    const selected = TRANSLATORS.find((t) => t.key === value);
    return `Translator: ${selected?.shortLabel ?? "Diyanet"}`;
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          className={cn(
            "shrink-0 h-11 px-3 rounded-lg text-sm font-medium",
            "bg-[var(--color-bg-surface)] text-[var(--color-text-secondary)]",
            "border border-[var(--color-border-subtle)]",
            "hover:border-[var(--color-border-glow)] transition-colors duration-200",
            "focus:outline-none focus:ring-1 focus:ring-[var(--color-accent-primary)]/20 focus:border-[var(--color-accent-primary)]"
          )}
        >
          {getBadgeText()}
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuRadioGroup value={value} onValueChange={onChange}>
          {TRANSLATORS.map((translator) => (
            <DropdownMenuRadioItem key={translator.key} value={translator.key}>
              <span className="flex items-center justify-between w-full">
                <span className="font-medium">{translator.label}</span>
                <span className="text-[var(--color-text-muted)] text-xs ml-3 font-normal">
                  {translator.shortLabel.toUpperCase()}
                </span>
              </span>
            </DropdownMenuRadioItem>
          ))}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
