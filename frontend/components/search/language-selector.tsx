"use client";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";

export const SUPPORTED_LANGUAGES = [
  { code: "en", label: "English", nativeName: "English" },
  { code: "tr", label: "Turkish", nativeName: "Türkçe" },
  { code: "es", label: "Spanish", nativeName: "Español" },
  { code: "fr", label: "French", nativeName: "Français" },
  { code: "it", label: "Italian", nativeName: "Italiano" },
  { code: "pt", label: "Portuguese", nativeName: "Português" },
  { code: "ar", label: "Arabic", nativeName: "العربية" },
  { code: "de", label: "German", nativeName: "Deutsch" },
] as const;

interface LanguageSelectorProps {
  value: string | null;
  onChange: (lang: string | null) => void;
  detectedLanguage?: string;
}

export function LanguageSelector({
  value,
  onChange,
  detectedLanguage,
}: LanguageSelectorProps) {
  // Convert null to "auto" for Radix RadioGroup (requires string values)
  const internalValue = value ?? "auto";

  // Handle selection change: convert "auto" back to null
  const handleValueChange = (newValue: string) => {
    onChange(newValue === "auto" ? null : newValue);
  };

  // Display logic for badge text
  const getBadgeText = () => {
    if (value === null) {
      // Auto-detect mode
      if (detectedLanguage) {
        const detected = SUPPORTED_LANGUAGES.find(
          (lang) => lang.code === detectedLanguage
        );
        return `Language: Auto (${detected?.code.toUpperCase() ?? detectedLanguage.toUpperCase()})`;
      }
      return "Language: Auto";
    }
    // Manual selection
    return `Language: ${value.toUpperCase()}`;
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
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuRadioGroup
          value={internalValue}
          onValueChange={handleValueChange}
        >
          {/* Auto-detect option */}
          <DropdownMenuRadioItem value="auto">
            <span className="flex items-center justify-between w-full">
              <span>Auto-detect</span>
              <span className="text-[var(--color-text-muted)] text-xs ml-2">
                AUTO
              </span>
            </span>
          </DropdownMenuRadioItem>

          {/* Language options */}
          {SUPPORTED_LANGUAGES.map((lang) => (
            <DropdownMenuRadioItem key={lang.code} value={lang.code}>
              <span className="flex items-center justify-between w-full">
                <span>{lang.nativeName}</span>
                <span className="text-[var(--color-text-muted)] text-xs ml-2">
                  {lang.code.toUpperCase()}
                </span>
              </span>
            </DropdownMenuRadioItem>
          ))}
        </DropdownMenuRadioGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
