"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { forwardRef } from "react";

function hexToRgba(hex: string, alpha: number = 1): string {
  let hexValue = hex.replace("#", "");

  if (hexValue.length === 3) {
    hexValue = hexValue
      .split("")
      .map((char) => char + char)
      .join("");
  }

  const r = parseInt(hexValue.substring(0, 2), 16);
  const g = parseInt(hexValue.substring(2, 4), 16);
  const b = parseInt(hexValue.substring(4, 6), 16);

  if (isNaN(r) || isNaN(g) || isNaN(b)) {
    console.error("Invalid hex color:", hex);
    return "rgba(0, 0, 0, 1)";
  }

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

interface GlowingButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  glowColor?: string;
  variant?: "default" | "subtle" | "intense";
  size?: "sm" | "md" | "lg";
}

export const GlowingButton = forwardRef<HTMLButtonElement, GlowingButtonProps>(
  (
    {
      children,
      className,
      glowColor = "#8b5cf6",
      variant = "default",
      size = "md",
      ...props
    },
    ref
  ) => {
    const glowColorRgba = hexToRgba(glowColor);
    const glowColorVia = hexToRgba(glowColor, 0.075);
    const glowColorTo = hexToRgba(glowColor, 0.2);

    const sizeClasses = {
      sm: "h-9 px-4 text-sm",
      md: "h-11 px-6 text-sm",
      lg: "h-12 px-8 text-base",
    };

    const variantClasses = {
      default: "from-[var(--color-bg-secondary)] to-[var(--color-bg-tertiary)]",
      subtle: "from-transparent to-transparent hover:from-[var(--color-bg-secondary)] hover:to-[var(--color-bg-tertiary)]",
      intense: "from-[var(--color-bg-tertiary)] to-[var(--color-bg-elevated)]",
    };

    return (
      <button
        ref={ref}
        style={
          {
            "--glow-color": glowColorRgba,
            "--glow-color-via": glowColorVia,
            "--glow-color-to": glowColorTo,
          } as React.CSSProperties
        }
        className={cn(
          "relative rounded-xl border flex items-center justify-center font-medium",
          "transition-all duration-300 overflow-hidden",
          "bg-gradient-to-t border-white/10",
          "text-[var(--color-text-primary)] hover:text-white",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--glow-color)] focus-visible:ring-offset-2 focus-visible:ring-offset-[var(--color-bg-primary)]",
          // Glow effects
          "after:inset-0 after:absolute after:rounded-[inherit]",
          "after:bg-gradient-to-r after:from-transparent after:from-40%",
          "after:via-[var(--glow-color-via)] after:to-[var(--glow-color-to)] after:via-70%",
          "after:shadow-[hsl(var(--foreground)/0.15)_0px_1px_0px_inset] after:z-0",
          // Right edge glow
          "before:absolute before:w-[4px] hover:before:translate-x-full",
          "before:transition-all before:duration-500 before:ease-out",
          "before:h-[60%] before:bg-[var(--glow-color)]",
          "before:right-0 before:rounded-l before:shadow-[-2px_0_12px_var(--glow-color)] before:z-10",
          "before:opacity-0 hover:before:opacity-100",
          sizeClasses[size],
          variantClasses[variant],
          className
        )}
        {...props}
      >
        <span className="relative z-20">{children}</span>
      </button>
    );
  }
);

GlowingButton.displayName = "GlowingButton";

// Shiny Button - Premium luxury feel
interface ShinyButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?: React.ReactNode;
}

