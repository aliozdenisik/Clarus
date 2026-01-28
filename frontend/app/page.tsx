"use client";

import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { MagneticButton } from "@/components/ui/magnetic-button";
import { GlowCard } from "@/components/ui/glow-card";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/auth-context";
import {
  Search,
  Sparkles,
  GitCompare,
  Zap,
  BookOpen,
  ArrowRight,
  Database,
  Brain,
  Layers,
} from "lucide-react";
import Image from "next/image";

const features = [
  {
    icon: Database,
    title: "Hybrid Search",
    description:
      "Dense + sparse vector fusion with RRF algorithm. Semantic understanding meets keyword precision.",
  },
  {
    icon: Brain,
    title: "Multi-Agent Analysis",
    description:
      "5 specialized AI agents analyze each scripture independently, then synthesize insights.",
  },
  {
    icon: Layers,
    title: "Cross-Scripture",
    description:
      "Search across Quran, Old Testament, New Testament, and Apocrypha simultaneously.",
  },
];

const steps = [
  {
    icon: Search,
    label: "Query",
    desc: "Enter your question",
    detail: "Natural language input with semantic understanding",
  },
  {
    icon: Sparkles,
    label: "Enhance",
    desc: "AI expands context",
    detail: "LLM generates synonyms and related concepts",
  },
  {
    icon: Database,
    label: "Search",
    desc: "Hybrid retrieval",
    detail: "Dense + sparse vectors with RRF fusion",
  },
  {
    icon: Brain,
    label: "Analyze",
    desc: "Multi-agent synthesis",
    detail: "5 specialized agents synthesize insights",
  },
];

