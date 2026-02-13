import { defineRouting } from "next-intl/routing"

export const routing = defineRouting({
  locales: ["en", "tr"],
  defaultLocale: "tr",
  localePrefix: "always",
})
