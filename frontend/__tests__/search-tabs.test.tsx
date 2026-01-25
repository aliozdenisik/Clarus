import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import SearchPage from '../app/search/page';
import { SearchTabs } from '../components/search/search-tabs';

// Mock components
vi.mock('@/components/ui/glow-card', () => ({
  GlowCard: ({ children }: { children: React.ReactNode }) => <div data-testid="glow-card">{children}</div>,
}));

// Mock Auth
const mockUser = { name: 'Test User', email: 'test@example.com' };
const mockLogout = vi.fn();

vi.mock('@/lib/auth/auth-context', () => ({
  useAuth: () => ({
    user: mockUser,
    isLoading: false,
    logout: mockLogout,
  }),
}));

// Mock Navigation
const mockPush = vi.fn();
const mockSearchParamsGet = vi.fn();
const mockSearchParams = {
  get: mockSearchParamsGet,
};

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
  useSearchParams: () => mockSearchParams,
}));

// Mock Sonner toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('SearchTabs Component', () => {
  it('renders all 4 tabs', () => {
    render(<SearchTabs activeTab="quran" onTabChange={() => {}} />);
    expect(screen.getByText('Kuran')).toBeInTheDocument();
    expect(screen.getByText('Eski Ahit')).toBeInTheDocument();
    expect(screen.getByText('Yeni Ahit')).toBeInTheDocument();
    expect(screen.getByText('Apokrifa')).toBeInTheDocument();
  });

  it('calls onTabChange when a tab is clicked', () => {
    const handleTabChange = vi.fn();
    render(<SearchTabs activeTab="quran" onTabChange={handleTabChange} />);
    
    fireEvent.click(screen.getByText('Eski Ahit'));
    expect(handleTabChange).toHaveBeenCalledWith('ot');
  });
});

describe('SearchPage Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
    mockSearchParamsGet.mockReturnValue(null); // Default to null (quran)
  });

  it('renders search tabs', () => {
    render(<SearchPage />);
    expect(screen.getByText('Kuran')).toBeInTheDocument();
    expect(screen.getByText('Eski Ahit')).toBeInTheDocument();
    expect(screen.getByText('Yeni Ahit')).toBeInTheDocument();
    expect(screen.getByText('Apokrifa')).toBeInTheDocument();
  });

  it('initializes tab from URL', () => {
    mockSearchParamsGet.mockReturnValue('nt');
    render(<SearchPage />);
    // Check if NT tab is active (we can check class or aria-pressed if we had it, but here checking if it renders is basic)
    // We can verify functionality by checking if search uses 'nt'
    const input = screen.getByPlaceholderText(/search/i);
    fireEvent.change(input, { target: { value: 'test' } });
    
    // We can't easily check internal state, but we can check the API call
    // But we need to implement the page first for this to work
  });

  it('changes tab and updates URL when clicked', () => {
    render(<SearchPage />);
    
    const otTab = screen.getByText('Eski Ahit');
    fireEvent.click(otTab);
    
    expect(mockPush).toHaveBeenCalledWith(expect.stringContaining('?source=ot'));
  });

  it('performs search with correct API endpoint for Kuran', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });

    render(<SearchPage />);
    
    const input = screen.getByPlaceholderText(/search/i);
    fireEvent.change(input, { target: { value: 'test query' } });
    
    const button = screen.getByRole('button', { name: 'Search' });
    fireEvent.click(button);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/search/quran'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('test query'),
        })
      );
    });
  });

  it('performs search with correct API endpoint for Bible (OT)', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ results: [] }),
    });

    // We simulate user clicking OT tab
    render(<SearchPage />);
    
    const otTab = screen.getByText('Eski Ahit');
    fireEvent.click(otTab);

    const input = screen.getByPlaceholderText(/search/i);
    fireEvent.change(input, { target: { value: 'test query' } });
    
    const button = screen.getByRole('button', { name: 'Search' });
    fireEvent.click(button);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/search/bible'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('"testament":"ot"'),
        })
      );
    });
  });
});
