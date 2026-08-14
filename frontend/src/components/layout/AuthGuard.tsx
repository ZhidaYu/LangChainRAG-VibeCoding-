import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuth } from '../../hooks/useAuth';

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  const hasToken = !!localStorage.getItem('rag_access_token');

  // No token at all → redirect immediately, no spinner
  if (!hasToken) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Token exists but user not yet loaded → show spinner briefly
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  // Token exists, user loaded → show children
  if (user) {
    return <>{children}</>;
  }

  // Token exists but user failed to load → redirect to login
  return <Navigate to="/login" state={{ from: location }} replace />;
}
