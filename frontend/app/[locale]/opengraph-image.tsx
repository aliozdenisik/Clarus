import { ImageResponse } from "next/og"

export const alt = "Clarus - AI-Powered Sacred Text Search"
export const size = { width: 1200, height: 630 }
export const contentType = "image/png"

/**
 * Dynamically generated OpenGraph / Twitter card image for all pages under the
 * [locale] segment. Self-contained (no external assets) so social previews work
 * out of the box.
 */
export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background:
            "radial-gradient(circle at 30% 20%, #1e293b 0%, #0a0a0a 55%, #020617 100%)",
          color: "white",
          fontFamily: "sans-serif",
        }}
      >
        <div
          style={{
            fontSize: 120,
            fontWeight: 700,
            letterSpacing: "-0.04em",
            background: "linear-gradient(90deg, #818cf8 0%, #38bdf8 100%)",
            backgroundClip: "text",
            color: "transparent",
          }}
        >
          Clarus
        </div>
        <div
          style={{
            fontSize: 40,
            marginTop: 16,
            color: "#cbd5e1",
            maxWidth: 900,
            textAlign: "center",
          }}
        >
          AI-Powered Sacred Text Search
        </div>
        <div
          style={{
            fontSize: 26,
            marginTop: 28,
            color: "#94a3b8",
          }}
        >
          Quran · Bible · Compare · Discover
        </div>
      </div>
    ),
    { ...size },
  )
}
