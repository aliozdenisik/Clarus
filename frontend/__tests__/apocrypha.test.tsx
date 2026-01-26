import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import ApocryphaPage from '../app/apocrypha/page';

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

describe('Apocrypha Browse Page', () => {
  const mockBooks = [
    { nr: 1, name: 'Tobit', chapters_count: 14, testament: 'apocrypha' },
    { nr: 2, name: 'Judith', chapters_count: 16, testament: 'apocrypha' },
    { nr: 3, name: 'Wisdom', chapters_count: 19, testament: 'apocrypha' },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it('fetches and displays Apocrypha books', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: { books: mockBooks } }),
    });

    render(<ApocryphaPage />);

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/metadata/bible/books?testament=apocrypha'),
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: expect.stringContaining('Bearer'),
        }),
      })
    );

    await waitFor(() => {
      expect(screen.getByText('Tobit')).toBeInTheDocument();
      expect(screen.getByText('Judith')).toBeInTheDocument();
      expect(screen.getByText('Wisdom')).toBeInTheDocument();
    });

    expect(screen.getByText('14 chapters')).toBeInTheDocument();
  });

  it('filters books by name', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: { books: mockBooks } }),
    });

    render(<ApocryphaPage />);

    await waitFor(() => {
      expect(screen.getByText('Tobit')).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText(/search book/i);
    fireEvent.change(input, { target: { value: 'Judit' } });

    expect(screen.queryByText('Tobit')).not.toBeInTheDocument();
    expect(screen.getByText('Judith')).toBeInTheDocument();
  });

  it('navigates to search on book click', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: { books: mockBooks } }),
    });

    render(<ApocryphaPage />);

    await waitFor(() => {
      expect(screen.getByText('Tobit')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Tobit'));

    expect(mockPush).toHaveBeenCalledWith('/search?source=apocrypha&book=1');
  });

  it('handles empty state or loading', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: { books: [] } }),
    });

    render(<ApocryphaPage />);
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });
});
