"use client"

import { create } from "zustand"
import { persist } from "zustand/middleware"

export interface OnboardingState {
  // Step management
  currentStep: number // 0-5 (welcome, purpose, language, arabic, interests, complete)
  direction: number // 1 (forward) or -1 (backward), for TransitionPanel
  totalSteps: number // 6

  // Collected answers
  usagePurpose: string | null // academic, personal, preaching, comparative, textual
  language: string // tr, en
  arabicProficiency: string // none, basic, intermediate, advanced
  interests: string[] // array of selected academic discipline IDs

  // Actions
  goNext: () => void // MUST set direction=1 BEFORE incrementing step
  goBack: () => void // MUST set direction=-1 BEFORE decrementing step
  setUsagePurpose: (purpose: string) => void
  setLanguage: (lang: string) => void
  setArabicProficiency: (level: string) => void
  toggleInterest: (interest: string) => void
  reset: () => void

  // Persistence
  isComplete: boolean
  markComplete: () => void
}

const DEFAULT_STATE: Omit<
  OnboardingState,
  | "goNext"
  | "goBack"
  | "setUsagePurpose"
  | "setLanguage"
  | "setArabicProficiency"
  | "toggleInterest"
  | "reset"
  | "markComplete"
> = {
  currentStep: 0,
  direction: 1,
  totalSteps: 6,
  usagePurpose: null,
  language: "tr",
  arabicProficiency: "none",
  interests: [],
  isComplete: false,
}

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set, get) => ({
      ...DEFAULT_STATE,

      goNext: () =>
        set((state) => ({
          direction: 1,
          currentStep: Math.min(state.currentStep + 1, state.totalSteps - 1),
        })),

      goBack: () =>
        set((state) => ({
          direction: -1,
          currentStep: Math.max(0, state.currentStep - 1),
        })),

      setUsagePurpose: (purpose: string) => {
        set({ usagePurpose: purpose })
      },

      setLanguage: (lang: string) => {
        set({ language: lang })
      },

      setArabicProficiency: (level: string) => {
        set({ arabicProficiency: level })
      },

      toggleInterest: (interest: string) => {
        const { interests } = get()
        if (interests.includes(interest)) {
          set({ interests: interests.filter((i) => i !== interest) })
        } else {
          set({ interests: [...interests, interest] })
        }
      },

      reset: () => {
        set({
          ...DEFAULT_STATE,
        })
      },

      markComplete: () => {
        set({ isComplete: true })
      },
    }),
    {
      name: "onboarding-storage",
      partialize: (state) => ({
        currentStep: state.currentStep,
        totalSteps: state.totalSteps,
        usagePurpose: state.usagePurpose,
        language: state.language,
        arabicProficiency: state.arabicProficiency,
        interests: state.interests,
        isComplete: state.isComplete,
        // EXCLUDE direction from persistence (transient state)
      }),
    }
  )
)
