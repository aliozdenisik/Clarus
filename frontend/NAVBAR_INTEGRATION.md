# Navbar Component Integration Guide

## Status: ✅ COMPLETE

**Integration Date:** 2026-02-05  
**Component Source:** shadcnblocks.com

---

## What Was Integrated

### New shadcn/ui Components Added

| Component         | Path                                | Purpose                             |
| ----------------- | ----------------------------------- | ----------------------------------- |
| `accordion`       | `components/ui/accordion.tsx`       | Mobile menu collapsible sections    |
| `navigation-menu` | `components/ui/navigation-menu.tsx` | Desktop dropdown navigation         |
| `sheet`           | `components/ui/sheet.tsx`           | Mobile slide-out menu               |
| `label`           | `components/ui/label.tsx`           | Form label component                |
| `navbar`          | `components/ui/navbar.tsx`          | Main navigation component (Navbar1) |

### Dependencies Installed

```bash
npm install @radix-ui/react-accordion @radix-ui/react-navigation-menu @radix-ui/react-label @radix-ui/react-icons
```

**Already Present:**

- `@radix-ui/react-dialog` (used by Sheet)
- `@radix-ui/react-slot` (used by Button)
- `class-variance-authority`
- `lucide-react`

---

## Usage

### Basic Implementation

```tsx
import { Navbar1 } from "@/components/ui/navbar"

export default function Page() {
  return <Navbar1 />
}
```

### Custom Configuration

```tsx
import { Navbar1 } from "@/components/ui/navbar"
import { Book, Sunset, Trees, Zap } from "lucide-react"

const customData = {
  logo: {
    url: "/",
    src: "/logo.svg",
    alt: "Clarus Logo",
    title: "Clarus",
  },
  menu: [
    { title: "Search", url: "/search" },
    { title: "Compare", url: "/compare" },
    {
      title: "Browse",
      url: "#",
      items: [
        {
          title: "Quran",
          description: "Browse Quran verses in Turkish",
          icon: <Book className="size-5 shrink-0" />,
          url: "/quran",
        },
        {
          title: "Old Testament",
          description: "Browse Old Testament passages",
          icon: <Trees className="size-5 shrink-0" />,
          url: "/ot",
        },
        {
          title: "New Testament",
          description: "Browse New Testament passages",
          icon: <Sunset className="size-5 shrink-0" />,
          url: "/nt",
        },
        {
          title: "Apocrypha",
          description: "Browse Apocrypha texts",
          icon: <Zap className="size-5 shrink-0" />,
          url: "/apocrypha",
        },
      ],
    },
    { title: "History", url: "/history" },
  ],
  mobileExtraLinks: [
    { name: "Settings", url: "/settings" },
    { name: "About", url: "/about" },
  ],
  auth: {
    login: { text: "Sign In", url: "/login" },
    signup: { text: "Register", url: "/register" },
  },
}

export default function Page() {
  return <Navbar1 {...customData} />
}
```

---

## Integration Points for Clarus

### Recommended Usage Locations

1. **Root Layout** (`app/layout.tsx`)
   - Add to main layout for global navigation
   - Replace existing header/nav components

2. **Landing Page** (`app/page.tsx`)
   - Use as hero section navigation
   - Connects to auth pages

3. **Application Pages**
   - Search, Compare, History pages
   - Scripture browsing pages

### Clarus-Specific Configuration

```tsx
// Recommended menu structure for Clarus
const clarusMenu = [
  { title: "Home", url: "/" },
  { title: "Search", url: "/search" },
  { title: "Compare", url: "/compare" },
  {
    title: "Scripture",
    url: "#",
    items: [
      {
        title: "Quran",
        description: "Turkish translation with search",
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
  { title: "History", url: "/history" },
]

const clarusAuth = {
  login: { text: "Sign In", url: "/login" },
  signup: { text: "Register", url: "/register" },
}
```

---

## Component Props

### `Navbar1Props`

```typescript
interface Navbar1Props {
  logo?: {
    url: string // Logo click destination
    src: string // Logo image URL
    alt: string // Image alt text
    title: string // Text next to logo
  }
  menu?: MenuItem[] // Navigation menu items
  mobileExtraLinks?: {
    // Additional mobile-only links
    name: string
    url: string
  }[]
  auth?: {
    // Authentication buttons
    login: {
      text: string
      url: string
    }
    signup: {
      text: string
      url: string
    }
  }
}

interface MenuItem {
  title: string
  url: string
  description?: string // For dropdown items
  icon?: JSX.Element // lucide-react icon
  items?: MenuItem[] // Nested dropdown items
}
```