export const ShinyButton = forwardRef<HTMLButtonElement, ShinyButtonProps>(
  ({ children = "Click", className, ...props }, ref) => {
    return (
      <div className="relative group">
        {/* Outer glow */}
        <div
          className="absolute -inset-1 rounded-2xl opacity-0 group-hover:opacity-50 transition-opacity duration-500 blur-xl"
          style={{
            background: "linear-gradient(90deg, #f97316 0%, #8b5cf6 50%, #06b6d4 100%)",
          }}
        />

        <button
          ref={ref}
          className={cn(
            "relative flex items-center justify-center",
            "px-8 py-3 rounded-xl",
            "bg-[var(--color-bg-tertiary)]",
            "border border-white/10",
            "text-[var(--color-text-primary)] font-medium",
            "overflow-hidden",
            "transition-all duration-300",
            "hover:border-white/20",
            "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/20",
            className
          )}
          {...props}
        >
          {/* Animated gradient border */}
          <div className="absolute inset-0 overflow-hidden rounded-xl">
            <div
              className="absolute -inset-[150%] opacity-0 group-hover:opacity-100 transition-opacity duration-500"
              style={{
                background: "conic-gradient(from 90deg at 50% 50%, transparent 0deg, rgba(139, 92, 246, 0.3) 120deg, transparent 240deg)",
                animation: "spin 4s linear infinite",
              }}
            />
          </div>

          {/* Inner background */}
          <div className="absolute inset-[1px] rounded-[11px] bg-[var(--color-bg-tertiary)]" />

          <span className="relative z-10">{children}</span>
        </button>
      </div>
    );
  }
);

ShinyButton.displayName = "ShinyButton";

// Cosmic Glow Button - Ultra premium
interface CosmicGlowButtonProps {
  color?: string;
  speed?: string;
  children?: React.ReactNode;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: "button" | "submit" | "reset";
}

export const CosmicGlowButton = forwardRef<HTMLButtonElement, CosmicGlowButtonProps>(
  ({ className, color = "hsl(262, 83%, 58%)", speed = "5s", children, onClick, disabled, type = "button" }, ref) => {
    return (
      <motion.button
        ref={ref}
        type={type}
        onClick={onClick}
        disabled={disabled}
        className={cn(
          "relative inline-flex items-center justify-center",
          "py-4 px-8 rounded-2xl font-semibold",
          "bg-gradient-to-r from-[var(--color-bg-tertiary)] via-[var(--color-bg-secondary)] to-[var(--color-bg-tertiary)]",
          "text-white shadow-2xl shadow-black/40",
          "overflow-hidden",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/20",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          className
        )}
        whileHover={disabled ? {} : { scale: 1.02 }}
        whileTap={disabled ? {} : { scale: 0.98 }}
      >
        {/* Pulsing glow */}
        <span
          className="absolute inset-0 rounded-2xl blur-xl opacity-40"
          style={{
            background: `radial-gradient(circle at center, ${color} 10%, transparent 60%)`,
            animation: `pulse ${speed} ease-in-out infinite`,
          }}
        />

        {/* Rotating conic gradient */}
        <span
          className="absolute inset-0 rounded-2xl opacity-20"
          style={{
            background: `conic-gradient(from 90deg at 50% 50%, transparent 0deg, ${color} 120deg, transparent 240deg)`,
            animation: `spin ${speed} linear infinite`,
          }}
        />

        <span className="relative z-10">{children}</span>
      </motion.button>
    );
  }
);

CosmicGlowButton.displayName = "CosmicGlowButton";

// Magnetic Button - Interactive luxury feel
interface MagneticButtonProps {
  children: React.ReactNode;
  magneticStrength?: number;
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
  type?: "button" | "submit" | "reset";
}

export function MagneticButton({
  children,
  className,
  magneticStrength = 0.3,
  onClick,
  disabled,
  type = "button",
}: MagneticButtonProps) {
  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "relative px-6 py-3 rounded-xl",
        "bg-[var(--color-bg-tertiary)] border border-white/10",
        "text-[var(--color-text-primary)] font-medium",
        "transition-colors duration-300",
        "hover:bg-[var(--color-bg-elevated)] hover:border-white/20",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/20",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        className
      )}
      whileHover={disabled ? {} : { scale: 1.05 }}
      whileTap={disabled ? {} : { scale: 0.95 }}
    >
      {children}
    </motion.button>
  );
}
