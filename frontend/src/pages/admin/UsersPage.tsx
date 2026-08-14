import { useEffect, useState, useCallback } from 'react';
import { Table, Tag, Button, Popconfirm, message } from 'antd';
import { DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import apiClient from '../../api/client';

interface UserItem {
  id: string;
  username: string;
  role: string;
  is_active: number;
  created_at: string;
}

export default function UsersPage() {
  const [users, setUsers] = useState<UserItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  const loadUsers = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiClient.get<UserItem[]>('/users');
      setUsers(res.data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!mounted) {
      setMounted(true);
      loadUsers();
    }
  }, [mounted, loadUsers]);

  const handleDelete = async (id: string) => {
    try {
      await apiClient.delete(`/users/${id}`);
      message.success('已禁用');
      loadUsers();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '操作失败');
    }
  };

  const columns = [
    { title: '用户名', dataIndex: 'username', key: 'username' },
    { title: '角色', dataIndex: 'role', key: 'role', width: 100,
      render: (v: string) => <Tag color={v === 'admin' ? 'red' : 'blue'}>{v === 'admin' ? '管理员' : '用户'}</Tag> },
    { title: '状态', dataIndex: 'is_active', key: 'active', width: 80,
      render: (v: number) => <Tag color={v ? 'green' : 'red'}>{v ? '正常' : '已禁用'}</Tag> },
    {
      title: '操作', key: 'actions', width: 80,
      render: (_: unknown, r: UserItem) =>
        r.role !== 'admin' ? (
          <Popconfirm title="确认禁用该用户？" onConfirm={() => handleDelete(r.id)}>
            <Button type="text" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        ) : null,
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 16 }}>
        <Button icon={<ReloadOutlined />} onClick={loadUsers}>刷新</Button>
      </div>
      <Table columns={columns} dataSource={users} rowKey="id" loading={loading} />
    </div>
  );
}
