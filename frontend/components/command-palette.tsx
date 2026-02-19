"use client"

import { useState, useEffect } from "react"
import { Command } from "cmdk"
import { useTranslations } from "next-intl"
import { useRouter } from "@/i18n/navigation"
import {
  Search,
  GitCompareArrows,
  Book,
  BookOpen,
  Languages,
  History,
  Settings,
  ArrowRight,
  ScrollText,
  FileText,
} from "lucide-react"

interface CommandItem {
  icon: React.ReactNode
  label: string
  hint?: string
  href: string
}

export function CommandPalette() {
  const [open, setOpen] = useState(false)
  const t = useTranslations("CommandPalette")
  const router = useRouter()

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((prev) => !prev)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  const runCommand = (href: string) => {
    setOpen(false)
    router.push(href as Parameters<typeof router.push>[0])
  }

  const quickActions: CommandItem[] = [
    {
      icon: <Search className="h-4 w-4 shrink-0 text-indigo-400" />,
      label: t("search"),
      hint: "Quran",
      href: "/search",
    },
    {
      icon: <GitCompareArrows className="h-4 w-4 shrink-0 text-violet-400" />,
      label: t("compare"),
      hint: "Multi-agent",
      href: "/compare",
    },
    {
      icon: <Languages className="h-4 w-4 shrink-0 text-emerald-400" />,
      label: t("keywordSearch"),
      hint: "Arabic / Hebrew / Greek",
      href: "/keyword-search",
    },
    {
      icon: <Book className="h-4 w-4 shrink-0 text-amber-400" />,
      label: t("browseQuran"),
      hint: "114 Surahs",
      href: "/quran",
    },
    {
      icon: <BookOpen className="h-4 w-4 shrink-0 text-sky-400" />,
      label: t("browseBible"),
      hint: "Old Testament",
      href: "/old-testament",
    },
  ]

  const navigationItems: CommandItem[] = [
    {
      icon: <Search className="h-4 w-4 shrink-0 opacity-50" />,
      label: t("search"),
      href: "/search",
    },
    {
      icon: <Search className="h-4 w-4 shrink-0 opacity-50" />,
      label: t("searchOT"),
      href: "/search?source=ot",
    },
    {
      icon: <Search className="h-4 w-4 shrink-0 opacity-50" />,
      label: t("searchNT"),
      href: "/search?source=nt",
    },
    {
      icon: <Search className="h-4 w-4 shrink-0 opacity-50" />,
      label: t("searchApocrypha"),
      href: "/search?source=apocrypha",
    },
    {
      icon: <Book className="h-4 w-4 shrink-0 opacity-50" />,
      label: t("quran"),
      href: "/quran",
    },
    {
      icon: <BookOpen className="h-4 w-4 shrink-0 opacity-50" />,
      label: t("oldTestament"),
      href: "/old-testament",
    },
    {
      icon: <ScrollText className="h-4 w-4 shrink-0 opacity-50" />,
      label: t("newTestament"),
      href: "/new-testament",
    },
    {
      icon: <FileText className="h-4 w-4 shrink-0 opacity-50" />,
      label: t("apocrypha"),
      href: "/apocrypha",
    },
    {
      icon: <GitCompareArrows className="h-4 w-4 shrink-0 opacity-50" />,
      label: t("compare"),
      href: "/compare",
    },
    {
      icon: <History className="h-4 w-4 shrink-0 opacity-50" />,
      label: t("history"),
      href: "/history",
    },
    {
      icon: <Settings className="h-4 w-4 shrink-0 opacity-50" />,
      label: t("settings"),
      href: "/settings",
    },
  ]

  return (
    <>
      {/* cmdk uses [cmdk-overlay] and [cmdk-dialog] data-attributes — must be positioned via CSS */}
      <style>{`
        [cmdk-overlay] {
          position: fixed;
          inset: 0;
          z-index: 9998;
          background: rgba(0, 0, 0, 0.6);
          backdrop-filter: blur(6px);
          -webkit-backdrop-filter: blur(6px);
        }

        [cmdk-dialog] {
          position: fixed;
          top: 13%;
          left: 50%;
          transform: translateX(-50%);
          z-index: 9999;
          width: 100%;
          max-width: 38rem;
          padding: 0 1rem;
          box-sizing: border-box;
        }
      `}</style>

      <Command.Dialog open={open} onOpenChange={setOpen} label={t("placeholder")}>
        <div className="overflow-hidden rounded-xl border border-white/[0.06] bg-[#0f0f12] shadow-[0_32px_80px_rgba(0,0,0,0.8)]">
          <div className="flex items-center gap-3 border-b border-white/[0.06] px-4 py-3">
            <Search className="h-4 w-4 shrink-0 text-white/30" />
            <Command.Input
              placeholder={t("placeholder")}
              className="flex-1 bg-transparent text-sm text-white/90 caret-indigo-400 outline-none placeholder:text-white/30"
              autoFocus
            />
            <kbd className="hidden items-center gap-1 rounded border border-white/[0.06] bg-white/[0.04] px-1.5 py-0.5 font-mono text-[10px] text-white/20 sm:inline-flex">
              ESC
            </kbd>
          </div>

          <Command.List className="max-h-[26rem] overflow-y-auto overscroll-contain py-2">
            <Command.Empty className="py-10 text-center text-sm text-white/30">
              {t("noResults")}
            </Command.Empty>

            <Command.Group
              heading={
                <span className="px-4 py-2 text-[10px] font-semibold tracking-widest text-white/25 uppercase select-none">
                  {t("quickActions")}
                </span>
              }
            >
              {quickActions.map((item) => (
                <Command.Item
                  key={item.href}
                  value={item.label}
                  onSelect={() => runCommand(item.href)}
                  className="group mx-2 flex cursor-pointer items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-white/70 transition-colors data-[selected=true]:bg-white/[0.06] data-[selected=true]:text-white"
                >
                  {item.icon}
                  <span className="flex-1 font-medium">{item.label}</span>
                  {item.hint && (
                    <span className="text-[11px] text-white/25 group-data-[selected=true]:text-white/40">
                      {item.hint}
                    </span>
                  )}
                  <ArrowRight className="h-3.5 w-3.5 text-white/0 transition-colors group-data-[selected=true]:text-white/30" />
                </Command.Item>
              ))}
            </Command.Group>

            <div className="mx-4 my-1.5 h-px bg-white/[0.04]" />

            <Command.Group
              heading={
                <span className="px-4 py-2 text-[10px] font-semibold tracking-widest text-white/25 uppercase select-none">
                  {t("navigation")}
                </span>
              }
            >
              {navigationItems.map((item) => (
                <Command.Item
                  key={item.href + item.label}
                  value={item.label + item.href}
                  onSelect={() => runCommand(item.href)}
                  className="group mx-2 flex cursor-pointer items-center gap-3 rounded-lg px-3 py-2 text-sm text-white/50 transition-colors data-[selected=true]:bg-white/[0.06] data-[selected=true]:text-white/80"
                >
                  {item.icon}
                  <span className="flex-1">{item.label}</span>
                  <ArrowRight className="h-3.5 w-3.5 text-white/0 transition-colors group-data-[selected=true]:text-white/25" />
                </Command.Item>
              ))}
            </Command.Group>
          </Command.List>

          <div className="flex items-center justify-between border-t border-white/[0.04] px-4 py-2.5">
            <div className="flex items-center gap-3">
              <span className="flex items-center gap-1 text-[10px] text-white/20">
                <kbd className="rounded border border-white/[0.06] bg-white/[0.04] px-1.5 py-0.5 font-mono">
                  ↑
                </kbd>
                <kbd className="rounded border border-white/[0.06] bg-white/[0.04] px-1.5 py-0.5 font-mono">
                  ↓
                </kbd>
                <span className="ml-1">navigate</span>
              </span>
              <span className="flex items-center gap-1 text-[10px] text-white/20">
                <kbd className="rounded border border-white/[0.06] bg-white/[0.04] px-1.5 py-0.5 font-mono">
                  ↵
                </kbd>
                <span className="ml-1">open</span>
              </span>
            </div>
            <span className="flex items-center gap-1 text-[10px] text-white/15">
              <kbd className="rounded border border-white/[0.06] bg-white/[0.04] px-1.5 py-0.5 font-mono">
                ⌘K
              </kbd>
              <span className="ml-1">toggle</span>
            </span>
          </div>
        </div>
      </Command.Dialog>
    </>
  )
}
