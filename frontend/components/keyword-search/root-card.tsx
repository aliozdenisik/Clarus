"use client";

import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";

interface RootCardProps {
  root: string | null;
  rootSource: string;
  rootBuckwalter?: string | null;
}

export function RootCard({ root, rootSource, rootBuckwalter }: RootCardProps) {

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
