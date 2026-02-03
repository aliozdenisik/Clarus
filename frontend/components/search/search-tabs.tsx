"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { springPresets } from "@/lib/design-system";

export type SearchSource = "quran" | "ot" | "nt" | "apocrypha";

interface SearchTabsProps {
  activeTab: SearchSource;
  onTabChange: (tab: SearchSource) => void;
}

const tabs: { id: SearchSource; label: string }[] = [
  { id: "quran", label: "Quran" },
  { id: "ot", label: "Old Testament" },
  { id: "nt", label: "New Testament" },
  { id: "apocrypha", label: "Apocrypha" },
];

export function SearchTabs({ activeTab, onTabChange }: SearchTabsProps) {
  return (
    <div className="flex flex-wrap gap-1 p-1 bg-[var(--color-bg-surface)] rounded-lg border border-[var(--color-border-subtle)] w-fit mb-6">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <div key={tab.id} className="relative">
             {isActive && (
              <motion.div
                layoutId="activeTab"
                className="absolute inset-0 bg-[var(--color-bg-elevated)] rounded-md border border-[var(--color-border-subtle)] shadow-sm"
                initial={false}
                transition={springPresets.snappy}
              />
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onTabChange(tab.id)}
              className={cn(
                "relative z-10 hover:bg-transparent transition-colors duration-200",
                isActive 
                  ? "text-[var(--color-accent-primary)] font-medium" 
                  : "text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
              )}
              data-state={isActive ? "active" : "inactive"}
            >
              {tab.label}
            </Button>
          </div>
        );
      })}
    </div>
  );
}
