import { useState } from 'react';
import { Card, Form, Input, Button, Descriptions, message, Divider } from 'antd';
import { useAuthStore } from '../stores/authStore';

export default function ProfilePage() {
  const { user, changePassword } = useAuthStore();
  const [loading, setLoading] = useState(false);

  const onChangePassword = async (values: { old: string; newPwd: string; confirm: string }) => {
    if (values.newPwd !== values.confirm) {
      message.error('两次密码输入不一致');
      return;
    }
    setLoading(true);
    try {
      await changePassword(values.old, values.newPwd);
      message.success('密码修改成功');
    } catch (err: any) {
      message.error(err.response?.data?.detail || '修改失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 600, margin: '0 auto' }}>
      <Card title="个人信息">
        <Descriptions column={1}>
          <Descriptions.Item label="用户名">{user?.username}</Descriptions.Item>
          <Descriptions.Item label="角色">{user?.role === 'admin' ? '管理员' : '普通用户'}</Descriptions.Item>
        </Descriptions>
        <Divider />
        <Card title="修改密码" type="inner" style={{ marginTop: 16 }}>
          <Form onFinish={onChangePassword} layout="vertical">
            <Form.Item name="old" label="旧密码" rules={[{ required: true, message: '请输入旧密码' }]}>
              <Input.Password />
            </Form.Item>
            <Form.Item name="newPwd" label="新密码" rules={[{ required: true, min: 6, message: '密码至少6位' }]}>
              <Input.Password />
            </Form.Item>
            <Form.Item name="confirm" label="确认密码" rules={[{ required: true, message: '请确认密码' }]}>
              <Input.Password />
            </Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              修改密码
            </Button>
          </Form>
        </Card>
      </Card>
    </div>
  );
}
