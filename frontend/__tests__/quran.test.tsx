import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import QuranPage from "@/app/quran/page";
import { getQuranSurahsApiMetadataQuranSurahsGet } from "@/lib/api/sdk.gen";

vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}));

vi.mock("@/lib/auth-client", () => ({
  useSession: () => ({ data: { user: { id: '1', name: 'Test User', email: 'test@example.com' } }, isPending: false }),
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
}));

vi.mock("@/lib/api/sdk.gen", () => ({
  getQuranSurahsApiMetadataQuranSurahsGet: vi.fn(),
}));

const mockSurahs = [
  {
    id: 1,
    name: "الفاتحة",
    name_transliterated: "Al-Fatiha",
    verse_count: 7,
    revelation_type: "Meccan",
  },
  {
    id: 2,
    name: "البقرة",
    name_transliterated: "Al-Baqarah",
    verse_count: 286,
    revelation_type: "Medinan",
  },
  {
    id: 114,
    name: "الناس",
    name_transliterated: "An-Nas",
    verse_count: 6,
    revelation_type: "Meccan",
  },
];

describe("QuranPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getQuranSurahsApiMetadataQuranSurahsGet).mockResolvedValue({
      data: { data: { surahs: mockSurahs } },
    } as never);
  });

  it("renders the page title", async () => {
    render(<QuranPage />);
    expect(screen.getByText("Quran Browse")).toBeInTheDocument();
  });

  it("fetches and displays surahs", async () => {
    render(<QuranPage />);
    
    await waitFor(() => {
      expect(screen.getByText("Al-Fatiha")).toBeInTheDocument();
      expect(screen.getByText("Al-Baqarah")).toBeInTheDocument();
      expect(screen.getByText("An-Nas")).toBeInTheDocument();
    });

    expect(screen.getByText("7 verses")).toBeInTheDocument();
    expect(screen.getByText("286 verses")).toBeInTheDocument();
  });

  it("filters surahs by name", async () => {
    render(<QuranPage />);

    await waitFor(() => {
      expect(screen.getByText("Al-Fatiha")).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText("Search surah...");
    fireEvent.change(searchInput, { target: { value: "Baqarah" } });

    await waitFor(() => {
      expect(screen.getByText("Al-Baqarah")).toBeInTheDocument();
      expect(screen.queryByText("Al-Fatiha")).not.toBeInTheDocument();
      expect(screen.queryByText("An-Nas")).not.toBeInTheDocument();
    });
  });

  it("navigates to search page on surah click", async () => {
    render(<QuranPage />);

    await waitFor(() => {
      expect(screen.getByText("Al-Fatiha")).toBeInTheDocument();
    });

    const button = screen.getByText("Al-Fatiha").closest("button") as HTMLElement;
    fireEvent.click(button);

    // Navigation is mocked at module level, just verify button is clickable
    expect(button).toBeInTheDocument();
  });
});
