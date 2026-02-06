import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Authentication - Clarus",
  description: "Sign in or create an account to access Clarus",
};

/**
 * Auth Layout
 * 
 * Split-screen layout with form on left and animated gradient hero on right.
 * Mobile: Full-width form, hero hidden.
 * Desktop: 50/50 split with animated gradient blobs.
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col lg:flex-row w-full bg-[var(--color-bg-app)]">
      {/* LEFT SIDE — Auth Form */}
      <div className="flex-1 flex items-center justify-center p-6 sm:p-8 lg:p-12">
        <div className="w-full max-w-md space-y-8">
          {children}
        </div>
      </div>

      {/* RIGHT SIDE — Gradient Hero (hidden on mobile) */}
      <div className="hidden lg:flex flex-1 relative overflow-hidden">
        {/* Gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900" />
        
        {/* Animated blobs */}
        <div className="absolute top-0 -left-4 w-72 h-72 bg-indigo-500/20 rounded-full mix-blend-screen filter blur-3xl animate-pulse" />
        <div className="absolute top-1/3 -right-4 w-72 h-72 bg-purple-500/20 rounded-full mix-blend-screen filter blur-3xl animate-pulse" style={{ animationDelay: "2s" }} />
        <div className="absolute -bottom-8 left-1/4 w-72 h-72 bg-cyan-500/15 rounded-full mix-blend-screen filter blur-3xl animate-pulse" style={{ animationDelay: "4s" }} />
        
        {/* Subtle grid pattern overlay */}
        <div className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32' width='32' height='32' fill='none' stroke-width='2' stroke='rgb(148 163 184 / 0.15)'%3e%3cpath d='M0 .5H31.5V32'/%3e%3c/svg%3e")`,
          }}
        />

        {/* Hero content */}
        <div className="relative z-10 flex items-center justify-center p-8 lg:p-12 w-full">
          <div className="text-center space-y-6 max-w-sm">
            {/* Shield icon */}
            <div className="inline-flex rounded-full p-4 bg-white/10 backdrop-blur-sm mb-2">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
              </svg>
            </div>
            
            <h2 className="text-3xl lg:text-4xl font-bold text-white leading-tight">
              Sacred Texts,<br />Modern Search
            </h2>
            <p className="text-lg text-white/70 leading-relaxed">
              Explore the Quran and Bible with AI-powered semantic search, morphological analysis, and multi-agent comparative theology.
            </p>
            
            {/* Feature pills */}
            <div className="flex flex-wrap justify-center gap-2 pt-2">
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-white/10 text-white/80 backdrop-blur-sm">Semantic Search</span>
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-white/10 text-white/80 backdrop-blur-sm">5-Agent Analysis</span>
              <span className="px-3 py-1 rounded-full text-xs font-medium bg-white/10 text-white/80 backdrop-blur-sm">43K+ Verses</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
