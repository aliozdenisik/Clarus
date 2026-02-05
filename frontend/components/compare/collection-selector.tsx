"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

export interface CollectionOption {
  id: string;
  label: string;
  labelTr: string;
}

export const COLLECTION_OPTIONS: CollectionOption[] = [
  { id: "quran_tr", label: "Quran", labelTr: "Kuran" },
  { id: "bible_ot", label: "Old Testament", labelTr: "Eski Ahit" },
  { id: "bible_nt", label: "New Testament", labelTr: "Yeni Ahit" },
  { id: "bible_apocrypha", label: "Apocrypha", labelTr: "Apokrifa" },
];

export interface CollectionSelectorProps {
  selected: string[];
  onChange: (collections: string[]) => void;
  disabled?: boolean;
  className?: string;
}

export function CollectionSelector({
  selected,
  onChange,
  disabled = false,
  className,
}: CollectionSelectorProps) {
  const toggleCollection = (collectionId: string) => {
    if (disabled) return;

    const isSelected = selected.includes(collectionId);
    if (isSelected) {
      onChange(selected.filter((id) => id !== collectionId));
    } else {
      onChange([...selected, collectionId]);
    }
  };

  return (
    <div className={cn("flex flex-wrap items-center gap-1.5", className)}>
      {COLLECTION_OPTIONS.map((option) => {
        const isSelected = selected.includes(option.id);

        return (
          <motion.button
            key={option.id}
            type="button"
            onClick={() => toggleCollection(option.id)}
            disabled={disabled}
            initial={false}
            animate={{
              backgroundColor: isSelected
                ? "rgba(99, 102, 241, 0.85)"
                : "rgba(39, 39, 42, 0.6)",
              borderColor: isSelected
                ? "rgba(129, 140, 248, 0.6)"
                : "rgba(63, 63, 70, 0.4)",
            }}
            whileHover={{
              backgroundColor: isSelected
                ? "rgba(99, 102, 241, 1)"
                : "rgba(39, 39, 42, 0.9)",
            }}
            whileTap={{ scale: 0.96 }}
            transition={{ duration: 0.15 }}
            className={cn(
              "px-3 py-1.5 rounded-lg text-xs font-medium border transition-shadow cursor-pointer",
              "focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/40",
              isSelected
                ? "text-white shadow-sm shadow-indigo-500/20"
                : "text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]",
              disabled && "opacity-50 cursor-not-allowed"
            )}
          >
            {option.labelTr}
            <AnimatePresence>
              {isSelected && (
                <motion.span
                  initial={{ width: 0, opacity: 0, marginLeft: 0 }}
                  animate={{ width: 12, opacity: 1, marginLeft: 4 }}
                  exit={{ width: 0, opacity: 0, marginLeft: 0 }}
                  transition={{ duration: 0.15 }}
                  className="inline-flex items-center overflow-hidden"
                >
                  <svg width="12" height="12" viewBox="0 0 20 20" fill="none">
                    <path
                      d="M5 10.5L9 14.5L15 7.5"
                      stroke="currentColor"
                      strokeWidth="2.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </motion.span>
              )}
            </AnimatePresence>
          </motion.button>
        );
      })}
    </div>
  );
}

export default CollectionSelector;
