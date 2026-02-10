"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Loader2, AlertCircle } from "lucide-react";
import { lookupVerseApiVerseLookupGet } from "@/lib/api";
import type { VerseLookupResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

interface VerseLookupInputProps {
  placeholder?: string;
  className?: string;
  onSuccess?: (response: VerseLookupResponse) => void;
}

export function VerseLookupInput({
  placeholder = "Bakara 183 veya Genesis 1:1",
  className,
  onSuccess,
}: VerseLookupInputProps) {
  const [value, setValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await lookupVerseApiVerseLookupGet({
        query: { ref: value.trim() },
      });

      if (response.data?.success && response.data.verses.length > 0) {
        const verse = response.data.verses[0];

        // Navigate to appropriate page based on source
        if (verse.source === "quran" && verse.surah_id) {
          router.push(`/quran/${verse.surah_id}?verse=${verse.verse_id}`);
        } else if (verse.book_id) {
          router.push(
            `/bible/${verse.book_id}?chapter=${verse.chapter}&verse=${verse.verse}`
          );
        }

        onSuccess?.(response.data);
        setValue(""); // Clear input on success
      } else {
        setError("Ayet bulunamadı. Lütfen formatı kontrol edin.");
      }
    } catch {
      setError("Ayet bulunamadı. Lütfen formatı kontrol edin.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={cn("w-full space-y-2", className)}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative group">
          {/* Glow effect on focus */}
          <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/20 to-primary/10 rounded-lg opacity-0 group-focus-within:opacity-100 blur transition-opacity duration-300" />

          <div className="relative flex items-center gap-2 bg-[var(--color-bg-card)] border border-border/50 rounded-lg p-1 transition-all duration-200 group-focus-within:border-primary/50">
            <Search className="ml-3 size-4 text-muted-foreground/70 transition-colors group-focus-within:text-primary" />

            <Input
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={placeholder}
              disabled={isLoading}
              className="flex-1 border-0 bg-transparent shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-muted-foreground/50"
            />

            <Button
              type="submit"
              size="sm"
              disabled={isLoading || !value.trim()}
              className="mr-1 relative overflow-hidden group/btn"
            >
              <AnimatePresence mode="wait">
                {isLoading ? (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    transition={{ duration: 0.15 }}
                  >
                    <Loader2 className="size-4 animate-spin" />
                  </motion.div>
                ) : (
                  <motion.span
                    key="text"
                    initial={{ opacity: 0, y: 5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -5 }}
                    transition={{ duration: 0.15 }}
                  >
                    Ara
                  </motion.span>
                )}
              </AnimatePresence>
            </Button>
          </div>
        </div>
      </form>

      {/* Error message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10, height: 0 }}
            animate={{ opacity: 1, y: 0, height: "auto" }}
            exit={{ opacity: 0, y: -10, height: 0 }}
            transition={{ duration: 0.2 }}
            className="flex items-center gap-2 px-3 py-2 text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-lg"
          >
            <AlertCircle className="size-4 shrink-0" />
            <p>{error}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
