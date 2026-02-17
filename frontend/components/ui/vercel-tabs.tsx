"use client"

import { AnimatedBackground } from "@/components/motion-primitives/animated-background"
import { cn } from "@/lib/utils"

interface TabItem {
  id: string
  label: string
}

interface TabsProps {
  tabs: TabItem[]
  activeTab: string
  onTabChange: (tabId: string) => void
  className?: string
}

export function Tabs({ tabs, activeTab, onTabChange, className }: TabsProps) {
  return (
    <div className={className}>
      <AnimatedBackground
        defaultValue={activeTab}
        onValueChange={(tabId) => {
          if (tabId) {
            onTabChange(tabId)
          }
        }}
        className="rounded-lg bg-white/[0.08]"
        transition={{ type: "spring", bounce: 0.15, duration: 0.5 }}
      >
        {tabs.map((tab) => (
          <button
            key={tab.id}
            data-id={tab.id}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.id}
            className={cn(
              "px-3 py-1.5 text-sm font-medium text-[var(--color-text-secondary)] transition-colors",
              "data-[checked=true]:text-white"
            )}
          >
            {tab.label}
          </button>
        ))}
      </AnimatedBackground>
    </div>
  )
}
