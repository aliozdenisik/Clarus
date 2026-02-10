import { describe, it, expect } from "vitest"
import { render } from "@testing-library/react"
import { OfflineBannerWrapper } from "@/components/layout/offline-banner"

describe("OfflineBannerWrapper", () => {
  it("returns null (feature removed during Better Auth migration)", () => {
    const { container } = render(<OfflineBannerWrapper />)

    expect(container.firstChild).toBeNull()
  })
})
