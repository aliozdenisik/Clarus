"use client";

import { Tabs, Tab } from "@/components/ui/vercel-tabs";
import { cn } from "@/lib/utils";
import { AnimatePresence, motion, Transition } from "framer-motion";
import {
  Children,
  cloneElement,
  ReactElement,
  useEffect,
  useState,
  useId,
  useCallback,
  isValidElement,
} from "react";

interface ChildProps {
  "data-id": string;
  className?: string;
  children?: React.ReactNode;
  key?: React.Key;
  "aria-selected"?: boolean;
  "data-checked"?: string;
  onClick?: () => void;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
}

type AnimatedBackgroundProps = {
  children:
    | ReactElement<ChildProps>[]
    | ReactElement<ChildProps>;
  defaultValue?: string;
  onValueChange?: (newActiveId: string | null) => void;
  className?: string;
  transition?: Transition;
  enableHover?: boolean;
};

export function AnimatedBackground({
  children,
  defaultValue,
  onValueChange,
  className,
  transition = { type: "spring", bounce: 0.15, duration: 0.5 },
  enableHover = false,
}: AnimatedBackgroundProps) {
  const [activeId, setActiveId] = useState<string | null>(null);
  const uniqueId = useId();

  const handleSetActiveId = useCallback(
    (id: string | null) => {
      setActiveId(id);
      if (onValueChange) {
        onValueChange(id);
      }
    },
    [onValueChange]
  );

  useEffect(() => {
    if (defaultValue !== undefined) {
      setActiveId(defaultValue);
    }
  }, [defaultValue]);

  return Children.map(children, (child, index) => {
    if (!isValidElement<ChildProps>(child)) return child;
    
    const id = child.props["data-id"];
    const childClassName = child.props.className;
    const childContent = child.props.children;

    const interactionProps = enableHover
      ? {
          onMouseEnter: () => handleSetActiveId(id),
          onMouseLeave: () => handleSetActiveId(null),
        }
      : {
          onClick: () => handleSetActiveId(id),
        };

    const newProps: ChildProps = {
      "data-id": id,
      key: index,
      className: cn("relative inline-flex", childClassName),
      "aria-selected": activeId === id,
      "data-checked": activeId === id ? "true" : "false",
      ...interactionProps,
    };
    
    return cloneElement(
      child,
      newProps,
      <>
        <AnimatePresence initial={false}>
          {activeId === id && (
            <motion.div
              layoutId={`background-${uniqueId}`}
              className={cn("absolute inset-0", className)}
              transition={transition}
              initial={{ opacity: defaultValue ? 1 : 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />
          )}
        </AnimatePresence>
        <span className="z-10">{childContent}</span>
      </>
    );
  });
}

// Premium Filter Tabs with Vercel-style underline
export type FilterType = "all" | "quran" | "old_testament" | "new_testament" | "apocrypha";

interface AnimatedFilterTabsProps {
  activeFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
  counts?: Partial<Record<FilterType, number>>;
}

const FILTER_LABELS: Record<FilterType, string> = {
  all: "All Sources",
  quran: "Quran",
  old_testament: "Old Testament",
  new_testament: "New Testament",
  apocrypha: "Apocrypha",
};

const FILTERS: FilterType[] = ["all", "quran", "old_testament", "new_testament", "apocrypha"];

export function AnimatedFilterTabs({
  activeFilter,
  onFilterChange,
  counts,
}: AnimatedFilterTabsProps) {
  // Only show tabs for sources that have results (count > 0), plus "all"
  const tabs: Tab[] = FILTERS
    .filter((filter) => filter === "all" || (counts && (counts[filter] ?? 0) > 0))
    .map((filter) => ({
      id: filter,
      label: FILTER_LABELS[filter],
    }));

  // If active filter was removed (no results for that source), reset to "all"
  const effectiveFilter = tabs.some((t) => t.id === activeFilter) ? activeFilter : "all";

  return (
    <Tabs
      tabs={tabs}
      activeTab={effectiveFilter}
      onTabChange={(tabId) => onFilterChange(tabId as FilterType)}
    />
  );
}

// Segmented Control variant using Vercel tabs
interface SegmentedControlProps<T extends string> {
  value: T;
  onChange: (value: T) => void;
  options: { value: T; label: string }[];
  className?: string;
}

export function SegmentedControl<T extends string>({
  value,
  onChange,
  options,
  className,
}: SegmentedControlProps<T>) {
  const tabs: Tab[] = options.map((opt) => ({
    id: opt.value,
    label: opt.label,
  }));

  return (
    <Tabs
      tabs={tabs}
      activeTab={value}
      onTabChange={(tabId) => onChange(tabId as T)}
      className={className}
    />
  );
}
