"use client";

import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { InlineCitation } from "@/components/compare/inline-citation";
import { parseCitations } from "@/lib/utils/parse-citations";
import { springPresets } from "@/lib/design-system";
import { cn } from "@/lib/utils";

interface VerseDetail {
  text: string;
  book_name?: string;
  chapter?: number;
  verse?: number;
  source: string;
  translation?: string;
  book_nr?: number;
  surah_id?: number;
  surah_name?: string;
  verse_id?: number;
}

interface AIInterpretationProps {
  text: string;
  verseDetails?: Record<string, VerseDetail>;
  onNavigate?: (reference: string) => void;
  className?: string;
}

export function AIInterpretation({
  text,
  verseDetails = {},
  onNavigate,
  className,
}: AIInterpretationProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={springPresets.fluid}
      className={cn(
        "relative my-8 pl-6 pr-4 py-4 rounded-r-lg",
        "bg-gradient-to-br from-zinc-900/40 via-transparent to-zinc-900/20",
        "border-l-[3px] border-indigo-500/60",
        "shadow-[inset_2px_0_8px_rgba(99,102,241,0.15)]",
        className
      )}
    >
      {/* Header Label */}
      <div className="flex items-center gap-1.5 mb-4">
        <Sparkles className="w-3 h-3 text-indigo-400/70" strokeWidth={2.5} />
        <span className="text-[10px] font-semibold uppercase tracking-[0.2em] text-zinc-500">
          AI Interpretation
        </span>
      </div>

      {/* Interpretation Text with Citations */}
      <div className="font-serif text-[17px] text-zinc-300 leading-[1.9] tracking-wide">
        {parseCitations(text).map((part, i) => {
          if (typeof part === "string") {
            return <span key={i}>{part}</span>;
          }

          const verse = verseDetails[part.reference];

          return (
            <InlineCitation
              key={i}
              reference={part.reference}
              verseDetail={verse}
              onNavigate={onNavigate || (() => {})}
            />
          );
        })}
      </div>
    </motion.div>
  );
}
