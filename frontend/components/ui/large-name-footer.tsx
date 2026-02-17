"use client"
import Link from "next/link"
import Image from "next/image"
import { useTranslations } from "next-intl"
import { usePathname } from "next/navigation"

import { Icons } from "@/components/ui/icons"
import { Button } from "@/components/ui/button"

function Footer() {
  const t = useTranslations("Footer")
  const pathname = usePathname()
  const segments = pathname.split("/").filter(Boolean)
  const page = segments.length > 0 ? segments[segments.length - 1] : ""

  if (page === "sign-in" || page === "sign-up") {
    return null
  }

  return (
    <footer className="border-border/40 bg-background border-t px-6 py-16 md:px-8">
      <div className="mx-auto max-w-6xl">
        <div className="grid grid-cols-1 gap-12 md:grid-cols-2 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-3">
              <Image
                src="/logo-dark-nobg.png"
                alt="Clarus"
                width={32}
                height={32}
                className="opacity-90"
              />
              <span className="text-xl font-bold text-zinc-900 dark:text-zinc-100">Clarus</span>
            </Link>

            <p className="mt-4 max-w-xs text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
              {t("description")}
            </p>

            <div className="mt-6">
              <Link href="https://github.com/aliozdenisik/Clarus">
                <Button variant="secondary">
                  {t("starOnGithub")}
                  <Icons.gitHub className="ml-1 h-4 w-4" />
                </Button>
              </Link>
            </div>

            <p className="mt-8 text-xs text-zinc-400 dark:text-zinc-400">
              {t("copyright", { year: new Date().getFullYear() })}
            </p>
          </div>

          <div>
            <h3 className="mb-6 text-[11px] font-semibold tracking-widest text-zinc-400 uppercase dark:text-zinc-500">
              {t("pages")}
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/search"
                  className="text-sm font-medium text-zinc-600 transition-colors duration-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  {t("search")}
                </Link>
              </li>
              <li>
                <Link
                  href="/compare"
                  className="text-sm font-medium text-zinc-600 transition-colors duration-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  {t("compare")}
                </Link>
              </li>
              <li>
                <Link
                  href="/keyword-search"
                  className="text-sm font-medium text-zinc-600 transition-colors duration-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  {t("keywordSearch")}
                </Link>
              </li>
              <li>
                <Link
                  href="/history"
                  className="text-sm font-medium text-zinc-600 transition-colors duration-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  {t("history")}
                </Link>
              </li>
              <li>
                <Link
                  href="/settings"
                  className="text-sm font-medium text-zinc-600 transition-colors duration-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  {t("settings")}
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="mb-6 text-[11px] font-semibold tracking-widest text-zinc-400 uppercase dark:text-zinc-500">
              {t("scriptures")}
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/quran"
                  className="text-sm font-medium text-zinc-600 transition-colors duration-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  {t("quran")}
                </Link>
              </li>
              <li>
                <Link
                  href="/old-testament"
                  className="text-sm font-medium text-zinc-600 transition-colors duration-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  {t("oldTestament")}
                </Link>
              </li>
              <li>
                <Link
                  href="/new-testament"
                  className="text-sm font-medium text-zinc-600 transition-colors duration-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  {t("newTestament")}
                </Link>
              </li>
              <li>
                <Link
                  href="/apocrypha"
                  className="text-sm font-medium text-zinc-600 transition-colors duration-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  {t("apocrypha")}
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="mb-6 text-[11px] font-semibold tracking-widest text-zinc-400 uppercase dark:text-zinc-500">
              {t("links")}
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  href="https://github.com/aliozdenisik/Clarus"
                  className="text-sm font-medium text-zinc-600 transition-colors duration-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  {t("github")}
                </Link>
              </li>
              <li>
                <Link
                  href="https://github.com/aliozdenisik/Clarus/issues"
                  className="text-sm font-medium text-zinc-600 transition-colors duration-200 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
                >
                  {t("reportIssue")}
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </footer>
  )
}

export { Footer }
