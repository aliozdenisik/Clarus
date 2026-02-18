"use client"

import { create } from "zustand"
import { persist } from "zustand/middleware"
import {
  getPreferencesApiPreferencesGet,
  updatePreferencesApiPreferencesPut,
} from "@/lib/api/sdk.gen"

export interface UserPreferences {
  theme: "light" | "dark" | "system"
  language: "tr" | "en" | "ar"
  default_search_source: "quran" | "bible" | "all"
  default_bible_testament: "ot" | "nt" | "apocrypha" | "all"
  results_per_page: number
  enable_streaming: boolean
  enable_multi_agent: boolean
  usage_purpose: string | null
  arabic_proficiency: string | null
  interests: string[]
  onboarding_completed: boolean
}

interface PreferencesState extends UserPreferences {
  isLoading: boolean
  error: string | null
  setTheme: (theme: "light" | "dark" | "system") => void
  setLanguage: (language: "tr" | "en" | "ar") => void
  setDefaultSearchSource: (source: "quran" | "bible" | "all") => void
  setDefaultBibleTestament: (testament: "ot" | "nt" | "apocrypha" | "all") => void
  setResultsPerPage: (count: number) => void
  setEnableStreaming: (enabled: boolean) => void
  setEnableMultiAgent: (enabled: boolean) => void
  setUsagePurpose: (purpose: string) => void
  setArabicProficiency: (level: string) => void
  setInterests: (interests: string[]) => void
  setOnboardingCompleted: (completed: boolean) => void
  fetchPreferences: () => Promise<void>
  savePreferences: () => Promise<void>
  reset: () => void
}

const DEFAULT_PREFERENCES: UserPreferences = {
  theme: "system",
  language: "en",
  default_search_source: "all",
  default_bible_testament: "all",
  results_per_page: 10,
  enable_streaming: true,
  enable_multi_agent: false,
  usage_purpose: null,
  arabic_proficiency: null,
  interests: [],
  onboarding_completed: false,
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set, get) => ({
      ...DEFAULT_PREFERENCES,
      isLoading: false,
      error: null,

      setTheme: (theme) => {
        set({ theme })
      },

      setLanguage: (language) => {
        set({ language })
      },

      setDefaultSearchSource: (source) => {
        set({ default_search_source: source })
      },

      setDefaultBibleTestament: (testament) => {
        set({ default_bible_testament: testament })
      },

      setResultsPerPage: (count) => {
        if (count < 5 || count > 50) {
          set({ error: "Results per page must be between 5 and 50" })
          return
        }
        set({ results_per_page: count, error: null })
      },

      setEnableStreaming: (enabled) => {
        set({ enable_streaming: enabled })
      },

      setEnableMultiAgent: (enabled) => {
        set({ enable_multi_agent: enabled })
      },

      setUsagePurpose: (purpose) => {
        set({ usage_purpose: purpose })
      },

      setArabicProficiency: (level) => {
        set({ arabic_proficiency: level })
      },

      setInterests: (interests) => {
        set({ interests })
      },

      setOnboardingCompleted: (completed) => {
        set({ onboarding_completed: completed })
      },

      fetchPreferences: async () => {
        set({ isLoading: true, error: null })
        try {
          const response = await getPreferencesApiPreferencesGet()

          const data = response.data as unknown as UserPreferences
          set({ ...data, isLoading: false, error: null })
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : "Unknown error"
          set({ isLoading: false, error: errorMessage })
        }
      },

      savePreferences: async () => {
        set({ isLoading: true, error: null })
        try {
          const state = get()
          const preferences: UserPreferences = {
            theme: state.theme,
            language: state.language,
            default_search_source: state.default_search_source,
            default_bible_testament: state.default_bible_testament,
            results_per_page: state.results_per_page,
            enable_streaming: state.enable_streaming,
            enable_multi_agent: state.enable_multi_agent,
            usage_purpose: state.usage_purpose,
            arabic_proficiency: state.arabic_proficiency,
            interests: state.interests,
            onboarding_completed: state.onboarding_completed,
          }

          const response = await updatePreferencesApiPreferencesPut({
            body: preferences,
          })

          const data = response.data as unknown as UserPreferences
          set({ ...data, isLoading: false, error: null })
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : "Unknown error"
          set({ isLoading: false, error: errorMessage })
        }
      },

      reset: () => {
        set({ ...DEFAULT_PREFERENCES, error: null })
      },
    }),
    {
      name: "preferences-storage",
      partialize: (state) => ({
        theme: state.theme,
        language: state.language,
        default_search_source: state.default_search_source,
        default_bible_testament: state.default_bible_testament,
        results_per_page: state.results_per_page,
        enable_streaming: state.enable_streaming,
        enable_multi_agent: state.enable_multi_agent,
        usage_purpose: state.usage_purpose,
        arabic_proficiency: state.arabic_proficiency,
        interests: state.interests,
        onboarding_completed: state.onboarding_completed,
      }),
    }
  )
)
