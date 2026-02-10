"use client"

import { cn } from "@/lib/utils"
import { motion } from "framer-motion"
import { Check, Loader2 } from "lucide-react"

/**
 * Pipeline phases — backend step IDs mapped to user-facing phases.
 * Multiple backend steps collapse into a single visible phase.
 */
interface Phase {
  id: string
  label: string
  /** Backend step IDs that belong to this phase */
  steps: string[]
}

const PHASES: Phase[] = [
  {
    id: "query",
    label: "Preparing query",
    steps: [
      "pipeline_started",
      "translating_query",
      "query_translated",
      "generating_queries",
      "queries_generated",
    ],
  },
  {
    id: "search",
    label: "Searching scriptures",
    steps: ["searching_vectors", "vectors_found", "building_verse_details"],
  },
  {
    id: "agents",
    label: "Running specialist agents",
    steps: ["agents_starting", "agent_completed"],
  },
  {
    id: "synthesis",
    label: "Synthesizing essay",
    steps: ["summary_starting", "summary_completed"],
  },
  {
    id: "finalize",
    label: "Finalizing",
    steps: ["scoring_confidence", "translating_response"],
  },
]

interface ProgressEvent {
  step: string
  message: string
}

interface AnalysisProgressProps {
  progressEvents: ProgressEvent[]
  hasParagraphs: boolean
  className?: string
}

function getPhaseStatus(
  phase: Phase,
  seenSteps: Set<string>,
  latestPhaseId: string | null
): "pending" | "active" | "completed" {
  const hasAny = phase.steps.some((s) => seenSteps.has(s))
  const hasAll = phase.steps.every((s) => seenSteps.has(s))

  if (!hasAny) return "pending"
  if (hasAll && latestPhaseId !== phase.id) return "completed"
  if (latestPhaseId === phase.id) return "active"
  // Phase has some steps seen but is not the latest — completed
  return "completed"
}

export function AnalysisProgress({
  progressEvents,
  hasParagraphs,
  className,
}: AnalysisProgressProps) {
  const seenSteps = new Set<string>()
  let agentCompletedCount = 0
  let agentTotalCount = 0

  for (const event of progressEvents) {
    seenSteps.add(event.step)

    if (event.step === "agent_completed") {
      agentCompletedCount++
      const match = event.message.match(/\((\d+)\/(\d+)\)/)
      if (match) agentTotalCount = parseInt(match[2], 10)
    }
    if (event.step === "agents_starting") {
      const match = event.message.match(/Running (\d+)/)
      if (match) agentTotalCount = parseInt(match[1], 10)
    }
  }

  // Determine which phase is currently active (last phase with any seen step)
  let latestPhaseId: string | null = null
  for (const phase of PHASES) {
    if (phase.steps.some((s) => seenSteps.has(s))) {
      latestPhaseId = phase.id
    }
  }

  if (hasParagraphs) {
    latestPhaseId = null
  }

  // Only show phases that are active/completed, plus the next pending one
  const visiblePhases = PHASES.filter((phase, idx) => {
    const status = getPhaseStatus(phase, seenSteps, latestPhaseId)
    if (status === "completed" || status === "active") return true
    // Show next pending if previous is done
    if (idx > 0) {
      const prev = PHASES[idx - 1]
      const prevStatus = getPhaseStatus(prev, seenSteps, latestPhaseId)
      return prevStatus === "completed" || prevStatus === "active"
    }
    return idx === 0
  })

  return (
    <div className={cn("pl-1", className)}>
      {visiblePhases.map((phase, idx) => {
        const status = hasParagraphs ? "completed" : getPhaseStatus(phase, seenSteps, latestPhaseId)
        const isLast = idx === visiblePhases.length - 1

        // Dynamic label for agents phase
        let label = phase.label
        if (phase.id === "agents" && agentTotalCount > 0) {
          if (status === "active" && agentCompletedCount > 0) {
            label = `Running agents (${agentCompletedCount}/${agentTotalCount})`
          } else if (status === "active") {
            label = `Running ${agentTotalCount} agents`
          } else if (status === "completed") {
            label = `${agentTotalCount} agents completed`
          }
        }

        return (
          <motion.div
            key={phase.id}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, delay: idx * 0.04 }}
            className="flex gap-3"
          >
            {/* Indicator column: icon + connector line */}
            <div className="flex flex-col items-center">
              {/* Icon */}
              <div className="flex h-5 w-5 flex-shrink-0 items-center justify-center">
                {status === "completed" ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: "spring", stiffness: 400, damping: 20 }}
                    className="flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500/15"
                  >
                    <Check className="h-3 w-3 text-emerald-400" strokeWidth={3} />
                  </motion.div>
                ) : status === "active" ? (
                  <div className="flex h-5 w-5 items-center justify-center rounded-full bg-[var(--color-accent-primary)]/15">
                    <Loader2 className="h-3 w-3 animate-spin text-[var(--color-accent-primary)]" />
                  </div>
                ) : (
                  <div className="flex h-5 w-5 items-center justify-center rounded-full border border-[var(--color-border-subtle)]">
                    <div className="h-1.5 w-1.5 rounded-full bg-[var(--color-text-muted)] opacity-30" />
                  </div>
                )}
              </div>

              {/* Connector line */}
              {!isLast && (
                <div
                  className={cn(
                    "my-0.5 min-h-[16px] w-px flex-1 transition-colors duration-300",
                    status === "completed" ? "bg-emerald-500/30" : "bg-[var(--color-border-subtle)]"
                  )}
                />
              )}
            </div>

            {/* Label */}
            <div className={cn("pb-4", isLast && "pb-0")}>
              <span
                className={cn(
                  "text-[13px] leading-5 transition-colors duration-200",
                  status === "completed" && "text-[var(--color-text-muted)]",
                  status === "active" && "font-medium text-[var(--color-text-primary)]",
                  status === "pending" && "text-[var(--color-text-muted)] opacity-40"
                )}
              >
                {label}
              </span>
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}
