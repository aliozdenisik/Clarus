"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

export type LanguageTab = "quran" | "hebrew_ot";

interface LanguageTabsProps {
  activeTab: LanguageTab;
  onTabChange: (tab: LanguageTab) => void;
}

const tabs = [
  { id: "quran" as const, label: "Kur'an Arapça", icon: "🕌" },
  { id: "hebrew_ot" as const, label: "İbranice Eski Ahit", icon: "📜" },
];

export function LanguageTabs({ activeTab, onTabChange }: LanguageTabsProps) {
  return (
    <div className="flex gap-1 p-1 bg-zinc-900/50 rounded-lg border border-zinc-800">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={cn(
            "relative px-4 py-2 text-sm font-medium rounded-md transition-colors",
            activeTab === tab.id
              ? "text-white"
              : "text-zinc-400 hover:text-zinc-200"
          )}
        >
          {activeTab === tab.id && (
            <motion.div
              layoutId="activeLanguageTab"
              className="absolute inset-0 bg-zinc-800 rounded-md"
              transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
            />
          )}
          <span className="relative z-10">{tab.icon} {tab.label}</span>
        </button>
      ))}
    </div>
  );
}
