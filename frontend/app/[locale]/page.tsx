"use client"

import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { LuxuryQuote } from "@/components/ui/luxury-quote"
import { useLocale, useTranslations } from "next-intl"

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
  ShieldCheck,
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
    badge: "text-emerald-300/80 border border-emerald-500/30",
    stat: "text-emerald-400/80",
    dot: "bg-emerald-400",
    line: "bg-emerald-600/30",
  },
  amber: {
    gradient: "bg-gradient-to-b from-amber-500/5 to-transparent",
    iconBg: "bg-amber-500/10",
    iconBorder: "border-amber-500/20",
    text: "text-amber-400",
    badge: "text-amber-300/80 border border-amber-500/30",
    stat: "text-amber-400/80",
    dot: "bg-amber-400",
    line: "bg-amber-600/30",
  },
  sky: {
    gradient: "bg-gradient-to-b from-sky-500/5 to-transparent",
    iconBg: "bg-sky-500/10",
    iconBorder: "border-sky-500/20",
    text: "text-sky-400",
    badge: "text-sky-300/80 border border-sky-500/30",
    stat: "text-sky-400/80",
    dot: "bg-sky-400",
    line: "bg-sky-600/30",
  },
  purple: {
    gradient: "bg-gradient-to-b from-purple-500/5 to-transparent",
    iconBg: "bg-purple-500/10",
    iconBorder: "border-purple-500/20",
    text: "text-purple-400",
    badge: "text-purple-300/80 border border-purple-500/30",
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
  const locale = useLocale()

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
            <h1 className="mb-6 font-[family-name:var(--font-display)] text-5xl leading-[1.2] font-semibold tracking-[-0.02em] md:text-7xl">
              <span className="text-[var(--color-text-primary)]">{tLanding("hero.title")}</span>
              <br />
              <span className="text-purple-400">{tLanding("hero.titleAI")}</span>
            </h1>

            <p className="mx-auto mb-10 max-w-[540px] text-lg leading-[1.65] font-light tracking-wide text-[#D1D5DB] md:text-xl">
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
                    <Search className="h-5 w-5" />
                    {tLanding("hero.goToSearch")}
                  </motion.button>
                  <motion.button
                    onClick={() => router.push("/compare")}
                    className="flex items-center justify-center gap-3 rounded-xl border border-white/[0.12] bg-transparent px-10 py-4 font-medium text-[#9CA3AF] transition-colors duration-200 hover:border-white/20 hover:bg-white/5 hover:text-white"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <GitCompare className="h-5 w-5" />
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
                    <ArrowRight className="h-5 w-5" />
                  </motion.button>
                  <motion.button
                    onClick={() => router.push("/sign-in")}
                    className="flex items-center justify-center gap-3 rounded-xl border border-white/[0.12] bg-transparent px-10 py-4 font-medium text-[#9CA3AF] transition-colors duration-200 hover:border-white/20 hover:bg-white/5 hover:text-white"
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
              quotes={
                locale === "tr"
                  ? [
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
                        text: "Rabbim! İlmimi artır.",
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
                    ]
                  : [
                      {
                        text: "Recite: In the Name of thy Lord who created.",
                        source: "Al-Alaq 96:1",
                      },
                      {
                        text: "The heart of the prudent getteth knowledge...",
                        source: "Proverbs 18:15",
                      },
                      {
                        text: "Are they equal — those who know and those who know not?",
                        source: "Az-Zumar 39:9",
                      },
                      {
                        text: "Charity suffereth long, and is kind...",
                        source: "1 Corinthians 13:4",
                      },
                      {
                        text: "O my Lord, increase me in knowledge.",
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
                    ]
              }
              rotationInterval={8000}
              className="py-8"
            />
          </motion.div>
        </div>
      </section>

      {/* Features Section - Bento Grid */}
      <section className="relative px-6 py-20 md:py-28">
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
              {tLanding("sections.whyClarus")}
            </span>
            <h2 className="mx-auto max-w-[700px] font-[family-name:var(--font-serif)] text-5xl leading-tight font-normal tracking-tight text-[var(--color-text-primary)] md:text-6xl">
              {tLanding("sections.builtForDepth")}
            </h2>
          </motion.div>

          {/* Bento Grid */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ ...springPresets.gentle, duration: 1 }}
          >
            <BentoGrid className="grid-cols-1 gap-6 md:grid-cols-3">
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
                <span className="text-[11px] font-medium tracking-[0.06em] text-[var(--color-text-muted)]">
                  {feature.techNote}
                </span>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Multi-Agent Section - Sophisticated Color-Coding */}
      <section className="relative overflow-hidden px-6 py-20 md:py-28">
        <div className="mx-auto max-w-[1200px]">
          {/* Section Header */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ ...springPresets.gentle, duration: 1 }}
            className="mb-20 text-center"
          >
            <span className="mb-6 inline-block bg-gradient-to-r from-purple-400 to-violet-400 bg-clip-text text-xs font-semibold tracking-[0.12em] text-transparent uppercase">
              {tLanding("sections.coreFeature")}
            </span>
            <h2 className="mx-auto mb-8 max-w-[700px] font-[family-name:var(--font-serif)] text-5xl leading-tight font-normal tracking-tight text-[var(--color-text-primary)] md:text-6xl">
              {tLanding("agents.title")}
            </h2>
            <p className="mx-auto max-w-[650px] text-lg leading-relaxed font-light text-[var(--color-text-secondary)]">
              {tLanding("agents.subtitle")}
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
                    className={`group relative h-full rounded-2xl border border-white/[0.12] bg-gradient-to-b from-white/[0.05] to-transparent p-6 shadow-lg shadow-black/20 backdrop-blur-xl transition-all duration-500 hover:border-white/[0.22] hover:from-white/[0.08]`}
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
                      <h3 className="mb-1.5 text-lg font-semibold tracking-tight text-white">
                        {agent.name}
                      </h3>
                      <span
                        className={`mb-5 inline-block rounded-md px-2 py-0.5 text-[11px] font-medium tracking-[0.08em] uppercase ${colors.badge}`}
                      >
                        {agent.role}
                      </span>

                      {/* Description */}
                      <p className="mb-5 text-sm leading-relaxed text-zinc-300">
                        {agent.description}
                      </p>

                      {/* Stats */}
                      <div className="flex items-center gap-2 border-t border-white/[0.06] pt-4">
                        <div className={`h-1.5 w-1.5 rounded-full ${colors.dot}`} />
                        <p className={`text-xs font-medium tabular-nums ${colors.stat}`}>
                          {agent.verseCount} {tLanding("agents.versesIndexed")}
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
            <div className="group relative rounded-2xl border border-white/[0.12] bg-gradient-to-b from-white/[0.05] to-transparent p-8 shadow-lg shadow-black/20 backdrop-blur-xl transition-all duration-500 hover:border-white/[0.22] hover:from-white/[0.08]">
              {/* Subtle gradient overlay */}
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-b from-purple-500/5 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />

              {/* Content */}
              <div className="relative z-10">
                {/* Icon */}
                <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-xl border border-purple-500/25 bg-purple-500/10">
                  <Sparkles className="h-6 w-6 text-purple-300" />
                </div>

                {/* Name & Role Badge */}
                <h3 className="mb-2 text-2xl font-semibold tracking-tight text-white">
                  {tLanding("agents.synthesis.name")}
                </h3>
                <span className="mb-5 inline-block rounded-md border border-purple-500/30 px-2.5 py-0.5 text-[11px] font-medium tracking-[0.08em] text-purple-300/80 uppercase">
                  {tLanding("agents.synthesis.role")}
                </span>

                {/* Description */}
                <p className="mb-8 max-w-2xl text-base leading-relaxed text-zinc-300">
                  {tLanding("agents.synthesis.description")}
                </p>

                {/* Output Tags */}
                <div className="flex flex-wrap gap-2 border-t border-white/[0.06] pt-6">
                  {[
                    tLanding("agents.synthesis.tags.essay"),
                    tLanding("agents.synthesis.tags.themes"),
                    tLanding("agents.synthesis.tags.differences"),
                    tLanding("agents.synthesis.tags.citations"),
                  ].map((tag) => (
                    <span
                      key={tag}
                      className="rounded-lg border border-white/[0.1] bg-white/[0.05] px-3 py-2 text-[11px] font-medium text-zinc-300 capitalize transition-colors hover:bg-white/[0.1] hover:text-zinc-200"
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
              {tLanding("sections.yourJourney")}
            </span>
            <h2 className="mx-auto max-w-[700px] font-[family-name:var(--font-serif)] text-5xl leading-tight font-normal tracking-tight text-[var(--color-text-primary)] md:text-6xl">
              {tLanding("howItWorks.title")}
            </h2>
          </motion.div>

          {/* Steps Grid */}
          <div
            data-testid="how-it-works-grid"
            className="mx-auto grid max-w-[1120px] grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4 xl:gap-8"
          >
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
                className="relative h-full"
              >
                <div
                  data-testid={`how-it-works-step-${index + 1}`}
                  className="group relative flex h-full flex-col rounded-2xl border border-white/[0.08] bg-gradient-to-b from-white/[0.04] to-transparent p-6 shadow-lg shadow-black/20 backdrop-blur-xl transition-all duration-500 hover:border-white/[0.15] hover:from-white/[0.06]"
                >
                  <span
                    aria-hidden="true"
                    className="pointer-events-none absolute -top-2.5 -left-2.5 inline-flex h-7 min-w-7 items-center justify-center rounded-lg border border-indigo-500/30 bg-indigo-500/15 px-2 text-[10px] font-semibold tracking-[0.12em] text-indigo-300 tabular-nums"
                  >
                    {String(index + 1).padStart(2, "0")}
                  </span>

                  {/* Icon */}
                  <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-xl border border-indigo-500/30 bg-indigo-500/10">
                    <step.icon className="h-6 w-6 text-indigo-300" />
                  </div>

                  {/* Text Content */}
                  <h3 className="mb-1 text-xl font-semibold tracking-wide text-white">
                    {step.label}
                  </h3>
                  <p className="mb-4 text-sm font-semibold tracking-wide text-indigo-300">
                    {step.desc}
                  </p>
                  <p className="max-w-[30ch] text-sm leading-relaxed text-zinc-300">
                    {step.detail}
                  </p>

                  {index === 2 ? (
                    <p className="mt-4 inline-flex w-fit items-center rounded-full border border-indigo-500/30 bg-indigo-500/10 px-2.5 py-1 text-[11px] font-medium tracking-wide text-indigo-200 tabular-nums">
                      {tLanding("cta.versesIndexed")}
                    </p>
                  ) : null}
                </div>

                {index < steps.length - 1 ? (
                  <div
                    aria-hidden="true"
                    className="pointer-events-none absolute top-7 left-[calc(100%-0.5rem)] hidden w-[calc(100%+1.5rem)] xl:block"
                  >
                    <div className="h-px bg-gradient-to-r from-indigo-500/40 to-transparent" />
                  </div>
                ) : null}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="relative overflow-hidden bg-[var(--color-bg-app)] px-6 py-24 md:py-28">
        <div className="mx-auto max-w-5xl text-center">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ ...springPresets.gentle, duration: 1.2 }}
            className="relative z-10"
          >
            <h2 className="mx-auto mb-4 max-w-4xl bg-gradient-to-r from-[var(--color-text-primary)] via-[var(--color-text-primary)] to-[var(--color-accent-secondary)] bg-clip-text font-[family-name:var(--font-sans)] text-4xl leading-tight font-semibold tracking-tight text-balance text-transparent md:text-6xl">
              {tLanding("cta.title")}
            </h2>
            <p className="mx-auto mb-8 max-w-2xl text-base leading-relaxed font-medium text-[var(--color-text-primary)] md:text-xl">
              {tLanding("cta.description")}
            </p>
            <motion.button
              onClick={() => router.push(user ? "/search" : "/sign-up")}
              className="mx-auto flex items-center gap-2.5 rounded-xl border border-[#4f46e5]/50 bg-[#4f46e5] px-10 py-4 text-lg font-semibold text-white shadow-lg shadow-[#4f46e526] transition-colors duration-200 hover:bg-[#4338ca]"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {user ? tLanding("cta.goToSearch") : tLanding("cta.signUp")}
              <ArrowRight className="h-5 w-5" />
            </motion.button>
            <ul className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-3 text-sm font-medium text-[var(--color-text-secondary)]">
              <li className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-[var(--color-accent-primary)]" />
                <span>{tLanding("cta.noCreditCard")}</span>
              </li>
              <li className="flex items-center gap-2">
                <Library className="h-4 w-4 text-[var(--color-accent-primary)]" />
                <span>{tLanding("cta.versesIndexed")}</span>
              </li>
              <li className="flex items-center gap-2">
                <Brain className="h-4 w-4 text-[var(--color-accent-primary)]" />
                <span>{tLanding("cta.agentAnalysis")}</span>
              </li>
            </ul>
          </motion.div>
        </div>
        {/* Background blurs */}
        <div className="pointer-events-none absolute top-0 left-0 h-full w-full opacity-[0.12]">
          <div className="absolute top-1/4 left-1/4 h-96 w-96 rounded-full bg-[var(--color-accent-primary)] blur-3xl" />
          <div className="absolute right-1/4 bottom-1/4 h-96 w-96 rounded-full bg-[var(--color-accent-secondary)] blur-3xl" />
        </div>
      </section>
    </main>
  )
}
