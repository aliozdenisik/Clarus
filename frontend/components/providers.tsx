"use client";

import { ApiProvider } from "@/lib/api-provider";

export function Providers({ children }: { children: React.ReactNode }) {
  return <ApiProvider>{children}</ApiProvider>;
}
