import { Result, Button } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../stores/authStore';

export default function AdminGuard({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  const navigate = useNavigate();

  // If user still loading, wait
  if (!user) return null;

  if (user.role !== 'admin') {
    return (
      <Result
        status="403"
        title="403"
        subTitle="需要管理员权限才能访问此页面"
        extra={<Button type="primary" onClick={() => navigate('/chat')}>返回对话</Button>}
      />
    );
  }

  return <>{children}</>;
}
