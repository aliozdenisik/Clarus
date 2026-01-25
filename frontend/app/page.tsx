"use client";

import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { MagneticButton } from "@/components/ui/magnetic-button";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/auth-context";
import { useEffect } from "react";

export default function HomePage() {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && user) {
      router.push("/search");
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-[var(--color-bg-app)] p-4">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={springPresets.fluid}
        className="text-center"
      >
        <h1 className="bg-gradient-to-r from-[var(--color-text-primary)] to-[var(--color-text-secondary)] bg-clip-text text-6xl font-bold text-transparent">
          Clarus
        </h1>
        <p className="mt-4 text-lg text-[var(--color-text-secondary)]">
          Explore Quran and Bible with AI-powered insights
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ ...springPresets.gentle, delay: 0.2 }}
        className="mt-12"
      >
        <div className="relative">
          <input
            type="text"
            placeholder="Search sacred texts..."
            disabled
            onClick={() => router.push("/login")}
            className="w-96 cursor-pointer rounded-lg border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] px-6 py-4 text-[var(--color-text-primary)] placeholder-[var(--color-text-muted)] transition-all focus:border-[var(--color-border-glow)] focus:outline-none focus:ring-2 focus:ring-[var(--color-accent-glow)]"
          />
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ ...springPresets.gentle, delay: 0.4 }}
        className="mt-8 flex gap-4"
      >
        <MagneticButton onClick={() => router.push("/login")}>
          Sign In
        </MagneticButton>
        <MagneticButton
          onClick={() => router.push("/register")}
          className="bg-[var(--color-bg-elevated)] text-[var(--color-text-primary)]"
        >
          Get Started
        </MagneticButton>
      </motion.div>
    </main>
  );
}
