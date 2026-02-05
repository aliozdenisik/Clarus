"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";
import { BookOpen, BookText, Cross, ScrollText } from "lucide-react";

export interface CollectionOption {
  id: string;
  label: string;
  labelTr: string;
  icon: React.ReactNode;
}

export const COLLECTION_OPTIONS: CollectionOption[] = [
  {
    id: "quran_tr",
    label: "Quran",
    labelTr: "Kuran",
    icon: <BookOpen className="w-4 h-4" />,
  },
  {
    id: "bible_ot",
    label: "Old Testament",
    labelTr: "Eski Ahit",
    icon: <ScrollText className="w-4 h-4" />,
  },
  {
    id: "bible_nt",
    label: "New Testament",
    labelTr: "Yeni Ahit",
    icon: <Cross className="w-4 h-4" />,
  },
  {
    id: "bible_apocrypha",
    label: "Apocrypha",
    labelTr: "Apokrifa",
    icon: <BookText className="w-4 h-4" />,
  },
];

export interface CollectionSelectorProps {
  selected: string[];
  onChange: (collections: string[]) => void;
  minSelection?: number;
  disabled?: boolean;
  className?: string;
}

export function CollectionSelector({
  selected,
  onChange,
  minSelection = 2,
  disabled = false,
  className,
}: CollectionSelectorProps) {
  const toggleCollection = (collectionId: string) => {
    if (disabled) return;

    const isSelected = selected.includes(collectionId);

    if (isSelected) {
      // Don't allow deselecting if it would go below minimum
      if (selected.length <= minSelection) return;
      onChange(selected.filter((id) => id !== collectionId));
    } else {
      onChange([...selected, collectionId]);
    }
  };

  const selectionCount = selected.length;
  const isMinimumMet = selectionCount >= minSelection;

  return (
    <div className={cn("w-full", className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <label className="text-sm font-medium text-[var(--color-text-secondary)]">
          Karşılaştırılacak Kaynaklar
        </label>
        <span
          className={cn(
            "text-xs font-medium px-2 py-0.5 rounded-full transition-colors",
            isMinimumMet
              ? "bg-emerald-500/10 text-emerald-400"
              : "bg-amber-500/10 text-amber-400"
          )}
        >
          {selectionCount} / {COLLECTION_OPTIONS.length} seçili
        </span>
      </div>

      {/* Collection Chips */}
      <div className="flex flex-wrap gap-2 p-4 bg-[var(--color-bg-surface)]/50 rounded-2xl border border-white/5">
        {COLLECTION_OPTIONS.map((option) => {
          const isSelected = selected.includes(option.id);
          const canDeselect = selected.length > minSelection;

          return (
            <motion.button
              key={option.id}
              type="button"
              onClick={() => toggleCollection(option.id)}
              disabled={disabled || (isSelected && !canDeselect)}
              initial={false}
              animate={{
                backgroundColor: isSelected
                  ? "rgba(99, 102, 241, 0.9)"
                  : "rgba(39, 39, 42, 0.8)",
                borderColor: isSelected
                  ? "rgba(99, 102, 241, 1)"
                  : "rgba(63, 63, 70, 0.5)",
                scale: isSelected ? 1.02 : 1,
              }}
              whileHover={{
                scale: disabled ? 1 : 1.05,
                backgroundColor: isSelected
                  ? "rgba(99, 102, 241, 1)"
                  : "rgba(39, 39, 42, 1)",
              }}
              whileTap={{ scale: disabled ? 1 : 0.98 }}
              transition={{
                backgroundColor: { duration: 0.15 },
                borderColor: { duration: 0.15 },
                scale: { type: "spring", stiffness: 400, damping: 25 },
              }}
              className={cn(
                "flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium",
                "border transition-shadow cursor-pointer",
                "focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-primary)]/50",
                isSelected
                  ? "text-white shadow-lg shadow-indigo-500/20"
                  : "text-[var(--color-text-secondary)]",
                disabled && "opacity-50 cursor-not-allowed",
                isSelected && !canDeselect && "cursor-not-allowed"
              )}
            >
              {/* Icon */}
              <span
                className={cn(
                  "transition-colors",
                  isSelected
                    ? "text-white"
                    : "text-[var(--color-text-muted)]"
                )}
              >
                {option.icon}
              </span>

              {/* Label */}
              <span>{option.labelTr}</span>

              {/* Checkmark */}
              <motion.span
                animate={{
                  width: isSelected ? 18 : 0,
                  marginLeft: isSelected ? 4 : 0,
                  opacity: isSelected ? 1 : 0,
                }}
                transition={{ type: "spring", stiffness: 500, damping: 30 }}
                className="flex items-center overflow-hidden"
              >
                <AnimatePresence>
                  {isSelected && (
                    <motion.svg
                      key="tick"
                      width="18"
                      height="18"
                      viewBox="0 0 20 20"
                      fill="none"
                      initial={{ scale: 0, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      exit={{ scale: 0, opacity: 0 }}
                      transition={{
                        type: "spring",
                        stiffness: 500,
                        damping: 20,
                      }}
                    >
                      <motion.path
                        d="M5 10.5L9 14.5L15 7.5"
                        stroke="currentColor"
                        strokeWidth="2.2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: 1 }}
                        transition={{ duration: 0.25 }}
                      />
                    </motion.svg>
                  )}
                </AnimatePresence>
              </motion.span>
            </motion.button>
          );
        })}
      </div>

      {/* Validation Message */}
      <AnimatePresence>
        {!isMinimumMet && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-2 text-xs text-amber-400"
          >
            En az {minSelection} kaynak seçilmelidir
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
}

export default CollectionSelector;
