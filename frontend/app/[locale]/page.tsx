"use client"

import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { LuxuryQuote } from "@/components/ui/text-rotate"
import { useTranslations } from "next-intl"

import { DotPattern, RadialGradient } from "@/components/ui/dot-pattern"
import { useRouter } from "next/navigation"
import { useSession } from "@/lib/auth-client"
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
} from "lucide-react"
import Image from "next/image"
import { BentoGrid, BentoCard } from "@/components/ui/bento-grid"

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
} as const

export default function HomePage() {
  const router = useRouter()
  const { data: session } = useSession()
  const user = session?.user
  const tLanding = useTranslations("Landing")
  const tCommon = useTranslations("Common")

  const features = [
    {
      icon: Sparkles,
      title: tLanding("features.semantic.title"),
      description: tLanding("features.semantic.description"),
      techNote: tLanding("features.semantic.techNote"),
    },
    {
      icon: Layers,
      title: tLanding("features.parallel.title"),
      description: tLanding("features.parallel.description"),
      techNote: tLanding("features.parallel.techNote"),
    },
    {
      icon: BookMarked,
      title: tLanding("features.traceable.title"),
      description: tLanding("features.traceable.description"),
      techNote: tLanding("features.traceable.techNote"),
    },
  ]

  const steps = [
    {
      icon: Search,
      label: tLanding("howItWorks.ask.label"),
      desc: tLanding("howItWorks.ask.description"),
      detail: tLanding("howItWorks.ask.detail"),
    },
    {
      icon: Sparkles,
      label: tLanding("howItWorks.enrich.label"),
      desc: tLanding("howItWorks.enrich.description"),
      detail: tLanding("howItWorks.enrich.detail"),
    },
    {
      icon: Layers,
      label: tLanding("howItWorks.discover.label"),
      desc: tLanding("howItWorks.discover.description"),
      detail: tLanding("howItWorks.discover.detail"),
    },
    {
      icon: Brain,
      label: tLanding("howItWorks.understand.label"),
      desc: tLanding("howItWorks.understand.description"),
      detail: tLanding("howItWorks.understand.detail"),
    },
  ]

  const agents = [
    {
      name: tLanding("agents.quran.name"),
      role: tLanding("agents.quran.role"),
      description: tLanding("agents.quran.description"),
      collection: tLanding("agents.quran.collection"),
      verseCount: tLanding("agents.quran.verseCount"),
      color: "emerald" as const,
      icon: BookOpen,
    },
    {
      name: tLanding("agents.oldTestament.name"),
      role: tLanding("agents.oldTestament.role"),
      description: tLanding("agents.oldTestament.description"),
      collection: tLanding("agents.oldTestament.collection"),
      verseCount: tLanding("agents.oldTestament.verseCount"),
      color: "amber" as const,
      icon: ScrollText,
    },
    {
      name: tLanding("agents.newTestament.name"),
      role: tLanding("agents.newTestament.role"),
      description: tLanding("agents.newTestament.description"),
      collection: tLanding("agents.newTestament.collection"),
      verseCount: tLanding("agents.newTestament.verseCount"),
      color: "sky" as const,
      icon: BookMarked,
    },
    {
      name: tLanding("agents.apocrypha.name"),
      role: tLanding("agents.apocrypha.role"),
      description: tLanding("agents.apocrypha.description"),
      collection: tLanding("agents.apocrypha.collection"),
      verseCount: tLanding("agents.apocrypha.verseCount"),
      color: "purple" as const,
      icon: Library,
    },
  ]

  return (
    <main className="min-h-screen overflow-hidden bg-[var(--color-bg-app)]">
      {/* Premium ambient effects */}
      <div className="pointer-events-none fixed inset-0">
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
        <div className="mx-auto flex max-w-[1200px] flex-col items-center text-center">
          {/* Logo - Centered */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.gentle, duration: 1.2 }}
            className="mb-16"
          >
            <div className="relative">
              <div className="absolute inset-0 scale-150 rounded-full bg-[var(--color-accent-primary)] opacity-10 blur-3xl" />
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
            className="flex max-w-[900px] flex-col items-center"
          >
            <h1 className="mb-8 font-[family-name:var(--font-serif)] text-6xl leading-[1.1] font-normal tracking-tight md:text-8xl">
              <span className="text-[var(--color-text-primary)]">{tLanding("hero.title")}</span>
              <br />
              <span className="text-[var(--color-accent-primary)]">{tLanding("hero.titleAI")}</span>
            </h1>

            <p className="mx-auto mb-16 max-w-[600px] text-xl leading-relaxed font-light tracking-wide text-[var(--color-text-secondary)] md:text-2xl">
              {tLanding("hero.subtitle")}
            </p>

            {/* CTA Buttons - Luxury */}
            <div className="flex flex-col gap-5 sm:flex-row">
              {user ? (
                <>
                  <motion.button
                    onClick={() => router.push("/search")}
                    className="flex items-center justify-center gap-3 rounded-xl border border-indigo-500/50 bg-indigo-600 px-10 py-4 font-medium text-white transition-colors duration-200 hover:bg-indigo-500"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Search className="h-4 w-4" />
                    {tLanding("hero.goToSearch")}
                  </motion.button>
                  <motion.button
                    onClick={() => router.push("/compare")}
                    className="flex items-center justify-center gap-3 rounded-xl border border-white/20 bg-transparent px-10 py-4 font-medium text-white transition-colors duration-200 hover:border-white/30 hover:bg-white/5"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <GitCompare className="h-4 w-4" />
                    {tLanding("hero.goToCompare")}
                  </motion.button>
                </>
              ) : (
                <>
                  <motion.button
                    onClick={() => router.push("/sign-up")}
                    className="flex items-center justify-center gap-3 rounded-xl border border-indigo-500/50 bg-indigo-600 px-10 py-4 font-medium text-white transition-colors duration-200 hover:bg-indigo-500"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {tCommon("getStarted")}
                    <ArrowRight className="h-4 w-4" />
                  </motion.button>
                  <motion.button
                    onClick={() => router.push("/sign-in")}
                    className="flex items-center justify-center gap-3 rounded-xl border border-white/20 bg-transparent px-10 py-4 font-medium text-white transition-colors duration-200 hover:border-white/30 hover:bg-white/5"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {tCommon("signIn")}
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
                  text: "Yaratan Rabbinin adıyla oku!",
                  source: "Al-Alaq 96:1",
                },
                {
                  text: "The heart of the prudent getteth knowledge...",
                  source: "Proverbs 18:15",
                },
                {
                  text: "Bilenlerle bilmeyenler bir olur mu?",
                  source: "Az-Zumar 39:9",
                },
                {
                  text: "Charity suffereth long, and is kind...",
                  source: "1 Corinthians 13:4",
                },
                {
                  text: "Rabbim! ilmimi artır",
                  source: "Taha 20:114",
                },
                {
                  text: "Wisdom is the principal thing; therefore get wisdom...",
                  source: "Proverbs 4:7",
                },
                {
                  text: "Wisdom is glorious, and never fadeth away...",
                  source: "Wisdom 6:12",
                },
              ]}
              rotationInterval={8000}
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
            <span className="mb-6 inline-block text-xs font-medium tracking-[0.2em] text-[var(--color-accent-primary)] uppercase">
              Why Clarus
            </span>
            <h2 className="mx-auto max-w-[700px] font-[family-name:var(--font-serif)] text-5xl leading-tight font-normal tracking-tight text-[var(--color-text-primary)] md:text-6xl">
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
              {features.map((feature) => (
                <BentoCard
                  key={feature.title}
                  name={feature.title}
                  className="md:col-span-1"
                  background={
                    <div className="absolute inset-0 bg-gradient-to-br from-[var(--color-accent-primary)]/5 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                  }
                  Icon={feature.icon}
                  description={feature.description}
                  href={user ? "/search" : "/sign-up"}
                  cta={tCommon("learnMore")}
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
            className="mt-8 grid gap-8 md:grid-cols-3"
          >
            {features.map((feature) => (
              <div key={feature.techNote} className="text-center">
                <span className="text-[10px] font-medium tracking-[0.15em] text-[var(--color-text-muted)] uppercase">
                  {feature.techNote}
                </span>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Multi-Agent Section - Sophisticated Color-Coding */}
      <section className="relative overflow-hidden px-6 py-28 md:py-36">
        <div className="mx-auto max-w-[1200px]">
          {/* Section Header */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ ...springPresets.gentle, duration: 1 }}
            className="mb-20 text-center"
          >
            <span className="mb-6 inline-block text-xs font-medium tracking-[0.2em] text-[var(--color-accent-primary)] uppercase">
              Core Feature
            </span>
            <h2 className="mx-auto mb-8 max-w-[700px] font-[family-name:var(--font-serif)] text-5xl leading-tight font-normal tracking-tight text-[var(--color-text-primary)] md:text-6xl">
              {tLanding("agents.title")}
            </h2>
            <p className="mx-auto max-w-[650px] text-lg leading-relaxed font-light text-[var(--color-text-secondary)]">
              Each question is analyzed by 5 specialized AI agents in parallel — 4 scripture experts
              and 1 comparative theologian — producing a comprehensive essay with full citations.
            </p>
          </motion.div>

          {/* 4 Specialist Agent Cards */}
          <div className="mb-12 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {agents.map((agent, index) => {
              const colors = agentColorMap[agent.color]
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
                  <div
                    className={`group relative h-full rounded-2xl border border-white/[0.08] bg-gradient-to-b from-white/[0.04] to-transparent p-6 shadow-lg shadow-black/20 backdrop-blur-xl transition-all duration-500 hover:border-white/[0.15] hover:from-white/[0.06]`}
                  >
                    {/* Subtle gradient overlay */}
                    <div
                      className={`absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-500 group-hover:opacity-100 ${colors.gradient}`}
                    />

                    {/* Content */}
                    <div className="relative z-10">
                      {/* Icon */}
                      <div
                        className={`mb-5 flex h-12 w-12 items-center justify-center rounded-xl ${colors.iconBg} border ${colors.iconBorder}`}
                      >
                        <agent.icon className={`h-5 w-5 ${colors.text}`} />
                      </div>

                      {/* Name & Role Badge */}
                      <h3 className="mb-2 text-base font-semibold text-white">{agent.name}</h3>
                      <span
                        className={`mb-4 inline-block rounded-full px-2.5 py-1 text-[10px] font-medium tracking-wide uppercase ${colors.badge}`}
                      >
                        {agent.role}
                      </span>

                      {/* Description */}
                      <p className="mb-5 text-sm leading-relaxed text-zinc-400">
                        {agent.description}
                      </p>

                      {/* Stats */}
                      <div className="flex items-center gap-2 border-t border-white/[0.06] pt-4">
                        <div className={`h-1.5 w-1.5 rounded-full ${colors.dot}`} />
                        <p className={`text-xs font-medium tabular-nums ${colors.stat}`}>
                          {agent.verseCount} verses indexed
                        </p>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>

          {/* Summary Agent Card */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ ...springPresets.gentle, delay: 0.7, duration: 1 }}
            className="mx-auto max-w-[800px]"
          >
            <div className="group relative rounded-2xl border border-white/[0.08] bg-gradient-to-b from-white/[0.04] to-transparent p-10 shadow-lg shadow-black/20 backdrop-blur-xl transition-all duration-500 hover:border-white/[0.15] hover:from-white/[0.06]">
              {/* Subtle gradient overlay */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-indigo-500/5 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />

              {/* Content */}
              <div className="relative z-10">
                {/* Icon */}
                <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-xl border border-indigo-500/20 bg-indigo-500/10">
                  <Sparkles className="h-6 w-6 text-indigo-400" />
                </div>

                {/* Name & Role Badge */}
                <h3 className="mb-3 text-xl font-semibold text-white">Synthesis Agent</h3>
                <span className="mb-5 inline-block rounded-full border border-indigo-500/20 bg-indigo-500/15 px-3 py-1.5 text-[10px] font-medium tracking-wide text-indigo-400 uppercase">
                  Comparative Theologian
                </span>

                {/* Description */}
                <p className="mb-8 max-w-2xl text-base leading-relaxed text-zinc-400">
                  Synthesizes all 4 perspectives into a unified comparative essay — identifying
                  common themes, key differences, and cross-scripture connections with full citation
                  traceability.
                </p>

                {/* Output Tags */}
                <div className="flex flex-wrap gap-2 border-t border-white/[0.06] pt-6">
                  {["5-Paragraph Essay", "Common Themes", "Key Differences", "Full Citations"].map(
                    (tag) => (
                      <span
                        key={tag}
                        className="rounded-lg border border-white/[0.08] bg-white/[0.04] px-3 py-1.5 text-[10px] font-medium tracking-wide text-zinc-400 uppercase transition-colors hover:bg-white/[0.08] hover:text-zinc-300"
                      >
                        {tag}
                      </span>
                    )
                  )}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How It Works Section - Clean Timeline */}
      <section className="relative overflow-hidden px-6 py-28 md:py-36">
        <div className="mx-auto max-w-[1200px]">
          {/* Section Header */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ ...springPresets.gentle, duration: 1 }}
            className="mb-20 text-center"
          >
            <span className="mb-6 inline-block text-xs font-medium tracking-[0.2em] text-[var(--color-accent-primary)] uppercase">
              Your Journey
            </span>
            <h2 className="mx-auto max-w-[700px] font-[family-name:var(--font-serif)] text-5xl leading-tight font-normal tracking-tight text-[var(--color-text-primary)] md:text-6xl">
              {tLanding("howItWorks.title")}
            </h2>
          </motion.div>

          {/* Steps Grid */}
          <div className="grid grid-cols-1 gap-12 md:grid-cols-4">
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
                  <span className="font-[family-name:var(--font-serif)] text-6xl text-[var(--color-accent-primary)]/20">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>

                {/* Icon */}
                <div className="mb-6 flex h-12 w-12 items-center justify-center border border-[var(--color-border-subtle)]">
                  <step.icon className="h-5 w-5 text-[var(--color-accent-primary)]" />
                </div>

                {/* Text Content */}
                <h3 className="mb-3 text-xl font-medium tracking-wide text-[var(--color-text-primary)]">
                  {step.label}
                </h3>
                <p className="mb-4 text-sm font-light text-[var(--color-text-muted)]">
                  {step.desc}
                </p>
                <p className="text-sm leading-relaxed font-light text-[var(--color-text-secondary)]">
                  {step.detail}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section - 21st.dev Pattern */}
      <section className="relative overflow-hidden bg-[var(--color-bg-app)] px-6 py-36">
        <div className="mx-auto max-w-5xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ ...springPresets.gentle, duration: 1.2 }}
          >
            <h2 className="mb-8 font-[family-name:var(--font-serif)] text-6xl leading-tight text-[var(--color-text-primary)] md:text-7xl">
              {tLanding("cta.title")}{" "}
              <span className="text-[var(--color-accent-primary)]">
                {user ? "Discovery" : "Insight"}
              </span>
            </h2>
            <p className="mx-auto mb-12 max-w-2xl text-lg leading-relaxed text-[var(--color-text-secondary)] md:text-xl">
              {tLanding("cta.description")}
            </p>
            <div className="inline-block">
              <motion.button
                onClick={() => router.push(user ? "/search" : "/sign-up")}
                className="flex items-center gap-3 rounded-xl border border-indigo-500/50 bg-indigo-600 px-12 py-5 text-lg font-medium text-white transition-colors duration-200 hover:bg-indigo-500"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                {user ? tLanding("hero.goToSearch") : tLanding("cta.signUp")}
                <ArrowRight className="h-5 w-5" />
              </motion.button>
            </div>
            <div className="mt-16 flex items-center justify-center gap-8 text-sm text-[var(--color-text-muted)]">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-[var(--color-accent-primary)]" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-[var(--color-accent-primary)]" />
                <span>43,055 verses indexed</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-[var(--color-accent-primary)]" />
                <span>5-agent AI analysis</span>
              </div>
            </div>
          </motion.div>
        </div>
        {/* Background blurs */}
        <div className="pointer-events-none absolute top-0 left-0 h-full w-full opacity-5">
          <div className="absolute top-1/4 left-1/4 h-96 w-96 rounded-full bg-[var(--color-accent-primary)] blur-3xl" />
          <div className="absolute right-1/4 bottom-1/4 h-96 w-96 rounded-full bg-[var(--color-accent-primary)] blur-3xl" />
        </div>
      </section>
    </main>
  )
}
