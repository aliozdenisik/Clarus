"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Search, Loader2, AlertCircle } from "lucide-react"
import { lookupVerseApiVerseLookupGet } from "@/lib/api"
import type { VerseLookupResponse } from "@/lib/api"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

interface VerseLookupInputProps {
  placeholder?: string
  className?: string
  onSuccess?: (response: VerseLookupResponse) => void
}

export function VerseLookupInput({
  placeholder = "Bakara 183 veya Genesis 1:1",
  className,
  onSuccess,
}: VerseLookupInputProps) {
  const [value, setValue] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!value.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await lookupVerseApiVerseLookupGet({
        query: { ref: value.trim() },
      })

      if (response.data?.success && response.data.verses.length > 0) {
        const verse = response.data.verses[0]

        // Navigate to appropriate page based on source
        if (verse.source === "quran" && verse.surah_id) {
          router.push(`/quran/${verse.surah_id}?verse=${verse.verse_id}`)
        } else if (verse.book_id) {
          router.push(`/bible/${verse.book_id}?chapter=${verse.chapter}&verse=${verse.verse}`)
        }

        onSuccess?.(response.data)
        setValue("") // Clear input on success
      } else {
        setError("Ayet bulunamadı. Lütfen formatı kontrol edin.")
      }
    } catch {
      setError("Ayet bulunamadı. Lütfen formatı kontrol edin.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className={cn("w-full space-y-2", className)}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="group relative">
          {/* Glow effect on focus */}
          <div className="from-primary/20 to-primary/10 absolute -inset-0.5 rounded-lg bg-gradient-to-r opacity-0 blur transition-opacity duration-300 group-focus-within:opacity-100" />

          <div className="border-border/50 group-focus-within:border-primary/50 relative flex items-center gap-2 rounded-lg border bg-[var(--color-bg-card)] p-1 transition-all duration-200">
            <Search className="text-muted-foreground/70 group-focus-within:text-primary ml-3 size-4 transition-colors" />

            <Input
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={placeholder}
              disabled={isLoading}
              className="placeholder:text-muted-foreground/50 flex-1 border-0 bg-transparent shadow-none focus-visible:ring-0 focus-visible:ring-offset-0"
            />

            <Button
              type="submit"
              size="sm"
              disabled={isLoading || !value.trim()}
              className="group/btn relative mr-1 overflow-hidden"
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
            className="text-destructive bg-destructive/10 border-destructive/20 flex items-center gap-2 rounded-lg border px-3 py-2 text-sm"
          >
            <AlertCircle className="size-4 shrink-0" />
            <p>{error}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
