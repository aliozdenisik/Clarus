import React from "react"
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, it, expect, vi } from "vitest"
import { FilterTabs } from "@/components/compare/filter-tabs"

vi.mock("@/components/motion-primitives/animated-background", () => ({
  AnimatedBackground: ({
    children,
    defaultValue,
    onValueChange,
  }: {
    children: React.ReactNode
    defaultValue?: string
    onValueChange?: (id: string | null) => void
    className?: string
    transition?: object
  }) => (
    <div data-testid="animated-background" data-active={defaultValue}>
      {React.Children.map(children, (child) => {
        if (!React.isValidElement(child)) return child
        const props = child.props as Record<string, unknown>
        const dataId = props["data-id"] as string
        return (
          <button
            type="button"
            data-id={dataId}
            data-checked={dataId === defaultValue ? "true" : "false"}
            onClick={() => onValueChange?.(dataId)}
          >
            {props.children as React.ReactNode}
          </button>
        )
      })}
    </div>
  ),
}))

describe("FilterTabs", () => {
  it("renders all 5 filter options", () => {
    render(<FilterTabs activeFilter="all" onFilterChange={vi.fn()} counts={{}} />)
    expect(screen.getByText("All")).toBeInTheDocument()
    expect(screen.getByText("Quran")).toBeInTheDocument()
    expect(screen.getByText("Old Testament")).toBeInTheDocument()
    expect(screen.getByText("New Testament")).toBeInTheDocument()
    expect(screen.getByText("Apocrypha")).toBeInTheDocument()
  })

  it("highlights active tab with data-checked attribute", () => {
    render(<FilterTabs activeFilter="quran" onFilterChange={vi.fn()} counts={{}} />)
    const quranTab = screen.getByText("Quran").closest("button")
    expect(quranTab).toHaveAttribute("data-checked", "true")
  })

  it("renders AnimatedBackground container", () => {
    render(<FilterTabs activeFilter="all" onFilterChange={vi.fn()} counts={{}} />)
    expect(screen.getByTestId("animated-background")).toBeInTheDocument()
  })

  it("renders all tab labels even with counts provided", () => {
    render(
      <FilterTabs
        activeFilter="all"
        onFilterChange={vi.fn()}
        counts={{ all: 15, quran: 5, old_testament: 10, new_testament: 0, apocrypha: 0 }}
      />
    )
    expect(screen.getByText("All")).toBeInTheDocument()
    expect(screen.getByText("Quran")).toBeInTheDocument()
    expect(screen.getByText("Old Testament")).toBeInTheDocument()
  })

  it("marks inactive tabs with data-checked false", () => {
    render(
      <FilterTabs
        activeFilter="all"
        onFilterChange={vi.fn()}
        counts={{ all: 15, quran: 5, old_testament: 10, new_testament: 0, apocrypha: 0 }}
      />
    )
    const quranTab = screen.getByText("Quran").closest("button")
    expect(quranTab).toHaveAttribute("data-checked", "false")
  })

  it("calls onFilterChange when tab clicked", async () => {
    const handleChange = vi.fn()
    render(<FilterTabs activeFilter="all" onFilterChange={handleChange} counts={{}} />)
    await userEvent.click(screen.getByText("Quran"))
    expect(handleChange).toHaveBeenCalledWith("quran")
  })
})
