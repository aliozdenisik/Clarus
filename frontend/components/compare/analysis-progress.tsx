"use client";

import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { Check, Loader2 } from "lucide-react";

/**
 * Pipeline step definition — maps backend step IDs to display labels.
 * Order matters: steps are displayed in this sequence.
 */
interface PipelineStep {
  id: string;
  label: string;
}

const PIPELINE_STEPS: PipelineStep[] = [
  { id: "pipeline_started", label: "Initializing pipeline" },
  { id: "translating_query", label: "Translating query (TR / EN)" },
  { id: "query_translated", label: "Query translated" },
  { id: "generating_queries", label: "Generating multi-query variants" },
  { id: "queries_generated", label: "Query variants ready" },
  { id: "searching_vectors", label: "Searching across collections" },
  { id: "vectors_found", label: "Verses retrieved" },
  { id: "building_verse_details", label: "Extracting verse metadata" },
  { id: "agents_starting", label: "Running specialist agents..." },
  { id: "agent_completed", label: "Specialist agents working..." },
  { id: "summary_starting", label: "Synthesizing comparative essay" },
  { id: "summary_completed", label: "Synthesis complete" },
  { id: "scoring_confidence", label: "Calculating confidence score" },
  { id: "translating_response", label: "Translating response" },
];

interface ProgressEvent {
  step: string;
  message: string;
}

interface AnalysisProgressProps {
  /** Progress events received from SSE stream */
  progressEvents: ProgressEvent[];
  /** Whether paragraphs have started arriving (analysis nearly done) */
  hasParagraphs: boolean;
  className?: string;
}

/**
 * Determines step status based on which steps have been seen.
 */
function getStepStatus(
  stepId: string,
  seenSteps: Set<string>,
  latestStep: string | null
): "pending" | "active" | "completed" {
  if (seenSteps.has(stepId)) {
    // If this step was seen and it's not the latest, it's completed
    if (latestStep !== stepId) return "completed";
    return "active";
  }
  return "pending";
}

export function AnalysisProgress({
  progressEvents,
  hasParagraphs,
  className,
}: AnalysisProgressProps) {
  // Build set of seen step IDs and track the latest
  const seenSteps = new Set<string>();
  let latestStep: string | null = null;
  let latestMessage: string | null = null;

  // Track agent completion count and total from messages
  let agentCompletedCount = 0;
  let agentTotalCount = 0;

  for (const event of progressEvents) {
    seenSteps.add(event.step);
    latestStep = event.step;
    latestMessage = event.message;

    if (event.step === "agent_completed") {
      agentCompletedCount++;
      // Parse total from backend message: "... (2/3)"
      const match = event.message.match(/\((\d+)\/(\d+)\)/);
      if (match) {
        agentTotalCount = parseInt(match[2], 10);
      }
    }

    // Parse agent count from agents_starting message: "Running 3 specialist agents..."
    if (event.step === "agents_starting") {
      const match = event.message.match(/Running (\d+)/);
      if (match) {
        agentTotalCount = parseInt(match[1], 10);
      }
    }
  }

  // If paragraphs are arriving, mark everything as completed
  if (hasParagraphs) {
    latestStep = null; // No step is "active" anymore
    for (const step of PIPELINE_STEPS) {
      seenSteps.add(step.id);
    }
  }

  // Filter out steps that are purely transitional (show condensed view)
  // Group related steps: show the latest in each phase
  const displaySteps = PIPELINE_STEPS.filter((step) => {
    // Always show if it's been reached or is the next pending step
    const status = getStepStatus(step.id, seenSteps, latestStep);
    if (status === "completed" || status === "active") return true;

    // Show next pending step only if a previous step was completed
    if (status === "pending") {
      const idx = PIPELINE_STEPS.findIndex((s) => s.id === step.id);
      if (idx === 0) return true;
      const prevStep = PIPELINE_STEPS[idx - 1];
      return seenSteps.has(prevStep.id);
    }
    return false;
  });

  return (
    <div className={cn("space-y-1", className)}>
      {/* Current status headline */}
      {latestMessage && !hasParagraphs && (
        <motion.div
          key={latestMessage}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="flex items-center gap-2 mb-3 px-1"
        >
          <Loader2 className="h-3.5 w-3.5 animate-spin text-[var(--color-accent-primary)]" />
          <span className="text-sm text-[var(--color-text-secondary)]">
            {latestMessage}
          </span>
        </motion.div>
      )}

      {/* Step list */}
      <div className="space-y-0.5">
        <AnimatePresence mode="popLayout">
          {displaySteps.map((step) => {
            const status = getStepStatus(step.id, seenSteps, latestStep);
            let label: string = step.label;

            // Dynamic labels for agent progress steps
            if (step.id === "agents_starting" && agentTotalCount > 0) {
              label = `Running ${agentTotalCount} specialist agents in parallel`;
            }
            if (step.id === "agent_completed" && agentCompletedCount > 0) {
              const total = agentTotalCount || agentCompletedCount;
              label = `Specialist agents (${agentCompletedCount}/${total} completed)`;
            }

            return (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 8 }}
                transition={springPresets.snappy}
                className="flex items-center gap-2.5 py-1 px-1"
              >
                {/* Status indicator */}
                <div className="flex-shrink-0 w-4 h-4 flex items-center justify-center">
                  {status === "completed" ? (
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={springPresets.snappy}
                    >
                      <Check className="h-3.5 w-3.5 text-emerald-400" />
                    </motion.div>
                  ) : status === "active" ? (
                    <div className="relative">
                      <div className="w-2 h-2 rounded-full bg-[var(--color-accent-primary)]" />
                      <div className="absolute inset-0 w-2 h-2 rounded-full bg-[var(--color-accent-primary)] animate-ping opacity-50" />
                    </div>
                  ) : (
                    <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-text-muted)] opacity-40" />
                  )}
                </div>

                {/* Label */}
                <span
                  className={cn(
                    "text-xs transition-colors duration-200",
                    status === "completed" && "text-[var(--color-text-muted)]",
                    status === "active" && "text-[var(--color-text-secondary)] font-medium",
                    status === "pending" && "text-[var(--color-text-muted)] opacity-50"
                  )}
                >
                  {label}
                </span>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
}
