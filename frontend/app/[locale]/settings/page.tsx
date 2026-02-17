"use client"

import { useEffect, useState } from "react"
import { useRouter, usePathname } from "@/i18n/navigation"
import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { useSession } from "@/lib/auth-client"
import { usePreferencesStore } from "@/lib/stores/preferences-store"
import { MagicCard } from "@/components/ui/magic-card"
import { Button } from "@/components/ui/button"
import { DotPattern, RadialGradient } from "@/components/ui/dot-pattern"
import { toast } from "sonner"
import { useTranslations } from "next-intl"
import { Settings, Save, RotateCcw, Palette, Search, Zap } from "lucide-react"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"

export default function SettingsPage() {
  const { data: session, isPending: authLoading } = useSession()
  const user = session?.user
  const router = useRouter()
  const pathname = usePathname()
  const t = useTranslations("Settings")
  const tToast = useTranslations("Toast")
  const tCommon = useTranslations("Common")
  const {
    theme,
    language,
    default_search_source,
    default_bible_testament,
    results_per_page,
    enable_streaming,
    enable_multi_agent,
    isLoading: storeLoading,
    setTheme,
    setLanguage,
    setDefaultSearchSource,
    setDefaultBibleTestament,
    setResultsPerPage,
    setEnableStreaming,
    setEnableMultiAgent,
    fetchPreferences,
    savePreferences,
    reset,
  } = usePreferencesStore()

  const [isSaving, setIsSaving] = useState(false)
  const [isResetting, setIsResetting] = useState(false)

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in")
    }
  }, [user, authLoading, router])

  useEffect(() => {
    if (user) {
      fetchPreferences()
    }
  }, [user, fetchPreferences])

  const handleSave = async () => {
    try {
      setIsSaving(true)
      await savePreferences()
      toast.success(tToast("preferencesSaved"))
    } catch {
      toast.error(tToast("preferencesFailed"))
    } finally {
      setIsSaving(false)
    }
  }

  const handleReset = async () => {
    if (!confirm(t("confirmReset"))) {
      return
    }

    try {
      setIsResetting(true)
      const response = await fetch("/api/preferences", {
        method: "DELETE",
        credentials: "include",
      })

      if (!response.ok) {
        throw new Error("Failed to reset preferences")
      }

      reset()
      toast.success(t("resetSuccess"))
    } catch {
      toast.error(t("resetFailed"))
    } finally {
      setIsResetting(false)
    }
  }

  if (authLoading || (!user && !authLoading)) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-secondary)]">{tCommon("loading")}</div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen overflow-hidden bg-[var(--color-bg-app)] p-4 md:p-8">
      {/* Premium ambient effects */}
      <div className="pointer-events-none fixed inset-0">
        <DotPattern width={40} height={40} cr={0.4} className="opacity-[0.025]" />
        <RadialGradient
          className="inset-0"
          color="var(--color-accent-primary)"
          size="800px"
          position="20% 20%"
          opacity={0.04}
        />
        <RadialGradient
          className="inset-0"
          color="var(--color-accent-secondary)"
          size="600px"
          position="80% 70%"
          opacity={0.03}
        />
      </div>

      <div className="relative z-10 mx-auto max-w-2xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.snappy}
          className="mb-8"
        >
          <h1 className="flex items-center gap-3 text-3xl font-bold text-[var(--color-text-primary)]">
            <Settings className="h-8 w-8 text-[var(--color-accent-primary)]" />
            {t("title")}
          </h1>
          <p className="mt-2 text-[var(--color-text-secondary)]">{t("subtitle")}</p>
        </motion.div>

        <div className="space-y-6">
          {/* General Settings Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.fluid, delay: 0.1 }}
          >
            <MagicCard
              className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/80 p-6 backdrop-blur-xl"
              gradientSize={200}
              gradientColor="#1a1a2e"
              gradientFrom="#7c3aed"
              gradientTo="#4f46e5"
            >
              <div className="mb-6 flex items-center gap-2">
                <Palette className="h-5 w-5 text-[var(--color-accent-primary)]" />
                <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
                  {t("general")}
                </h2>
              </div>

              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-[var(--color-text-primary)]">
                    {t("theme")}
                  </label>
                  <Select
                    value={theme}
                    onValueChange={(value) => setTheme(value as "light" | "dark" | "system")}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t("selectTheme")} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">{t("themeLight")}</SelectItem>
                      <SelectItem value="dark">{t("themeDark")}</SelectItem>
                      <SelectItem value="system">{t("themeSystem")}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium text-[var(--color-text-primary)]">
                    {t("language")}
                  </label>
                  <Select
                    value={language}
                    onValueChange={async (value) => {
                      const newLocale = value as "tr" | "en" | "ar"
                      setLanguage(newLocale)
                      try {
                        await savePreferences()
                        router.replace(pathname, { locale: newLocale })
                      } catch {
                        toast.error(tToast("preferencesFailed"))
                      }
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t("selectLanguage")} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="tr">{t("languageTurkish")}</SelectItem>
                      <SelectItem value="en">{t("languageEnglish")}</SelectItem>
                      <SelectItem value="ar" disabled>
                        {t("languageArabic")} (Coming soon)
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </MagicCard>
          </motion.div>

          {/* Search Defaults Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.fluid, delay: 0.2 }}
          >
            <MagicCard
              className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/80 p-6 backdrop-blur-xl"
              gradientSize={200}
              gradientColor="#1a1a2e"
              gradientFrom="#7c3aed"
              gradientTo="#4f46e5"
            >
              <div className="mb-6 flex items-center gap-2">
                <Search className="h-5 w-5 text-[var(--color-accent-primary)]" />
                <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
                  {t("searchDefaults")}
                </h2>
              </div>

              <div className="space-y-6">
                <div className="grid gap-6 md:grid-cols-2">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-[var(--color-text-primary)]">
                      {t("defaultSource")}
                    </label>
                    <Select
                      value={default_search_source}
                      onValueChange={(value) =>
                        setDefaultSearchSource(value as "quran" | "bible" | "all")
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={t("selectSource")} />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="quran">{t("sourceQuran")}</SelectItem>
                        <SelectItem value="bible">{t("sourceBible")}</SelectItem>
                        <SelectItem value="all">{t("sourceAll")}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-[var(--color-text-primary)]">
                      {t("defaultBibleTestament")}
                    </label>
                    <Select
                      value={default_bible_testament}
                      onValueChange={(value) =>
                        setDefaultBibleTestament(value as "all" | "ot" | "nt" | "apocrypha")
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder={t("selectTestament")} />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">{t("sourceAll")}</SelectItem>
                        <SelectItem value="ot">{t("sourceOldTestament")}</SelectItem>
                        <SelectItem value="nt">{t("sourceNewTestament")}</SelectItem>
                        <SelectItem value="apocrypha">{t("sourceApocrypha")}</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="pt-2">
                  <Slider
                    label={t("resultsPerPage")}
                    showValue
                    min={5}
                    max={50}
                    step={5}
                    value={[results_per_page]}
                    onValueChange={(value) => setResultsPerPage(value[0])}
                  />
                </div>
              </div>
            </MagicCard>
          </motion.div>

          {/* Advanced Settings Card */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.fluid, delay: 0.3 }}
          >
            <MagicCard
              className="rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]/80 p-6 backdrop-blur-xl"
              gradientSize={200}
              gradientColor="#1a1a2e"
              gradientFrom="#7c3aed"
              gradientTo="#4f46e5"
            >
              <div className="mb-6 flex items-center gap-2">
                <Zap className="h-5 w-5 text-[var(--color-accent-primary)]" />
                <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
                  {t("advanced")}
                </h2>
              </div>

              <div className="space-y-6">
                <div className="rounded-lg border border-[var(--color-border)] p-4 transition-colors hover:border-[var(--color-accent-primary)]/30">
                  <Switch
                    label={t("enableStreaming")}
                    description={t("enableStreamingDesc")}
                    checked={enable_streaming}
                    onCheckedChange={setEnableStreaming}
                  />
                </div>

                <div className="rounded-lg border border-[var(--color-border)] p-4 transition-colors hover:border-[var(--color-accent-primary)]/30">
                  <Switch
                    label={t("enableMultiAgent")}
                    description={t("enableMultiAgentDesc")}
                    checked={enable_multi_agent}
                    onCheckedChange={setEnableMultiAgent}
                  />
                </div>
              </div>
            </MagicCard>
          </motion.div>

          {/* Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ ...springPresets.fluid, delay: 0.4 }}
            className="flex items-center justify-between pt-2"
          >
            <Button
              variant="outline"
              onClick={handleReset}
              disabled={isResetting || storeLoading}
              className="flex items-center gap-2 border-red-500/30 text-red-400 hover:border-red-500/50 hover:bg-red-500/10"
            >
              <RotateCcw className="h-4 w-4" />
              {t("resetToDefaults")}
            </Button>

            <Button
              onClick={handleSave}
              disabled={isSaving || storeLoading}
              className="flex items-center gap-2 bg-[var(--color-accent-primary)] shadow-[var(--color-accent-primary)]/20 shadow-lg hover:bg-[var(--color-accent-primary)]/90"
            >
              <Save className="h-4 w-4" />
              {t("savePreferences")}
            </Button>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