---

## Features

✅ **Responsive Design**

- Desktop: Full horizontal navigation with dropdowns
- Mobile: Hamburger menu with slide-out sheet

✅ **Accessibility**

- Semantic HTML
- ARIA labels
- Keyboard navigation support

✅ **Dark Mode Compatible**

- Uses Tailwind theme variables
- Automatic color adaptation

✅ **Nested Menus**

- Support for dropdown submenus
- Icons + descriptions for menu items

---

## Styling Customization

### Container Width

The navbar uses `container` class from Tailwind. To customize:

```css
/* globals.css */
.container {
  max-width: 1280px; /* Adjust as needed */
  padding: 0 1rem;
}
```

### Mobile Breakpoint

Navbar switches to mobile at `lg` breakpoint (1024px). To change:

```tsx
// Replace lg:flex and lg:hidden classes
<nav className="hidden justify-between xl:flex">  {/* Desktop at 1280px */}
<div className="block xl:hidden">                 {/* Mobile below 1280px */}
```

### Color Scheme

Uses theme tokens from `tailwind.config`:

- `background` - Main background
- `foreground` - Text color
- `muted` - Hover states
- `accent-foreground` - Active states

---

## Testing Recommendations

### Manual Tests

1. **Desktop Navigation**
   - [ ] All menu items clickable
   - [ ] Dropdown menus open/close correctly
   - [ ] Auth buttons functional

2. **Mobile Navigation**
   - [ ] Hamburger menu opens sheet
   - [ ] Accordion sections expand/collapse
   - [ ] Extra links visible
   - [ ] Auth buttons accessible

3. **Responsive Behavior**
   - [ ] Switch between desktop/mobile at 1024px
   - [ ] Logo visible at all sizes
   - [ ] No horizontal scroll

### Automated Tests

```tsx
// __tests__/navbar.test.tsx
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Navbar1 } from "@/components/ui/navbar"

describe("Navbar1", () => {
  it("renders desktop navigation", () => {
    render(<Navbar1 />)
    expect(screen.getByText("Home")).toBeInTheDocument()
  })

  it("renders mobile menu trigger", () => {
    render(<Navbar1 />)
    expect(screen.getByRole("button", { name: /menu/i })).toBeInTheDocument()
  })

  it("opens dropdown on hover", async () => {
    const user = userEvent.setup()
    render(<Navbar1 />)

    const trigger = screen.getByText("Products")
    await user.hover(trigger)

    expect(screen.getByText("Blog")).toBeVisible()
  })
})
```

---

## Known Limitations

1. **No SSR for Navigation Menu**
   - Uses Radix primitives with client-side state
   - May flash on initial render
   - **Solution:** Add loading skeleton

2. **Image Optimization**
   - Uses `<img>` instead of Next.js `<Image>`
   - **Solution:** Replace with `next/image` if needed

3. **No Active State**
   - Doesn't highlight current page
   - **Solution:** Use `usePathname()` to compare URLs

---

## Migration from Existing Navigation

If replacing existing navigation components:

1. **Backup Current Navigation**

   ```bash
   cp components/layout/header.tsx components/layout/header.tsx.bak
   ```

2. **Update Layout**

   ```tsx
   // app/layout.tsx
   import { Navbar1 } from "@/components/ui/navbar"

   export default function RootLayout({ children }) {
     return (
       <html>
         <body>
           <Navbar1 {...clarusConfig} />
           {children}
         </body>
       </html>
     )
   }
   ```

3. **Remove Old Components**
   - Delete unused header/nav files
   - Clean up unused dependencies

---

## Additional Resources

- [shadcn/ui Documentation](https://ui.shadcn.com/docs)
- [Radix UI Primitives](https://www.radix-ui.com/primitives)
- [Lucide Icons](https://lucide.dev)
- [Original Component Source](https://www.shadcnblocks.com)

---

## Support

For issues or questions:

1. Check TypeScript errors with `npm run build`
2. Verify all dependencies installed
3. Review console for runtime errors
4. Consult shadcn/ui docs for component APIs

---

**Integration completed successfully. All components pass TypeScript validation.**
