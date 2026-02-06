import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Authentication - Clarus",
  description: "Sign in or create an account to access Clarus",
};

/**
 * Auth Layout
 * 
 * Minimal centered layout for authentication pages.
 * Removes navigation and footer for focused auth experience.
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="relative min-h-screen bg-[var(--color-bg-app)] flex items-center justify-center p-4">
      {/* Background decoration */}
      <div
        className="absolute right-0 top-0 z-0 size-[50vw]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' width='32' height='32' fill='none' stroke-width='2' stroke='rgb(99 102 241 / 0.3)'%3e%3cpath d='M0 .5H31.5V32'/%3e%3c/svg%3e")`,
        }}
      >
        <div
          className="absolute inset-0"
          style={{
            backgroundImage:
              "radial-gradient(100% 100% at 100% 0%, rgba(9,9,11,0), rgba(9,9,11,1))",
          }}
        />
      </div>

      {/* Content */}
      <div className="relative z-10 w-full max-w-md">
        {children}
      </div>
    </div>
  );
}