const sources = [
  { name: "Quran", count: "6,236", color: "emerald" },
  { name: "Old Testament", count: "23,145", color: "amber" },
  { name: "New Testament", count: "7,957", color: "sky" },
  { name: "Apocrypha", count: "5,717", color: "purple" },
];

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
            <motion.div
              animate={{
                y: [0, -8, 0],
              }}
              transition={{
                duration: 4,
                repeat: Infinity,
                ease: "easeInOut",
              }}
              className="relative"
            >
              <div className="absolute inset-0 blur-2xl bg-[var(--color-accent-primary)] opacity-20 rounded-full scale-150" />
              <Image
                src="/logo-dark-nobg.png"
                alt="Clarus"
                width={180}
                height={180}
                className="relative drop-shadow-2xl"
                priority
              />
            </motion.div>
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
            Semantic search and multi-agent analysis across Quran and Bible.
            Discover connections, compare perspectives, find answers.
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
      <section className="relative px-4 py-20 md:py-28">
        <div className="mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={springPresets.fluid}
            className="text-center mb-12"
          >
            <h2 className="text-2xl md:text-3xl font-bold text-[var(--color-text-primary)]">
              Powerful Features
            </h2>
            <p className="mt-3 text-[var(--color-text-muted)]">
              Built for scholars, researchers, and the curious
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ ...springPresets.fluid, delay: index * 0.1 }}
              >
                <GlowCard className="h-full">
                  <div className="flex flex-col h-full">
                    <div className="w-12 h-12 rounded-lg bg-[var(--color-accent-glow)] flex items-center justify-center mb-4">
                      <feature.icon className="w-6 h-6 text-[var(--color-accent-primary)]" />
                    </div>
                    <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </GlowCard>
              </motion.div>
            ))}
          </div>
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
              Pipeline
            </motion.span>
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--color-text-primary)] tracking-tight">
              How It Works
            </h2>
            <p className="mt-4 text-[var(--color-text-secondary)] max-w-md mx-auto">
              From question to insight — powered by hybrid search and multi-agent AI
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
                    className="relative"
                  >
                    {/* Glow effect on hover */}
                    <div className="absolute -inset-px rounded-2xl bg-gradient-to-b from-[var(--color-accent-primary)]/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl" />

                    {/* Card Content */}
                    <div className="relative p-6 rounded-2xl bg-[var(--color-bg-surface)]/80 backdrop-blur-sm border border-[var(--color-border-subtle)] group-hover:border-[var(--color-accent-primary)]/30 transition-colors duration-300">
                      {/* Step Number Badge */}
                      <div className="absolute -top-3 -right-3 w-8 h-8 rounded-full bg-[var(--color-bg-app)] border-2 border-[var(--color-accent-primary)] flex items-center justify-center">
                        <span className="text-xs font-bold text-[var(--color-accent-primary)]">
                          {String(index + 1).padStart(2, "0")}
                        </span>
                      </div>

                      {/* Icon Container */}
                      <div className="relative mb-5">
                        <div className="absolute inset-0 bg-[var(--color-accent-primary)] opacity-0 group-hover:opacity-20 blur-2xl rounded-full transition-opacity duration-500" />
                        <div className="relative w-14 h-14 rounded-xl bg-gradient-to-br from-[var(--color-bg-elevated)] to-[var(--color-bg-surface)] border border-[var(--color-border-subtle)] flex items-center justify-center">
                          <step.icon className="w-6 h-6 text-[var(--color-accent-primary)]" />
                        </div>
                      </div>

                      {/* Text Content */}
                      <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-1">
                        {step.label}
                      </h3>
                      <p className="text-sm text-[var(--color-text-muted)] mb-3">
                        {step.desc}
                      </p>

                      {/* Detail - Revealed on hover */}
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        whileInView={{ height: "auto", opacity: 1 }}
                        className="overflow-hidden"
                      >
                        <p className="text-xs text-[var(--color-text-secondary)] pt-3 border-t border-[var(--color-border-subtle)]">
                          {step.detail}
                        </p>
                      </motion.div>
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

      {/* Sources Section */}
      <section className="relative px-4 py-20 md:py-28">
        <div className="mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={springPresets.fluid}
            className="text-center mb-12"
          >
            <h2 className="text-2xl md:text-3xl font-bold text-[var(--color-text-primary)]">
              Scripture Sources
            </h2>
            <p className="mt-3 text-[var(--color-text-muted)]">
              43,055 verses indexed and searchable
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {sources.map((source, index) => (
              <motion.div
                key={source.name}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ ...springPresets.fluid, delay: index * 0.05 }}
              >
                <motion.div
                  whileHover={{ y: -4 }}
                  transition={springPresets.snappy}
                  className="p-5 rounded-lg bg-[var(--color-bg-surface)] border border-[var(--color-border-subtle)] text-center"
                >
                  <BookOpen
                    className={`w-8 h-8 mx-auto mb-3 ${
                      source.color === "emerald"
                        ? "text-emerald-500"
                        : source.color === "amber"
                          ? "text-amber-500"
                          : source.color === "sky"
                            ? "text-sky-500"
                            : "text-purple-500"
                    }`}
                  />
                  <h3 className="font-medium text-[var(--color-text-primary)] text-sm">
                    {source.name}
                  </h3>
                  <p className="text-xs text-[var(--color-text-muted)] mt-1">
                    {source.count} verses
                  </p>
                </motion.div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="relative px-4 py-12 border-y border-[var(--color-border-subtle)]">
        <div className="mx-auto max-w-5xl">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="flex flex-wrap justify-center gap-8 md:gap-16"
          >
            {[
              { value: "43,055", label: "Indexed Verses" },
              { value: "4", label: "Scripture Collections" },
              { value: "5", label: "AI Agents" },
              { value: "3072", label: "Vector Dimensions" },
            ].map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ ...springPresets.fluid, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="text-2xl md:text-3xl font-bold text-[var(--color-text-primary)]">
                  {stat.value}
                </div>
                <div className="text-xs text-[var(--color-text-muted)] mt-1">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Footer */}
      <section className="relative px-4 py-24 md:py-32">
        <div className="mx-auto max-w-3xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={springPresets.fluid}
          >
            <GitCompare className="w-12 h-12 mx-auto mb-6 text-[var(--color-accent-primary)]" />
            <h2 className="text-2xl md:text-4xl font-bold text-[var(--color-text-primary)] mb-4">
              {user ? "Start Exploring" : "Ready to Explore?"}
            </h2>
            <p className="text-[var(--color-text-secondary)] mb-8 max-w-lg mx-auto">
              {user
                ? "Dive into semantic search and multi-agent analysis across sacred texts."
                : "Join researchers and scholars using AI to discover insights across sacred texts."}
            </p>
            <MagneticButton
              onClick={() => router.push(user ? "/search" : "/register")}
              className="px-10 py-4 text-base font-medium"
            >
              <span className="flex items-center gap-2">
                {user ? <Search className="w-4 h-4" /> : <Zap className="w-4 h-4" />}
                {user ? "Go to Search" : "Get Started"}
              </span>
            </MagneticButton>
          </motion.div>
        </div>
      </section>

      {/* Footer - Premium */}
      <footer className="relative border-t border-[var(--color-border-subtle)]">
        {/* Background gradient */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-[var(--color-accent-primary)] opacity-[0.02] blur-[100px] rounded-full" />
        </div>

        <div className="relative mx-auto max-w-6xl px-4 py-16">
          {/* Main Footer Content */}
          <div className="grid grid-cols-1 md:grid-cols-12 gap-12 md:gap-8 mb-12">
            {/* Brand Column */}
            <div className="md:col-span-4">
              <div className="flex items-center gap-3 mb-4">
                <Image src="/logo-dark-nobg.png" alt="Clarus" width={40} height={40} />
                <span className="text-xl font-semibold text-[var(--color-text-primary)]">
                  Clarus
                </span>
              </div>
              <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed mb-6 max-w-xs">
                AI-powered semantic search engine for sacred texts. Explore Quran and Bible with hybrid vector search and multi-agent analysis.
              </p>
              {/* Tech Badges */}
              <div className="flex flex-wrap gap-2">
                {["Qdrant", "FastAPI", "Next.js", "OpenAI"].map((tech) => (
                  <span
                    key={tech}
                    className="px-2.5 py-1 text-xs rounded-md bg-[var(--color-bg-surface)] border border-[var(--color-border-subtle)] text-[var(--color-text-muted)]"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>

            {/* Navigation Column */}
            <div className="md:col-span-2">
              <h4 className="text-sm font-semibold text-[var(--color-text-primary)] mb-4">
                Navigate
              </h4>
              <ul className="space-y-3">
                {[
                  { label: "Search", href: "/search" },
                  { label: "Compare", href: "/compare" },
                  { label: "History", href: "/history" },
                  { label: "Settings", href: "/settings" },
                ].map((link) => (
                  <li key={link.label}>
                    <button
                      onClick={() => router.push(link.href)}
                      className="text-sm text-[var(--color-text-muted)] hover:text-[var(--color-accent-primary)] transition-colors"
                    >
                      {link.label}
                    </button>
                  </li>
                ))}
              </ul>
            </div>

            {/* Sources Column */}
            <div className="md:col-span-3">
              <h4 className="text-sm font-semibold text-[var(--color-text-primary)] mb-4">
                Scripture Sources
              </h4>
              <ul className="space-y-3">
                {[
                  { label: "Quran (Turkish)", count: "6,236" },
                  { label: "Old Testament", count: "23,145" },
                  { label: "New Testament", count: "7,957" },
                  { label: "Apocrypha", count: "5,717" },
                ].map((source) => (
                  <li key={source.label} className="flex items-center justify-between text-sm">
                    <span className="text-[var(--color-text-muted)]">{source.label}</span>
                    <span className="text-[var(--color-text-secondary)] tabular-nums">
                      {source.count}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Stats Column */}
            <div className="md:col-span-3">
              <h4 className="text-sm font-semibold text-[var(--color-text-primary)] mb-4">
                Platform
              </h4>
              <div className="space-y-4">
                <div className="p-4 rounded-lg bg-[var(--color-bg-surface)]/50 border border-[var(--color-border-subtle)]">
                  <div className="text-2xl font-bold text-[var(--color-text-primary)] mb-1">
                    43,055
                  </div>
                  <div className="text-xs text-[var(--color-text-muted)]">
                    Total Indexed Verses
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded-lg bg-[var(--color-bg-surface)]/30 border border-[var(--color-border-subtle)] text-center">
                    <div className="text-lg font-semibold text-[var(--color-accent-primary)]">5</div>
                    <div className="text-xs text-[var(--color-text-muted)]">AI Agents</div>
                  </div>
                  <div className="p-3 rounded-lg bg-[var(--color-bg-surface)]/30 border border-[var(--color-border-subtle)] text-center">
                    <div className="text-lg font-semibold text-[var(--color-accent-primary)]">3072</div>
                    <div className="text-xs text-[var(--color-text-muted)]">Dimensions</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="h-px bg-gradient-to-r from-transparent via-[var(--color-border-subtle)] to-transparent mb-8" />

          {/* Bottom Bar */}
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-[var(--color-text-muted)]">
            <div className="flex items-center gap-1">
              <span>Built with</span>
              <span className="text-[var(--color-accent-primary)]">hybrid search</span>
              <span>& multi-agent AI</span>
            </div>
            <div className="flex items-center gap-6">
              <span>Qdrant Vector DB</span>
              <span className="w-1 h-1 rounded-full bg-[var(--color-border-glow)]" />
              <span>OpenAI Embeddings</span>
              <span className="w-1 h-1 rounded-full bg-[var(--color-border-glow)]" />
              <span>RRF Fusion</span>
            </div>
          </div>
        </div>
      </footer>
    </main>
  );
}
