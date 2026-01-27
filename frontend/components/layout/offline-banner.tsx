'use client';
import { useAuth } from '@/lib/auth/auth-context';

export function OfflineBannerWrapper() {
  const { backendStatus } = useAuth();
  if (backendStatus !== 'offline') return null;
  return (
    <div className="fixed top-0 left-0 right-0 bg-red-600 text-white text-center py-2 z-50">
      <span className="mr-2">⚠️</span>
      Backend offline - some features unavailable
    </div>
  );
}
