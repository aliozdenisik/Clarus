"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { Button } from "@/components/ui/button";
import { GlowCard } from "@/components/ui/glow-card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { ArrowLeft, BookOpen, User, LogOut, ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChapterSummary {
  chapter: number;
  verses_count: number;
}

interface BookDetail {
  nr: number;
  name: string;
  testament: string;
  chapters: ChapterSummary[];
}

interface Verse {
  verse: number;
  text: string;
}

interface ChapterContent {
  book_name: string;
  chapter: number;
  verses: Verse[];
}

export default function BookDetailPage() {
  const params = useParams();
  const bookNr = params.bookNr as string;
  const searchParams = useSearchParams();
  const [book, setBook] = useState<BookDetail | null>(null);
  const [selectedChapter, setSelectedChapter] = useState<number | null>(null);
  const [chapterContent, setChapterContent] = useState<ChapterContent | null>(null);
  const [isLoadingBook, setIsLoadingBook] = useState(true);
  const [isLoadingChapter, setIsLoadingChapter] = useState(false);
  const [highlightedVerse, setHighlightedVerse] = useState<number | null>(null);
  const { user, isLoading: authLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  // Read URL params on mount
  useEffect(() => {
    const chapterParam = searchParams.get('chapter');
    const verseParam = searchParams.get('verse');
    
    if (chapterParam) {
      const chapterNum = parseInt(chapterParam, 10);
      if (!isNaN(chapterNum)) {
        setSelectedChapter(chapterNum);
      }
    }
    if (verseParam) {
      const verseNum = parseInt(verseParam, 10);
      if (!isNaN(verseNum)) {
        setHighlightedVerse(verseNum);
      }
    }
  }, [searchParams]);

  // Fetch book details
  useEffect(() => {
    const fetchBook = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const response = await fetch(
          `http://localhost:8000/api/metadata/bible/books/${bookNr}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch book");
        }

        const data = await response.json();
        setBook(data.data?.book || null);
        // Auto-select chapter 1 only if no chapter param in URL
        if (data.data?.book?.chapters?.length > 0 && !searchParams.get('chapter')) {
          setSelectedChapter(1);
        }
      } catch (error) {
        toast.error("Failed to load book");
      } finally {
        setIsLoadingBook(false);
      }
    };

    if (user && bookNr) {
      fetchBook();
    }
  }, [user, bookNr, searchParams]);

  // Fetch chapter content when selected
  useEffect(() => {
    const fetchChapter = async () => {
      if (!selectedChapter) return;
      
      setIsLoadingChapter(true);
      try {
        const token = localStorage.getItem("access_token");
        const response = await fetch(
          `http://localhost:8000/api/metadata/bible/books/${bookNr}/chapters/${selectedChapter}`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch chapter");
        }

        const data = await response.json();
        setChapterContent(data.data || null);
      } catch (error) {
        toast.error("Failed to load chapter");
      } finally {
        setIsLoadingChapter(false);
      }
    };

    if (user && selectedChapter) {
      fetchChapter();
    }
  }, [user, bookNr, selectedChapter]);

  // Scroll to verse when chapter content loads and highlightedVerse is set
  useEffect(() => {
    if (highlightedVerse && chapterContent) {
      const timer = setTimeout(() => {
        const element = document.querySelector(`[data-verse-id="${highlightedVerse}"]`);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
          setTimeout(() => setHighlightedVerse(null), 2000);
        }
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [highlightedVerse, chapterContent]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
    toast.success("Logged out successfully");
  };

  const getBackRoute = () => {
    if (!book) return "/old-testament";
    switch (book.testament) {
      case "old_testament":
        return "/old-testament";
      case "new_testament":
        return "/new-testament";
      case "apocrypha":
        return "/apocrypha";
      default:
        return "/old-testament";
    }
  };

  const getTestamentLabel = () => {
    if (!book) return "";
    switch (book.testament) {
      case "old_testament":
        return "Old Testament";
      case "new_testament":
        return "New Testament";
      case "apocrypha":
        return "Apocrypha";
      default:
        return "";
    }
  };

  if (authLoading || isLoadingBook) {
    return (
      <div className="min-h-screen bg-[var(--color-bg-app)] p-8">
        <div className="mx-auto max-w-4xl">
          <Skeleton className="h-12 w-64 mb-4" />
          <Skeleton className="h-6 w-48 mb-8" />
          <Skeleton className="h-12 w-full mb-4" />
          <div className="space-y-4">
            {[...Array(10)].map((_, i) => (
              <Skeleton key={i} className="h-20 w-full" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!book) {
    return (
      <div className="min-h-screen bg-[var(--color-bg-app)] p-8 flex items-center justify-center">
        <div className="text-center">
          <p className="text-[var(--color-text-muted)] mb-4">Book not found</p>
          <Button onClick={() => router.push("/old-testament")}>Back to Books</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[var(--color-bg-app)] p-8">
      <div className="mx-auto max-w-4xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.snappy}
          className="mb-6 flex items-center justify-between"
        >
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push(getBackRoute())}
            className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to {getTestamentLabel()}
          </Button>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-[var(--color-text-secondary)]">
              <User className="h-4 w-4" />
              <span className="text-sm">{user?.name || user?.email}</span>
            </div>
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

        {/* Book Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
          className="mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <BookOpen className="h-8 w-8 text-[var(--color-accent-primary)]" />
            <h1 className="text-3xl font-bold text-[var(--color-text-primary)]">
              {book.name}
            </h1>
          </div>
          <p className="text-[var(--color-text-muted)]">
            {getTestamentLabel()} • {book.chapters.length} chapters
          </p>
        </motion.div>

        {/* Chapter Selector */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <p className="text-sm text-[var(--color-text-muted)] mb-3">Select Chapter</p>
          <div className="flex flex-wrap gap-2">
            {book.chapters.map((ch) => (
              <button
                key={ch.chapter}
                onClick={() => setSelectedChapter(ch.chapter)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  selectedChapter === ch.chapter
                    ? "bg-[var(--color-accent-primary)] text-white"
                    : "bg-[var(--color-bg-surface)] text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-elevated)] hover:text-[var(--color-text-primary)]"
                }`}
              >
                {ch.chapter}
              </button>
            ))}
          </div>
        </motion.div>

        {/* Chapter Content */}
        <AnimatePresence mode="wait">
          {isLoadingChapter ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-4"
            >
              {[...Array(10)].map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </motion.div>
          ) : chapterContent ? (
            <motion.div
              key={`chapter-${selectedChapter}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={springPresets.fluid}
            >
              <GlowCard className="p-6">
                <h3 className="text-lg font-bold text-[var(--color-text-primary)] mb-4">
                  Chapter {chapterContent.chapter}
                </h3>
                <div className="space-y-3">
                  {chapterContent.verses.map((verse) => (
                    <p 
                      key={verse.verse} 
                      data-verse-id={verse.verse}
                      className={cn(
                        "text-[var(--color-text-primary)] leading-relaxed",
                        highlightedVerse === verse.verse && 
                          "ring-2 ring-[var(--color-accent-primary)] shadow-lg shadow-[var(--color-accent-primary)]/20 rounded-lg p-2 transition-all duration-500"
                      )}
                    >
                      <span className="text-sm font-bold text-[var(--color-accent-primary)] mr-2">
                        {verse.verse}
                      </span>
                      {verse.text}
                    </p>
                  ))}
                </div>
              </GlowCard>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12 text-[var(--color-text-muted)]"
            >
              Select a chapter to start reading
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
