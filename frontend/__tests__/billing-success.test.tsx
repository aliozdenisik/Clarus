import { describe, expect, it, vi } from "vitest"
import { render, screen } from "./test-utils"
import BillingSuccessPage from "../app/[locale]/billing/success/page"
import trMessages from "../messages/tr.json"

const mockPush = vi.fn()

vi.mock("@/i18n/navigation", () => ({
  useRouter: () => ({ push: mockPush }),
  usePathname: () => "/billing/success",
  Link: ({ children, ...props }: Record<string, unknown>) => (
    <a {...(props as Record<string, unknown>)}>{children as React.ReactNode}</a>
  ),
  redirect: vi.fn(),
}))

vi.mock("lucide-react", () => {
  const Icon = () => <svg aria-hidden="true" />
  return { CheckCircle: Icon, ArrowLeft: Icon }
})

describe("BillingSuccessPage", () => {
  it("renders success heading from i18n", () => {
    render(<BillingSuccessPage />)

    expect(screen.getByText("Welcome to Pro!")).toBeInTheDocument()
  })

  it("renders success description text", () => {
    render(<BillingSuccessPage />)

    expect(
      screen.getByText("Your subscription is now active. Enjoy 500 searches per day.")
    ).toBeInTheDocument()
  })

  it("renders Back to Search button linking to /search", () => {
    render(<BillingSuccessPage />)

    const backBtn = screen.getByRole("button", { name: /Back to Search/i })
    expect(backBtn).toBeInTheDocument()
  })

  it("navigates to /search when Back to Search is clicked", () => {
    render(<BillingSuccessPage />)

    const backBtn = screen.getByRole("button", { name: /Back to Search/i })
    backBtn.click()

    expect(mockPush).toHaveBeenCalledWith("/search")
  })

  it("renders Turkish translations when locale is tr", () => {
    render(<BillingSuccessPage />, "tr", trMessages)

    expect(screen.getByText("Pro'ya ho\u015f geldiniz!")).toBeInTheDocument()
    expect(
      screen.getByText("Aboneliğiniz aktif. Günde 500 arama keyfini çıkarın.")
    ).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /Aramaya Dön/i })).toBeInTheDocument()
  })
})
