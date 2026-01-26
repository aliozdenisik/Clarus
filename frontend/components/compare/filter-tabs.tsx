import { cn } from "@/lib/utils";

export type FilterType = 'all' | 'quran' | 'old_testament' | 'new_testament' | 'apocrypha';

interface FilterTabsProps {
  activeFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
  counts: Partial<Record<FilterType, number>>;
}

const FILTER_LABELS: Record<FilterType, string> = {
  all: 'Tumu',
  quran: 'Kuran',
  old_testament: 'Eski Ahit',
  new_testament: 'Yeni Ahit',
  apocrypha: 'Apokrifa'
};

const FILTERS: FilterType[] = ['all', 'quran', 'old_testament', 'new_testament', 'apocrypha'];

export function FilterTabs({ activeFilter, onFilterChange, counts }: FilterTabsProps) {
  return (
    <div role="tablist" className="flex flex-wrap gap-2">
      {FILTERS.map(filter => (
        <button
          key={filter}
          role="tab"
          aria-selected={activeFilter === filter}
          onClick={() => onFilterChange(filter)}
          className={cn(
            "px-3 py-1.5 rounded-md text-sm font-medium transition-colors",
            activeFilter === filter
              ? "bg-[var(--color-accent-primary)] text-white"
              : "bg-[var(--color-bg-tertiary)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-elevated)]"
          )}
        >
          {FILTER_LABELS[filter]}
          {counts[filter] !== undefined && counts[filter]! > 0 && (
            <span className="ml-1 text-xs opacity-75">
              ({counts[filter]})
            </span>
          )}
        </button>
      ))}
    </div>
  );
}
