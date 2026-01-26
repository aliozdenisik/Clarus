"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { GlowCard } from "@/components/ui/glow-card";
import { toast } from "sonner";
import Link from "next/link";
import { GoogleLogin } from '@react-oauth/google';

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
    } catch (error) {
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
    <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)] p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={springPresets.fluid}
        className="w-full max-w-md"
      >
        <GlowCard>
          <div className="mb-6 text-center">
            <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
              Welcome Back
            </h1>
            <p className="mt-2 text-sm text-[var(--color-text-secondary)]">
              Sign in to continue your search
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="email"
                className="mb-2 block text-sm font-medium text-[var(--color-text-primary)]"
              >
                Email
              </label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="w-full"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="mb-2 block text-sm font-medium text-[var(--color-text-primary)]"
              >
                Password
              </label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full"
              />
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-[var(--color-accent-primary)] hover:bg-[var(--color-accent-primary)]/90"
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </Button>
          </form>

          {/* OR Divider */}
          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-[var(--color-border-primary)]" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="bg-[var(--color-bg-secondary)] px-4 text-[var(--color-text-secondary)]">
                OR
              </span>
            </div>
          </div>

          {/* Google Sign-In Button */}
          <div className="flex justify-center">
            <GoogleLogin
              onSuccess={handleGoogleSuccess}
              onError={() => {
                setIsLoading(false);
              }}
              useOneTap={false}
              theme="filled_black"
              size="large"
              text="signin_with"
              shape="rectangular"
            />
          </div>

          {/* Google Error Message */}
          {googleError && (
            <p className="mt-2 text-center text-sm text-red-500">
              {googleError}
            </p>
          )}

          <div className="mt-6 text-center text-sm text-[var(--color-text-secondary)]">
            Don't have an account?{" "}
            <Link
              href="/register"
              className="font-medium text-[var(--color-accent-primary)] hover:underline"
            >
              Sign up
            </Link>
          </div>
        </GlowCard>
      </motion.div>
    </div>
  );
}
