import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { describe, it, expect, vi } from "vitest"
import { FilterTabs } from "@/components/compare/filter-tabs"

describe("FilterTabs", () => {
  it("renders all 5 filter options", () => {
    render(<FilterTabs activeFilter="all" onFilterChange={vi.fn()} counts={{}} />)
    expect(screen.getByText("All")).toBeInTheDocument()
    expect(screen.getByText("Quran")).toBeInTheDocument()
    expect(screen.getByText("Old Testament")).toBeInTheDocument()
    expect(screen.getByText("New Testament")).toBeInTheDocument()
    expect(screen.getByText("Apocrypha")).toBeInTheDocument()
  })

  it("highlights active tab with different styling", () => {
    render(<FilterTabs activeFilter="quran" onFilterChange={vi.fn()} counts={{}} />)
    // Active tab has text-[#0e0e10] class, inactive has text-[#0e0f1199]
    const quranTab = screen.getByText("Quran").closest('div[class*="cursor-pointer"]')
    expect(quranTab).toBeInTheDocument()
    expect(quranTab?.className).toContain("text-[#0e0e10]")
  })

  it("renders tab container", () => {
    render(<FilterTabs activeFilter="all" onFilterChange={vi.fn()} counts={{}} />)
    // Vercel tabs renders a container with flex layout
    const container = screen.getByText("All").closest('div[class*="flex"]')
    expect(container).toBeInTheDocument()
  })

  it("renders all tab labels even with counts provided", () => {
    render(
      <FilterTabs
        activeFilter="all"
        onFilterChange={vi.fn()}
        counts={{ all: 15, quran: 5, old_testament: 10, new_testament: 0, apocrypha: 0 }}
      />
    )
    // Component renders labels; counts are passed as tab data
    expect(screen.getByText("All")).toBeInTheDocument()
    expect(screen.getByText("Quran")).toBeInTheDocument()
    expect(screen.getByText("Old Testament")).toBeInTheDocument()
  })

  it("renders inactive tabs with muted styling", () => {
    render(
      <FilterTabs
        activeFilter="all"
        onFilterChange={vi.fn()}
        counts={{ all: 15, quran: 5, old_testament: 10, new_testament: 0, apocrypha: 0 }}
      />
    )
    // Inactive tabs should have the muted text color class
    const quranTab = screen.getByText("Quran").closest('div[class*="cursor-pointer"]')
    expect(quranTab?.className).toContain("text-[#0e0f1199]")
  })

  it("calls onFilterChange when tab clicked", async () => {
    const handleChange = vi.fn()
    render(<FilterTabs activeFilter="all" onFilterChange={handleChange} counts={{}} />)
    await userEvent.click(screen.getByText("Quran"))
    expect(handleChange).toHaveBeenCalledWith("quran")
  })
})
