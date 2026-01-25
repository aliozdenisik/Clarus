import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import SettingsPage from '../app/settings/page';
import * as PreferencesStore from '@/lib/stores/preferences-store';
import * as AuthContext from '@/lib/auth/auth-context';

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
}));

// Mock Sonner toast
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

// Mock fetch for the component's direct API calls (like DELETE)
global.fetch = vi.fn();

describe('SettingsPage', () => {
  const mockSetTheme = vi.fn();
  const mockSetLanguage = vi.fn();
  const mockSetDefaultSearchSource = vi.fn();
  const mockSetDefaultBibleTestament = vi.fn();
  const mockSetResultsPerPage = vi.fn();
  const mockSetEnableStreaming = vi.fn();
  const mockSetEnableMultiAgent = vi.fn();
  const mockSavePreferences = vi.fn();
  const mockFetchPreferences = vi.fn();
  const mockReset = vi.fn();

  const defaultPreferences = {
    theme: 'system',
    language: 'tr',
    default_search_source: 'quran',
    default_bible_testament: 'all',
    results_per_page: 10,
    enable_streaming: true,
    enable_multi_agent: false,
    isLoading: false,
    error: null,
    setTheme: mockSetTheme,
    setLanguage: mockSetLanguage,
    setDefaultSearchSource: mockSetDefaultSearchSource,
    setDefaultBibleTestament: mockSetDefaultBibleTestament,
    setResultsPerPage: mockSetResultsPerPage,
    setEnableStreaming: mockSetEnableStreaming,
    setEnableMultiAgent: mockSetEnableMultiAgent,
    savePreferences: mockSavePreferences,
    fetchPreferences: mockFetchPreferences,
    reset: mockReset,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock window.confirm
    window.confirm = vi.fn(() => true);

    // Mock Auth
    vi.spyOn(AuthContext, 'useAuth').mockReturnValue({
      user: { id: 1, email: 'test@example.com', name: 'Test User', created_at: '2023-01-01' },
      isLoading: false,
      login: vi.fn(),
      register: vi.fn(),
      logout: vi.fn(),
    });

    // Mock Store
    // We need to mock the selector behavior if the component uses selectors,
    // or just return the whole state if it calls the hook without selectors.
    // Assuming the component uses: const { ... } = usePreferencesStore();
    vi.spyOn(PreferencesStore, 'usePreferencesStore').mockImplementation((selector) => {
      if (selector) return selector(defaultPreferences);
      return defaultPreferences;
    });
  });

  it('renders the settings form with current preferences', () => {
    render(<SettingsPage />);
    
    expect(screen.getByText('User Preferences')).toBeDefined();
    
    // Check for form fields (using test ids or labels is better, assuming labels)
    expect(screen.getByLabelText(/Language/i)).toBeDefined();
    expect(screen.getByLabelText(/Theme/i)).toBeDefined();
    expect(screen.getByLabelText(/Default Source/i)).toBeDefined();
    expect(screen.getByLabelText(/Results Per Page/i)).toBeDefined();
  });

  it('fetches preferences on mount', () => {
    render(<SettingsPage />);
    expect(mockFetchPreferences).toHaveBeenCalled();
  });

  it('updates preferences when fields change', async () => {
    render(<SettingsPage />);
    
    // Change Language
    // Note: Select interactions can be tricky in tests depending on the UI library.
    // Assuming standard HTML select or reachable elements.
    // If using Radix UI (which the project seems to use), we might need to click the trigger then the option.
    // For now, let's assume standard inputs or check if we can simulate the change.
    
    // Check if we can find the language select
    const languageSelect = screen.getByLabelText(/Language/i);
    fireEvent.change(languageSelect, { target: { value: 'en' } });
    expect(mockSetLanguage).toHaveBeenCalledWith('en');
  });

  it('calls savePreferences when Save button is clicked', async () => {
    render(<SettingsPage />);
    
    const saveButton = screen.getByRole('button', { name: /Save Changes/i });
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(mockSavePreferences).toHaveBeenCalled();
    });
  });

  it('calls DELETE api and reset when Reset button is clicked', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ success: true }),
    });

    render(<SettingsPage />);
    
    const resetButton = screen.getByRole('button', { name: /Reset to Defaults/i });
    fireEvent.click(resetButton);
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/preferences'),
        expect.objectContaining({ method: 'DELETE' })
      );
      expect(mockReset).toHaveBeenCalled();
    });
  });
});
