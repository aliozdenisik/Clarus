"use client";

import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { MagneticButton } from "@/components/ui/magnetic-button";
import { TextRotate, LuxuryQuote } from "@/components/ui/text-rotate";

import { DotPattern, RadialGradient, GridPattern } from "@/components/ui/dot-pattern";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/auth-context";
import {
  Search,
  Sparkles,
  GitCompare,
  BookOpen,
  ArrowRight,
  Brain,
  Layers,
  ScrollText,
  BookMarked,
  Library,
} from "lucide-react";
import Image from "next/image";
import { BentoGrid, BentoCard } from "@/components/ui/bento-grid";

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
    gradient: "bg-gradient-to-b from-emerald-500/5 to-transparent",
    iconBg: "bg-emerald-500/10",
    iconBorder: "border-emerald-500/20",
    text: "text-emerald-400",
    badge: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/20",
    stat: "text-emerald-400/80",
    dot: "bg-emerald-400",
    line: "bg-emerald-600/30",
  },
  amber: {
    gradient: "bg-gradient-to-b from-amber-500/5 to-transparent",
    iconBg: "bg-amber-500/10",
    iconBorder: "border-amber-500/20",
    text: "text-amber-400",
    badge: "bg-amber-500/15 text-amber-400 border border-amber-500/20",
    stat: "text-amber-400/80",
    dot: "bg-amber-400",
    line: "bg-amber-600/30",
  },
  sky: {
    gradient: "bg-gradient-to-b from-sky-500/5 to-transparent",
    iconBg: "bg-sky-500/10",
    iconBorder: "border-sky-500/20",
    text: "text-sky-400",
    badge: "bg-sky-500/15 text-sky-400 border border-sky-500/20",
    stat: "text-sky-400/80",
    dot: "bg-sky-400",
    line: "bg-sky-600/30",
  },
  purple: {
    gradient: "bg-gradient-to-b from-purple-500/5 to-transparent",
    iconBg: "bg-purple-500/10",
    iconBorder: "border-purple-500/20",
    text: "text-purple-400",
    badge: "bg-purple-500/15 text-purple-400 border border-purple-500/20",
    stat: "text-purple-400/80",
    dot: "bg-purple-400",
    line: "bg-purple-600/30",
  },
} as const;

