'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';
import { Menu, X, ChevronDown, LogOut, Settings, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
} from '@/components/ui/dropdown-menu';
import { useAuth } from '@/lib/auth/auth-context';
import { motion, AnimatePresence } from 'framer-motion';

export default function Navigation() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => pathname === path;

  const handleLogout = async () => {
    await logout();
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
              Sacred Texts
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex md:items-center md:space-x-1">
            {/* Search Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="text-gray-300 hover:text-white">
                  Search <ChevronDown className="ml-1 h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuItem asChild>
                  <Link href="/search">Quran Search</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/search?source=bible">Bible Search</Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Browse Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="text-gray-300 hover:text-white">
                  Browse <ChevronDown className="ml-1 h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start">
                <DropdownMenuItem asChild>
                  <Link href="/quran">Quran (114 Surahs)</Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/old-testament">Old Testament (39 Books)</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/new-testament">New Testament (27 Books)</Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/apocrypha">Apocrypha</Link>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Compare Link */}
            <Link href="/compare">
              <Button
                variant="ghost"
                className={`text-gray-300 hover:text-white ${
                  isActive('/compare') ? 'text-purple-400 border-b-2 border-purple-400 rounded-none' : ''
                }`}
              >
                Compare
              </Button>
            </Link>

            {/* History Link */}
            <Link href="/history">
              <Button
                variant="ghost"
                className={`text-gray-300 hover:text-white ${
                  isActive('/history') ? 'text-purple-400 border-b-2 border-purple-400 rounded-none' : ''
                }`}
              >
                History
              </Button>
            </Link>
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
              <Link href="/login">
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
                  href="/search?source=bible"
                  className="block px-3 py-2 text-base text-gray-300 hover:bg-white/5 hover:text-white rounded-md"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Bible Search
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
                  Apocrypha
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
