import { useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { getAccessToken } from '../utils/token';

// Track whether init has been called across hook instances
let initCalled = false;

export function useAuth() {
  const user = useAuthStore((s) => s.user);

  useEffect(() => {
    if (!initCalled) {
      initCalled = true;
      useAuthStore.getState().init();
    }
  }, []);

  // Sync check: if token exists, assume logged in (async validation happens in background)
  const hasToken = !!getAccessToken();

  return {
    user,
    loading: hasToken && !user,  // only "loading" when token exists but user not yet validated
    isAuthenticated: !!user || hasToken,
    isAdmin: user?.role === 'admin',
  };
}
