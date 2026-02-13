"use client"

import { Navbar1 } from "@/components/ui/navbar"
import { Book, Sunset, Trees, Zap } from "lucide-react"
import { useEffect, useState } from "react"

const demoData = {
  logo: {
    url: "/",
    src: "https://www.shadcnblocks.com/images/block/block-1.svg",
    alt: "Clarus",
    title: "Clarus",
  },
  menu: [
    {
      title: "Home",
      url: "/",
    },
    {
      title: "Scripture",
      url: "#",
      items: [
        {
          title: "Quran",
          description: "Turkish translation with semantic search",
          icon: <Book className="size-5 shrink-0" />,
          url: "/quran",
        },
        {
          title: "Old Testament",
          description: "KJVA English translation",
          icon: <Trees className="size-5 shrink-0" />,
          url: "/ot",
        },
        {
          title: "New Testament",
          description: "KJVA English translation",
          icon: <Sunset className="size-5 shrink-0" />,
          url: "/nt",
        },
        {
          title: "Apocrypha",
          description: "Deuterocanonical texts",
          icon: <Zap className="size-5 shrink-0" />,
          url: "/apocrypha",
        },
      ],
    },
    {
      title: "Features",
      url: "#",
      items: [
        {
          title: "Search",
          description: "Hybrid semantic + keyword search",
          icon: <Zap className="size-5 shrink-0" />,
          url: "/search",
        },
        {
          title: "Compare",
          description: "Multi-agent comparative analysis",
          icon: <Sunset className="size-5 shrink-0" />,
          url: "/compare",
        },
        {
          title: "History",
          description: "View your search history",
          icon: <Trees className="size-5 shrink-0" />,
          url: "/history",
        },
        {
          title: "Settings",
          description: "Customize your experience",
          icon: <Book className="size-5 shrink-0" />,
          url: "/settings",
        },
      ],
    },
    {
      title: "Search",
      url: "/search",
    },
    {
      title: "Compare",
      url: "/compare",
    },
  ],
  mobileExtraLinks: [
    { name: "About", url: "/about" },
    { name: "Contact", url: "/contact" },
    { name: "Privacy", url: "/privacy" },
    { name: "Terms", url: "/terms" },
  ],
  auth: {
    login: { text: "Sign In", url: "/sign-in" },
    signup: { text: "Register", url: "/sign-up" },
  },
}

export default function NavbarDemoPage() {
  const [viewportWidth, setViewportWidth] = useState<string>("")

  useEffect(() => {
    const updateWidth = () => {
      setViewportWidth(`${window.innerWidth}px`)
    }

    updateWidth()
    window.addEventListener("resize", updateWidth)
    return () => window.removeEventListener("resize", updateWidth)
  }, [])

  return (
    <div className="bg-background min-h-screen">
      <Navbar1 {...demoData} />

      <main className="container py-12">
        <div className="mx-auto max-w-3xl space-y-8">
          <div>
            <h1 className="mb-4 text-4xl font-bold">Navbar Component Demo</h1>
            <p className="text-muted-foreground text-lg">
              This page demonstrates the Navbar1 component with Clarus-specific configuration.
            </p>
          </div>

          <div className="space-y-4 rounded-lg border p-6">
            <h2 className="text-2xl font-semibold">Features Demonstrated</h2>
            <ul className="text-muted-foreground list-inside list-disc space-y-2">
              <li>Desktop navigation with dropdown menus</li>
              <li>Mobile-responsive hamburger menu</li>
              <li>Nested menu items with icons and descriptions</li>
              <li>Authentication buttons (Sign In / Register)</li>
              <li>Mobile-only extra links in slide-out sheet</li>
            </ul>
          </div>

          <div className="space-y-4 rounded-lg border p-6">
            <h2 className="text-2xl font-semibold">Testing Instructions</h2>
            <div className="text-muted-foreground space-y-3">
              <p>
                <strong>Desktop (≥1024px):</strong>
              </p>
              <ul className="ml-4 list-inside list-disc space-y-1">
                <li>
                  Hover over &quot;Scripture&quot; or &quot;Features&quot; to see dropdown menus
                </li>
                <li>Click on menu items to navigate</li>
                <li>Click &quot;Sign In&quot; or &quot;Register&quot; buttons</li>
              </ul>

              <p className="pt-2">
                <strong>Mobile (&lt;1024px):</strong>
              </p>
              <ul className="ml-4 list-inside list-disc space-y-1">
                <li>Click hamburger menu icon (three lines)</li>
                <li>Expand &quot;Scripture&quot; or &quot;Features&quot; accordion sections</li>
                <li>Scroll to see mobile extra links (About, Contact, etc.)</li>
                <li>Click authentication buttons at bottom</li>
              </ul>
            </div>
          </div>

          <div className="bg-muted/50 space-y-4 rounded-lg border p-6">
            <h2 className="text-2xl font-semibold">Responsive Breakpoint</h2>
            <p className="text-muted-foreground">
              The navbar switches between desktop and mobile views at{" "}
              <code className="bg-background rounded px-2 py-1">1024px</code> width. Resize your
              browser window to see the transition.
            </p>
            <p className="text-muted-foreground text-sm">
              Current viewport width:{" "}
              <span className="font-mono">{viewportWidth || "Calculating..."}</span>
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}
