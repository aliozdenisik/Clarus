"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState, useSyncExternalStore } from "react"
import { useTranslations } from "next-intl"
import {
  Menu,
  X,
  LogOut,
  Settings,
  User,
  Book,
  BookOpen,
  ScrollText,
  FileText,
  Search as SearchIcon,
  Home,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from "@/components/ui/navigation-menu"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useSession, signOut } from "@/lib/auth-client"
import { motion, AnimatePresence } from "framer-motion"

export default function Navigation() {
  const pathname = usePathname()
  const { data: session } = useSession()
  const user = session?.user
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const mounted = useSyncExternalStore(
    () => () => {},
    () => true,
    () => false
  )
  const t = useTranslations("Navigation")
  const tCommon = useTranslations("Common")

  const isActive = (path: string) => pathname === path

  const handleLogout = async () => {
    await signOut()
  }

  // Don't show navigation on auth and landing pages
  // With locale routing, pathname includes locale prefix (e.g. /en, /tr)
  const segments = pathname.split("/").filter(Boolean)
  const page = segments.length > 1 ? segments[segments.length - 1] : ""
  const isLandingPage = segments.length <= 1 // e.g. /en or /tr
  if (page === "sign-in" || page === "sign-up" || isLandingPage) {
    return null
  }

  return (
    <nav className="sticky top-0 z-50 border-b border-white/10 bg-black/50 backdrop-blur-xl">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <Link
              href="/"
              className="text-xl font-bold text-white transition-colors hover:text-purple-400"
            >
              Clarus
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-1">
            {mounted ? (
              <NavigationMenu>
                <NavigationMenuList>
                  {/* Hub Link */}
                  <NavigationMenuItem>
                    <Link
                      href="/hub"
                      className={`group hover:bg-accent hover:text-accent-foreground inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors ${
                        isActive("/hub") ? "text-purple-400" : "text-gray-300"
                      }`}
                    >
                      <Home className="mr-2 h-4 w-4" />
                      {t("hub")}
                    </Link>
                  </NavigationMenuItem>

                  {/* Search Dropdown */}
                  <NavigationMenuItem value="search" className="text-muted-foreground">
                    <NavigationMenuTrigger className="bg-transparent text-gray-300 hover:bg-white/5 hover:text-white data-[state=open]:bg-white/5">
                      {t("search")}
                    </NavigationMenuTrigger>
                    <NavigationMenuContent>
                      <ul className="w-80 p-3">
                        <li>
                          <NavigationMenuLink asChild>
                            <Link
                              href="/search"
                              className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                            >
                              <Book className="size-5 shrink-0" />
                              <div>
                                <div className="text-sm font-semibold">{t("quranSearch")}</div>
                                <p className="text-muted-foreground text-sm leading-snug">
                                  {t("quranSearchDesc")}
                                </p>
                              </div>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                        <li>
                          <NavigationMenuLink asChild>
                            <Link
                              href="/search?source=ot"
                              className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                            >
                              <BookOpen className="size-5 shrink-0" />
                              <div>
                                <div className="text-sm font-semibold">
                                  {t("oldTestamentSearch")}
                                </div>
                                <p className="text-muted-foreground text-sm leading-snug">
                                  {t("oldTestamentSearchDesc")}
                                </p>
                              </div>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                        <li>
                          <NavigationMenuLink asChild>
                            <Link
                              href="/search?source=nt"
                              className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                            >
                              <ScrollText className="size-5 shrink-0" />
                              <div>
                                <div className="text-sm font-semibold">
                                  {t("newTestamentSearch")}
                                </div>
                                <p className="text-muted-foreground text-sm leading-snug">
                                  {t("newTestamentSearchDesc")}
                                </p>
                              </div>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                        <li>
                          <NavigationMenuLink asChild>
                            <Link
                              href="/search?source=apocrypha"
                              className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                            >
                              <FileText className="size-5 shrink-0" />
                              <div>
                                <div className="text-sm font-semibold">{t("apocryphaSearch")}</div>
                                <p className="text-muted-foreground text-sm leading-snug">
                                  {t("apocryphaSearchDesc")}
                                </p>
                              </div>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                        <li>
                          <NavigationMenuLink asChild>
                            <Link
                              href="/keyword-search"
                              className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                            >
                              <SearchIcon className="size-5 shrink-0" />
                              <div>
                                <div className="text-sm font-semibold">{t("wordSearch")}</div>
                                <p className="text-muted-foreground text-sm leading-snug">
                                  {t("wordSearchDesc")}
                                </p>
                              </div>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                      </ul>
                    </NavigationMenuContent>
                  </NavigationMenuItem>

                  {/* Browse Dropdown */}
                  <NavigationMenuItem value="browse" className="text-muted-foreground">
                    <NavigationMenuTrigger className="bg-transparent text-gray-300 hover:bg-white/5 hover:text-white data-[state=open]:bg-white/5">
                      {t("browse")}
                    </NavigationMenuTrigger>
                    <NavigationMenuContent>
                      <ul className="w-80 p-3">
                        <li>
                          <NavigationMenuLink asChild>
                            <Link
                              href="/quran"
                              className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                            >
                              <Book className="size-5 shrink-0" />
                              <div>
                                <div className="text-sm font-semibold">{t("quranBrowse")}</div>
                                <p className="text-muted-foreground text-sm leading-snug">
                                  {t("quranBrowseDesc")}
                                </p>
                              </div>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                        <li>
                          <NavigationMenuLink asChild>
                            <Link
                              href="/old-testament"
                              className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                            >
                              <BookOpen className="size-5 shrink-0" />
                              <div>
                                <div className="text-sm font-semibold">
                                  {t("oldTestamentBrowse")}
                                </div>
                                <p className="text-muted-foreground text-sm leading-snug">
                                  {t("oldTestamentBrowseDesc")}
                                </p>
                              </div>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                        <li>
                          <NavigationMenuLink asChild>
                            <Link
                              href="/new-testament"
                              className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                            >
                              <ScrollText className="size-5 shrink-0" />
                              <div>
                                <div className="text-sm font-semibold">
                                  {t("newTestamentBrowse")}
                                </div>
                                <p className="text-muted-foreground text-sm leading-snug">
                                  {t("newTestamentBrowseDesc")}
                                </p>
                              </div>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                        <li>
                          <NavigationMenuLink asChild>
                            <Link
                              href="/apocrypha"
                              className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                            >
                              <FileText className="size-5 shrink-0" />
                              <div>
                                <div className="text-sm font-semibold">{t("apocrypha")}</div>
                                <p className="text-muted-foreground text-sm leading-snug">
                                  {t("apocryphaDesc")}
                                </p>
                              </div>
                            </Link>
                          </NavigationMenuLink>
                        </li>
                      </ul>
                    </NavigationMenuContent>
                  </NavigationMenuItem>

                  {/* Word Search Link */}
                  <NavigationMenuItem>
                    <Link
                      href="/keyword-search"
                      className={`group hover:bg-accent hover:text-accent-foreground inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors ${
                        isActive("/keyword-search") ? "text-purple-400" : "text-gray-300"
                      }`}
                    >
                      {t("wordSearch")}
                    </Link>
                  </NavigationMenuItem>

                  {/* Compare Link */}
                  <NavigationMenuItem>
                    <Link
                      href="/compare"
                      className={`group hover:bg-accent hover:text-accent-foreground inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors ${
                        isActive("/compare") ? "text-purple-400" : "text-gray-300"
                      }`}
                    >
                      {t("compare")}
                    </Link>
                  </NavigationMenuItem>

                  {/* History Link */}
                  <NavigationMenuItem>
                    <Link
                      href="/history"
                      className={`group hover:bg-accent hover:text-accent-foreground inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors ${
                        isActive("/history") ? "text-purple-400" : "text-gray-300"
                      }`}
                    >
                      {t("history")}
                    </Link>
                  </NavigationMenuItem>

                  {/* Pricing Link */}
                  <NavigationMenuItem>
                    <Link
                      href="/pricing"
                      className={`group hover:bg-accent hover:text-accent-foreground inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors ${
                        isActive("/pricing") ? "text-purple-400" : "text-gray-300"
                      }`}
                    >
                      {t("pricing")}
                      {t("pricing")}
                    </Link>
                  </NavigationMenuItem>
                </NavigationMenuList>
              </NavigationMenu>
            ) : (
              <div className="flex items-center gap-1">
                <Link
                  href="/hub"
                  className={`inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors hover:bg-white/5 hover:text-white ${
                    isActive("/hub") ? "text-purple-400" : "text-gray-300"
                  }`}
                >
                  {t("hub")}
                </Link>
                <Link
                  href="/search"
                  className="inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium text-gray-300 transition-colors hover:bg-white/5 hover:text-white"
                >
                  {t("search")}
                </Link>
                <Link
                  href="/quran"
                  className="inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium text-gray-300 transition-colors hover:bg-white/5 hover:text-white"
                >
                  {t("browse")}
                </Link>
                <Link
                  href="/keyword-search"
                  className={`inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors hover:bg-white/5 hover:text-white ${
                    isActive("/keyword-search") ? "text-purple-400" : "text-gray-300"
                  }`}
                >
                  {t("wordSearch")}
                </Link>
                <Link
                  href="/compare"
                  className={`inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors hover:bg-white/5 hover:text-white ${
                    isActive("/compare") ? "text-purple-400" : "text-gray-300"
                  }`}
                >
                  {t("compare")}
                </Link>
                <Link
                  href="/history"
                  className={`inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors hover:bg-white/5 hover:text-white ${
                    isActive("/history") ? "text-purple-400" : "text-gray-300"
                  }`}
                >
                  {t("history")}
                </Link>
              </div>
            )}
          </div>

          {/* User Menu (Desktop) */}
          <div className="hidden md:flex md:items-center">
            {mounted && user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="text-gray-300 hover:text-white">
                    <User className="mr-2 h-4 w-4" />
                    {user.name}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuLabel>
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium">{user.name}</p>
                      <p className="text-xs text-gray-500">{user.email}</p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem asChild>
                    <Link href="/settings">
                      <Settings className="mr-2 h-4 w-4" />
                      {t("settings")}
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} variant="destructive">
                    <LogOut className="mr-2 h-4 w-4" />
                    {tCommon("logout")}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Link href="/sign-in">
                <Button variant="outline">{tCommon("signIn")}</Button>
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex md:hidden">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="text-gray-300 hover:text-white"
            >
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="border-t border-white/10 md:hidden"
          >
            <div className="space-y-1 px-4 pt-2 pb-3">
              {/* Search Section */}
              <div className="space-y-1">
                <p className="px-3 py-2 text-xs font-semibold tracking-wider text-gray-400 uppercase">
                  {t("search")}
                </p>
                <Link
                  href="/search"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("quranSearch")}
                </Link>
                <Link
                  href="/search?source=ot"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("oldTestamentSearch")}
                </Link>
                <Link
                  href="/search?source=nt"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("newTestamentSearch")}
                </Link>
                <Link
                  href="/search?source=apocrypha"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("apocryphaSearch")}
                </Link>
                <Link
                  href="/keyword-search"
                  className={`block rounded-md px-3 py-2 text-base ${
                    isActive("/keyword-search")
                      ? "bg-purple-500/20 text-purple-400"
                      : "text-gray-300 hover:bg-white/5 hover:text-white"
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("wordSearch")}
                </Link>
              </div>

              {/* Browse Section */}
              <div className="space-y-1 pt-2">
                <p className="px-3 py-2 text-xs font-semibold tracking-wider text-gray-400 uppercase">
                  {t("browse")}
                </p>
                <Link
                  href="/quran"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("quranBrowse")}
                </Link>
                <Link
                  href="/old-testament"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("oldTestamentBrowse")}
                </Link>
                <Link
                  href="/new-testament"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("newTestamentBrowse")}
                </Link>
                <Link
                  href="/apocrypha"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("apocrypha")}
                </Link>
              </div>

              {/* Other Links */}
              <div className="space-y-1 pt-2">
                <Link
                  href="/hub"
                  className={`block rounded-md px-3 py-2 text-base ${
                    isActive("/hub")
                      ? "bg-purple-500/20 text-purple-400"
                      : "text-gray-300 hover:bg-white/5 hover:text-white"
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("hub")}
                </Link>
                <Link
                  href="/compare"
                  className={`block rounded-md px-3 py-2 text-base ${
                    isActive("/compare")
                      ? "bg-purple-500/20 text-purple-400"
                      : "text-gray-300 hover:bg-white/5 hover:text-white"
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("compare")}
                </Link>
                <Link
                  href="/history"
                  className={`block rounded-md px-3 py-2 text-base ${
                    isActive("/history")
                      ? "bg-purple-500/20 text-purple-400"
                      : "text-gray-300 hover:bg-white/5 hover:text-white"
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("history")}
                </Link>
                <Link
                  href="/pricing"
                  className={`block rounded-md px-3 py-2 text-base ${
                    isActive("/pricing")
                      ? "bg-purple-500/20 text-purple-400"
                      : "text-gray-300 hover:bg-white/5 hover:text-white"
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {t("pricing")}
                </Link>
              </div>

              {/* User Section */}
              {mounted && user && (
                <div className="mt-2 space-y-1 border-t border-white/10 pt-2">
                  <div className="px-3 py-2">
                    <p className="text-sm font-medium text-white">{user.name}</p>
                    <p className="text-xs text-gray-500">{user.email}</p>
                  </div>
                  <Link
                    href="/settings"
                    className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Settings className="mr-2 inline h-4 w-4" />
                    {t("settings")}
                  </Link>
                  <button
                    type="button"
                    onClick={() => {
                      handleLogout()
                      setMobileMenuOpen(false)
                    }}
                    className="w-full rounded-md px-3 py-2 text-left text-base text-red-400 hover:bg-red-500/10"
                  >
                    <LogOut className="mr-2 inline h-4 w-4" />
                    {tCommon("logout")}
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  )
}
