"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { springPresets } from "@/lib/design-system";
import { useAuth } from "@/lib/auth/auth-context";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { GlowCard } from "@/components/ui/glow-card";
import { Skeleton } from "@/components/ui/skeleton";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { BookOpen, Search, User, LogOut } from "lucide-react";

interface Surah {
  id: number;
  name: string;
  name_transliterated: string;
  verse_count: number;
  revelation_type: string;
}

// API response format (may vary)
interface ApiSurah {
  id: number;
  name?: string;
  name_arabic?: string;
  transliteration?: string;
  name_transliterated?: string;
  total_verses?: number;
  verse_count?: number;
  type?: string;
  revelation_type?: string;
}

export default function QuranPage() {
  const [surahs, setSurahs] = useState<Surah[]>([]);
  const [filter, setFilter] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const { user, isLoading: authLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/login");
    }
  }, [user, authLoading, router]);

  useEffect(() => {
    const fetchSurahs = async () => {
      try {
        const token = localStorage.getItem("access_token");
        const response = await fetch("http://localhost:8000/api/metadata/quran/surahs", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error("Failed to fetch surahs");
        }

        const data = await response.json();
        // Handle wrapped response format: {success: true, data: {surahs: [...]}}
        const surahList: ApiSurah[] = data.data?.surahs || data.surahs || data || [];
        // Map API field names to component expected names
        const mappedSurahs: Surah[] = surahList.map((s: ApiSurah) => ({
          id: s.id,
          name: s.name_arabic || s.name || '',
          name_transliterated: s.transliteration || s.name_transliterated || s.name || '',
          verse_count: s.total_verses || s.verse_count || 0,
          revelation_type: s.type || s.revelation_type || '',
        }));
        setSurahs(mappedSurahs);
      } catch (error) {
        toast.error("Failed to load surahs");
      } finally {
        setIsLoading(false);
      }
    };

    if (user) {
      fetchSurahs();
    }
  }, [user]);

  const handleLogout = async () => {
    await logout();
    router.push("/login");
    toast.success("Logged out successfully");
  };

  const filteredSurahs = surahs.filter((surah) =>
    surah.name_transliterated.toLowerCase().includes(filter.toLowerCase()) ||
    surah.id.toString().includes(filter)
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
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.snappy}
          className="mb-6 flex items-center justify-between"
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

        {/* Title & Filter */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={springPresets.fluid}
          className="mb-8"
        >
          <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="mb-2 text-3xl font-bold text-[var(--color-text-primary)] flex items-center gap-3">
                <BookOpen className="h-8 w-8 text-[var(--color-accent-primary)]" />
                Quran Browse
              </h1>
              <p className="text-[var(--color-text-muted)]">
                Browse all 114 surahs of the Holy Quran
              </p>
            </div>
            <div className="w-full md:w-72">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-text-muted)]" />
                <Input
                  type="text"
                  placeholder="Search surah..."
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
          </div>
        </motion.div>

        {/* Content */}
        {isLoading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {[...Array(12)].map((_, i) => (
              <Skeleton key={i} className="h-32 w-full" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            <AnimatePresence mode="popLayout">
              {filteredSurahs.map((surah, i) => (
                <motion.div
                  key={surah.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  layout
                  transition={{ ...springPresets.snappy, delay: i * 0.02 }}
                >
                  <button
                    onClick={() => router.push(`/search?surah=${surah.id}`)}
                    className="w-full text-left"
                  >
                    <GlowCard className="h-full hover:border-[var(--color-accent-primary)] transition-colors">
                      <div className="flex flex-col h-full justify-between gap-4">
                        <div className="flex items-start justify-between">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--color-bg-secondary)] text-sm font-medium text-[var(--color-text-secondary)]">
                            {surah.id}
                          </div>
                          <span className="font-arabic text-xl text-[var(--color-text-primary)]">
                            {surah.name}
                          </span>
                        </div>
                        
                        <div>
                          <h3 className="text-lg font-bold text-[var(--color-text-primary)]">
                            {surah.name_transliterated}
                          </h3>
                          <div className="mt-1 flex items-center gap-2 text-xs text-[var(--color-text-muted)]">
                            <span>{surah.revelation_type}</span>
                            <span>•</span>
                            <span>{surah.verse_count} verses</span>
                          </div>
                        </div>
                      </div>
                    </GlowCard>
                  </button>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
        
        {!isLoading && filteredSurahs.length === 0 && (
          <div className="py-20 text-center text-[var(--color-text-muted)]">
            No surahs found matching "{filter}"
          </div>
        )}
      </div>
    </div>
  );
}
