"use client"

import { useEffect } from "react"

interface LocaleSetterProps {
  locale: string
}

export function LocaleSetter({ locale }: LocaleSetterProps) {
  useEffect(() => {
    document.documentElement.lang = locale
  }, [locale])

  return null
}
