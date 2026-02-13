import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { renderHook, act } from "@testing-library/react"
import { useSSE } from "@/lib/hooks/use-sse"

// Mock toast notifications
vi.mock("sonner", () => ({
  toast: {
    info: vi.fn(),
    error: vi.fn(),
  },
}))

// Store instances for testing
let mockEventSourceInstances: MockEventSource[] = []

// Mock EventSource globally (jsdom doesn't have it)
class MockEventSource {
  url: string
  withCredentials: boolean
  readyState: number = 0 // CONNECTING
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(url: string, options?: { withCredentials?: boolean }) {
    this.url = url
    this.withCredentials = options?.withCredentials ?? false
    mockEventSourceInstances.push(this)
  }

  close() {
    this.readyState = 2 // CLOSED
  }

  static readonly CONNECTING = 0
  static readonly OPEN = 1
  static readonly CLOSED = 2
}

// Track constructor calls
let constructorCalls: Array<{ url: string; options?: { withCredentials?: boolean } }> = []

// Create a constructor wrapper
const MockEventSourceConstructor = function (url: string, options?: { withCredentials?: boolean }) {
  constructorCalls.push({ url, options })
  return new MockEventSource(url, options)
} as unknown as typeof EventSource

// Copy static properties
Object.defineProperties(MockEventSourceConstructor, {
  CONNECTING: { value: 0 },
  OPEN: { value: 1 },
  CLOSED: { value: 2 },
})

global.EventSource = MockEventSourceConstructor

