"use client"

import * as React from "react"
import { useState, useRef, useEffect } from "react"
import { cn } from "@/lib/utils"

interface Tab {
  id: string
  label: string
  count?: number
}

interface TabsProps extends React.HTMLAttributes<HTMLDivElement> {
  tabs: Tab[]
  activeTab?: string
  onTabChange?: (tabId: string) => void
}

const Tabs = React.forwardRef<HTMLDivElement, TabsProps>(
  ({ className, tabs, activeTab, onTabChange, ...props }, ref) => {
    const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)
    const [activeIndex, setActiveIndex] = useState(() => {
      if (activeTab) {
        const idx = tabs.findIndex(t => t.id === activeTab)
        return idx >= 0 ? idx : 0
      }
      return 0
    })
    const [hoverStyle, setHoverStyle] = useState({})
    const [activeStyle, setActiveStyle] = useState({ left: "0px", width: "0px" })
    const tabRefs = useRef<(HTMLDivElement | null)[]>([])

    // Sync activeIndex with activeTab prop
    useEffect(() => {
      if (activeTab) {
        const idx = tabs.findIndex(t => t.id === activeTab)
        if (idx >= 0 && idx !== activeIndex) {
          setActiveIndex(idx)
        }
      }
    }, [activeTab, tabs, activeIndex])

    useEffect(() => {
      if (hoveredIndex !== null) {
        const hoveredElement = tabRefs.current[hoveredIndex]
        if (hoveredElement) {
          const { offsetLeft, offsetWidth } = hoveredElement
          setHoverStyle({
            left: `${offsetLeft}px`,
            width: `${offsetWidth}px`,
          })
        }
      }
    }, [hoveredIndex])

    useEffect(() => {
      const activeElement = tabRefs.current[activeIndex]
      if (activeElement) {
        const { offsetLeft, offsetWidth } = activeElement
        setActiveStyle({
          left: `${offsetLeft}px`,
          width: `${offsetWidth}px`,
        })
      }
    }, [activeIndex])

    useEffect(() => {
      requestAnimationFrame(() => {
        const activeElement = tabRefs.current[activeIndex]
        if (activeElement) {
          const { offsetLeft, offsetWidth } = activeElement
          setActiveStyle({
            left: `${offsetLeft}px`,
            width: `${offsetWidth}px`,
          })
        }
      })
    }, [activeIndex, tabs])

    return (
      <div 
        ref={ref} 
        className={cn("relative", className)} 
        {...props}
      >
        <div className="relative">
          {/* Hover Highlight */}
          <div
            className="absolute h-[32px] transition-all duration-200 ease-out bg-[var(--color-bg-elevated)] rounded-md flex items-center"
            style={{
              ...hoverStyle,
              opacity: hoveredIndex !== null ? 1 : 0,
            }}
          />

          {/* Active Indicator */}
          <div
            className="absolute bottom-[-8px] h-[1px] bg-[var(--color-accent-primary)] transition-all duration-200 ease-out"
            style={activeStyle}
          />

          {/* Tabs */}
          <div className="relative flex space-x-1 items-center" role="tablist">
            {tabs.map((tab, index) => (
              <div
                key={tab.id}
                ref={(el) => { tabRefs.current[index] = el }}
                role="tab"
                aria-selected={index === activeIndex}
                tabIndex={index === activeIndex ? 0 : -1}
                className={cn(
                  "px-3 py-2 cursor-pointer transition-colors duration-200 h-[32px] rounded-md",
                  index === activeIndex 
                    ? "text-[var(--color-text-primary)]" 
                    : "text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
                )}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                onClick={() => {
                  setActiveIndex(index)
                  onTabChange?.(tab.id)
                }}
              >
                <div className="text-sm font-medium leading-5 whitespace-nowrap flex items-center justify-center h-full gap-2">
                  {tab.label}
                  {tab.count !== undefined && tab.count > 0 && (
                    <span
                      className={cn(
                        "text-xs px-1.5 py-0.5 rounded-full transition-colors",
                        index === activeIndex
                          ? "bg-[var(--color-accent-primary)]/20 text-[var(--color-accent-primary)]"
                          : "bg-[var(--color-bg-elevated)] text-[var(--color-text-muted)]"
                      )}
                    >
                      {tab.count}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }
)
Tabs.displayName = "Tabs"

export { Tabs }
export type { Tab, TabsProps }
