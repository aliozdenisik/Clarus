"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { useTheme } from "next-themes";
import { signIn, useSession } from "@/lib/auth-client";
import { toast } from "sonner";
import Link from "next/link";

import { ChevronLeft, Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [googleError, setGoogleError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const result = await signIn.email({
        email,
        password,
      });
      
      if (result.error) {
        throw new Error(result.error.message || "Login failed");
      }
      
      toast.success("Login successful!");
      router.push("/search");
    } catch (error) {
      const message = error instanceof Error ? error.message : "Login failed. Please check your credentials.";
      toast.error(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setGoogleError(null);

    try {
      const result = await signIn.social({
        provider: "google",
        callbackURL: "/search",
      });
      
      if (result.error) {
        throw new Error(result.error.message || "Google login failed");
      }
      
      toast.success("Login successful!");
      // Note: Better Auth handles redirect automatically with callbackURL
    } catch (error) {
      const message = error instanceof Error ? error.message : "Google login failed";
      setGoogleError(message);
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
          <button
            type="button"
            onClick={handleGoogleLogin}
            disabled={isLoading}
            className="w-full max-w-md flex items-center justify-center gap-3 px-6 py-3 rounded-md bg-white text-gray-900 font-medium hover:bg-gray-100 transition-colors duration-200 border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Sign in with Google
          </button>
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
            <div className="relative">
              <input
                id="password-input"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                required
                className="w-full rounded-md border border-[var(--color-border-subtle)]
                bg-[var(--color-bg-surface)] px-3 py-2 pr-10 text-[var(--color-text-primary)]
                placeholder-[var(--color-text-muted)]
                ring-1 ring-transparent transition-shadow focus:outline-0 focus:ring-[var(--color-accent-primary)] focus:border-[var(--color-border-glow)]"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)] transition-colors"
                tabIndex={-1}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
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
