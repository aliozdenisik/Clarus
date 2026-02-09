"use client";

import * as React from "react";
import * as SliderPrimitive from "@radix-ui/react-slider";

import { cn } from "@/lib/utils";

interface SliderProps extends React.ComponentPropsWithoutRef<typeof SliderPrimitive.Root> {
  label?: string;
  showValue?: boolean;
  formatValue?: (value: number) => string;
}

const Slider = React.forwardRef<
  React.ElementRef<typeof SliderPrimitive.Root>,
  SliderProps
>(({ className, label, showValue = false, formatValue, min = 0, max = 100, ...props }, ref) => {
  const [internalValue, setInternalValue] = React.useState<number[]>(
    (props.defaultValue as number[]) ?? (props.value as number[]) ?? [min]
  );

  React.useEffect(() => {
    if (props.value !== undefined) {
      setInternalValue(props.value as number[]);
    }
  }, [props.value]);

  const handleValueChange = (newValue: number[]) => {
    setInternalValue(newValue);
    props.onValueChange?.(newValue);
  };

  const displayValue = formatValue 
    ? formatValue(internalValue[0]) 
    : internalValue[0].toString();

  const sliderId = React.useId();

  const sliderElement = (
    <SliderPrimitive.Root
      ref={ref}
      id={sliderId}
      min={min}
      max={max}
      className={cn(
        "relative flex w-full touch-none select-none items-center",
        className
      )}
      onValueChange={handleValueChange}
      {...props}
    >
      <SliderPrimitive.Track className="relative h-2 w-full grow overflow-hidden rounded-full bg-[var(--color-border)]">
        <SliderPrimitive.Range className="absolute h-full bg-[var(--color-accent-primary)] transition-all" />
      </SliderPrimitive.Track>
      {internalValue.map((_, index) => (
        <SliderPrimitive.Thumb
          key={`thumb-${sliderId}-${index}`}
          className="block h-5 w-5 rounded-full border-2 border-[var(--color-accent-primary)] bg-white shadow-md transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-primary)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg-app)] disabled:pointer-events-none disabled:opacity-50 hover:scale-110 hover:shadow-lg"
        />
      ))}
    </SliderPrimitive.Root>
  );

  if (label || showValue) {
    return (
      <div className="space-y-3">
        {(label || showValue) && (
          <div className="flex items-center justify-between gap-2">
            {label && (
              <label
                htmlFor={sliderId}
                className="text-sm font-medium leading-none text-[var(--color-text-primary)]"
              >
                {label}
              </label>
            )}
            {showValue && (
              <output className="text-sm font-medium tabular-nums text-[var(--color-text-secondary)] bg-[var(--color-bg-elevated)] px-2 py-0.5 rounded">
                {displayValue}
              </output>
            )}
          </div>
        )}
        {sliderElement}
      </div>
    );
  }

  return sliderElement;
});

Slider.displayName = SliderPrimitive.Root.displayName;

export { Slider };
export type { SliderProps };
