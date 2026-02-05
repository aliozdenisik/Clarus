import { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

interface BentoGridProps {
  children: ReactNode;
  className?: string;
}

export const BentoGrid = ({ children, className }: BentoGridProps) => {
  return (
    <div className={cn("grid w-full grid-cols-1 md:grid-cols-3 gap-4", className)}>
      {children}
    </div>
  );
};

interface BentoCardProps {
  name: string;
  className: string;
  background: ReactNode;
  Icon: any;
  description: string;
  href: string;
  cta: string;
}

export const BentoCard = ({
  name,
  className,
  background,
  Icon,
  description,
  href,
  cta,
}: BentoCardProps) => (
  <div
    key={name}
    className={cn(
      "group relative col-span-1 flex flex-col overflow-hidden rounded-none",
      "bg-[var(--color-bg-surface)]/40 backdrop-blur-sm border border-[var(--color-border-subtle)]",
      "transform-gpu hover:border-[var(--color-border-glow)] transition-all duration-500",
      className,
    )}
  >
    {background}
    <div className="z-10 flex flex-col items-center text-center p-8 transition-all duration-300">
      <Icon className="h-10 w-10 mb-6 text-[var(--color-accent-primary)] transition-all duration-300 ease-in-out group-hover:scale-110" />
      <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-3">{name}</h3>
      <p className="text-sm text-[var(--color-text-secondary)] leading-relaxed">{description}</p>
    </div>
    <div className={cn(
      "absolute bottom-0 left-0 right-0 flex justify-center p-4 opacity-0 translate-y-4 transition-all duration-300 group-hover:translate-y-0 group-hover:opacity-100",
    )}>
      <Button variant="ghost" asChild size="sm" className="pointer-events-auto">
        <a href={href}>
          {cta}
          <ArrowRight className="ml-2 h-4 w-4" />
        </a>
      </Button>
    </div>
    <div className="pointer-events-none absolute inset-0 transform-gpu transition-all duration-300 group-hover:bg-[var(--color-accent-primary)]/[.03]" />
  </div>
);
