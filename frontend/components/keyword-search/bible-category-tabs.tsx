"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export type BibleCategoryFilter = "all" | "ot" | "nt" | "apocrypha" | "pseudepigrapha" | "gnostic" | "apostolic_fathers";

interface BibleCategoryTabsProps {
  activeCategory: BibleCategoryFilter;
  onCategoryChange: (category: BibleCategoryFilter) => void;
  languageMode: "hebrew_ot" | "greek_nt";
}

// Categories available for Hebrew OT mode
const hebrewCategories: { id: BibleCategoryFilter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "ot", label: "Old Testament" },
  { id: "apocrypha", label: "Apocrypha" },
  { id: "pseudepigrapha", label: "Pseudepigrapha" },
];

// Categories available for Greek NT mode
const greekCategories: { id: BibleCategoryFilter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "nt", label: "New Testament" },
  { id: "apocrypha", label: "Apocrypha" },
  { id: "gnostic", label: "Gnostic" },
  { id: "apostolic_fathers", label: "Apostolic Fathers" },
];

export function BibleCategoryTabs({ activeCategory, onCategoryChange, languageMode }: BibleCategoryTabsProps) {
  const categories = languageMode === "hebrew_ot" ? hebrewCategories : greekCategories;

  return (
    <div className="flex flex-wrap gap-1 p-1 bg-zinc-900/50 rounded-lg border border-zinc-800">
      {categories.map((cat) => (
        <button
          key={cat.id}
          onClick={() => onCategoryChange(cat.id)}
          className={cn(
            "relative px-3 py-1.5 text-xs font-medium rounded-md transition-colors",
            activeCategory === cat.id
              ? "text-white"
              : "text-zinc-400 hover:text-zinc-200"
          )}
        >
          {activeCategory === cat.id && (
            <motion.div
              layoutId="activeBibleCategoryTab"
              className="absolute inset-0 bg-zinc-800 rounded-md"
              transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
            />
          )}
          <span className="relative z-10">{cat.label}</span>
        </button>
      ))}
    </div>
  );
}
