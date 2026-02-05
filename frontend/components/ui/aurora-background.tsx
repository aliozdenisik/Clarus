"use client";

import { cn } from "@/lib/utils";
import React, { ReactNode } from "react";
import { motion } from "framer-motion";

interface AuroraBackgroundProps extends React.HTMLProps<HTMLDivElement> {
  children: ReactNode;
  showRadialGradient?: boolean;
  intensity?: "subtle" | "normal" | "intense";
}

export function AuroraBackground({
  className,
  children,
  showRadialGradient = true,
  intensity = "normal",
  ...props
}: AuroraBackgroundProps) {
  const opacityMap = {
    subtle: "opacity-30",
    normal: "opacity-50",
    intense: "opacity-70",
  };

  return (
    <div
      className={cn(
        "relative flex flex-col items-center justify-center overflow-hidden",
        className
      )}
      {...props}
    >
      {/* Aurora effect layer */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          initial={{ backgroundPosition: "0% 50%" }}
          animate={{
            backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
          }}
          transition={{
            duration: 20,
            ease: "linear",
            repeat: Infinity,
          }}
          className={cn(
            "pointer-events-none absolute -inset-[10px] will-change-transform",
            opacityMap[intensity],
            "[--aurora:repeating-linear-gradient(100deg,var(--color-aurora-1)_10%,var(--color-aurora-2)_15%,var(--color-aurora-3)_20%,var(--color-aurora-4)_25%,var(--color-aurora-5)_30%)]",
            "[background-image:var(--aurora)]",
            "[background-size:300%_200%]",
            "blur-[100px]"
          )}
          style={{
            "--color-aurora-1": "rgba(59, 130, 246, 0.3)",
            "--color-aurora-2": "rgba(99, 102, 241, 0.25)",
            "--color-aurora-3": "rgba(139, 92, 246, 0.2)",
            "--color-aurora-4": "rgba(168, 85, 247, 0.25)",
            "--color-aurora-5": "rgba(79, 70, 229, 0.3)",
          } as React.CSSProperties}
        />
      </div>

      {/* Animated floating orbs */}
      <motion.div
        animate={{
          y: [0, -20, 0],
          x: [0, 10, 0],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-1/4 left-1/4 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"
      />
      <motion.div
        animate={{
          y: [0, 15, 0],
          x: [0, -15, 0],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1,
        }}
        className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-violet-500/8 rounded-full blur-3xl pointer-events-none"
      />
      <motion.div
        animate={{
          y: [0, -10, 0],
          scale: [1, 1.1, 1],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2,
        }}
        className="absolute top-1/3 right-1/3 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"
      />

      {/* Radial gradient for depth */}
      {showRadialGradient && (
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_20%,var(--color-bg-app)_80%)]" />
      )}

      {/* Content */}
      <div className="relative z-10 w-full">{children}</div>
    </div>
  );
}

// Compact version for page sections (not full screen)
export function AuroraSectionBackground({
  className,
  children,
  ...props
}: Omit<AuroraBackgroundProps, "showRadialGradient">) {
  return (
    <div
      className={cn("relative overflow-hidden", className)}
      {...props}
    >
      {/* Subtle aurora glow */}
      <motion.div
        animate={{
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute inset-0 pointer-events-none"
      >
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-gradient-to-b from-indigo-500/15 via-violet-500/10 to-transparent blur-3xl" />
      </motion.div>

      {/* Subtle side glows */}
      <div className="absolute top-0 left-0 w-1/3 h-full bg-gradient-to-r from-blue-500/5 to-transparent pointer-events-none" />
      <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-purple-500/5 to-transparent pointer-events-none" />

      {/* Edge fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[var(--color-bg-app)] to-transparent pointer-events-none" />

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </div>
  );
}
