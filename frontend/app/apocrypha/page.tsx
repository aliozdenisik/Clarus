"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { springPresets } from "@/lib/design-system"
import { GlowCard } from "@/components/ui/glow-card"
import { Input } from "@/components/ui/input"
import { useRouter } from "next/navigation"
import { Search, BookOpen, User, LogOut } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { useSession, signOut } from "@/lib/auth-client"
import { Button } from "@/components/ui/button"
import { toast } from "sonner"
import { logger } from "@/lib/logger"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface Book {
  nr: number
  name: string
  chapters_count: number
  testament: string
}

export default function ApocryphaPage() {
  const [books, setBooks] = useState<Book[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const { data: session, isPending: authLoading } = useSession()
  const user = session?.user
  const router = useRouter()

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in")
    }
  }, [user, authLoading, router])

  useEffect(() => {
    const controller = new AbortController()

    const fetchBooks = async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/metadata/bible/books?testament=apocrypha`,
          {
            credentials: "include",
            signal: controller.signal,
          }
        )

        if (controller.signal.aborted) {
          return
        }

        if (!response.ok) throw new Error("Failed to fetch books")
        const data = await response.json()

        if (controller.signal.aborted) {
          return
        }

        setBooks(data.data?.books || [])
      } catch (error) {
        if (
          (error instanceof DOMException && error.name === "AbortError") ||
          (error instanceof Error && error.name === "AbortError")
        ) {
          return
        }

        logger.error("Failed to load books", error, { component: "ApocryphaPage" })
        toast.error("Failed to load books")
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      }
    }

    if (user) {
      fetchBooks()
    }

    return () => {
      controller.abort()
    }
  }, [user])

  const handleLogout = async () => {
    await signOut()
    router.push("/sign-in")
    toast.success("Logged out successfully")
  }

  const filteredBooks = books.filter((book) =>
    book.name.toLowerCase().includes(searchQuery.toLowerCase())
  )

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[var(--color-bg-app)] p-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.snappy}
          className="mb-8 flex items-center justify-between"
        >
          <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
            <User className="h-4 w-4" />
            <span className="text-sm">{user?.name || user?.email}</span>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push("/search")}
              className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
            >
              <Search className="h-4 w-4" />
              Search
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
          className="mb-8"
        >
          <h1 className="mb-2 flex items-center gap-3 text-3xl font-bold text-[var(--color-text-primary)]">
            <BookOpen className="h-8 w-8 text-[var(--color-accent-primary)]" />
            Apocrypha
          </h1>
          <p className="text-[var(--color-text-secondary)]">Browse the books of the Apocrypha</p>
        </motion.div>

        {/* Search */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="relative mb-8 max-w-md"
        >
          <Search className="absolute top-1/2 left-3 h-4 w-4 -translate-y-1/2 text-[var(--color-text-muted)]" />
          <Input
            placeholder="Search book..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="border-[var(--color-border-subtle)] bg-[var(--color-bg-surface)] pl-10"
          />
        </motion.div>

        {/* Grid */}
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {isLoading
            ? [...Array(12)].map((_, i) => (
                <Skeleton key={`apocrypha-skeleton-${i}`} className="h-32 w-full rounded-xl" />
              ))
            : filteredBooks.map((book, i) => (
                <motion.div
                  key={book.nr}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{
                    ...springPresets.snappy,
                    delay: i * 0.03, // Stagger effect
                  }}
                  onClick={() => router.push(`/bible/${book.nr}`)}
                  className="cursor-pointer"
                >
                  <GlowCard className="group h-full transition-colors hover:border-[var(--color-accent-glow)]">
                    <div className="flex h-full flex-col justify-between">
                      <div>
                        <h3 className="text-xl font-bold text-[var(--color-text-primary)] transition-colors group-hover:text-[var(--color-accent-primary)]">
                          {book.name}
                        </h3>
                      </div>
                      <div className="mt-4 flex items-center justify-between border-t border-[var(--color-border-subtle)] pt-4 text-xs text-[var(--color-text-muted)]">
                        <span>{book.chapters_count} chapters</span>
                        <span className="font-medium text-[var(--color-accent-primary)] opacity-0 transition-opacity group-hover:opacity-100">
                          Read &rarr;
                        </span>
                      </div>
                    </div>
                  </GlowCard>
                </motion.div>
              ))}
        </div>

        {!isLoading && filteredBooks.length === 0 && (
          <div className="py-20 text-center text-[var(--color-text-muted)]">
            <p>No books found matching &quot;{searchQuery}&quot;</p>
          </div>
        )}
      </div>
    </div>
  )
}
