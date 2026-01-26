import { cn } from "@/lib/utils";

export type SourceType = 'quran' | 'old_testament' | 'new_testament' | 'apocrypha';

interface SourceBadgeProps {
  source: SourceType;
}

const LABELS: Record<SourceType, string> = {
  quran: 'Kuran',
  old_testament: 'Eski Ahit',
  new_testament: 'Yeni Ahit',
  apocrypha: 'Apokrifa'
};

const COLORS: Record<SourceType, string> = {
  quran: 'bg-emerald-500 text-white',        // #10b981
  old_testament: 'bg-blue-500 text-white',   // #3b82f6
  new_testament: 'bg-amber-500 text-white',  // #f59e0b
  apocrypha: 'bg-purple-500 text-white'      // #a855f7
};

export function SourceBadge({ source }: SourceBadgeProps) {
  const label = LABELS[source] || 'Unknown';
  const colorClass = COLORS[source] || 'bg-gray-500 text-white';
  
  return (
    <span 
      role="status" 
      className={cn("px-2 py-1 rounded text-xs font-medium", colorClass)}
    >
      {label}
    </span>
  );
}
