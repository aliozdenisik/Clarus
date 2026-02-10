"use client"
import Link from "next/link"
import Image from "next/image"

import { Icons } from "@/components/ui/icons"
import { Button } from "@/components/ui/button"

function Footer() {
  return (
    <footer className="bg-background border-border/40 border-t px-4 py-12 md:px-6">
      <div className="container mx-auto">
        <div className="flex flex-col justify-between md:flex-row">
          <div className="mb-8 md:mb-0">
            <Link href="/" className="flex items-center gap-3">
              <Image
                src="/logo-dark-nobg.png"
                alt="Clarus"
                width={32}
                height={32}
                className="opacity-90"
              />
              <h2 className="text-lg font-bold">Clarus</h2>
            </Link>

            <p className="mt-4 max-w-xs dark:text-gray-300">
              Maximum-accuracy RAG search for sacred texts with AI-powered comparative analysis.
            </p>
            <div className="mt-4">
              <Link href="https://github.com/aliozdenisik/Clarus">
                <Button variant="secondary">
                  Star on GitHub
                  <Icons.gitHub className="ml-1 h-4 w-4" />
                </Button>
              </Link>
            </div>
            <p className="mt-5 text-sm dark:text-gray-400">
              © {new Date().getFullYear()} Clarus. All rights reserved.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-8 md:grid-cols-3">
            <div>
              <h3 className="mb-4 font-semibold">Pages</h3>
              <ul className="space-y-2">
                <li>
                  <Link
                    href="/search"
                    className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white"
                  >
                    Search
                  </Link>
                </li>
                <li>
                  <Link
                    href="/compare"
                    className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white"
                  >
                    Compare
                  </Link>
                </li>
                <li>
                  <Link
                    href="/keyword-search"
                    className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white"
                  >
                    Keyword Search
                  </Link>
                </li>
                <li>
                  <Link
                    href="/history"
                    className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white"
                  >
                    History
                  </Link>
                </li>
                <li>
                  <Link
                    href="/settings"
                    className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white"
                  >
                    Settings
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="mb-4 font-semibold">Scriptures</h3>
              <ul className="space-y-2">
                <li>
                  <Link
                    href="/quran"
                    className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white"
                  >
                    Quran
                  </Link>
                </li>
                <li>
                  <Link
                    href="/old-testament"
                    className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white"
                  >
                    Old Testament
                  </Link>
                </li>
                <li>
                  <Link
                    href="/new-testament"
                    className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white"
                  >
                    New Testament
                  </Link>
                </li>
                <li>
                  <Link
                    href="/apocrypha"
                    className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white"
                  >
                    Apocrypha
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h3 className="mb-4 font-semibold">Links</h3>
              <ul className="space-y-2">
                <li>
                  <Link
                    href="https://github.com/aliozdenisik/Clarus"
                    className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white"
                  >
                    GitHub
                  </Link>
                </li>
                <li>
                  <Link
                    href="https://github.com/aliozdenisik/Clarus/issues"
                    className="text-gray-600 hover:text-black dark:text-gray-400 dark:hover:text-white"
                  >
                    Report Issue
                  </Link>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div className="mt-8 flex w-full items-center justify-center">
          <h1 className="bg-gradient-to-b from-neutral-700 to-neutral-900 bg-clip-text text-center text-3xl font-bold text-transparent select-none md:text-5xl lg:text-[10rem] dark:from-neutral-400 dark:to-neutral-700">
            Clarus
          </h1>
        </div>
      </div>
    </footer>
  )
}

export { Footer }
