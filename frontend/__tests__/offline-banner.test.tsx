import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OfflineBannerWrapper } from '@/components/layout/offline-banner';

// Mock the auth context
vi.mock('@/lib/auth/auth-context', () => ({
  useAuth: vi.fn()
}));

import { useAuth } from '@/lib/auth/auth-context';

describe('OfflineBannerWrapper', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns null when backendStatus is online', () => {
    (useAuth as any).mockReturnValue({ backendStatus: 'online' });
    
    const { container } = render(<OfflineBannerWrapper />);
    
    expect(container.firstChild).toBeNull();
  });

  it('returns null when backendStatus is unknown', () => {
    (useAuth as any).mockReturnValue({ backendStatus: 'unknown' });
    
    const { container } = render(<OfflineBannerWrapper />);
    
    expect(container.firstChild).toBeNull();
  });

  it('renders red banner when backendStatus is offline', () => {
    (useAuth as any).mockReturnValue({ backendStatus: 'offline' });
    
    render(<OfflineBannerWrapper />);
    
    const banner = screen.getByText(/Backend offline/).closest('div');
    expect(banner).toBeInTheDocument();
  });

  it('displays warning icon in banner', () => {
    (useAuth as any).mockReturnValue({ backendStatus: 'offline' });
    
    render(<OfflineBannerWrapper />);
    
    expect(screen.getByText('⚠️')).toBeInTheDocument();
  });

  it('displays offline message in banner', () => {
    (useAuth as any).mockReturnValue({ backendStatus: 'offline' });
    
    render(<OfflineBannerWrapper />);
    
    expect(screen.getByText(/Backend offline - some features unavailable/)).toBeInTheDocument();
  });

  it('applies correct styling classes to banner', () => {
    (useAuth as any).mockReturnValue({ backendStatus: 'offline' });
    
    render(<OfflineBannerWrapper />);
    
    const banner = screen.getByText(/Backend offline/).closest('div');
    expect(banner).toHaveClass('fixed', 'top-0', 'left-0', 'right-0', 'bg-red-600', 'text-white', 'text-center', 'py-2', 'z-50');
  });

  it('positions banner at top of viewport', () => {
    (useAuth as any).mockReturnValue({ backendStatus: 'offline' });
    
    render(<OfflineBannerWrapper />);
    
    const banner = screen.getByText(/Backend offline/).closest('div');
    expect(banner).toHaveClass('fixed', 'top-0');
  });

  it('spans full width of viewport', () => {
    (useAuth as any).mockReturnValue({ backendStatus: 'offline' });
    
    render(<OfflineBannerWrapper />);
    
    const banner = screen.getByText(/Backend offline/).closest('div');
    expect(banner).toHaveClass('left-0', 'right-0');
  });

  it('has high z-index to appear above other content', () => {
    (useAuth as any).mockReturnValue({ backendStatus: 'offline' });
    
    render(<OfflineBannerWrapper />);
    
    const banner = screen.getByText(/Backend offline/).closest('div');
    expect(banner).toHaveClass('z-50');
  });

  it('warning icon has proper spacing', () => {
    (useAuth as any).mockReturnValue({ backendStatus: 'offline' });
    
    render(<OfflineBannerWrapper />);
    
    const warningSpan = screen.getByText('⚠️').closest('span');
    expect(warningSpan).toHaveClass('mr-2');
  });
});
