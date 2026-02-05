"use client";

import * as React from "react";
import { motion, useReducedMotion } from "framer-motion";
import { cn } from "@/lib/utils";

export type SearchSource = "quran" | "ot" | "nt" | "apocrypha";

interface SlidingTabsProps {
  activeTab: SearchSource;
  onTabChange: (tab: SearchSource) => void;
  className?: string;
}

const tabs = [
  { value: "quran" as const, label: "Quran" },
  { value: "ot" as const, label: "Old Testament" },
  { value: "nt" as const, label: "New Testament" },
  { value: "apocrypha" as const, label: "Apocrypha" },
];

export function SlidingTabs({ activeTab, onTabChange, className }: SlidingTabsProps) {
  const [hoveredTab, setHoveredTab] = React.useState<SearchSource | null>(null);
  const containerRef = React.useRef<HTMLDivElement>(null);
  const [indicatorStyle, setIndicatorStyle] = React.useState({ left: 0, width: 0 });
  const prefersReducedMotion = useReducedMotion();

  // Calculate indicator position based on active tab
  React.useEffect(() => {
    if (!containerRef.current) return;

    const activeButton = containerRef.current.querySelector(
      `[data-value="${activeTab}"]`
    ) as HTMLButtonElement;

    if (activeButton) {
      const containerRect = containerRef.current.getBoundingClientRect();
      const buttonRect = activeButton.getBoundingClientRect();
      
      setIndicatorStyle({
        left: buttonRect.left - containerRect.left,
        width: buttonRect.width,
      });
    }
  }, [activeTab]);

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent, currentTab: SearchSource) => {
    const currentIndex = tabs.findIndex((tab) => tab.value === currentTab);
    let nextIndex = currentIndex;

    if (e.key === "ArrowLeft") {
      e.preventDefault();
      nextIndex = currentIndex > 0 ? currentIndex - 1 : tabs.length - 1;
    } else if (e.key === "ArrowRight") {
      e.preventDefault();
      nextIndex = currentIndex < tabs.length - 1 ? currentIndex + 1 : 0;
    } else if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onTabChange(currentTab);
      return;
    }

    if (nextIndex !== currentIndex) {
      const nextButton = containerRef.current?.querySelector(
        `[data-value="${tabs[nextIndex].value}"]`
      ) as HTMLButtonElement;
      nextButton?.focus();
    }
  };

  return (
    <div
      ref={containerRef}
      role="tablist"
      aria-label="Search source selection"
      className={cn(
        "relative inline-flex items-center gap-1 p-1",
        "bg-zinc-900/80 backdrop-blur-sm",
        "border border-zinc-800/50",
        "rounded-xl",
        "shadow-inner shadow-black/20",
        className
      )}
      data-slot="sliding-tabs-container"
    >
      {/* Gradient Glow Indicator */}
      <motion.div
        className="absolute pointer-events-none"
        style={{
          left: indicatorStyle.left,
          width: indicatorStyle.width,
          height: "calc(100% - 6px)",
          top: "3px",
        }}
        initial={false}
        animate={{
          left: indicatorStyle.left,
          width: indicatorStyle.width,
        }}
        transition={
          prefersReducedMotion
            ? { type: "tween", duration: 0.1 }
            : { type: "spring", stiffness: 400, damping: 35 }
        }
        data-slot="sliding-indicator"
      >
        <div
          className="w-full h-full rounded-[10px]"
          style={{
            background: "linear-gradient(135deg, #6366f1 0%, #818cf8 50%, #6366f1 100%)",
            boxShadow:
              "inset 0 1px 0 rgba(255,255,255,0.1), 0 0 20px rgba(99, 102, 241, 0.4), 0 4px 12px rgba(0,0,0,0.3)",
          }}
        />
      </motion.div>

      {/* Tab Buttons */}
      {tabs.map((tab) => {
        const isActive = activeTab === tab.value;
        const isHovered = hoveredTab === tab.value;

        return (
          <button
            key={tab.value}
            data-value={tab.value}
            role="tab"
            aria-selected={isActive}
            tabIndex={isActive ? 0 : -1}
            onClick={() => onTabChange(tab.value)}
            onMouseEnter={() => setHoveredTab(tab.value)}
            onMouseLeave={() => setHoveredTab(null)}
            onKeyDown={(e) => handleKeyDown(e, tab.value)}
            className={cn(
              "relative z-10 px-5 py-2.5",
              "text-sm font-medium tracking-wide",
              "transition-all duration-200",
              "rounded-[10px]",
              "focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-900",
              isActive
                ? "text-white font-semibold"
                : "text-zinc-500 hover:text-zinc-300",
              isHovered && !isActive && "scale-[1.02]"
            )}
            style={{
              textShadow: isActive ? "0 0 8px rgba(255,255,255,0.3)" : "none",
            }}
            data-slot="tab-button"
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}
