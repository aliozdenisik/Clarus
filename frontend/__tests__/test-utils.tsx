import { render, RenderOptions } from "@testing-library/react"
import { ReactElement, ReactNode } from "react"
import { NextIntlClientProvider } from "next-intl"
import enMessages from "../messages/en.json"

/**
 * Custom render function that wraps components with NextIntlClientProvider
 * for testing components that use next-intl translations
 */
export function renderWithIntl(
  ui: ReactElement,
  locale: string = "en",
  messages: IntlMessages = enMessages,
  options?: Omit<RenderOptions, "wrapper">
) {
  function Wrapper({ children }: { children: ReactNode }) {
    return (
      <NextIntlClientProvider locale={locale} messages={messages}>
        {children}
      </NextIntlClientProvider>
    )
  }

  return render(ui, { wrapper: Wrapper, ...options })
}

// Re-export everything from React Testing Library
export * from "@testing-library/react"

// Override the default render with our custom render
export { renderWithIntl as render }
