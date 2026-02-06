"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { GlowCard } from "@/components/ui/glow-card";
import { Input } from "@/components/ui/input";
import { useRouter } from "next/navigation";
import { Search, BookOpen, User, LogOut } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { useSession, signOut } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

interface Book {
  nr: number;
  name: string;
  chapters_count: number;
  testament: string;
}

export default function ApocryphaPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const { data: session, isPending: authLoading } = useSession();
  const user = session?.user;
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    const fetchBooks = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const response = await fetch("http://localhost:8000/api/metadata/bible/books?testament=apocrypha", {
           headers: {
             Authorization: `Bearer ${token}`,
           },
        });
        if (!response.ok) throw new Error("Failed to fetch books");
        const data = await response.json();
        setBooks(data.data?.books || []);
      } catch (error) {
        console.error(error);
        toast.error("Failed to load books");
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchBooks();
    }
  }, [user]);

  const handleLogout = async () => {
    await signOut();
    router.push("/sign-in");
    toast.success("Logged out successfully");
  };

  const filteredBooks = books.filter((book) =>
    book.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (authLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--color-bg-app)]">
        <div className="text-[var(--color-text-secondary)]">Loading...</div>
      </div>
    );
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
          <h1 className="mb-2 text-3xl font-bold text-[var(--color-text-primary)] flex items-center gap-3">
            <BookOpen className="h-8 w-8 text-[var(--color-accent-primary)]" />
            Apocrypha
          </h1>
          <p className="text-[var(--color-text-secondary)]">
            Browse the books of the Apocrypha
          </p>
        </motion.div>


        {/* Search */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-8 max-w-md relative"
        >
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--color-text-muted)]" />
          <Input
            placeholder="Search book..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-[var(--color-bg-surface)] border-[var(--color-border-subtle)]"
          />
        </motion.div>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {isLoading
            ? [...Array(12)].map((_, i) => (
                <Skeleton key={i} className="h-32 w-full rounded-xl" />
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
                  <GlowCard
                    className="h-full hover:border-[var(--color-accent-glow)] transition-colors group"
                  >
                    <div className="flex flex-col h-full justify-between">
                        <div>
                        <h3 className="text-xl font-bold text-[var(--color-text-primary)] group-hover:text-[var(--color-accent-primary)] transition-colors">
                          {book.name}
                        </h3>
                      </div>
                      <div className="mt-4 pt-4 border-t border-[var(--color-border-subtle)] flex items-center justify-between text-xs text-[var(--color-text-muted)]">
                        <span>{book.chapters_count} chapters</span>
                        <span className="opacity-0 group-hover:opacity-100 transition-opacity text-[var(--color-accent-primary)] font-medium">
                          Read &rarr;
                        </span>
                      </div>
                    </div>
                  </GlowCard>
                </motion.div>
              ))}
        </div>

        {!isLoading && filteredBooks.length === 0 && (
          <div className="text-center py-20 text-[var(--color-text-muted)]">
            <p>No books found matching "{searchQuery}"</p>
          </div>
        )}
      </div>
    </div>
  );
}
