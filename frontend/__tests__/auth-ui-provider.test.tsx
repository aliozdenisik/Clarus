import { render, screen } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import type React from "react"

const mockBetterAuthUIProvider = vi.fn()
const mockRefresh = vi.fn()

vi.mock("@daveyplate/better-auth-ui", () => ({
  AuthUIProvider: (props: { children: React.ReactNode }) => {
    mockBetterAuthUIProvider(props)
    return <div data-testid="better-auth-ui-provider">{props.children}</div>
  },
}))

vi.mock("@/lib/auth-client", () => ({
  authClient: {},
}))

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn(),
    refresh: mockRefresh,
  }),
}))

vi.mock("next-intl", () => ({
  useTranslations: () => (key: string) => `translated:${key}`,
}))

vi.mock("next/link", () => ({
  default: ({ children, href, ...props }: { children: React.ReactNode; href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}))

import { AuthUIProvider } from "@/components/providers/auth-ui-provider"

describe("AuthUIProvider", () => {
  beforeEach(() => {
    mockBetterAuthUIProvider.mockClear()
    mockRefresh.mockClear()
  })

  it("passes localized labels to BetterAuthUIProvider", () => {
    render(
      <AuthUIProvider>
        <div>child</div>
      </AuthUIProvider>
    )

    expect(screen.getByText("child")).toBeInTheDocument()
    expect(mockBetterAuthUIProvider).toHaveBeenCalledTimes(1)

    const props = mockBetterAuthUIProvider.mock.calls[0][0]
    expect(props.localization).toBeDefined()
    expect(props.localization.SIGN_IN_ACTION).toBe("translated:SIGN_IN_ACTION")
    expect(props.localization.SIGN_IN_DESCRIPTION).toBe("translated:SIGN_IN_DESCRIPTION")
  })

  it("refreshes router on session change", () => {
    render(
      <AuthUIProvider>
        <div>child</div>
      </AuthUIProvider>
    )

    const props = mockBetterAuthUIProvider.mock.calls[0][0]
    props.onSessionChange()

    expect(mockRefresh).toHaveBeenCalledTimes(1)
  })
})
