"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { usePreferencesStore } from "@/lib/stores/preferences-store";
import { GlowCard } from "@/components/ui/glow-card";
import { Button } from "@/components/ui/button";
import { GlowingButton } from "@/components/ui/glowing-button";
import { DotPattern, RadialGradient } from "@/components/ui/dot-pattern";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Settings, Save, RotateCcw } from "lucide-react";

export default function SettingsPage() {
  const { user, isLoading: authLoading } = useAuth();
  const router = useRouter();
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
  } = usePreferencesStore();

  const [isSaving, setIsSaving] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    if (user) {
      fetchPreferences();
    }
  }, [user, fetchPreferences]);

  const handleSave = async () => {
    try {
      setIsSaving(true);
      await savePreferences();
      toast.success("Preferences saved successfully");
    } catch (error) {
      toast.error("Failed to save preferences");
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = async () => {
    if (!confirm("Are you sure you want to reset all preferences to defaults?")) {
      return;
    }

    try {
      setIsResetting(true);
      const token = localStorage.getItem("access_token");
      const response = await fetch("/api/preferences", {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to reset preferences");
      }

      reset();
      toast.success("Preferences reset to defaults");
    } catch (error) {
      toast.error("Failed to reset preferences");
    } finally {
      setIsResetting(false);
    }
  };

  if (authLoading || (!user && !authLoading)) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    );
  }

  const selectClassName = "flex h-10 w-full rounded-md border border-[var(--color-border)] bg-[var(--color-bg-surface)] px-3 py-2 text-sm ring-offset-[var(--color-bg-app)] file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-[var(--color-text-muted)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-primary)] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-[var(--color-text-primary)]";

  const labelClassName = "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-[var(--color-text-primary)] mb-2 block";

  return (
    <div className="relative min-h-screen bg-[var(--color-bg-app)] p-4 md:p-8 overflow-hidden">
      {/* Premium ambient effects */}
      <div className="fixed inset-0 pointer-events-none">
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
      
      <div className="relative mx-auto max-w-2xl z-10">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.snappy}
          className="mb-8"
        >
          <h1 className="flex items-center gap-3 text-3xl font-bold text-[var(--color-text-primary)]">
            <Settings className="h-8 w-8 text-[var(--color-accent-primary)]" />
            User Preferences
          </h1>
          <p className="mt-2 text-[var(--color-text-secondary)]">
            Customize your search experience and interface settings
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
        >
          <GlowCard className="space-y-8 p-6 backdrop-blur-xl bg-[var(--color-bg-surface)]/80">
            {/* General Settings */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--color-text-primary)] border-b border-[var(--color-border)] pb-2">
                General
              </h2>
              
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label htmlFor="theme" className={labelClassName}>
                    Theme
                  </label>
                  <select
                    id="theme"
                    value={theme}
                    onChange={(e) => setTheme(e.target.value as any)}
                    className={selectClassName}
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="system">System</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="language" className={labelClassName}>
                    Language
                  </label>
                  <select
                    id="language"
                    value={language}
                    onChange={(e) => setLanguage(e.target.value as any)}
                    className={selectClassName}
                  >
                    <option value="tr">Türkçe</option>
                    <option value="en">English</option>
                    <option value="ar">Arabic</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Search Defaults */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--color-text-primary)] border-b border-[var(--color-border)] pb-2">
                Search Defaults
              </h2>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <label htmlFor="search-source" className={labelClassName}>
                    Default Source
                  </label>
                  <select
                    id="search-source"
                    value={default_search_source}
                    onChange={(e) => setDefaultSearchSource(e.target.value as any)}
                    className={selectClassName}
                  >
                    <option value="quran">Quran</option>
                    <option value="bible">Bible</option>
                    <option value="all">All</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="bible-testament" className={labelClassName}>
                    Default Bible Testament
                  </label>
                  <select
                    id="bible-testament"
                    value={default_bible_testament}
                    onChange={(e) => setDefaultBibleTestament(e.target.value as any)}
                    className={selectClassName}
                  >
                    <option value="all">All</option>
                    <option value="ot">Old Testament</option>
                    <option value="nt">New Testament</option>
                    <option value="apocrypha">Apocrypha</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="results-per-page" className={labelClassName}>
                    Results Per Page (5-50)
                  </label>
                  <Input
                    id="results-per-page"
                    type="number"
                    min={5}
                    max={50}
                    value={results_per_page}
                    onChange={(e) => setResultsPerPage(parseInt(e.target.value))}
                  />
                </div>
              </div>
            </div>

            {/* Advanced Settings */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-[var(--color-text-primary)] border-b border-[var(--color-border)] pb-2">
                Advanced
              </h2>

              <div className="space-y-4">
                <div className="flex items-center justify-between rounded-lg border border-[var(--color-border)] p-4">
                  <div className="space-y-0.5">
                    <label htmlFor="streaming" className="text-sm font-medium text-[var(--color-text-primary)]">
                      Enable Streaming
                    </label>
                    <p className="text-xs text-[var(--color-text-secondary)]">
                      Stream search results and answers in real-time
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    id="streaming"
                    checked={enable_streaming}
                    onChange={(e) => setEnableStreaming(e.target.checked)}
                    className="h-4 w-4 rounded border-[var(--color-border)] bg-[var(--color-bg-surface)] text-[var(--color-accent-primary)] focus:ring-[var(--color-accent-primary)]"
                  />
                </div>

                <div className="flex items-center justify-between rounded-lg border border-[var(--color-border)] p-4">
                  <div className="space-y-0.5">
                    <label htmlFor="multi-agent" className="text-sm font-medium text-[var(--color-text-primary)]">
                      Enable Multi-Agent
                    </label>
                    <p className="text-xs text-[var(--color-text-secondary)]">
                      Use multiple AI agents for comprehensive answers (slower)
                    </p>
                  </div>
                  <input
                    type="checkbox"
                    id="multi-agent"
                    checked={enable_multi_agent}
                    onChange={(e) => setEnableMultiAgent(e.target.checked)}
                    className="h-4 w-4 rounded border-[var(--color-border)] bg-[var(--color-bg-surface)] text-[var(--color-accent-primary)] focus:ring-[var(--color-accent-primary)]"
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-[var(--color-border)]">
              <Button
                variant="destructive" // Using destructive style for reset
                onClick={handleReset}
                disabled={isResetting || storeLoading}
                className="flex items-center gap-2"
              >
                <RotateCcw className="h-4 w-4" />
                Reset to Defaults
              </Button>

              <Button
                onClick={handleSave}
                disabled={isSaving || storeLoading}
                className="bg-[var(--color-accent-primary)] hover:bg-[var(--color-accent-primary)]/90 flex items-center gap-2"
              >
                <Save className="h-4 w-4" />
                Save Changes
              </Button>
            </div>
          </GlowCard>
        </motion.div>
      </div>
    </div>
  );
}
