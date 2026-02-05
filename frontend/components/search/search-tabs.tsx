"use client";

import * as React from "react";
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { cn } from "@/lib/utils";

export type SearchSource = "quran" | "ot" | "nt" | "apocrypha";

interface SearchTabsProps {
  activeTab: SearchSource;
  onTabChange: (tab: SearchSource) => void;
}

const tabs = [
  { value: "quran" as const, label: "Quran" },
  { value: "ot" as const, label: "Old Testament" },
  { value: "nt" as const, label: "New Testament" },
  { value: "apocrypha" as const, label: "Apocrypha" },
];

export function SearchTabs({ activeTab, onTabChange }: SearchTabsProps) {
  return (
    <TabsPrimitive.Root value={activeTab} onValueChange={onTabChange as any} className="mb-6">
      <TabsPrimitive.List className="inline-flex h-auto gap-4 rounded-none border-b border-[var(--color-border-subtle)] bg-transparent px-0 py-1 text-foreground">
        {tabs.map((tab) => (
          <TabsPrimitive.Trigger
            key={tab.value}
            value={tab.value}
            className={cn(
              "relative px-3 py-1.5 text-sm font-medium transition-colors",
              "text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-bg-elevated)] rounded-md",
              "after:absolute after:inset-x-0 after:bottom-0 after:-mb-1 after:h-0.5",
              "data-[state=active]:bg-transparent data-[state=active]:text-[var(--color-text-primary)] data-[state=active]:shadow-none data-[state=active]:after:bg-[var(--color-accent-primary)]",
            )}
          >
            {tab.label}
          </TabsPrimitive.Trigger>
        ))}
      </TabsPrimitive.List>
    </TabsPrimitive.Root>
  );
}
