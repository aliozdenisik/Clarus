"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"
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

  const isActive = (path: string) => pathname === path

  const handleLogout = async () => {
    await signOut()
  }

  // Don't show navigation on login/register pages
  if (pathname === "/login" || pathname === "/register" || pathname === "/") {
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
            <NavigationMenu>
              <NavigationMenuList>
                {/* Search Dropdown */}
                <NavigationMenuItem className="text-muted-foreground">
                  <NavigationMenuTrigger className="bg-transparent text-gray-300 hover:bg-white/5 hover:text-white data-[state=open]:bg-white/5">
                    Search
                  </NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <ul className="w-80 p-3">
                      <NavigationMenuLink asChild>
                        <Link
                          href="/search"
                          className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                        >
                          <Book className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Quran Search</div>
                            <p className="text-muted-foreground text-sm leading-snug">
                              Semantic search across Turkish Quran translation
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/search?source=ot"
                          className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                        >
                          <BookOpen className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Old Testament Search</div>
                            <p className="text-muted-foreground text-sm leading-snug">
                              Search through 39 books of the Old Testament
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/search?source=nt"
                          className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                        >
                          <ScrollText className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">New Testament Search</div>
                            <p className="text-muted-foreground text-sm leading-snug">
                              Search the Gospels, Acts, and Epistles
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/search?source=apocrypha"
                          className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                        >
                          <FileText className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Apocrypha Search</div>
                            <p className="text-muted-foreground text-sm leading-snug">
                              Explore deuterocanonical texts and writings
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/keyword-search"
                          className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                        >
                          <SearchIcon className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Word Search</div>
                            <p className="text-muted-foreground text-sm leading-snug">
                              Morphological keyword search with roots
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                    </ul>
                  </NavigationMenuContent>
                </NavigationMenuItem>

                {/* Browse Dropdown */}
                <NavigationMenuItem className="text-muted-foreground">
                  <NavigationMenuTrigger className="bg-transparent text-gray-300 hover:bg-white/5 hover:text-white data-[state=open]:bg-white/5">
                    Browse
                  </NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <ul className="w-80 p-3">
                      <NavigationMenuLink asChild>
                        <Link
                          href="/quran"
                          className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                        >
                          <Book className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Quran</div>
                            <p className="text-muted-foreground text-sm leading-snug">
                              Browse all 114 Surahs with translations
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/old-testament"
                          className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                        >
                          <BookOpen className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Old Testament</div>
                            <p className="text-muted-foreground text-sm leading-snug">
                              39 books from Genesis to Malachi
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/new-testament"
                          className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                        >
                          <ScrollText className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">New Testament</div>
                            <p className="text-muted-foreground text-sm leading-snug">
                              27 books including Gospels and Epistles
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/apocrypha"
                          className="hover:bg-accent hover:text-accent-foreground flex gap-4 rounded-md p-3 leading-none no-underline transition-colors outline-none select-none"
                        >
                          <FileText className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Apocrypha</div>
                            <p className="text-muted-foreground text-sm leading-snug">
                              14 deuterocanonical books and texts
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                    </ul>
                  </NavigationMenuContent>
                </NavigationMenuItem>

                {/* Word Search Link */}
                <Link
                  href="/keyword-search"
                  className={`group hover:bg-accent hover:text-accent-foreground inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors ${
                    isActive("/keyword-search") ? "text-purple-400" : "text-gray-300"
                  }`}
                >
                  Word Search
                </Link>

                {/* Compare Link */}
                <Link
                  href="/compare"
                  className={`group hover:bg-accent hover:text-accent-foreground inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors ${
                    isActive("/compare") ? "text-purple-400" : "text-gray-300"
                  }`}
                >
                  Compare
                </Link>

                {/* History Link */}
                <Link
                  href="/history"
                  className={`group hover:bg-accent hover:text-accent-foreground inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors ${
                    isActive("/history") ? "text-purple-400" : "text-gray-300"
                  }`}
                >
                  History
                </Link>
              </NavigationMenuList>
            </NavigationMenu>
          </div>

          {/* User Menu (Desktop) */}
          <div className="hidden md:flex md:items-center">
            {user ? (
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
                      Settings
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} variant="destructive">
                    <LogOut className="mr-2 h-4 w-4" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Link href="/sign-in">
                <Button variant="outline">Sign In</Button>
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
                  Search
                </p>
                <Link
                  href="/search"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Quran Search
                </Link>
                <Link
                  href="/search?source=ot"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Old Testament Search
                </Link>
                <Link
                  href="/search?source=nt"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  New Testament Search
                </Link>
                <Link
                  href="/search?source=apocrypha"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Apocrypha Search
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
                  Word Search
                </Link>
              </div>

              {/* Browse Section */}
              <div className="space-y-1 pt-2">
                <p className="px-3 py-2 text-xs font-semibold tracking-wider text-gray-400 uppercase">
                  Browse
                </p>
                <Link
                  href="/quran"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Quran (114 Surahs)
                </Link>
                <Link
                  href="/old-testament"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Old Testament (39 Books)
                </Link>
                <Link
                  href="/new-testament"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  New Testament (27 Books)
                </Link>
                <Link
                  href="/apocrypha"
                  className="block rounded-md px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Apocrypha (14 Books)
                </Link>
              </div>

              {/* Other Links */}
              <div className="space-y-1 pt-2">
                <Link
                  href="/compare"
                  className={`block rounded-md px-3 py-2 text-base ${
                    isActive("/compare")
                      ? "bg-purple-500/20 text-purple-400"
                      : "text-gray-300 hover:bg-white/5 hover:text-white"
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Compare
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
                  History
                </Link>
              </div>

              {/* User Section */}
              {user && (
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
                    Settings
                  </Link>
                  <button
                    onClick={() => {
                      handleLogout()
                      setMobileMenuOpen(false)
                    }}
                    className="w-full rounded-md px-3 py-2 text-left text-base text-red-400 hover:bg-red-500/10"
                  >
                    <LogOut className="mr-2 inline h-4 w-4" />
                    Logout
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
