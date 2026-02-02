"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { GlowCard } from "@/components/ui/glow-card";
import { springPresets } from "@/lib/design-system";

interface SurahChartProps {
  data: Array<{
    surah_id: number;
    surah_name: string;
    count: number;
  }>;

}

interface CustomYAxisTickProps {
  x?: number;
  y?: number;
  payload?: { value: string };
}

interface CustomTooltipProps {
  active?: boolean;
  payload?: Array<{
    payload: {
      surah_name: string;
      count: number;
    };
  }>;
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
  );
}

function CustomTooltip({ active, payload }: CustomTooltipProps) {
  if (!active || !payload?.length) return null;
  const data = payload[0].payload;
  return (
    <div className="rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 shadow-xl">
      <p className="text-sm text-zinc-100">
        {data.surah_name}
      </p>
      <p className="text-xs text-zinc-400">{data.count} occurrences</p>
    </div>
  );
}

export function SurahChart({ data }: SurahChartProps) {
  const [showAll, setShowAll] = useState(false);

  // Empty state
  if (!data || data.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={springPresets.snappy}
      >
        <GlowCard>
          <p className="text-center text-sm text-[var(--color-text-muted)] py-8">
            No surah distribution data
          </p>
        </GlowCard>
      </motion.div>
    );
  }

  // Sort data by count descending
  const sortedData = [...data].sort((a, b) => b.count - a.count);

  // Show max 20 initially
  const displayData = showAll ? sortedData : sortedData.slice(0, 20);
  const barHeight = 36;
  const chartHeight = displayData.length * barHeight + 40;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={springPresets.snappy}
    >
      <GlowCard>
        {/* Section Header */}
        <div className="space-y-4 mb-6">
          <div className="text-center text-[var(--color-text-muted)] text-xs tracking-widest">
            ◆
          </div>
          <h3 className="text-lg font-medium text-[var(--color-text-primary)] text-center">
            Surah Distribution
          </h3>
        </div>

        {/* Chart */}
        <ResponsiveContainer width="100%" height={chartHeight}>
          <BarChart
            layout="vertical"
            data={displayData}
            margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#3f3f46"
              horizontal={true}
              vertical={false}
            />
            <XAxis
              type="number"
              tick={{ fill: "#a1a1aa", fontSize: 12 }}
              axisLine={{ stroke: "#3f3f46" }}
            />
            <YAxis
              type="category"
              dataKey="surah_name"
              tick={<CustomYAxisTick />}
              width={90}
              axisLine={{ stroke: "#3f3f46" }}
            />
            <Tooltip
              content={<CustomTooltip />}
              cursor={{ fill: "rgba(99, 102, 241, 0.1)" }}
            />
            <Bar
              dataKey="count"
              fill="#6366f1"
              fillOpacity={0.8}
              radius={[0, 4, 4, 0]}
              isAnimationActive={true}
              animationDuration={800}
            />
          </BarChart>
        </ResponsiveContainer>

        {/* Expand Button */}
        {sortedData.length > 20 && !showAll && (
          <button
            onClick={() => setShowAll(true)}
            className="mt-4 w-full text-center text-sm text-[var(--color-accent-primary)] hover:underline"
          >
            Show all {sortedData.length} surahs
          </button>
        )}
      </GlowCard>
    </motion.div>
  );
}