describe("useSSE", () => {
  beforeEach(() => {
    mockEventSourceInstances = []
    constructorCalls = []
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe("initial state", () => {
    it("should initialize with empty data, no streaming, and no error", () => {
      const { result } = renderHook(() => useSSE())

      expect(result.current.data).toEqual([])
      expect(result.current.isStreaming).toBe(false)
      expect(result.current.error).toBeNull()
    })

    it("should provide startStream and stopStream functions", () => {
      const { result } = renderHook(() => useSSE())

      expect(typeof result.current.startStream).toBe("function")
      expect(typeof result.current.stopStream).toBe("function")
    })
  })

  describe("startStream", () => {
    it("should create EventSource with correct URL and credentials", () => {
      const { result } = renderHook(() => useSSE())
      const testUrl = "/api/stream/search?q=test"

      act(() => {
        result.current.startStream(testUrl)
      })

      expect(constructorCalls).toHaveLength(1)
      expect(constructorCalls[0].url).toBe(testUrl + "&lang=tr")
      expect(constructorCalls[0].options?.withCredentials).toBe(true)
    })

    it("should set isStreaming to true", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      expect(result.current.isStreaming).toBe(true)
    })

    it("should reset data and error state on new stream", () => {
      const { result } = renderHook(() => useSSE())

      // First stream with some data
      act(() => {
        result.current.startStream("/api/stream/search?q=test1")
      })

      // Simulate receiving a message
      const mockEventSource = mockEventSourceInstances[0]
      act(() => {
        mockEventSource.onmessage?.({
          data: JSON.stringify({ type: "token", content: "hello" }),
        } as MessageEvent)
      })

      expect(result.current.data).toHaveLength(1)

      // Start new stream
      act(() => {
        result.current.startStream("/api/stream/search?q=test2")
      })

      expect(result.current.data).toEqual([])
      expect(result.current.error).toBeNull()
    })
  })

  describe("message parsing", () => {
    it("should parse JSON messages and append to data array", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]
      const testMessage = { type: "token", content: "hello world" }

      act(() => {
        mockEventSource.onmessage?.({
          data: JSON.stringify(testMessage),
        } as MessageEvent)
      })

      expect(result.current.data).toHaveLength(1)
      expect(result.current.data[0]).toEqual(testMessage)
    })

    it("should handle multiple messages in sequence", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]
      const messages = [
        { type: "token", content: "hello" },
        { type: "token", content: " world" },
        { type: "section", content: "section 1" },
      ]

      act(() => {
        messages.forEach((msg) => {
          mockEventSource.onmessage?.({
            data: JSON.stringify(msg),
          } as MessageEvent)
        })
      })

      expect(result.current.data).toHaveLength(3)
      expect(result.current.data).toEqual(messages)
    })

    it("should handle messages with verse_details", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]
      const messageWithDetails = {
        type: "token",
        content: "verse text",
        verse_details: { book: "Genesis", chapter: 1, verse: 1 },
      }

      act(() => {
        mockEventSource.onmessage?.({
          data: JSON.stringify(messageWithDetails),
        } as MessageEvent)
      })

      expect(result.current.data[0]).toEqual(messageWithDetails)
      expect(result.current.data[0].verse_details).toBeDefined()
    })

    it("should handle invalid JSON gracefully", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]

      act(() => {
        mockEventSource.onmessage?.({
          data: "invalid json {",
        } as MessageEvent)
      })

      expect(result.current.error).toBeTruthy()
      expect(result.current.isStreaming).toBe(false)
    })
  })

  describe("stream completion", () => {
    it('should close stream when message type is "complete"', () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]

      act(() => {
        mockEventSource.onmessage?.({
          data: JSON.stringify({ type: "complete", content: "done" }),
        } as MessageEvent)
      })

      expect(result.current.isStreaming).toBe(false)
    })

    it("should still append complete message to data before closing", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]

      act(() => {
        mockEventSource.onmessage?.({
          data: JSON.stringify({ type: "token", content: "hello" }),
        } as MessageEvent)
        mockEventSource.onmessage?.({
          data: JSON.stringify({ type: "complete" }),
        } as MessageEvent)
      })

      expect(result.current.data).toHaveLength(2)
      expect(result.current.data[1].type).toBe("complete")
    })
  })

  describe("onopen handler", () => {
    it("should clear error state on successful connection", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]

      // Trigger onopen
      act(() => {
        mockEventSource.onopen?.({} as Event)
      })

      expect(result.current.error).toBeNull()
    })
  })

  describe("exponential backoff", () => {
    it("should retry with 1s delay on first error", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]

      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      // Should have scheduled a timeout for 1s (2^0 * 1000)
      expect(vi.getTimerCount()).toBe(1)

      // Advance time by 1s
      act(() => {
        vi.advanceTimersByTime(1000)
      })

      // Should have created new EventSource
      expect(constructorCalls).toHaveLength(2)
    })

    it("should retry with 2s delay on second error", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      let mockEventSource = mockEventSourceInstances[0]

      // First error
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      act(() => {
        vi.advanceTimersByTime(1000)
      })

      // Second error
      mockEventSource = mockEventSourceInstances[1]
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      // Should have scheduled a timeout for 2s (2^1 * 1000)
      const timers = vi.getTimerCount()
      expect(timers).toBeGreaterThan(0)

      act(() => {
        vi.advanceTimersByTime(2000)
      })

      // Should have created third EventSource
      expect(constructorCalls).toHaveLength(3)
    })

    it("should retry with 4s delay on third error", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      let mockEventSource = mockEventSourceInstances[0]

      // First error
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      act(() => {
        vi.advanceTimersByTime(1000)
      })

      // Second error
      mockEventSource = mockEventSourceInstances[1]
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      act(() => {
        vi.advanceTimersByTime(2000)
      })

      // Third error
      mockEventSource = mockEventSourceInstances[2]
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      // Should have scheduled a timeout for 4s (2^2 * 1000)
      const timers = vi.getTimerCount()
      expect(timers).toBeGreaterThan(0)

      act(() => {
        vi.advanceTimersByTime(4000)
      })

      // Should have created fourth EventSource
      expect(constructorCalls).toHaveLength(4)
    })
  })

  describe("max retries", () => {
    it("should stop retrying after MAX_RETRIES (3) attempts", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      let mockEventSource = mockEventSourceInstances[0]

      // First error
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      act(() => {
        vi.advanceTimersByTime(1000)
      })

      // Second error
      mockEventSource = mockEventSourceInstances[1]
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      act(() => {
        vi.advanceTimersByTime(2000)
      })

      // Third error
      mockEventSource = mockEventSourceInstances[2]
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      act(() => {
        vi.advanceTimersByTime(4000)
      })

      // Fourth error - should NOT retry
      mockEventSource = mockEventSourceInstances[3]
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      // Should have error state set
      expect(result.current.error).toBeTruthy()
      expect(result.current.error).toContain("3 retries")
      expect(result.current.isStreaming).toBe(false)

      // Should NOT create a 5th EventSource
      expect(constructorCalls).toHaveLength(4)
    })

    it("should set error message after max retries", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      let mockEventSource = mockEventSourceInstances[0]

      // Trigger 3 errors
      for (let i = 0; i < 3; i++) {
        act(() => {
          mockEventSource.readyState = 2 // CLOSED
          mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
        })

        const delay = Math.pow(2, i) * 1000
        act(() => {
          vi.advanceTimersByTime(delay)
        })

        if (i < 2) {
          mockEventSource = mockEventSourceInstances[i + 1]
        }
      }

      // Fourth error
      mockEventSource = mockEventSourceInstances[3]
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      expect(result.current.error).toBe(
        "Connection failed after 3 retries. Falling back to standard request."
      )
    })
  })

  describe("stopStream", () => {
    it("should close EventSource", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]

      act(() => {
        result.current.stopStream()
      })

      expect(mockEventSource.readyState).toBe(2) // CLOSED
    })

    it("should set isStreaming to false", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      expect(result.current.isStreaming).toBe(true)

      act(() => {
        result.current.stopStream()
      })

      expect(result.current.isStreaming).toBe(false)
    })

    it("should handle stopStream when no stream is active", () => {
      const { result } = renderHook(() => useSSE())

      // Should not throw
      expect(() => {
        act(() => {
          result.current.stopStream()
        })
      }).not.toThrow()

      expect(result.current.isStreaming).toBe(false)
    })

    it("should clear EventSource reference", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      act(() => {
        result.current.stopStream()
      })

      // Starting a new stream should create a fresh EventSource
      act(() => {
        result.current.startStream("/api/stream/search?q=test2")
      })

      expect(constructorCalls).toHaveLength(2)
    })
  })

  describe("state transitions", () => {
    it("should transition from idle to streaming to complete", () => {
      const { result } = renderHook(() => useSSE())

      // Initial state
      expect(result.current.isStreaming).toBe(false)

      // Start streaming
      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      expect(result.current.isStreaming).toBe(true)

      // Receive complete message
      const mockEventSource = mockEventSourceInstances[0]
      act(() => {
        mockEventSource.onmessage?.({
          data: JSON.stringify({ type: "complete" }),
        } as MessageEvent)
      })

      expect(result.current.isStreaming).toBe(false)
    })

    it("should transition from streaming to error on parse failure", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      expect(result.current.isStreaming).toBe(true)
      expect(result.current.error).toBeNull()

      const mockEventSource = mockEventSourceInstances[0]
      act(() => {
        mockEventSource.onmessage?.({
          data: "invalid json",
        } as MessageEvent)
      })

      expect(result.current.isStreaming).toBe(false)
      expect(result.current.error).toBeTruthy()
    })

    it("should maintain data across state transitions", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]

      act(() => {
        mockEventSource.onmessage?.({
          data: JSON.stringify({ type: "token", content: "hello" }),
        } as MessageEvent)
        mockEventSource.onmessage?.({
          data: JSON.stringify({ type: "token", content: " world" }),
        } as MessageEvent)
      })

      expect(result.current.data).toHaveLength(2)

      act(() => {
        mockEventSource.onmessage?.({
          data: JSON.stringify({ type: "complete" }),
        } as MessageEvent)
      })

      // Data should still be there after completion
      expect(result.current.data).toHaveLength(3)
    })
  })

  describe("error handling", () => {
    it("should handle message parse errors with descriptive message", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]

      act(() => {
        mockEventSource.onmessage?.({
          data: '{"incomplete": ',
        } as MessageEvent)
      })

      expect(result.current.error).toBeTruthy()
      expect(result.current.error).toContain("JSON")
    })
  })

  describe("reconnection logic", () => {
    it("should preserve URL across reconnection attempts", () => {
      const { result } = renderHook(() => useSSE())
      const testUrl = "/api/stream/search?q=test&source=quran"

      act(() => {
        result.current.startStream(testUrl)
      })

      // Verify first EventSource was created with correct URL
      expect(constructorCalls[0].url).toBe(testUrl + "&lang=tr")

      const mockEventSource = mockEventSourceInstances[0]

      // First error
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      act(() => {
        vi.advanceTimersByTime(1000)
      })

      // Verify second EventSource uses same URL
      expect(constructorCalls[1].url).toBe(testUrl + "&lang=tr")
    })
  })

  describe("multiple concurrent operations", () => {
    it("should handle stopStream during reconnection delay", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test")
      })

      const mockEventSource = mockEventSourceInstances[0]

      // Trigger error
      act(() => {
        mockEventSource.readyState = 2 // CLOSED
        mockEventSource.onerror?.({ target: mockEventSource } as unknown as Event)
      })

      // Stop stream before reconnection delay completes
      act(() => {
        result.current.stopStream()
        vi.advanceTimersByTime(500) // Advance less than 1s
      })

      expect(result.current.isStreaming).toBe(false)
      // Should not create new EventSource
      expect(constructorCalls).toHaveLength(1)
    })

    it("should handle startStream while streaming", () => {
      const { result } = renderHook(() => useSSE())

      act(() => {
        result.current.startStream("/api/stream/search?q=test1")
      })

      const firstEventSource = mockEventSourceInstances[0]

      // Start new stream while first is active
      act(() => {
        result.current.startStream("/api/stream/search?q=test2")
      })

      // Should close previous EventSource
      expect(firstEventSource.readyState).toBe(2) // CLOSED
      // Should create new EventSource
      expect(constructorCalls).toHaveLength(2)
      // Data should be reset
      expect(result.current.data).toEqual([])
    })
  })
})
