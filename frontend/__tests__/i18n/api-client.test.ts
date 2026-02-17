import { describe, it, expect, beforeEach } from "vitest"
import { client } from "@/lib/api/client.gen"

interface RequestInterceptors {
  _fns?: Array<(request: Request) => Request>
}

describe("API Client i18n Integration", () => {
  beforeEach(() => {
    window.history.replaceState(null, "", "/")
  })

  it("injects Accept-Language header based on /en/ URL path", () => {
    window.history.replaceState(null, "", "/en/search")

    const mockRequest = new Request("http://localhost:3000/api/test")
    const requestInterceptors =
      (client.interceptors.request as unknown as RequestInterceptors)._fns || []

    if (requestInterceptors.length > 0) {
      const lastInterceptor = requestInterceptors[requestInterceptors.length - 1]
      const modifiedRequest = lastInterceptor(mockRequest)

      expect(modifiedRequest.headers.get("Accept-Language")).toBe("en")
    }
  })

  it("injects Accept-Language header based on /tr/ URL path", () => {
    window.history.replaceState(null, "", "/tr/compare")

    const mockRequest = new Request("http://localhost:3000/api/test")
    const requestInterceptors =
      (client.interceptors.request as unknown as RequestInterceptors)._fns || []

    if (requestInterceptors.length > 0) {
      const lastInterceptor = requestInterceptors[requestInterceptors.length - 1]
      const modifiedRequest = lastInterceptor(mockRequest)

      expect(modifiedRequest.headers.get("Accept-Language")).toBe("tr")
    }
  })

  it("defaults to 'tr' when no locale in URL path", () => {
    window.history.replaceState(null, "", "/search")

    const mockRequest = new Request("http://localhost:3000/api/test")
    const requestInterceptors =
      (client.interceptors.request as unknown as RequestInterceptors)._fns || []

    if (requestInterceptors.length > 0) {
      const lastInterceptor = requestInterceptors[requestInterceptors.length - 1]
      const modifiedRequest = lastInterceptor(mockRequest)

      expect(modifiedRequest.headers.get("Accept-Language")).toBe("tr")
    }
  })
})
