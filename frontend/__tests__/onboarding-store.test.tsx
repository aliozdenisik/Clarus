import { describe, it, expect, beforeEach } from "vitest"
import { useOnboardingStore } from "@/lib/stores/onboarding-store"

const DEFAULT_STATE = {
  currentStep: 0,
  direction: 1,
  totalSteps: 6,
  usagePurpose: null,
  language: "tr",
  arabicProficiency: "none",
  interests: [] as string[],
  isComplete: false,
}

describe("useOnboardingStore", () => {
  beforeEach(() => {
    useOnboardingStore.setState(DEFAULT_STATE)
  })

  it("initial state has currentStep=0, direction=1", () => {
    const state = useOnboardingStore.getState()
    expect(state.currentStep).toBe(0)
    expect(state.direction).toBe(1)
  })

  it("initial state has totalSteps=6, null usagePurpose, isComplete=false", () => {
    const state = useOnboardingStore.getState()
    expect(state.totalSteps).toBe(6)
    expect(state.usagePurpose).toBeNull()
    expect(state.isComplete).toBe(false)
    expect(state.interests).toHaveLength(0)
  })

  it("goNext() sets direction=1 and increments currentStep", () => {
    useOnboardingStore.getState().goNext()
    const state = useOnboardingStore.getState()
    expect(state.direction).toBe(1)
    expect(state.currentStep).toBe(1)
  })

  it("goBack() sets direction=-1 and decrements currentStep", () => {
    useOnboardingStore.setState({ currentStep: 2 })
    useOnboardingStore.getState().goBack()
    const state = useOnboardingStore.getState()
    expect(state.direction).toBe(-1)
    expect(state.currentStep).toBe(1)
  })

  it("goBack() on step 0 stays at 0", () => {
    useOnboardingStore.getState().goBack()
    expect(useOnboardingStore.getState().currentStep).toBe(0)
  })

  it("goNext() on last step (5) stays at 5", () => {
    useOnboardingStore.setState({ currentStep: 5 })
    useOnboardingStore.getState().goNext()
    expect(useOnboardingStore.getState().currentStep).toBe(5)
  })

  it("setUsagePurpose() updates usagePurpose value", () => {
    useOnboardingStore.getState().setUsagePurpose("academic")
    expect(useOnboardingStore.getState().usagePurpose).toBe("academic")
  })

  it("toggleInterest() adds a new interest", () => {
    useOnboardingStore.getState().toggleInterest("theology")
    expect(useOnboardingStore.getState().interests).toContain("theology")
  })

  it("toggleInterest() removes an existing interest", () => {
    useOnboardingStore.setState({ interests: ["theology", "history"] })
    useOnboardingStore.getState().toggleInterest("theology")
    const { interests } = useOnboardingStore.getState()
    expect(interests).not.toContain("theology")
    expect(interests).toContain("history")
  })

  it("markComplete() sets isComplete=true", () => {
    useOnboardingStore.getState().markComplete()
    expect(useOnboardingStore.getState().isComplete).toBe(true)
  })

  it("reset() restores default state", () => {
    useOnboardingStore.setState({ currentStep: 3, usagePurpose: "academic", isComplete: true })
    useOnboardingStore.getState().reset()
    const state = useOnboardingStore.getState()
    expect(state.currentStep).toBe(0)
    expect(state.usagePurpose).toBeNull()
    expect(state.isComplete).toBe(false)
  })
})
