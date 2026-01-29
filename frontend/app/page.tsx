"use client";

import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { MagneticButton } from "@/components/ui/magnetic-button";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/auth-context";
import {
  Search,
  Sparkles,
  GitCompare,
  BookOpen,
  ArrowRight,
  ArrowDown,
  Brain,
  Layers,
  ScrollText,
  BookMarked,
  Library,
} from "lucide-react";
import Image from "next/image";

const features = [
  {
    icon: Sparkles,
    title: "Understands What You Mean",
    description:
      "Describe a concept or explore an idea in your own words. The AI grasps meaning and context — surfacing relevant passages even when you don't know the exact terms to search for.",
    techNote: "Hybrid semantic + keyword search",
  },
  {
    icon: Layers,
    title: "Every Scripture at Once",
    description:
      "Quran, Old Testament, New Testament, and Apocrypha — all 43,055 verses searched simultaneously so no perspective goes unheard.",
    techNote: "Parallel multi-collection retrieval",
  },
  {
    icon: BookMarked,
    title: "Traceable to the Source",
    description:
      "Every insight is backed by exact verse references. Nothing is claimed without a source you can look up and verify yourself.",
    techNote: "AI-generated with full citation traceability",
  },
];

const steps = [
  {
    icon: Search,
    label: "Ask",
    desc: "Pose your question",
    detail:
      "Any theological concept, moral question, or scriptural topic — in your own words.",
  },
  {
    icon: Sparkles,
    label: "Enrich",
    desc: "Context is deepened",
    detail:
      "The AI expands your question with related concepts and terminology across traditions.",
  },
  {
    icon: Layers,
    label: "Discover",
    desc: "All scriptures searched",
    detail:
      "43,055 verses across Quran and Bible are scanned simultaneously for the most relevant passages.",
  },
  {
    icon: Brain,
    label: "Understand",
    desc: "Perspectives unite",
    detail:
      "5 specialist agents each contribute their scripture's voice, then a synthesis brings them together.",
  },
];

const agents = [
  {
    name: "Quran Agent",
    role: "Quran Specialist",
    description:
      "Surfaces the most relevant verses with precise Surah and Ayah citations — presenting the Quran's own words on any topic.",
    collection: "quran_tr",
    verseCount: "6,236",
    color: "emerald" as const,
    icon: BookOpen,
  },
  {
    name: "Old Testament Agent",
    role: "Old Testament Specialist",
    description:
      "Searches Genesis through Malachi to find relevant passages with exact chapter and verse references — the scripture in its own voice.",
    collection: "bible_ot",
    verseCount: "23,145",
    color: "amber" as const,
    icon: ScrollText,
  },
  {
    name: "New Testament Agent",
    role: "New Testament Specialist",
    description:
      "Retrieves relevant passages from the Gospels, Letters, and Revelation with precise citations — the text as it was written.",
    collection: "bible_nt",
    verseCount: "7,957",
    color: "sky" as const,
    icon: BookMarked,
  },
  {
    name: "Apocrypha Agent",
    role: "Apocrypha Specialist",
    description:
      "Explores books like Wisdom, Sirach, and Maccabees — scriptures cherished across Christian traditions, cited with full references.",
    collection: "bible_apocrypha",
    verseCount: "5,717",
    color: "purple" as const,
    icon: Library,
  },
];

const agentColorMap = {
  emerald: {
    glow: "bg-emerald-500/20",
    border: "group-hover:border-emerald-500/30",
    bg: "bg-emerald-500/10",
    text: "text-emerald-500",
    role: "text-emerald-400/70",
    stat: "text-emerald-400",
    line: "bg-emerald-500/40",
  },
  amber: {
    glow: "bg-amber-500/20",
    border: "group-hover:border-amber-500/30",
    bg: "bg-amber-500/10",
    text: "text-amber-500",
    role: "text-amber-400/70",
    stat: "text-amber-400",
    line: "bg-amber-500/40",
  },
  sky: {
    glow: "bg-sky-500/20",
    border: "group-hover:border-sky-500/30",
    bg: "bg-sky-500/10",
    text: "text-sky-500",
    role: "text-sky-400/70",
    stat: "text-sky-400",
    line: "bg-sky-500/40",
  },
  purple: {
    glow: "bg-purple-500/20",
    border: "group-hover:border-purple-500/30",
    bg: "bg-purple-500/10",
    text: "text-purple-500",
    role: "text-purple-400/70",
    stat: "text-purple-400",
    line: "bg-purple-500/40",
  },
} as const;

