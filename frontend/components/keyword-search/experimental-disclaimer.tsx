"use client";

import { AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface ExperimentalDisclaimerProps {
  className?: string;
}

export function ExperimentalDisclaimer({ className }: ExperimentalDisclaimerProps) {
  return (
    <div
      className={cn(
        "flex items-center justify-center gap-2 px-4 py-2 rounded-lg",
        "bg-amber-500/10 border border-amber-500/20",
        "text-amber-400 text-xs",
        className
      )}
    >
      <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
      <span>
        <strong>Experimental Feature:</strong> This morphological search is under active development. 
        Results should not be used as the sole basis for academic or theological research. 
        Always verify with authoritative sources.
      </span>
    </div>
  );
}
