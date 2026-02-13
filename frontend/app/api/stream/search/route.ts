import { NextRequest } from "next/server"

const BACKEND_URL = process.env.BACKEND_INTERNAL_URL || "http://127.0.0.1:8000"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams.toString()
  const backendUrl = `${BACKEND_URL}/api/stream/search${searchParams ? `?${searchParams}` : ""}`
  const cookieHeader = request.headers.get("cookie") || ""
  const acceptLanguage = request.headers.get("accept-language") || "tr"

  try {
    const response = await fetch(backendUrl, {
      headers: {
        Cookie: cookieHeader,
        Accept: "text/event-stream",
        "Accept-Language": acceptLanguage,
      },
      cache: "no-store",
    })

    if (!response.ok) {
      let message = response.statusText
      try {
        const body = await response.text()
        if (body) message = body
      } catch {
        /* ignore */
      }
      return new Response(JSON.stringify({ error: message }), {
        status: response.status,
        headers: { "Content-Type": "application/json" },
      })
    }

    const { readable, writable } = new TransformStream()
    const writer = writable.getWriter()
    const reader = (response.body as ReadableStream<Uint8Array>).getReader()

    const pump = async () => {
      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          await writer.write(value)
        }
      } catch {
        /* stream closed by client */
      } finally {
        try {
          writer.close()
        } catch {
          /* already closed */
        }
      }
    }
    pump()

    return new Response(readable, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        Connection: "keep-alive",
        "X-Accel-Buffering": "no",
      },
    })
  } catch {
    return new Response(JSON.stringify({ error: "Backend connection failed" }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    })
  }
}
