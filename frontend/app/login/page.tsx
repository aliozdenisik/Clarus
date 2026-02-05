"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useTheme } from "next-themes";
import { useAuth } from "@/lib/auth/auth-context";
import { toast } from "sonner";
import Link from "next/link";
import { GoogleLogin } from "@react-oauth/google";
import { ChevronLeft } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [googleError, setGoogleError] = useState<string | null>(null);
  const { login, loginWithGoogle } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await login(email, password);
      toast.success("Login successful!");
      router.push("/search");
    } catch {
      toast.error("Login failed. Please check your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: { credential?: string }) => {
    if (!credentialResponse.credential) {
      setGoogleError("Google login failed. Please try again.");
      return;
    }

    setIsLoading(true);
    setGoogleError(null);

    try {
      await loginWithGoogle(credentialResponse.credential);
      toast.success("Login successful!");
      router.push("/search");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Google login failed";
      setGoogleError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[var(--color-bg-app)] py-20 text-[var(--color-text-primary)] selection:bg-zinc-700">
      {/* Back Button */}
      <div className="absolute left-4 top-4">
        <button
          onClick={() => router.push("/")}
          className="relative z-0 flex items-center justify-center gap-2 overflow-hidden rounded-md 
          border border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)]
          px-4 py-2 font-semibold text-[var(--color-text-primary)] transition-all duration-500
          before:absolute before:inset-0 before:-z-10 before:translate-x-[150%] before:translate-y-[150%] before:scale-[2.5]
          before:rounded-[100%] before:bg-[var(--color-accent-primary)] before:transition-transform before:duration-1000 before:content-['']
          hover:scale-105 hover:text-white hover:before:translate-x-[0%] hover:before:translate-y-[0%] active:scale-95"
        >
          <ChevronLeft size={16} />
          <span>Home</span>
        </button>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1.25, ease: "easeInOut" }}
        className="relative z-10 mx-auto w-full max-w-xl p-4"
      >
        {/* Logo */}
        <div className="mb-6 flex justify-center">
          <span className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-indigo-600 bg-clip-text text-transparent">
            Clarus
          </span>
        </div>

        {/* Header */}
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-semibold">Sign in to your account</h1>
          <p className="mt-2 text-[var(--color-text-secondary)]">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="text-[var(--color-accent-primary)] hover:text-[var(--color-accent-hover)] hover:underline">
              Create one.
            </Link>
          </p>
        </div>

        {/* Google Sign-In */}
        <div className="mb-6 flex justify-center">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => {
              setGoogleError("Google login failed. Please try again.");
              setIsLoading(false);
            }}
            useOneTap={false}
            theme="filled_black"
            size="large"
            text="signin_with"
            shape="rectangular"
            width={400}
          />
        </div>

        {googleError && (
          <p className="mb-4 text-center text-sm text-red-500">{googleError}</p>
        )}

        {/* Divider */}
        <div className="my-6 flex items-center gap-3">
          <div className="h-[1px] w-full bg-[var(--color-border-subtle)]" />
          <span className="text-[var(--color-text-muted)]">OR</span>
          <div className="h-[1px] w-full bg-[var(--color-border-subtle)]" />
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label
              htmlFor="email-input"
              className="mb-1.5 block text-[var(--color-text-secondary)]"
            >
              Email
            </label>
            <input
              id="email-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your.email@provider.com"
              required
              className="w-full rounded-md border border-[var(--color-border-subtle)]
              bg-[var(--color-bg-surface)] px-3 py-2 text-[var(--color-text-primary)]
              placeholder-[var(--color-text-muted)]
              ring-1 ring-transparent transition-shadow focus:outline-0 focus:ring-[var(--color-accent-primary)] focus:border-[var(--color-border-glow)]"
            />
          </div>
          <div className="mb-6">
            <div className="mb-1.5 flex items-end justify-between">
              <label
                htmlFor="password-input"
                className="block text-[var(--color-text-secondary)]"
              >
                Password
              </label>
              <Link href="#" className="text-sm text-[var(--color-accent-primary)] hover:text-[var(--color-accent-hover)]">
                Forgot?
              </Link>
            </div>
            <input
              id="password-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••••••"
              required
              className="w-full rounded-md border border-[var(--color-border-subtle)]
              bg-[var(--color-bg-surface)] px-3 py-2 text-[var(--color-text-primary)]
              placeholder-[var(--color-text-muted)]
              ring-1 ring-transparent transition-shadow focus:outline-0 focus:ring-[var(--color-accent-primary)] focus:border-[var(--color-border-glow)]"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-md bg-gradient-to-br from-indigo-500 to-indigo-700 px-4 py-2 text-lg text-white 
            ring-2 ring-indigo-500/50 ring-offset-2 ring-offset-[var(--color-bg-app)]
            transition-all hover:scale-[1.02] hover:ring-transparent active:scale-[0.98] active:ring-indigo-500/70
            disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
          >
            {isLoading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        {/* Terms */}
        <p className="mt-9 text-xs text-[var(--color-text-muted)] text-center">
          By signing in, you agree to our{" "}
          <Link href="#" className="text-[var(--color-accent-primary)] hover:underline">
            Terms & Conditions
          </Link>{" "}
          and{" "}
          <Link href="#" className="text-[var(--color-accent-primary)] hover:underline">
            Privacy Policy.
          </Link>
        </p>
      </motion.div>

      {/* Background Decoration */}
      <BackgroundDecoration />
    </div>
  );
}

function BackgroundDecoration() {
  const { resolvedTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Wait for client-side hydration to complete
  useEffect(() => {
    setMounted(true);
  }, []);

  // Default to dark theme during SSR to avoid hydration mismatch
  const isDarkTheme = !mounted || resolvedTheme === "dark";

  return (
    <div
      className="absolute right-0 top-0 z-0 size-[50vw]"
      style={{
        backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' width='32' height='32' fill='none' stroke-width='2' stroke='rgb(99 102 241 / 0.3)'%3e%3cpath d='M0 .5H31.5V32'/%3e%3c/svg%3e")`,
      }}
    >
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: isDarkTheme
            ? "radial-gradient(100% 100% at 100% 0%, rgba(9,9,11,0), rgba(9,9,11,1))"
            : "radial-gradient(100% 100% at 100% 0%, rgba(255,255,255,0), rgba(255,255,255,1))",
        }}
      />
    </div>
  );
}