export default function HomePage() {
  const router = useRouter();
  const { user } = useAuth();

  return (
    <main className="min-h-screen bg-[var(--color-bg-app)] overflow-hidden">
      {/* Premium ambient effects */}
      <div className="fixed inset-0 pointer-events-none">
        <DotPattern width={40} height={40} cr={0.4} className="opacity-[0.04]" />
        <RadialGradient 
          className="inset-0" 
          color="var(--color-accent-primary)" 
          size="1200px" 
          position="50% -20%" 
          opacity={0.06}
        />
        <RadialGradient 
          className="inset-0" 
          color="var(--color-accent-secondary)" 
          size="800px" 
          position="80% 60%" 
          opacity={0.04}
        />
      </div>

      {/* Hero Section - Centered Layout */}
      <section className="relative px-6 pt-32 pb-32 md:pt-48 md:pb-40">
        <div className="mx-auto max-w-[1200px] flex flex-col items-center text-center">
          {/* Logo - Centered */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.gentle, duration: 1.2 }}
            className="mb-16"
          >
            <div className="relative">
              <div className="absolute inset-0 blur-3xl bg-[var(--color-accent-primary)] opacity-10 rounded-full scale-150" />
              <Image
                src="/logo-dark-nobg.png"
                alt="Clarus"
                width={120}
                height={120}
                className="relative opacity-90"
                priority
              />
            </div>
          </motion.div>

          {/* Headline - Large editorial typography */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.gentle, delay: 0.2, duration: 1.2 }}
            className="max-w-[900px] flex flex-col items-center"
          >
            <h1 className="font-[family-name:var(--font-serif)] text-6xl md:text-8xl font-normal tracking-tight leading-[1.1] mb-8">
              <span className="text-[var(--color-text-primary)]">
                Explore Sacred Texts
              </span>
              <br />
              <span className="text-[var(--color-accent-primary)]">
                with AI
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-[var(--color-text-secondary)] max-w-[600px] mx-auto leading-relaxed font-light tracking-wide mb-16">
              Search across Quran and Bible with AI. Discover connections,
              compare perspectives, find answers.
            </p>

            {/* CTA Buttons - Luxury */}
            <div className="flex flex-col sm:flex-row gap-5">
              {user ? (
                <>
                  <motion.button
                    onClick={() => router.push("/search")}
                    className="px-10 py-4 rounded-xl bg-indigo-600 border border-indigo-500/50 text-white font-medium hover:bg-indigo-500 transition-colors duration-200 flex items-center justify-center gap-3"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Search className="w-4 h-4" />
                    Go to Search
                  </motion.button>
                  <motion.button
                    onClick={() => router.push("/compare")}
                    className="px-10 py-4 rounded-xl bg-transparent border border-white/20 text-white font-medium hover:bg-white/5 hover:border-white/30 transition-colors duration-200 flex items-center justify-center gap-3"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <GitCompare className="w-4 h-4" />
                    Compare
                  </motion.button>
                </>
              ) : (
                <>
                  <motion.button
                    onClick={() => router.push("/register")}
                    className="px-10 py-4 rounded-xl bg-indigo-600 border border-indigo-500/50 text-white font-medium hover:bg-indigo-500 transition-colors duration-200 flex items-center justify-center gap-3"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Get Started
                    <ArrowRight className="w-4 h-4" />
                  </motion.button>
                  <motion.button
                    onClick={() => router.push("/login")}
                    className="px-10 py-4 rounded-xl bg-transparent border border-white/20 text-white font-medium hover:bg-white/5 hover:border-white/30 transition-colors duration-200 flex items-center justify-center gap-3"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    Sign In
                  </motion.button>
                </>
              )}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Inspiring Quote Section */}
      <section className="relative px-6 py-16 md:py-20">
        <div className="mx-auto max-w-[900px]">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 1.5 }}
          >
            <LuxuryQuote
              quotes={[
                { 
                  text: "The beginning of wisdom is the fear of the Lord, and knowledge of the Holy One is understanding.",
                  source: "Proverbs 9:10"
                },
                { 
                  text: "Indeed, with hardship comes ease. Indeed, with hardship comes ease.",
                  source: "Quran 94:5-6"
                },
                { 
                  text: "Love is patient, love is kind. It does not envy, it does not boast, it is not proud.",
                  source: "1 Corinthians 13:4"
                },
                { 
                  text: "And We have certainly made the Quran easy for remembrance, so is there any who will remember?",
                  source: "Quran 54:17"
                },
              ]}
              rotationInterval={6000}
              className="py-8"
            />
          </motion.div>
        </div>
      </section>

      {/* Features Section - Bento Grid */}
      <section className="relative px-6 py-28 md:py-36">
        <div className="mx-auto max-w-[1200px]">
          {/* Section Header - Centered */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ ...springPresets.gentle, duration: 1 }}
            className="mb-20 text-center"
          >
            <span className="inline-block text-xs font-medium tracking-[0.2em] uppercase text-[var(--color-accent-primary)] mb-6">
              Why Clarus
            </span>
            <h2 className="font-[family-name:var(--font-serif)] text-5xl md:text-6xl font-normal text-[var(--color-text-primary)] tracking-tight leading-tight max-w-[700px] mx-auto">
              Built for Depth, Not Just Speed
            </h2>
          </motion.div>

          {/* Bento Grid */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ ...springPresets.gentle, duration: 1 }}
          >
            <BentoGrid className="md:grid-cols-3">
              {features.map((feature, index) => (
                <BentoCard
                  key={feature.title}
                  name={feature.title}
                  className="md:col-span-1"
                  background={
                    <div className="absolute inset-0 bg-gradient-to-br from-[var(--color-accent-primary)]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  }
                  Icon={feature.icon}
                  description={feature.description}
                  href={user ? "/search" : "/register"}
                  cta="Explore"
                />
              ))}
            </BentoGrid>
          </motion.div>

          {/* Tech Notes - Below Grid */}
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5, duration: 1 }}
            className="mt-8 grid md:grid-cols-3 gap-8"
          >
            {features.map((feature) => (
              <div key={feature.techNote} className="text-center">
                <span className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-[0.15em] font-medium">
                  {feature.techNote}
                </span>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Multi-Agent Section - Sophisticated Color-Coding */}
      <section className="relative px-6 py-28 md:py-36 overflow-hidden">
        <div className="mx-auto max-w-[1200px]">
          {/* Section Header */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ ...springPresets.gentle, duration: 1 }}
            className="mb-20 text-center"
          >
            <span className="inline-block text-xs font-medium tracking-[0.2em] uppercase text-[var(--color-accent-primary)] mb-6">
              Core Feature
            </span>
            <h2 className="font-[family-name:var(--font-serif)] text-5xl md:text-6xl font-normal text-[var(--color-text-primary)] tracking-tight leading-tight mb-8 max-w-[700px] mx-auto">
              Multi-Agent Analysis
            </h2>
            <p className="text-lg text-[var(--color-text-secondary)] max-w-[650px] leading-relaxed font-light mx-auto">
              Each question is analyzed by 5 specialized AI agents in parallel
              — 4 scripture experts and 1 comparative theologian — producing a
              comprehensive essay with full citations.
            </p>
          </motion.div>

          {/* 4 Specialist Agent Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {agents.map((agent, index) => {
              const colors = agentColorMap[agent.color];
              return (
                <motion.div
                  key={agent.name}
                  initial={{ opacity: 0, y: 40 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{
                    ...springPresets.gentle,
                    delay: 0.2 + index * 0.1,
                    duration: 1,
                  }}
                >
                  <div className={`group relative h-full p-6 rounded-2xl border border-white/[0.08] bg-gradient-to-b from-white/[0.04] to-transparent backdrop-blur-xl shadow-lg shadow-black/20 hover:border-white/[0.15] hover:from-white/[0.06] transition-all duration-500`}>
                    {/* Subtle gradient overlay */}
                    <div className={`absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 ${colors.gradient}`} />
                    
                    {/* Content */}
                    <div className="relative z-10">
                      {/* Icon */}
                      <div className={`w-12 h-12 mb-5 flex items-center justify-center rounded-xl ${colors.iconBg} border ${colors.iconBorder}`}>
                        <agent.icon className={`w-5 h-5 ${colors.text}`} />
                      </div>

                      {/* Name & Role Badge */}
                      <h3 className="text-base font-semibold text-white mb-2">
                        {agent.name}
                      </h3>
                      <span className={`inline-block px-2.5 py-1 rounded-full text-[10px] font-medium tracking-wide uppercase mb-4 ${colors.badge}`}>
                        {agent.role}
                      </span>

                      {/* Description */}
                      <p className="text-sm text-zinc-400 leading-relaxed mb-5">
                        {agent.description}
                      </p>

                      {/* Stats */}
                      <div className="flex items-center gap-2 pt-4 border-t border-white/[0.06]">
                        <div className={`w-1.5 h-1.5 rounded-full ${colors.dot}`} />
                        <p className={`text-xs font-medium tabular-nums ${colors.stat}`}>
                          {agent.verseCount} verses indexed
                        </p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Summary Agent Card */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ ...springPresets.gentle, delay: 0.7, duration: 1 }}
            className="max-w-[800px] mx-auto"
          >
            <div className="group relative p-10 rounded-2xl border border-white/[0.08] bg-gradient-to-b from-white/[0.04] to-transparent backdrop-blur-xl shadow-lg shadow-black/20 hover:border-white/[0.15] hover:from-white/[0.06] transition-all duration-500">
              {/* Subtle gradient overlay */}
              <div className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-gradient-to-b from-indigo-500/5 to-transparent" />
              
              {/* Content */}
              <div className="relative z-10">
                {/* Icon */}
                <div className="w-14 h-14 mb-6 flex items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/20">
                  <Sparkles className="w-6 h-6 text-indigo-400" />
                </div>

                {/* Name & Role Badge */}
                <h3 className="text-xl font-semibold text-white mb-3">
                  Synthesis Agent
                </h3>
                <span className="inline-block px-3 py-1.5 rounded-full text-[10px] font-medium tracking-wide uppercase mb-5 bg-indigo-500/15 text-indigo-400 border border-indigo-500/20">
                  Comparative Theologian
                </span>

                {/* Description */}
                <p className="text-base text-zinc-400 leading-relaxed mb-8 max-w-2xl">
                  Synthesizes all 4 perspectives into a unified comparative
                  essay — identifying common themes, key differences, and
                  cross-scripture connections with full citation
                  traceability.
                </p>

                {/* Output Tags */}
                <div className="pt-6 border-t border-white/[0.06] flex flex-wrap gap-2">
                  {[
                    "5-Paragraph Essay",
                    "Common Themes",
                    "Key Differences",
                    "Full Citations",
                  ].map((tag) => (
                    <span
                      key={tag}
                      className="px-3 py-1.5 text-[10px] font-medium tracking-wide uppercase rounded-lg bg-white/[0.04] border border-white/[0.08] text-zinc-400 hover:bg-white/[0.08] hover:text-zinc-300 transition-colors"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How It Works Section - Clean Timeline */}
      <section className="relative px-6 py-28 md:py-36 overflow-hidden">
        <div className="mx-auto max-w-[1200px]">
          {/* Section Header */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ ...springPresets.gentle, duration: 1 }}
            className="mb-20 text-center"
          >
            <span className="inline-block text-xs font-medium tracking-[0.2em] uppercase text-[var(--color-accent-primary)] mb-6">
              Your Journey
            </span>
            <h2 className="font-[family-name:var(--font-serif)] text-5xl md:text-6xl font-normal text-[var(--color-text-primary)] tracking-tight leading-tight max-w-[700px] mx-auto">
              From Question to Insight
            </h2>
          </motion.div>

          {/* Steps Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
            {steps.map((step, index) => (
              <motion.div
                key={step.label}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{
                  ...springPresets.gentle,
                  delay: 0.2 + index * 0.15,
                  duration: 1,
                }}
                className="relative"
              >
                {/* Step Number */}
                <div className="mb-8">
                  <span className="text-6xl font-[family-name:var(--font-serif)] text-[var(--color-accent-primary)]/20">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>

                {/* Icon */}
                <div className="w-12 h-12 mb-6 flex items-center justify-center border border-[var(--color-border-subtle)]">
                  <step.icon className="w-5 h-5 text-[var(--color-accent-primary)]" />
                </div>

                {/* Text Content */}
                <h3 className="text-xl font-medium text-[var(--color-text-primary)] mb-3 tracking-wide">
                  {step.label}
                </h3>
                <p className="text-sm text-[var(--color-text-muted)] mb-4 font-light">
                  {step.desc}
                </p>
                <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed font-light">
                  {step.detail}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section - 21st.dev Pattern */}
      <section className="relative bg-[var(--color-bg-app)] py-36 px-6 overflow-hidden">
        <div className="max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ ...springPresets.gentle, duration: 1.2 }}
          >
            <h2 className="font-[family-name:var(--font-serif)] text-6xl md:text-7xl leading-tight mb-8 text-[var(--color-text-primary)]">
              {user ? "Your Scriptures Await" : "Transform Your Search Into"}{' '}
              <span className="text-[var(--color-accent-primary)]">
                {user ? "Discovery" : "Insight"}
              </span>
            </h2>
            <p className="text-lg md:text-xl text-[var(--color-text-secondary)] max-w-2xl mx-auto mb-12 leading-relaxed">
              {user
                ? "Search across 43,055 verses. Compare perspectives. Discover connections you never knew existed."
                : "Join thousands exploring sacred texts with AI-powered search. Every verse, every perspective, every answer — at your fingertips."}
            </p>
            <div className="inline-block">
              <motion.button
                onClick={() => router.push(user ? "/search" : "/register")}
                className="px-12 py-5 rounded-xl bg-indigo-600 border border-indigo-500/50 text-white text-lg font-medium hover:bg-indigo-500 transition-colors duration-200 flex items-center gap-3"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {user ? "Go to Search" : "Begin Your Journey"}
                <ArrowRight className="w-5 h-5" />
              </motion.button>
            </div>
            <div className="mt-16 flex items-center justify-center gap-8 text-sm text-[var(--color-text-muted)]">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[var(--color-accent-primary)]" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[var(--color-accent-primary)]" />
                <span>43,055 verses indexed</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[var(--color-accent-primary)]" />
                <span>5-agent AI analysis</span>
              </div>
            </div>
          </motion.div>
        </div>
        {/* Background blurs */}
        <div className="absolute top-0 left-0 w-full h-full pointer-events-none opacity-5">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[var(--color-accent-primary)] rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[var(--color-accent-primary)] rounded-full blur-3xl" />
        </div>
      </section>


    </main>
  );
}
