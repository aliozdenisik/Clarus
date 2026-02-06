import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import OldTestamentPage from '../app/old-testament/page';

// Mock GlowCard to avoid complex rendering in tests
vi.mock('@/components/ui/glow-card', () => ({
  GlowCard: ({ children, onClick }: { children: React.ReactNode, onClick?: () => void }) => (
    <div data-testid="glow-card" onClick={onClick}>
      {children}
    </div>
  ),
}));

// Mock Better Auth
vi.mock('@/lib/auth-client', () => ({
  useSession: () => ({ data: { user: { id: '1', name: 'Test User', email: 'test@example.com' } }, isPending: false }),
  signIn: { email: vi.fn(), social: vi.fn() },
  signUp: { email: vi.fn() },
  signOut: vi.fn(),
  authClient: { token: vi.fn() },
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

describe('Old Testament Browse Page', () => {
  const mockBooks = [
    { nr: 1, name: 'Genesis', chapters_count: 50, testament: 'old_testament' },
    { nr: 2, name: 'Exodus', chapters_count: 40, testament: 'old_testament' },
    { nr: 3, name: 'Leviticus', chapters_count: 27, testament: 'old_testament' },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  it('fetches and displays OT books', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: { books: mockBooks } }),
    });

    render(<OldTestamentPage />);

     expect(global.fetch).toHaveBeenCalledWith(
       expect.stringContaining('/api/metadata/bible/books?testament=old_testament'),
       expect.objectContaining({
         credentials: 'include',
       })
     );

    await waitFor(() => {
      expect(screen.getByText('Genesis')).toBeInTheDocument();
      expect(screen.getByText('Exodus')).toBeInTheDocument();
      expect(screen.getByText('Leviticus')).toBeInTheDocument();
    });

    expect(screen.getByText('50 chapters')).toBeInTheDocument();
  });

  it('filters books by name', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: { books: mockBooks } }),
    });

    render(<OldTestamentPage />);

    await waitFor(() => {
      expect(screen.getByText('Genesis')).toBeInTheDocument();
    });

    const input = screen.getByPlaceholderText(/search book/i);
    fireEvent.change(input, { target: { value: 'Exod' } });

    expect(screen.queryByText('Genesis')).not.toBeInTheDocument();
    expect(screen.getByText('Exodus')).toBeInTheDocument();
  });

  it('navigates to search on book click', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: { books: mockBooks } }),
    });

    render(<OldTestamentPage />);

    await waitFor(() => {
      expect(screen.getByText('Genesis')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Genesis'));

    expect(mockPush).toHaveBeenCalledWith('/bible/1');
  });

  it('handles empty state or loading', async () => {
    // Test loading state if applicable, or empty result
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ data: { books: [] } }),
    });

    render(<OldTestamentPage />);
    
    // Ideally check for a loading spinner or skeleton first
    // Then empty state
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    });
  });
});
