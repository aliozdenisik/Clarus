"use client"

import { motion } from "framer-motion"
import { ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { springPresets } from "@/lib/design-system"
import { useRouter } from "next/navigation"

interface SurahHeaderProps {
  id: number
  nameArabic: string
  transliteration: string
  type: string
  totalVerses: number
}

export function SurahHeader({
  id,
  nameArabic,
  transliteration,
  type,
  totalVerses,
}: SurahHeaderProps) {
  const router = useRouter()

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={springPresets.snappy}
      className="mb-8"
    >
      <Button
        variant="ghost"
        size="sm"
        onClick={() => router.push("/quran")}
        className="mb-6 flex items-center gap-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Quran
      </Button>

      <div className="text-center">
        <div className="mb-4 flex items-center justify-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-accent-primary)] text-xl font-bold text-white">
            {id}
          </div>
          <h1 className="font-arabic text-4xl text-[var(--color-text-primary)]">{nameArabic}</h1>
        </div>
        <h2 className="mb-2 text-2xl font-bold text-[var(--color-text-primary)]">
          {transliteration}
        </h2>
        <p className="text-[var(--color-text-muted)]">
          {type} • {totalVerses} verses
        </p>
      </div>
    </motion.div>
  )
}
