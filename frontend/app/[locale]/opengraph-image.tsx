import { ImageResponse } from "next/og"
import { getTranslations } from "next-intl/server"

export const alt = "Clarus - AI-Powered Sacred Text Search"
export const size = { width: 1200, height: 630 }
export const contentType = "image/png"

interface Props {
  params: Promise<{ locale: string }>
}

/**
 * Dynamically generated OpenGraph / Twitter card image for all pages under the
 * [locale] segment. Self-contained (no external assets) so social previews work
 * out of the box. Tagline and subtitle are localized to match the page locale.
 */
export default async function OpengraphImage({ params }: Props): Promise<ImageResponse> {
  const { locale } = await params
  const t = await getTranslations({ locale, namespace: "Metadata" })
  const tagline = t("ogTagline")
  const subtitle = t("ogSubtitle")

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
          {tagline}
        </div>
        <div
          style={{
            fontSize: 26,
            marginTop: 28,
            color: "#94a3b8",
          }}
        >
          {subtitle}
        </div>
      </div>
    ),
    { ...size },
  )
}
