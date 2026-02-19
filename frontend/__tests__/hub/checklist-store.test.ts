import { describe, it, expect, beforeEach } from "vitest"
import { renderHook } from "@testing-library/react"
import { useChecklistStore, useChecklistProgress } from "@/lib/stores/checklist-store"

const DEFAULT_ITEMS = [
  { id: "first-search", completed: false },
  { id: "try-compare", completed: false },
  { id: "keyword-search", completed: false },
  { id: "browse-quran", completed: false },
  { id: "view-history", completed: false },
]

describe("useChecklistStore", () => {
  beforeEach(() => {
    useChecklistStore.setState({
      items: DEFAULT_ITEMS.map((i) => ({ ...i })),
      dismissed: false,
    })
  })

  it("initializes with 5 uncompleted items", () => {
    const state = useChecklistStore.getState()
    expect(state.items).toHaveLength(5)
    expect(state.items.every((item) => !item.completed)).toBe(true)
    expect(state.dismissed).toBe(false)
  })

  it("completeItem(id) marks the item as completed", () => {
    useChecklistStore.getState().completeItem("first-search")
    const state = useChecklistStore.getState()
    const target = state.items.find((i) => i.id === "first-search")
    expect(target?.completed).toBe(true)
    const others = state.items.filter((i) => i.id !== "first-search")
    expect(others.every((i) => !i.completed)).toBe(true)
  })

  it("dismissChecklist() sets dismissed to true", () => {
    useChecklistStore.getState().dismissChecklist()
    expect(useChecklistStore.getState().dismissed).toBe(true)
  })

  it("resetChecklist() resets all items and dismissed flag", () => {
    useChecklistStore.setState({
      items: DEFAULT_ITEMS.map((i) => ({ ...i, completed: true })),
      dismissed: true,
    })
    useChecklistStore.getState().resetChecklist()
    const state = useChecklistStore.getState()
    expect(state.dismissed).toBe(false)
    expect(state.items.every((item) => !item.completed)).toBe(true)
    expect(state.items).toHaveLength(5)
  })

  it("useChecklistProgress() returns correct completed/total/percentage", () => {
    useChecklistStore.setState({
      items: [
        { id: "first-search", completed: true },
        { id: "try-compare", completed: true },
        { id: "keyword-search", completed: false },
        { id: "browse-quran", completed: false },
        { id: "view-history", completed: false },
      ],
      dismissed: false,
    })

    const { result } = renderHook(() => useChecklistProgress())
    expect(result.current.completed).toBe(2)
    expect(result.current.total).toBe(5)
    expect(result.current.percentage).toBe(40)
  })
})
