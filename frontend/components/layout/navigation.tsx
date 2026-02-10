'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { Menu, X, LogOut, Settings, User, Book, BookOpen, ScrollText, FileText, Search as SearchIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from '@/components/ui/navigation-menu';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useSession, signOut } from '@/lib/auth-client';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navigation() {
  const pathname = usePathname();
  const { data: session } = useSession();
  const user = session?.user;
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => pathname === path;

  const handleLogout = async () => {
    await signOut();
  };

  // Don't show navigation on login/register pages
  if (pathname === '/login' || pathname === '/register' || pathname === '/') {
    return null;
  }

  return (
    <nav className="border-b border-white/10 bg-black/50 backdrop-blur-xl sticky top-0 z-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="text-xl font-bold text-white hover:text-purple-400 transition-colors">
              Clarus
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-1">
            <NavigationMenu>
              <NavigationMenuList>
                {/* Search Dropdown */}
                <NavigationMenuItem className="text-muted-foreground">
                  <NavigationMenuTrigger className="text-gray-300 hover:text-white bg-transparent hover:bg-white/5 data-[state=open]:bg-white/5">
                    Search
                  </NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <ul className="w-80 p-3">
                      <NavigationMenuLink asChild>
                        <Link
                          href="/search"
                          className="flex select-none gap-4 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
                        >
                          <Book className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Quran Search</div>
                            <p className="text-sm leading-snug text-muted-foreground">
                              Semantic search across Turkish Quran translation
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/search?source=ot"
                          className="flex select-none gap-4 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
                        >
                          <BookOpen className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Old Testament Search</div>
                            <p className="text-sm leading-snug text-muted-foreground">
                              Search through 39 books of the Old Testament
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/search?source=nt"
                          className="flex select-none gap-4 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
                        >
                          <ScrollText className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">New Testament Search</div>
                            <p className="text-sm leading-snug text-muted-foreground">
                              Search the Gospels, Acts, and Epistles
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/search?source=apocrypha"
                          className="flex select-none gap-4 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
                        >
                          <FileText className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Apocrypha Search</div>
                            <p className="text-sm leading-snug text-muted-foreground">
                              Explore deuterocanonical texts and writings
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/keyword-search"
                          className="flex select-none gap-4 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
                        >
                          <SearchIcon className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Word Search</div>
                            <p className="text-sm leading-snug text-muted-foreground">
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
                  <NavigationMenuTrigger className="text-gray-300 hover:text-white bg-transparent hover:bg-white/5 data-[state=open]:bg-white/5">
                    Browse
                  </NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <ul className="w-80 p-3">
                      <NavigationMenuLink asChild>
                        <Link
                          href="/quran"
                          className="flex select-none gap-4 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
                        >
                          <Book className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Quran</div>
                            <p className="text-sm leading-snug text-muted-foreground">
                              Browse all 114 Surahs with translations
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/old-testament"
                          className="flex select-none gap-4 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
                        >
                          <BookOpen className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Old Testament</div>
                            <p className="text-sm leading-snug text-muted-foreground">
                              39 books from Genesis to Malachi
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/new-testament"
                          className="flex select-none gap-4 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
                        >
                          <ScrollText className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">New Testament</div>
                            <p className="text-sm leading-snug text-muted-foreground">
                              27 books including Gospels and Epistles
                            </p>
                          </div>
                        </Link>
                      </NavigationMenuLink>
                      <NavigationMenuLink asChild>
                        <Link
                          href="/apocrypha"
                          className="flex select-none gap-4 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground"
                        >
                          <FileText className="size-5 shrink-0" />
                          <div>
                            <div className="text-sm font-semibold">Apocrypha</div>
                            <p className="text-sm leading-snug text-muted-foreground">
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
                  className={`group inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground ${
                    isActive('/keyword-search') ? 'text-purple-400' : 'text-gray-300'
                  }`}
                >
                  Word Search
                </Link>

                {/* Compare Link */}
                <Link
                  href="/compare"
                  className={`group inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground ${
                    isActive('/compare') ? 'text-purple-400' : 'text-gray-300'
                  }`}
                >
                  Compare
                </Link>

                {/* History Link */}
                <Link
                  href="/history"
                  className={`group inline-flex h-10 w-max items-center justify-center rounded-md bg-transparent px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground ${
                    isActive('/history') ? 'text-purple-400' : 'text-gray-300'
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
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden border-t border-white/10"
          >
            <div className="space-y-1 px-4 pb-3 pt-2">
              {/* Search Section */}
              <div className="space-y-1">
                <p className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Search
                </p>
                <Link
                  href="/search"
                  className="block px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Quran Search
                </Link>
                <Link
                  href="/search?source=ot"
                  className="block px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Old Testament Search
                </Link>
                <Link
                  href="/search?source=nt"
                  className="block px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  New Testament Search
                </Link>
                <Link
                  href="/search?source=apocrypha"
                  className="block px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Apocrypha Search
                </Link>
                <Link
                  href="/keyword-search"
                  className={`block px-3 py-2 text-base rounded-md ${
                    isActive('/keyword-search')
                      ? 'bg-purple-500/20 text-purple-400'
                      : 'text-gray-300 hover:bg-white/5 hover:text-white'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Word Search
                </Link>
              </div>

              {/* Browse Section */}
              <div className="space-y-1 pt-2">
                <p className="px-3 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Browse
                </p>
                <Link
                  href="/quran"
                  className="block px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Quran (114 Surahs)
                </Link>
                <Link
                  href="/old-testament"
                  className="block px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Old Testament (39 Books)
                </Link>
                <Link
                  href="/new-testament"
                  className="block px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  New Testament (27 Books)
                </Link>
                <Link
                  href="/apocrypha"
                  className="block px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Apocrypha (14 Books)
                </Link>
              </div>

              {/* Other Links */}
              <div className="space-y-1 pt-2">
                <Link
                  href="/compare"
                  className={`block px-3 py-2 text-base rounded-md ${
                    isActive('/compare')
                      ? 'bg-purple-500/20 text-purple-400'
                      : 'text-gray-300 hover:bg-white/5 hover:text-white'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Compare
                </Link>
                <Link
                  href="/history"
                  className={`block px-3 py-2 text-base rounded-md ${
                    isActive('/history')
                      ? 'bg-purple-500/20 text-purple-400'
                      : 'text-gray-300 hover:bg-white/5 hover:text-white'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  History
                </Link>
              </div>

              {/* User Section */}
              {user && (
                <div className="space-y-1 pt-2 border-t border-white/10 mt-2">
                  <div className="px-3 py-2">
                    <p className="text-sm font-medium text-white">{user.name}</p>
                    <p className="text-xs text-gray-500">{user.email}</p>
                  </div>
                  <Link
                    href="/settings"
                    className="block px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white rounded-md"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <Settings className="inline mr-2 h-4 w-4" />
                    Settings
                  </Link>
                  <button
                    onClick={() => {
                      handleLogout();
                      setMobileMenuOpen(false);
                    }}
                    className="w-full text-left px-3 py-2 text-base text-red-400 hover:bg-red-500/10 rounded-md"
                  >
                    <LogOut className="inline mr-2 h-4 w-4" />
                    Logout
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
