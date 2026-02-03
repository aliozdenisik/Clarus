"use client";

import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";

interface RootCardProps {
  root: string | null;
  rootSource: string;
  rootBuckwalter?: string | null;
  strongNumber?: string | null;
  language?: "arabic" | "hebrew";
}

export function RootCard({ root, rootSource, rootBuckwalter, strongNumber, language = "arabic" }: RootCardProps) {
  const isHebrew = language === "hebrew";

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={springPresets.fluid}
      className="flex flex-col items-center gap-4 p-8 rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]"
    >
      {root ? (
        <>
          <div className="flex items-center gap-3">
            <p
              lang={isHebrew ? "he" : "ar"}
              className={`${isHebrew ? 'font-hebrew' : 'font-arabic'} text-5xl font-bold text-center text-[var(--color-text-primary)]`}
              dir="rtl"
            >
              <bdi>{root}</bdi>
            </p>
            {isHebrew && strongNumber && (
              <span className="px-2 py-1 text-xs font-mono bg-indigo-500/20 text-indigo-300 rounded border border-indigo-500/30">
                {strongNumber}
              </span>
            )}
          </div>
          {rootBuckwalter && (
            <p className="text-lg text-[var(--color-text-muted)] text-center tracking-wide">
              {rootBuckwalter}
            </p>
          )}
        </>
      ) : (
        <p className="text-[var(--color-text-muted)] text-center">
          No root found for this query
        </p>
      )}
    </motion.div>
  );
}
