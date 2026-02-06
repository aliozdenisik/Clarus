"use client";

import * as React from "react";
import * as SwitchPrimitive from "@radix-ui/react-switch";
import { motion } from "framer-motion";

import { cn } from "@/lib/utils";

interface SwitchProps extends React.ComponentPropsWithoutRef<typeof SwitchPrimitive.Root> {
  label?: string;
  description?: string;
}

const Switch = React.forwardRef<
  React.ElementRef<typeof SwitchPrimitive.Root>,
  SwitchProps
>(({ className, label, description, id, ...props }, ref) => {
  const [isChecked, setIsChecked] = React.useState(
    props?.checked ?? props?.defaultChecked ?? false
  );
  const switchId = id || React.useId();

  React.useEffect(() => {
    if (props?.checked !== undefined) {
      setIsChecked(props.checked);
    }
  }, [props?.checked]);

  const switchElement = (
    <SwitchPrimitive.Root
      ref={ref}
      id={switchId}
      checked={isChecked}
      onCheckedChange={(checked) => {
        setIsChecked(checked);
        props.onCheckedChange?.(checked);
      }}
      className={cn(
        "peer relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent-primary)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg-app)] disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-[var(--color-accent-primary)] data-[state=unchecked]:bg-[var(--color-border)]",
        className
      )}
      {...props}
    >
      <SwitchPrimitive.Thumb asChild>
        <motion.div
          className="pointer-events-none block h-5 w-5 rounded-full bg-white shadow-lg ring-0"
          layout
          transition={{
            type: "spring",
            stiffness: 500,
            damping: 30,
          }}
          style={{
            marginLeft: isChecked ? "auto" : "0",
            marginRight: isChecked ? "0" : "auto",
          }}
        />
      </SwitchPrimitive.Thumb>
    </SwitchPrimitive.Root>
  );

  if (label || description) {
    return (
      <div className="flex items-center justify-between gap-4">
        <div className="space-y-0.5">
          {label && (
            <label
              htmlFor={switchId}
              className="text-sm font-medium leading-none text-[var(--color-text-primary)] cursor-pointer"
            >
              {label}
            </label>
          )}
          {description && (
            <p className="text-xs text-[var(--color-text-secondary)]">
              {description}
            </p>
          )}
        </div>
        {switchElement}
      </div>
    );
  }

  return switchElement;
});

Switch.displayName = SwitchPrimitive.Root.displayName;

export { Switch };
export type { SwitchProps };
