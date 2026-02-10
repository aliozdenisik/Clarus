"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useSession, signOut } from "@/lib/auth-client";
import { Button } from "@/components/ui/button";
import { GlowCard } from "@/components/ui/glow-card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { ArrowLeft, User, LogOut } from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Verse {
  id: number;
  text: string;           // Arabic text (always present)
  translation: string;    // Turkish translation (always present in API)
}

interface SurahDetail {
  id: number;
  name: string;
  name_arabic: string;
  transliteration: string;
  type: string;
  total_verses: number;
  verses: Verse[];
}

export default function SurahDetailPage() {
  const params = useParams();
  const surahId = params.surahId as string;
  const searchParams = useSearchParams();
  const [surah, setSurah] = useState<SurahDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [highlightedVerse, setHighlightedVerse] = useState<number | null>(null);
  const { data: session, isPending: authLoading } = useSession();
  const user = session?.user;
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in");
    }
  }, [user, authLoading, router]);

  // Read verse parameter from URL on mount
  useEffect(() => {
    const verseParam = searchParams.get('verse');
    if (verseParam) {
      const verseId = parseInt(verseParam, 10);
      if (!isNaN(verseId)) {
        setHighlightedVerse(verseId);
      }
    }
  }, [searchParams]);

  // Scroll to verse when content loads and highlightedVerse is set
  useEffect(() => {
    if (highlightedVerse && surah) {
      // Small delay to ensure DOM is fully rendered
      const timer = setTimeout(() => {
        const element = document.querySelector(`[data-verse-id="${highlightedVerse}"]`);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
          // Clear highlight after 2 seconds
          setTimeout(() => setHighlightedVerse(null), 2000);
        }
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [highlightedVerse, surah]);

   useEffect(() => {
     const fetchSurah = async () => {
       try {
         const response = await fetch(
           `${API_BASE_URL}/api/metadata/quran/surahs/${surahId}`,
           {
             credentials: "include",
           }
         );

        if (!response.ok) {
          throw new Error("Failed to fetch surah");
        }

        const data = await response.json();
        setSurah(data.data?.surah || null);
      } catch {
        toast.error("Failed to load surah");
      } finally {
        setIsLoading(false);
      }
    };

    if (user && surahId) {
      fetchSurah();
    }
  }, [user, surahId]);

  const handleLogout = async () => {
    await signOut();
    router.push("/sign-in");
    toast.success("Logged out successfully");
  };

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-[var(--color-bg-app)] p-8">
        <div className="mx-auto max-w-4xl">
          <Skeleton className="h-12 w-64 mb-4" />
          <Skeleton className="h-6 w-48 mb-8" />
          <div className="space-y-4">
            {[...Array(10)].map((_, i) => (
              <Skeleton key={`surah-detail-skeleton-${i}`} className="h-24 w-full" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!surah) {
    return (
      <div className="min-h-screen bg-[var(--color-bg-app)] p-8 flex items-center justify-center">
        <div className="text-center">
          <p className="text-[var(--color-text-muted)] mb-4">Surah not found</p>
          <Button onClick={() => router.push("/quran")}>Back to Quran</Button>
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
            onClick={() => router.push("/quran")}
            className="flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Quran
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

        {/* Surah Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
          className="mb-8 text-center"
        >
          <div className="flex items-center justify-center gap-4 mb-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-accent-primary)] text-xl font-bold text-white">
              {surah.id}
            </div>
            <h1 className="text-4xl font-arabic text-[var(--color-text-primary)]">
              {surah.name_arabic}
            </h1>
          </div>
          <h2 className="text-2xl font-bold text-[var(--color-text-primary)] mb-2">
            {surah.transliteration}
          </h2>
          <p className="text-[var(--color-text-muted)]">
            {surah.type} • {surah.total_verses} verses
          </p>
        </motion.div>

        {/* Verses */}
        <div className="space-y-4">
          {surah.verses.map((verse, i) => (
            <motion.div
              key={verse.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ ...springPresets.snappy, delay: i * 0.02 }}
              data-verse-id={verse.id}
              className={
                highlightedVerse === verse.id
                  ? "ring-2 ring-[var(--color-accent-primary)] shadow-lg shadow-[var(--color-accent-primary)]/20 transition-all duration-500 rounded-lg"
                  : "transition-all duration-500"
              }
            >
              <GlowCard className="p-6">
                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-bg-secondary)] text-xl font-medium text-[var(--color-accent-primary)]">
                      {verse.id}
                    </div>
                  </div>
                  <div className="flex flex-col gap-3 flex-1">
                    {/* Arabic text - RTL with proper font */}
                    <p 
                      lang="ar" 
                      className="font-arabic text-2xl text-[var(--color-text-primary)]"
                    >
                      {verse.text}
                    </p>
                    
                    {/* Turkish translation - with fallback for safety */}
                    {verse.translation ? (
                      <p 
                        lang="tr" 
                        className="text-2xl leading-relaxed text-[var(--color-text-secondary)]"
                      >
                        {verse.translation}
                      </p>
                    ) : (
                      <p className="text-sm text-[var(--color-text-secondary)] italic">
                        Translation not available
                      </p>
                    )}
                  </div>
                </div>
              </GlowCard>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
