"use client";

import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { cn } from "@/lib/utils";

interface RootCardProps {
  root: string | null;
  rootSource: string;
}

const ROOT_SOURCE_LABELS: Record<string, string> = {
  exact_match: "Exact Match",
  prefix_stripped: "Prefix Stripped",
  algorithmic: "Algorithmic",
  buckwalter_exact: "Buckwalter Exact",
  buckwalter_fuzzy: "Buckwalter Fuzzy",
  not_found: "Not Found",
};

const ROOT_SOURCE_COLORS: Record<string, string> = {
  exact_match: "bg-emerald-500 text-white",
  prefix_stripped: "bg-amber-500 text-white",
  algorithmic: "bg-blue-500 text-white",
  buckwalter_exact: "bg-purple-500 text-white",
  buckwalter_fuzzy: "bg-purple-400 text-white",
  not_found: "bg-zinc-500 text-white",
};

export function RootCard({ root, rootSource }: RootCardProps) {
  const label = ROOT_SOURCE_LABELS[rootSource] || "Unknown";
  const colorClass = ROOT_SOURCE_COLORS[rootSource] || "bg-zinc-500 text-white";

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={springPresets.fluid}
      className="flex flex-col items-center gap-4 p-8 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]"
    >
      {root ? (
        <>
          <p
            lang="ar"
            className="font-arabic text-5xl font-bold text-center text-[var(--color-text-primary)]"
          >
            {root}
          </p>
          <span
            role="status"
            className={cn("px-3 py-1.5 rounded text-sm font-medium", colorClass)}
          >
            {label}
          </span>
        </>
      ) : (
        <p className="text-[var(--color-text-muted)] text-center">
          No root found for this query
        </p>
      )}
    </motion.div>
  );
}
