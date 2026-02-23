import { describe, expect, it, vi, beforeEach } from "vitest"
import { render, screen, fireEvent } from "./test-utils"
import PricingPage from "../app/[locale]/pricing/page"
import trMessages from "../messages/tr.json"
vi.mock("@/i18n/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/pricing",
  Link: ({ children, ...props }: Record<string, unknown>) => (
    <a {...(props as Record<string, unknown>)}>{children as React.ReactNode}</a>
  ),
  redirect: vi.fn(),
}))
vi.mock("@/lib/auth-client", () => ({
  useSession: vi.fn(() => ({ data: null, isPending: false })),
  authClient: {
    checkout: vi.fn(),
    customer: { portal: vi.fn() },
  },
}))
vi.mock("@/lib/logger", () => ({
  logger: { error: vi.fn(), info: vi.fn(), warn: vi.fn(), debug: vi.fn() },
}))
vi.mock("lucide-react", () => {
  const Icon = () => <svg aria-hidden="true" />
  return { Check: Icon, CreditCard: Icon, Lock: Icon }
})

import * as AuthClient from "@/lib/auth-client"
describe("PricingPage", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })
  it("renders three plan cards (Free, Starter, and Pro)", () => {
    render(<PricingPage />)
    expect(screen.getByText("Free")).toBeInTheDocument()
    expect(screen.getByText("Starter")).toBeInTheDocument()
    expect(screen.getByText("Pro")).toBeInTheDocument()
  })
  it("renders page title and subtitle from i18n", () => {
    render(<PricingPage />)
    expect(screen.getByRole("heading", { name: "Pricing" })).toBeInTheDocument()
    expect(screen.getByText("Choose the plan that works for you")).toBeInTheDocument()
  })
  it("shows Current Plan badge on Free card", () => {
    render(<PricingPage />)
    const currentPlanElements = screen.getAllByText("Current Plan")
    expect(currentPlanElements.length).toBeGreaterThanOrEqual(1)
  })
  it("shows login-required message and upgrade button when not logged in", () => {
    render(<PricingPage />)
    // Now there are two "Please sign in to subscribe" messages (one for Starter, one for Pro)
    const signInMessages = screen.getAllByText("Please sign in to subscribe")
    expect(signInMessages.length).toBeGreaterThanOrEqual(2)
    // Now there are two upgrade buttons (Starter and Pro)
    const upgradeButtons = screen.getAllByRole("button", { name: /Upgrade/i })
    expect(upgradeButtons.length).toBeGreaterThanOrEqual(2)
  })
  it("does not call checkout when unauthenticated user clicks upgrade", () => {
    vi.mocked(AuthClient.useSession).mockReturnValue({ data: null, isPending: false } as never)
    render(<PricingPage />)
    const upgradeBtn = screen.getByRole("button", { name: /Upgrade to Pro/i })
    fireEvent.click(upgradeBtn)
    expect(AuthClient.authClient.checkout).not.toHaveBeenCalled()
  })
  it("shows checkout and manage billing buttons when logged in", () => {
    vi.mocked(AuthClient.useSession).mockReturnValue({
      data: { user: { id: "user_1", name: "Test User", email: "test@example.com" } },
      isPending: false,
    } as never)
    render(<PricingPage />)
    // There are now two upgrade buttons (Starter and Pro)
    const upgradeButtons = screen.getAllByRole("button", { name: /Upgrade/i })
    expect(upgradeButtons.length).toBeGreaterThanOrEqual(2)
    // There are now two "Manage Billing" links
    const manageBillingLinks = screen.getAllByText("Manage Billing")
    expect(manageBillingLinks.length).toBeGreaterThanOrEqual(2)
  })
  it("calls authClient.checkout with slug 'pro' when logged in and upgrade clicked", () => {
    vi.mocked(AuthClient.useSession).mockReturnValue({
      data: { user: { id: "user_1", name: "Test User", email: "test@example.com" } },
      isPending: false,
    } as never)
    vi.mocked(AuthClient.authClient.checkout).mockResolvedValue(undefined as never)
    render(<PricingPage />)
    const upgradeBtn = screen.getByRole("button", { name: /Upgrade to Pro/i })
    fireEvent.click(upgradeBtn)
    expect(AuthClient.authClient.checkout).toHaveBeenCalledWith({ slug: "pro" })
  })
  it("renders Turkish translations when locale is tr", () => {
    render(<PricingPage />, "tr", trMessages)
    expect(screen.getByText("Size uygun plan\u0131 se\u00e7in")).toBeInTheDocument()
    expect(screen.getByText("\u00dccretsiz")).toBeInTheDocument()
  })
})
