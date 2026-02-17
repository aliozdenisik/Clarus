"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  LabelList,
} from "recharts"
import { GlowCard } from "@/components/ui/glow-card"
import { springPresets } from "@/lib/design-system"
import { useTranslations } from "next-intl"

interface SurahChartProps {
  data: Array<{
    surah_id: number
    surah_name: string
    count: number
  }>
  language: "quran" | "hebrew_ot" | "greek_nt"
}

interface CustomYAxisTickProps {
  x?: number
  y?: number
  payload?: { value: string }
}

interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{
    payload: {
      surah_name: string
      count: number
    }
  }>
  occurrencesLabel: string
}

function CustomYAxisTick({ x, y, payload }: CustomYAxisTickProps) {
  return (
    <text
      x={x}
      y={y}
      dy={4}
      textAnchor="end"
      style={{
        fontSize: 12,
        fill: "#a1a1aa",
      }}
    >
      {payload?.value}
    </text>
  )
}

function CustomTooltip({ active, payload, occurrencesLabel }: CustomTooltipProps) {
  if (!active || !payload?.length) return null
  const data = payload[0].payload
  return (
    <div
      role="tooltip"
      className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 shadow-xl"
    >
      <p className="text-sm text-zinc-100">{data.surah_name}</p>
      <p className="text-xs text-zinc-400">
        {data.count} {occurrencesLabel}
      </p>
    </div>
  )
}

const xAxisTickStyle = { fill: "#a1a1aa", fontSize: 12 }
const axisLineStyle = { stroke: "#3f3f46" }
const tooltipCursorStyle = { fill: "rgba(79, 70, 229, 0.1)" }
const barRadius: [number, number, number, number] = [0, 4, 4, 0]
const labelFill = "#a1a1aa"
const MIN_CHART_HEIGHT = 240

export function SurahChart({ data, language }: SurahChartProps) {
  const t = useTranslations("KeywordSearch")
  const [showAll, setShowAll] = useState(false)

  // Empty state
  if (!data || data.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={springPresets.snappy}
      >
        <GlowCard className="p-4">
          <div className="flex min-h-[240px] flex-col items-center justify-center gap-3 text-center">
            <p className="text-sm font-medium text-[var(--color-text-secondary)]">
              {language === "quran" ? t("chart.noSurahData") : t("chart.noBookData")}
            </p>
            <p className="text-xs text-[var(--color-text-muted)]">{t("emptyStateExamples")}</p>
          </div>
        </GlowCard>
      </motion.div>
    )
  }

  // Sort data by count descending
  const sortedData = [...data].sort((a, b) => b.count - a.count)

  // Show max 20 initially
  const displayData = showAll ? sortedData : sortedData.slice(0, 20)
  const barHeight = 36
  const chartHeight = Math.max(displayData.length * barHeight + 40, MIN_CHART_HEIGHT)

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={springPresets.snappy}>
      <GlowCard>
        {/* Section Header */}
        <div className="mb-6 space-y-4">
          <div className="text-center text-xs tracking-widest text-[var(--color-text-muted)]">
            ◆
          </div>
          <h3 className="text-center text-lg font-medium text-[var(--color-text-primary)]">
            {language === "quran" ? t("chart.title") : t("chart.bibleTitle")}
          </h3>
        </div>

        {/* Chart */}
        <ResponsiveContainer width="100%" height={chartHeight}>
          <BarChart
            layout="vertical"
            data={displayData}
            margin={{ top: 5, right: 48, left: 16, bottom: 5 }}
            role="img"
            aria-label={
              language === "quran" ? "Surah distribution chart" : "Book distribution chart"
            }
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#3f3f46"
              horizontal={true}
              vertical={false}
            />
            <XAxis type="number" tick={xAxisTickStyle} axisLine={axisLineStyle} tickLine={false} />
            <YAxis
              type="category"
              dataKey="surah_name"
              tick={<CustomYAxisTick />}
              width={110}
              axisLine={axisLineStyle}
              tickLine={false}
            />
            <Tooltip
              content={<CustomTooltip occurrencesLabel={t("chart.occurrences")} />}
              cursor={tooltipCursorStyle}
            />
            <Bar
              dataKey="count"
              fill="#4f46e5"
              fillOpacity={0.8}
              radius={barRadius}
              isAnimationActive={true}
              animationDuration={800}
            >
              <LabelList dataKey="count" position="right" fill={labelFill} fontSize={11} />
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        {/* Expand Button */}
        {sortedData.length > 20 && !showAll && (
          <button
            type="button"
            onClick={() => setShowAll(true)}
            className="mt-4 w-full text-center text-sm text-[var(--color-accent-primary)] hover:underline"
          >
            {t("chart.showAll", {
              count: sortedData.length,
              type: language === "quran" ? t("chart.surahs") : t("chart.books"),
            })}
          </button>
        )}
      </GlowCard>
    </motion.div>
  )
}
