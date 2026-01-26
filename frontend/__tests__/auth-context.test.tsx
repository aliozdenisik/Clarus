// frontend/__tests__/auth-context.test.tsx
import { describe, it, expect, vi, beforeEach, Mock } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/lib/auth/auth-context';

// Global fetch mock
global.fetch = vi.fn();

// Mock useRouter
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn() })
}));

describe('loginWithGoogle', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('should exchange Google credential for JWT token', async () => {
    (fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: 'mock-jwt',
        refresh_token: 'mock-refresh',
        user: { id: 1, email: 'test@google.com', name: 'Test', created_at: '2024-01-01' }
      })
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });
    
    await act(async () => {
      await result.current.loginWithGoogle('mock-credential');
    });
    
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/auth/google',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: 'mock-credential' })
      })
    );
  });

  it('should store tokens in localStorage', async () => {
    (fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: 'stored-jwt',
        refresh_token: 'stored-refresh',
        user: { id: 1, email: 'test@google.com', name: 'Test', created_at: '2024-01-01' }
      })
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });
    
    await act(async () => {
      await result.current.loginWithGoogle('mock-credential');
    });
    
    expect(localStorage.getItem('access_token')).toBe('stored-jwt');
    expect(localStorage.getItem('refresh_token')).toBe('stored-refresh');
  });

  it('should set user state after successful login', async () => {
    const mockUser = { id: 1, email: 'test@google.com', name: 'Test User', created_at: '2024-01-01' };
    (fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        access_token: 'jwt',
        refresh_token: 'refresh',
        user: mockUser
      })
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });
    
    await act(async () => {
      await result.current.loginWithGoogle('mock-credential');
    });
    
    expect(result.current.user).toEqual(mockUser);
  });

  it('should throw error when backend returns 400', async () => {
    (fetch as Mock).mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: 'Invalid Google token' })
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });
    
    await expect(
      act(async () => {
        await result.current.loginWithGoogle('invalid-credential');
      })
    ).rejects.toThrow('Google login failed. Please try again.');
  });

  it('should handle network errors gracefully', async () => {
    (fetch as Mock).mockRejectedValueOnce(new TypeError('Failed to fetch'));
    
    const { result } = renderHook(() => useAuth(), { wrapper: AuthProvider });
    
    await expect(
      act(async () => {
        await result.current.loginWithGoogle('mock-credential');
      })
    ).rejects.toThrow('Connection failed. Please check your internet.');
  });
});
