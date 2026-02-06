import { render, screen, waitFor } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import userEvent from "@testing-library/user-event";
import LoginPage from "../app/login/page";
import { useAuth } from "@/lib/auth/auth-context";
import { useRouter } from "next/navigation";

// Mock hooks
vi.mock("@/lib/auth/auth-context", () => ({
  useAuth: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: vi.fn(),
}));

// Mock components
vi.mock("@/components/ui/glow-card", () => ({
  GlowCard: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="glow-card">{children}</div>
  ),
}));

vi.mock("@/components/ui/button", () => ({
  Button: ({ children, onClick, disabled, type, className }: any) => (
    <button onClick={onClick} disabled={disabled} type={type} className={className}>
      {children}
    </button>
  ),
}));

vi.mock("@/components/ui/input", () => ({
  Input: (props: any) => <input {...props} />,
}));

vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

vi.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

vi.mock("@/lib/design-system", () => ({
  springPresets: { fluid: {} },
}));

// Mock @react-oauth/google
vi.mock('@react-oauth/google', () => ({
  GoogleOAuthProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  GoogleLogin: ({ onSuccess, onError }: { 
    onSuccess: (response: { credential?: string }) => void; 
    onError?: () => void 
  }) => (
    <button 
      data-testid="google-login-button"
      onClick={() => onSuccess({ credential: 'mock-google-credential' })}
    >
      Sign in with Google
    </button>
  )
}));

describe('LoginPage', () => {
  const mockLogin = vi.fn();
  const mockLoginWithGoogle = vi.fn();
  const mockPush = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuth).mockReturnValue({
      user: null,
      isLoading: false,
      backendStatus: 'online',
      login: mockLogin,
      loginWithGoogle: mockLoginWithGoogle,
      register: vi.fn(),
      logout: vi.fn(),
    });
    vi.mocked(useRouter).mockReturnValue({ push: mockPush } as any);
  });

  describe('Email/Password Login', () => {
    it('should render email and password inputs', () => {
      render(<LoginPage />);
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    });

    it('should render sign in button', () => {
      render(<LoginPage />);
      expect(screen.getByRole('button', { name: /^sign in$/i })).toBeInTheDocument();
    });
  });

  describe('Google Sign-In Button', () => {
    it('should render Google sign-in button', () => {
      render(<LoginPage />);
      expect(screen.getByTestId('google-login-button')).toBeInTheDocument();
    });

    it('should render OR divider between form and Google button', () => {
      render(<LoginPage />);
      expect(screen.getByText('OR')).toBeInTheDocument();
    });

    it('should call loginWithGoogle on successful Google response', async () => {
      render(<LoginPage />);
      await userEvent.click(screen.getByTestId('google-login-button'));
      
      expect(mockLoginWithGoogle).toHaveBeenCalledWith('mock-google-credential');
    });

    it('should show error message on Google login failure', async () => {
      mockLoginWithGoogle.mockRejectedValueOnce(new Error('Google login failed'));
      
      render(<LoginPage />);
      await userEvent.click(screen.getByTestId('google-login-button'));
      
      await waitFor(() => {
        expect(screen.getByText(/Google login failed/i)).toBeInTheDocument();
      });
    });

    it('should redirect to /search after successful Google login', async () => {
      mockLoginWithGoogle.mockResolvedValueOnce(undefined);
      
      render(<LoginPage />);
      await userEvent.click(screen.getByTestId('google-login-button'));
      
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/search');
      });
    });
  });
});
