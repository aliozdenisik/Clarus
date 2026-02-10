"use client"

import * as React from "react"
import { useState, useRef, useLayoutEffect } from "react"
import { cn } from "@/lib/utils"

interface Tab {
  id: string
  label: string
}

interface TabsProps extends React.HTMLAttributes<HTMLDivElement> {
  tabs: Tab[]
  activeTab?: string
  onTabChange?: (tabId: string) => void
}

interface IndicatorStyle {
  left: string
  width: string
}

const DEFAULT_INDICATOR_STYLE: IndicatorStyle = { left: "0px", width: "0px" }

function readIndicatorStyle(element: HTMLDivElement | null): IndicatorStyle {
  if (!element) {
    return DEFAULT_INDICATOR_STYLE
  }

  return {
    left: `${element.offsetLeft}px`,
    width: `${element.offsetWidth}px`,
  }
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
    const [hoverStyle, setHoverStyle] = useState<IndicatorStyle>(DEFAULT_INDICATOR_STYLE)
    const [activeStyle, setActiveStyle] = useState<IndicatorStyle>(DEFAULT_INDICATOR_STYLE)
    const tabRefs = useRef<(HTMLDivElement | null)[]>([])

    const controlledActiveIndex = activeTab
      ? Math.max(0, tabs.findIndex((t) => t.id === activeTab))
      : activeIndex

    useLayoutEffect(() => {
      const activeElement = tabRefs.current[controlledActiveIndex]
      const nextActiveStyle = readIndicatorStyle(activeElement)

      setActiveStyle((prevStyle) =>
        prevStyle.left === nextActiveStyle.left && prevStyle.width === nextActiveStyle.width
          ? prevStyle
          : nextActiveStyle
      )

      if (hoveredIndex === null) {
        return
      }

      const hoveredElement = tabRefs.current[hoveredIndex]
      const nextHoverStyle = readIndicatorStyle(hoveredElement)

      setHoverStyle((prevStyle) =>
        prevStyle.left === nextHoverStyle.left && prevStyle.width === nextHoverStyle.width
          ? prevStyle
          : nextHoverStyle
      )
    }, [controlledActiveIndex, hoveredIndex, tabs])

    return (
      <div 
        ref={ref} 
        className={cn("relative", className)} 
        {...props}
      >
        <div className="relative">
          {/* Hover Highlight */}
          <div
            className="absolute h-[30px] transition-all duration-300 ease-out bg-[#0e0f1114] dark:bg-[#ffffff1a] rounded-[6px] flex items-center"
            style={{
              ...hoverStyle,
              opacity: hoveredIndex !== null ? 1 : 0,
            }}
          />

          {/* Active Indicator */}
          <div
            className="absolute bottom-[-6px] h-[2px] bg-[#0e0f11] dark:bg-white transition-all duration-300 ease-out"
            style={activeStyle}
          />

          {/* Tabs */}
          <div className="relative flex space-x-[6px] items-center">
            {tabs.map((tab, index) => (
              <div
                key={tab.id}
                ref={(el) => { tabRefs.current[index] = el }}
                className={cn(
                  "px-3 py-2 cursor-pointer transition-colors duration-300 h-[30px]",
                  index === controlledActiveIndex 
                    ? "text-[#0e0e10] dark:text-white" 
                    : "text-[#0e0f1199] dark:text-[#ffffff99]"
                )}
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
                onClick={() => {
                  setActiveIndex(index)
                  onTabChange?.(tab.id)
                }}
              >
                <div className="text-sm font-medium leading-5 whitespace-nowrap flex items-center justify-center h-full">
                  {tab.label}
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
