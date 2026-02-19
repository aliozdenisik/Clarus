"use client"

import { create } from "zustand"
import { persist } from "zustand/middleware"

export interface ChecklistItem {
  id: string
  completed: boolean
}

export interface ChecklistState {
  items: ChecklistItem[]
  dismissed: boolean
  completeItem: (id: string) => void
  dismissChecklist: () => void
  resetChecklist: () => void
}

const DEFAULT_STATE: Omit<ChecklistState, "completeItem" | "dismissChecklist" | "resetChecklist"> =
  {
    items: [
      { id: "first-search", completed: false },
      { id: "try-compare", completed: false },
      { id: "keyword-search", completed: false },
      { id: "browse-quran", completed: false },
      { id: "view-history", completed: false },
    ],
    dismissed: false,
  }

export const useChecklistStore = create<ChecklistState>()(
  persist(
    (set) => ({
      ...DEFAULT_STATE,

      completeItem: (id: string) => {
        set((state) => ({
          items: state.items.map((item) => (item.id === id ? { ...item, completed: true } : item)),
        }))
      },

      dismissChecklist: () => {
        set({ dismissed: true })
      },

      resetChecklist: () => {
        set({
          ...DEFAULT_STATE,
        })
      },
    }),
    {
      name: "checklist-storage",
      partialize: (state) => ({
        items: state.items,
        dismissed: state.dismissed,
        // EXCLUDE actions from persistence
      }),
    }
  )
)

export function useChecklistProgress() {
  const items = useChecklistStore((s) => s.items)
  const completed = items.filter((i) => i.completed).length
  const total = items.length
  return { completed, total, percentage: Math.round((completed / total) * 100) }
}
