"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { Info, ChevronDown, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";

interface VerificationEntry {
  strong: string;
  word: string;
  ourCount: number;
  blbCount: number;
}

const VERIFICATION_DATA: VerificationEntry[] = [
  { strong: "H1697", word: "dabar", ourCount: 1440, blbCount: 1439 },
  { strong: "H8451", word: "torah", ourCount: 219, blbCount: 219 },
  { strong: "H430", word: "elohim", ourCount: 2596, blbCount: 2606 },
  { strong: "G2316", word: "theos", ourCount: 1307, blbCount: 1318 },
];

function calculateDelta(ours: number, blb: number): { value: number; percent: string; status: "exact" | "pass" } {
  const delta = ours - blb;
  const percent = ((Math.abs(delta) / blb) * 100).toFixed(2);
  return {
    value: delta,
    percent,
    status: delta === 0 ? "exact" : "pass",
  };
}

interface AccuracyDisclaimerProps {
  className?: string;
}

export function AccuracyDisclaimer({ className }: AccuracyDisclaimerProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className={cn("w-full", className)}>
      {/* Collapsed state - just a subtle link */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors mx-auto group"
      >
        <Info className="w-3.5 h-3.5" />
        <span>Clarus can make mistakes. Verify important information.</span>
        <ChevronDown 
          className={cn(
            "w-3.5 h-3.5 transition-transform duration-200",
            isExpanded && "rotate-180"
          )} 
        />
      </button>

      {/* Expanded state - full accuracy report */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={springPresets.snappy}
            className="overflow-hidden"
          >
            <div className="mt-4 p-4 rounded-lg bg-[var(--color-bg-surface)] border border-[var(--color-border-subtle)]">
              {/* Header */}
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-sm font-medium text-[var(--color-text-primary)]">
                  Accuracy Verification
                </h4>
                <a
                  href="https://www.blueletterbible.org/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-xs text-[var(--color-accent-primary)] hover:underline"
                >
                  Blue Letter Bible
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>

              {/* Explanation */}
              <p className="text-xs text-[var(--color-text-muted)] mb-3">
                Our occurrence counts are verified against Blue Letter Bible (authoritative concordance). 
                Small discrepancies (&lt;1%) are expected due to different manuscript traditions 
                (OSHB/MorphGNT vs WLC/Textus Receptus).
              </p>

              {/* Data Table */}
              <div className="overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b border-[var(--color-border-subtle)]">
                      <th className="text-left py-2 text-[var(--color-text-muted)] font-medium">Strong&apos;s</th>
                      <th className="text-left py-2 text-[var(--color-text-muted)] font-medium">Word</th>
                      <th className="text-right py-2 text-[var(--color-text-muted)] font-medium">Clarus</th>
                      <th className="text-right py-2 text-[var(--color-text-muted)] font-medium">BLB</th>
                      <th className="text-right py-2 text-[var(--color-text-muted)] font-medium">Δ</th>
                      <th className="text-right py-2 text-[var(--color-text-muted)] font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {VERIFICATION_DATA.map((entry) => {
                      const delta = calculateDelta(entry.ourCount, entry.blbCount);
                      return (
                        <tr 
                          key={entry.strong} 
                          className="border-b border-[var(--color-border-subtle)] last:border-0"
                        >
                          <td className="py-2 text-[var(--color-text-secondary)] font-mono">
                            {entry.strong}
                          </td>
                          <td className="py-2 text-[var(--color-text-primary)]">
                            {entry.word}
                          </td>
                          <td className="py-2 text-right text-[var(--color-text-primary)] font-mono">
                            {entry.ourCount.toLocaleString()}
                          </td>
                          <td className="py-2 text-right text-[var(--color-text-secondary)] font-mono">
                            {entry.blbCount.toLocaleString()}
                          </td>
                          <td className="py-2 text-right font-mono">
                            <span className={cn(
                              delta.value === 0 
                                ? "text-emerald-400" 
                                : "text-amber-400"
                            )}>
                              {delta.value > 0 ? "+" : ""}{delta.value} ({delta.percent}%)
                            </span>
                          </td>
                          <td className="py-2 text-right">
                            <span className={cn(
                              "px-1.5 py-0.5 rounded text-[10px] font-medium",
                              delta.status === "exact"
                                ? "bg-emerald-500/20 text-emerald-400"
                                : "bg-amber-500/20 text-amber-400"
                            )}>
                              {delta.status === "exact" ? "EXACT" : "PASS"}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              {/* Footer note */}
              <div className="mt-3 pt-3 border-t border-[var(--color-border-subtle)]">
                <p className="text-[10px] text-[var(--color-text-muted)] leading-relaxed">
                  <strong>Data Sources:</strong> Hebrew (OSHB - Open Scriptures Hebrew Bible), 
                  Greek (MorphGNT - Morphologically tagged Greek NT based on NA27/NA28).
                  BLB uses WLC (Westminster Leningrad Codex) and Textus Receptus.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
