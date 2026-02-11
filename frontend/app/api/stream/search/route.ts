import { NextRequest } from "next/server"

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export const runtime = "nodejs"
export const dynamic = "force-dynamic"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams.toString()
  const backendUrl = `${BACKEND_URL}/api/stream/search${searchParams ? `?${searchParams}` : ""}`
  const cookieHeader = request.headers.get("cookie") || ""

  const response = await fetch(backendUrl, {
    headers: {
      Cookie: cookieHeader,
      Accept: "text/event-stream",
    },
    cache: "no-store",
  })

  if (!response.ok) {
    let message = response.statusText
    try {
      const body = await response.text()
      if (body) {
        message = body
      }
    } catch {}

    return new Response(JSON.stringify({ error: message }), {
      status: response.status,
      headers: { "Content-Type": "application/json" },
    })
  }

  return new Response(response.body, {
    status: response.status,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      "X-Accel-Buffering": "no",
    },
  })
}
