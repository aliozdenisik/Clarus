"use client"

import React, { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { getVerseWordsApiQuranVersesSurahIdAyahNumberWordsGet } from "@/lib/api"
import type { WordItem } from "@/lib/api"
import { cn } from "@/lib/utils"
import { EtymologyPopup } from "./etymology-popup"

interface ClickableVerseProps {
  surahId: number
  ayahNumber: number
  arabicText: string
}

export function ClickableVerse({ surahId, ayahNumber, arabicText }: ClickableVerseProps) {
  const [activeWordIndex, setActiveWordIndex] = useState<number | null>(null)

  const { data, error, isLoading } = useQuery({
    queryKey: ["verse-words", surahId, ayahNumber],
    queryFn: async () => {
      const response = await getVerseWordsApiQuranVersesSurahIdAyahNumberWordsGet({
        path: {
          surah_id: surahId,
          ayah_number: ayahNumber,
        },
      })

      if (!response.data) {
        throw new Error("No data returned from verse words API")
      }

      return response.data
    },
    staleTime: Infinity,
    retry: 1,
  })

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement
    const wordIndexStr = target.dataset.wordIndex

    if (wordIndexStr !== undefined) {
      const wordIndex = parseInt(wordIndexStr, 10)
      const word = data?.words[wordIndex]

      if (word?.has_etymology) {
        setActiveWordIndex(wordIndex)
      }
    }
  }

  if (isLoading || error || !data?.words || data.words.length === 0) {
    return (
      <p lang="ar" className="font-arabic text-2xl text-[var(--color-text-primary)]">
        {arabicText}
      </p>
    )
  }

  const words = data.words

  return (
    <div dir="rtl" onClick={handleClick} className="select-text">
      {words.map((word: WordItem) => {
        const isActive = activeWordIndex === word.position
        const isClickable = word.has_etymology

        if (!isClickable) {
          return (
            <span
              key={`word-${word.position}`}
              lang="ar"
              className="font-arabic inline-block px-0.5 py-1 text-2xl text-[var(--color-text-primary)]"
            >
              {word.token}
            </span>
          )
        }

        return (
          <EtymologyPopup
            key={`word-${word.position}`}
            root={word.root || ""}
            rootBuckwalter={word.root_buckwalter || ""}
            open={isActive}
            onOpenChange={(open: boolean) => {
              if (!open && isActive) {
                setActiveWordIndex(null)
              }
            }}
          >
            <span
              data-word-index={word.position}
              lang="ar"
              className={cn(
                "font-arabic inline-block cursor-pointer px-0.5 py-1 text-2xl text-[var(--color-text-primary)]",
                "rounded transition-colors hover:bg-[var(--color-accent-primary)]/10",
                isActive && "bg-[var(--color-accent-primary)]/20"
              )}
              aria-label={word.token || undefined}
            >
              {word.token}
            </span>
          </EtymologyPopup>
        )
      })}
    </div>
  )
}