export default function HomePage() {
  const router = useRouter();
  const { user } = useAuth();

  return (
    <main className="min-h-screen bg-[var(--color-bg-app)] overflow-hidden">
      {/* Background gradient effect */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-[var(--color-accent-primary)] opacity-[0.03] blur-[120px] rounded-full" />
        <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-[var(--color-accent-primary)] opacity-[0.02] blur-[100px] rounded-full" />
      </div>

      {/* Hero Section */}
      <section className="relative px-4 pt-20 pb-24 md:pt-32 md:pb-32">
        <div className="mx-auto max-w-5xl text-center">
          {/* Animated Logo */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ ...springPresets.fluid, duration: 0.8 }}
            className="mb-8 flex justify-center"
          >
            <div className="relative">
              <div className="absolute inset-0 blur-2xl bg-[var(--color-accent-primary)] opacity-20 rounded-full scale-150" />
              <Image
                src="/logo-dark-nobg.png"
                alt="Clarus"
                width={110}
                height={110}
                className="relative drop-shadow-2xl"
                priority
              />
            </div>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.fluid, delay: 0.1 }}
            className="text-4xl md:text-6xl font-bold tracking-tight"
          >
            <span className="text-[var(--color-text-primary)]">
              Explore Sacred Texts
            </span>
            <br />
            <span className="bg-gradient-to-r from-[var(--color-accent-primary)] to-purple-400 bg-clip-text text-transparent">
              with AI
            </span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.fluid, delay: 0.2 }}
            className="mt-6 text-lg md:text-xl text-[var(--color-text-secondary)] max-w-2xl mx-auto leading-relaxed"
          >
            Search across Quran and Bible with AI. Discover connections,
            compare perspectives, find answers.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.fluid, delay: 0.3 }}
            className="mt-10 flex flex-col sm:flex-row gap-4 justify-center"
          >
            {user ? (
              <>
                <MagneticButton
                  onClick={() => router.push("/search")}
                  className="px-8 py-3 text-base font-medium"
                >
                  <span className="flex items-center gap-2">
                    <Search className="w-4 h-4" />
                    Go to Search
                  </span>
                </MagneticButton>
                <MagneticButton
                  onClick={() => router.push("/compare")}
                  className="px-8 py-3 text-base font-medium bg-[var(--color-bg-elevated)] text-[var(--color-text-primary)] border border-[var(--color-border-subtle)]"
                >
                  <span className="flex items-center gap-2">
                    <GitCompare className="w-4 h-4" />
                    Compare
                  </span>
                </MagneticButton>
              </>
            ) : (
              <>
                <MagneticButton
                  onClick={() => router.push("/register")}
                  className="px-8 py-3 text-base font-medium"
                >
                  <span className="flex items-center gap-2">
                    Get Started
                    <ArrowRight className="w-4 h-4" />
                  </span>
                </MagneticButton>
                <MagneticButton
                  onClick={() => router.push("/login")}
                  className="px-8 py-3 text-base font-medium bg-[var(--color-bg-elevated)] text-[var(--color-text-primary)] border border-[var(--color-border-subtle)]"
                >
                  Sign In
                </MagneticButton>
              </>
            )}
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="relative px-4 py-24 md:py-32">
        <div className="mx-auto max-w-6xl">
          {/* Section Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={springPresets.fluid}
            className="text-center mb-16"
          >
            <motion.span
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ ...springPresets.snappy, delay: 0.1 }}
              className="inline-block px-4 py-1.5 rounded-full text-xs font-medium tracking-wider uppercase bg-[var(--color-accent-glow)] text-[var(--color-accent-primary)] border border-[var(--color-accent-primary)]/20 mb-6"
            >
              Why Clarus
            </motion.span>
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-text-primary)] tracking-tight">
              Built for Depth, Not Just Speed
            </h2>
            <p className="mt-4 text-[var(--color-text-secondary)] max-w-lg mx-auto leading-relaxed">
              Every layer of the pipeline is designed to maximize retrieval
              accuracy and scholarly rigor.
            </p>
          </motion.div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ ...springPresets.fluid, delay: index * 0.12 }}
                className="group relative"
              >
                <motion.div
                  whileHover={{ y: -6 }}
                  transition={springPresets.snappy}
                  className="relative h-full"
                >
                  {/* Hover glow */}
                  <div className="absolute -inset-px rounded-2xl bg-gradient-to-b from-[var(--color-accent-primary)]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl" />

                  {/* Card */}
                  <div className="relative h-full p-8 rounded-2xl bg-[var(--color-bg-surface)]/80 backdrop-blur-sm border border-[var(--color-border-subtle)] group-hover:border-[var(--color-accent-primary)]/30 transition-colors duration-300 flex flex-col text-center">
                    {/* Icon */}
                    <div className="w-12 h-12 rounded-xl bg-[var(--color-accent-glow)] flex items-center justify-center mx-auto mb-5">
                      <feature.icon className="w-6 h-6 text-[var(--color-accent-primary)]" />
                    </div>

                    {/* Title */}
                    <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-3">
                      {feature.title}
                    </h3>

                    {/* Description */}
                    <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed flex-1">
                      {feature.description}
                    </p>

                    {/* Tech Note */}
                    <div className="mt-5 pt-4 border-t border-[var(--color-border-subtle)]">
                      <span className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest">
                        {feature.techNote}
                      </span>
                    </div>
                  </div>
                </motion.div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Multi-Agent Deep Dive Section */}
      <section className="relative px-4 py-24 md:py-32 overflow-hidden">
        {/* Background */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/3 left-1/4 w-[500px] h-[500px] bg-emerald-500 opacity-[0.02] blur-[120px] rounded-full" />
          <div className="absolute bottom-1/3 right-1/4 w-[500px] h-[500px] bg-purple-500 opacity-[0.02] blur-[120px] rounded-full" />
        </div>

        <div className="mx-auto max-w-6xl relative">
          {/* Section Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={springPresets.fluid}
            className="text-center mb-16"
          >
            <motion.span
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ ...springPresets.snappy, delay: 0.1 }}
              className="inline-block px-4 py-1.5 rounded-full text-xs font-medium tracking-wider uppercase bg-[var(--color-accent-glow)] text-[var(--color-accent-primary)] border border-[var(--color-accent-primary)]/20 mb-6"
            >
              Core Feature
            </motion.span>
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-text-primary)] tracking-tight">
              Multi-Agent Analysis
            </h2>
            <p className="mt-4 text-[var(--color-text-secondary)] max-w-2xl mx-auto leading-relaxed">
              Each question is analyzed by 5 specialized AI agents in parallel
              — 4 scripture experts and 1 comparative theologian — producing a
              comprehensive essay with full citations.
            </p>
          </motion.div>

          {/* 4 Specialist Agent Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {agents.map((agent, index) => {
              const colors = agentColorMap[agent.color];
              return (
                <motion.div
                  key={agent.name}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{
                    ...springPresets.fluid,
                    delay: 0.15 + index * 0.1,
                  }}
                >
                  <motion.div
                    whileHover={{ y: -6, scale: 1.02 }}
                    transition={springPresets.snappy}
                    className="group relative h-full"
                  >
                    {/* Glow effect */}
                    <div
                      className={`absolute -inset-px rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl ${colors.glow}`}
                    />

                    <div
                      className={`relative h-full p-5 rounded-xl bg-[var(--color-bg-surface)]/80 backdrop-blur-sm border border-[var(--color-border-subtle)] transition-colors duration-300 flex flex-col ${colors.border}`}
                    >
                      {/* Icon */}
                      <div
                        className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 mx-auto ${colors.bg}`}
                      >
                        <agent.icon className={`w-5 h-5 ${colors.text}`} />
                      </div>

                      {/* Name & Role */}
                      <h3 className="text-sm font-semibold text-[var(--color-text-primary)] mb-0.5 text-center">
                        {agent.name}
                      </h3>
                      <p className={`text-xs font-medium mb-2 text-center ${colors.role}`}>
                        {agent.role}
                      </p>

                      {/* Description */}
                      <p className="text-xs text-[var(--color-text-muted)] leading-relaxed mb-3 text-center flex-1">
                        {agent.description}
                      </p>

                      {/* Stats */}
                      <div className="pt-2 border-t border-[var(--color-border-subtle)] mt-auto">
                        <p className={`text-xs font-semibold tabular-nums text-center ${colors.stat}`}>
                          {agent.verseCount} verses
                        </p>
                      </div>
                    </div>
                  </motion.div>
                </motion.div>
              );
            })}
          </div>

          {/* Convergence Visual */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="flex justify-center py-4"
          >
            <div className="flex flex-col items-center gap-2">
              {/* Animated color lines */}
              <div className="flex gap-4">
                {(["emerald", "amber", "sky", "purple"] as const).map(
                  (color, i) => (
                    <motion.div
                      key={color}
                      className={`w-0.5 h-8 rounded-full ${agentColorMap[color].line}`}
                      animate={{ opacity: [0.2, 0.8, 0.2] }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        delay: i * 0.2,
                      }}
                    />
                  )
                )}
              </div>
              <ArrowDown className="w-4 h-4 text-[var(--color-accent-primary)] opacity-50" />
            </div>
          </motion.div>

          {/* Summary Agent Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ ...springPresets.fluid, delay: 0.6 }}
            className="max-w-2xl mx-auto"
          >
            <motion.div
              whileHover={{ y: -4 }}
              transition={springPresets.snappy}
              className="group relative"
            >
              {/* Gradient glow */}
              <div className="absolute -inset-px rounded-xl bg-gradient-to-r from-[var(--color-accent-primary)]/20 via-purple-500/20 to-[var(--color-accent-primary)]/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl" />

              <div className="relative p-6 rounded-xl bg-[var(--color-bg-surface)]/80 backdrop-blur-sm border border-[var(--color-border-subtle)] group-hover:border-[var(--color-accent-primary)]/30 transition-colors duration-300 text-center">
                  {/* Icon */}
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-[var(--color-accent-glow)] to-purple-500/10 border border-[var(--color-accent-primary)]/20 flex items-center justify-center mx-auto mb-3">
                    <Sparkles className="w-6 h-6 text-[var(--color-accent-primary)]" />
                  </div>

                  <h3 className="text-base font-semibold text-[var(--color-text-primary)] mb-0.5">
                    Synthesis Agent
                  </h3>
                  <p className="text-xs text-[var(--color-accent-primary)]/70 font-medium mb-2">
                    Comparative Theologian
                  </p>
                  <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed max-w-lg mx-auto">
                    Synthesizes all 4 perspectives into a unified comparative
                    essay — identifying common themes, key differences, and
                    cross-scripture connections with full citation
                    traceability.
                  </p>

                {/* Output Tags */}
                <div className="mt-4 pt-4 border-t border-[var(--color-border-subtle)] flex flex-wrap justify-center gap-2">
                  {[
                    "5-Paragraph Essay",
                    "Common Themes",
                    "Key Differences",
                    "Full Citations",
                  ].map((tag) => (
                    <span
                      key={tag}
                      className="px-2.5 py-1 text-[10px] font-medium rounded-md bg-[var(--color-bg-elevated)] text-[var(--color-text-muted)] border border-[var(--color-border-subtle)]"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* How It Works Section - Premium */}
      <section className="relative px-4 py-24 md:py-32 overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[var(--color-accent-primary)] opacity-[0.02] blur-[150px] rounded-full" />
        </div>

        <div className="mx-auto max-w-6xl relative">
          {/* Section Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={springPresets.fluid}
            className="text-center mb-20"
          >
            <motion.span
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ ...springPresets.snappy, delay: 0.1 }}
              className="inline-block px-4 py-1.5 rounded-full text-xs font-medium tracking-wider uppercase bg-[var(--color-accent-glow)] text-[var(--color-accent-primary)] border border-[var(--color-accent-primary)]/20 mb-6"
            >
              Your Journey
            </motion.span>
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-text-primary)] tracking-tight">
              From Question to Insight
            </h2>
            <p className="mt-4 text-[var(--color-text-secondary)] max-w-lg mx-auto leading-relaxed">
              Every question follows a thoughtful path — from your words to a
              fully cited, multi-perspective analysis.
            </p>
          </motion.div>

          {/* Steps Container */}
          <div className="relative">
            {/* Animated Connection Line - Desktop */}
            <svg
              className="hidden md:block absolute top-[60px] left-[12.5%] right-[12.5%] w-[75%] h-[4px] overflow-visible"
              preserveAspectRatio="none"
            >
              <defs>
                <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="var(--color-accent-primary)" stopOpacity="0" />
                  <stop offset="20%" stopColor="var(--color-accent-primary)" stopOpacity="0.5" />
                  <stop offset="50%" stopColor="var(--color-accent-primary)" stopOpacity="0.8" />
                  <stop offset="80%" stopColor="var(--color-accent-primary)" stopOpacity="0.5" />
                  <stop offset="100%" stopColor="var(--color-accent-primary)" stopOpacity="0" />
                </linearGradient>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur" />
                  <feMerge>
                    <feMergeNode in="coloredBlur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>
              <motion.line
                x1="0"
                y1="2"
                x2="100%"
                y2="2"
                stroke="url(#lineGradient)"
                strokeWidth="2"
                filter="url(#glow)"
                initial={{ pathLength: 0, opacity: 0 }}
                whileInView={{ pathLength: 1, opacity: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
              />
              {/* Animated pulse dot */}
              <motion.circle
                r="4"
                fill="var(--color-accent-primary)"
                filter="url(#glow)"
                initial={{ cx: "0%" }}
                animate={{ cx: ["0%", "100%", "0%"] }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
              >
                <animate attributeName="opacity" values="0;1;1;0" dur="4s" repeatCount="indefinite" />
              </motion.circle>
            </svg>

            {/* Steps Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 md:gap-4">
              {steps.map((step, index) => (
                <motion.div
                  key={step.label}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{
                    ...springPresets.fluid,
                    delay: 0.2 + index * 0.15,
                  }}
                  className="relative group"
                >
                  {/* Step Card */}
                  <motion.div
                    whileHover={{ y: -8, scale: 1.02 }}
                    transition={springPresets.snappy}
                    className="relative h-full"
                  >
                    {/* Glow effect on hover */}
                    <div className="absolute -inset-px rounded-2xl bg-gradient-to-b from-[var(--color-accent-primary)]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl" />

                    {/* Card Content */}
                    <div className="relative h-full p-6 rounded-2xl bg-[var(--color-bg-surface)]/80 backdrop-blur-sm border border-[var(--color-border-subtle)] group-hover:border-[var(--color-accent-primary)]/30 transition-colors duration-300 flex flex-col text-center">
                      {/* Step Number Badge */}
                      <div className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-[var(--color-bg-app)] border-2 border-[var(--color-accent-primary)] flex items-center justify-center">
                        <span className="text-xs font-bold text-[var(--color-accent-primary)]">
                          {String(index + 1).padStart(2, "0")}
                        </span>
                      </div>

                      {/* Icon Container */}
                      <div className="relative mb-5 flex justify-center">
                        <div className="absolute inset-0 bg-[var(--color-accent-primary)] opacity-0 group-hover:opacity-20 blur-2xl rounded-full transition-opacity duration-500" />
                        <div className="relative w-14 h-14 rounded-xl bg-gradient-to-br from-[var(--color-bg-elevated)] to-[var(--color-bg-surface)] border border-[var(--color-border-subtle)] flex items-center justify-center">
                          <step.icon className="w-6 h-6 text-[var(--color-accent-primary)]" />
                        </div>
                      </div>

                      {/* Text Content */}
                      <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-1">
                        {step.label}
                      </h3>
                      <p className="text-sm text-[var(--color-text-muted)] mb-3 flex-1">
                        {step.desc}
                      </p>

                      {/* Detail */}
                      <p className="text-xs text-[var(--color-text-secondary)] pt-3 mt-auto border-t border-[var(--color-border-subtle)]">
                        {step.detail}
                      </p>
                    </div>
                  </motion.div>

                  {/* Mobile Arrow Connector */}
                  {index < steps.length - 1 && (
                    <div className="flex justify-center my-4 md:hidden">
                      <motion.div
                        initial={{ opacity: 0, y: -5 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: 0.3 + index * 0.15 }}
                      >
                        <ArrowRight className="w-5 h-5 text-[var(--color-accent-primary)] rotate-90" />
                      </motion.div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative px-4 py-24 md:py-32 overflow-hidden">
        {/* Dramatic radial glow */}
        <div className="absolute inset-0 pointer-events-none">
          <motion.div
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] rounded-full"
            style={{
              background: "radial-gradient(ellipse at center, var(--color-accent-primary) 0%, transparent 70%)",
              opacity: 0.06,
            }}
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
          />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[300px] bg-purple-500 opacity-[0.03] blur-[100px] rounded-full" />
        </div>

        <div className="mx-auto max-w-3xl relative text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ ...springPresets.fluid, duration: 0.8 }}
          >
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
              <span className="text-[var(--color-text-primary)]">Start exploring </span>
              <span className="bg-gradient-to-r from-[var(--color-accent-primary)] to-purple-400 bg-clip-text text-transparent">
                sacred texts
              </span>
            </h2>
            <p className="text-lg md:text-xl text-[var(--color-text-secondary)] mb-12 max-w-xl mx-auto leading-relaxed">
              {user
                ? "Your scriptures are waiting. Search, compare, discover."
                : "Every verse, every perspective — powered by AI."}
            </p>

            {/* CTA Button with glow */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <motion.div
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.98 }}
                transition={springPresets.snappy}
                className="relative group"
              >
                {/* Button glow */}
                <div className="absolute -inset-1 bg-gradient-to-r from-[var(--color-accent-primary)] to-purple-500 rounded-xl opacity-40 group-hover:opacity-60 blur-lg transition-opacity duration-500" />
                <button
                  onClick={() => router.push(user ? "/search" : "/register")}
                  className="relative px-10 py-4 rounded-xl bg-[var(--color-accent-primary)] text-white font-semibold text-base tracking-wide flex items-center gap-2.5 transition-all duration-200"
                >
                  {user ? (
                    <>
                      <Search className="w-4.5 h-4.5" />
                      Go to Search
                    </>
                  ) : (
                    <>
                      Get Started
                      <ArrowRight className="w-4.5 h-4.5" />
                    </>
                  )}
                </button>
              </motion.div>

              {!user && (
                <button
                  onClick={() => router.push("/login")}
                  className="px-8 py-4 text-sm font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors duration-200"
                >
                  Already have an account?
                </button>
              )}
              {user && (
                <button
                  onClick={() => router.push("/compare")}
                  className="px-8 py-4 text-sm font-medium text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors duration-200 flex items-center gap-2"
                >
                  <GitCompare className="w-4 h-4" />
                  Compare Scriptures
                </button>
              )}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[var(--color-border-subtle)]">
        <div className="mx-auto max-w-6xl px-4 py-12">
          {/* Top: Brand + Nav */}
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-10 mb-10">
            {/* Brand */}
            <div className="flex items-center gap-3">
              <Image src="/logo-dark-nobg.png" alt="Clarus" width={32} height={32} />
              <span className="text-base font-semibold text-[var(--color-text-primary)]">
                Clarus
              </span>
            </div>

            {/* Nav Links */}
            <nav className="flex flex-wrap gap-x-8 gap-y-3">
              {[
                { label: "Search", href: "/search" },
                { label: "Compare", href: "/compare" },
                { label: "History", href: "/history" },
                { label: "Settings", href: "/settings" },
              ].map((link) => (
                <button
                  key={link.label}
                  onClick={() => router.push(link.href)}
                  className="text-sm text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors"
                >
                  {link.label}
                </button>
              ))}
            </nav>
          </div>

          {/* Divider */}
          <div className="h-px bg-[var(--color-border-subtle)] mb-6" />

          {/* Bottom: Copyright */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-3 text-xs text-[var(--color-text-muted)]">
            <span>&copy; {new Date().getFullYear()} Clarus</span>
            <span>AI-powered sacred text search</span>
          </div>
        </div>
      </footer>
    </main>
  );
}
