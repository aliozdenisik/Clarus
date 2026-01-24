"use client";

import { ApiProvider } from "@/lib/api-provider";
import { AuthProvider } from "@/lib/auth/auth-context";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ApiProvider>
      <AuthProvider>{children}</AuthProvider>
    </ApiProvider>
  );
}
