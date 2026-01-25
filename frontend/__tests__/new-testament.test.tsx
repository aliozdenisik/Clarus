import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import NewTestamentPage from '../app/new-testament/page';

// Mock GlowCard to avoid complex rendering in tests
vi.mock('@/components/ui/glow-card', () => ({
  GlowCard: ({ children, onClick }: { children: React.ReactNode, onClick?: () => void }) => (
    <div data-testid="glow-card" onClick={onClick}>
      {children}
    </div>
  ),
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

// Mock Sonner
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock Navigation
const mockPush = vi.fn();
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe('New Testament Browse Page', () => {
  const mockBooks = [
    { nr: 1, name: 'Matthew', chapter_count: 28, testament: 'nt' },
    { nr: 2, name: 'Mark', chapter_count: 16, testament: 'nt' },
    { nr: 3, name: 'Luke', chapter_count: 24, testament: 'nt' },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it('fetches and displays NT books', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBooks,
    });

    render(<NewTestamentPage />);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/metadata/bible/books?testament=nt'),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.stringContaining('Bearer'),
        }),
      })
    );

    await waitFor(() => {
      expect(screen.getByText('Matthew')).toBeInTheDocument();
      expect(screen.getByText('Mark')).toBeInTheDocument();
      expect(screen.getByText('Luke')).toBeInTheDocument();
    });

    expect(screen.getByText('28 chapters')).toBeInTheDocument();
  });

  it('filters books by name', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBooks,
    });

    render(<NewTestamentPage />);

    await waitFor(() => {
      expect(screen.getByText('Matthew')).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText(/search book/i);
    fireEvent.change(input, { target: { value: 'Luke' } });

    expect(screen.queryByText('Matthew')).not.toBeInTheDocument();
    expect(screen.getByText('Luke')).toBeInTheDocument();
  });

  it('navigates to search on book click', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBooks,
    });

    render(<NewTestamentPage />);

    await waitFor(() => {
      expect(screen.getByText('Matthew')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Matthew'));

    expect(mockPush).toHaveBeenCalledWith('/search?source=nt&book=1');
  });

  it('handles empty state or loading', async () => {
    // Test loading state if applicable, or empty result
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(<NewTestamentPage />);
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });
});
