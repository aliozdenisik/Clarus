"use client";

import { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { ExternalLink } from "lucide-react";
import { SourceBadge, SourceType } from "@/components/compare/source-badge";
import { cn } from "@/lib/utils";

interface SearchResultCardProps {
  source: string;
  reference: string;
  text: string;
  score: number;
  onClick?: () => void;
  className?: string;
}

// Map search source to SourceBadge type
const sourceMap: Record<string, SourceType> = {
  quran: 'quran',
  ot: 'old_testament',
  nt: 'new_testament',
  apocrypha: 'apocrypha',
  old_testament: 'old_testament',
  new_testament: 'new_testament',
};

export function SearchResultCard({
  source,
  reference,
  text,
  score,
  onClick,
  className,
}: SearchResultCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const prefersReducedMotion = useReducedMotion();
  
  // Map source to SourceBadge type
  const displaySource = sourceMap[source.toLowerCase()] || 'quran';
  
  // Format score as percentage with one decimal place
  const scorePercentage = (score * 100).toFixed(1);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (onClick && (e.key === 'Enter' || e.key === ' ')) {
      e.preventDefault();
      onClick();
    }
  };

  return (
    <motion.div
      role={onClick ? 'button' : undefined}
      aria-label={onClick ? `Verse ${reference}` : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={handleKeyDown}
      className={cn(
        "relative rounded-xl p-5",
        onClick && "cursor-pointer",
        "bg-gradient-to-b from-zinc-900/80 to-zinc-950/90",
        "border transition-all duration-200",
        "before:absolute before:inset-0 before:rounded-xl",
        "before:bg-gradient-to-b before:from-white/[0.03] before:to-transparent",
        "before:pointer-events-none",
        isHovered 
          ? "border-zinc-600/80 shadow-lg shadow-black/30" 
          : "border-zinc-800/60 shadow-sm shadow-black/10",
        onClick && "focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950",
        className
      )}
      style={
        isHovered
          ? {
              boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -4px rgba(0, 0, 0, 0.3), 0 0 30px rgba(99, 102, 241, 0.08)",
            }
          : undefined
      }
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      whileHover={prefersReducedMotion ? {} : { y: -2 }}
      transition={
        prefersReducedMotion
          ? { type: "tween", duration: 0.1 }
          : { type: "spring", stiffness: 300, damping: 30 }
      }
    >
      {/* Corner Squares - Editorial/Archival Aesthetic */}
      {[
        '-left-1 -top-1',
        '-right-1 -top-1',
        '-left-1 -bottom-1',
        '-right-1 -bottom-1'
      ].map((pos, i) => (
        <motion.div
          key={i}
          className={`absolute ${pos} h-2 w-2 bg-white/90`}
          initial={{ opacity: 0, scale: 0.8 }}
          animate={isHovered ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.8 }}
          transition={
            prefersReducedMotion
              ? { type: "tween", duration: 0.1 }
              : { type: "spring", stiffness: 500, damping: 25, delay: i * 0.02 }
          }
        />
      ))}

      {/* Header Row: Reference + Badge + Score */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <SourceBadge source={displaySource} />
          <span className="text-sm font-medium text-zinc-200">
            {reference}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-zinc-500 tabular-nums">
            {scorePercentage}%
          </span>
          <ExternalLink className="w-3.5 h-3.5 text-zinc-500" />
        </div>
      </div>

      {/* Verse Text */}
      <p className="text-sm text-zinc-400 leading-relaxed line-clamp-3">
        {text}
      </p>
    </motion.div>
  );
}
