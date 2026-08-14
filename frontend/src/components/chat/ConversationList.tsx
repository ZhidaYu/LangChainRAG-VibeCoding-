import { useEffect, useState, useCallback } from 'react';
import { List, Button, Input, Dropdown, message } from 'antd';
import { PlusOutlined, SearchOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { conversationAPI } from '../../api/chat';
import type { Conversation } from '../../api/chat';
import { formatDate } from '../../utils/format';

interface Props {
  currentId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}

export default function ConversationList({ currentId, onSelect, onNew, onDelete }: Props) {
  const [convs, setConvs] = useState<Conversation[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  const loadConvs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await conversationAPI.list();
      setConvs(res.data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!mounted) {
      setMounted(true);
      loadConvs();
    }
  }, [mounted, loadConvs]);

  const filtered = convs.filter((c) =>
    c.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: 12 }}>
        <Button type="primary" icon={<PlusOutlined />} block onClick={onNew}>
          新对话
        </Button>
      </div>
      <div style={{ padding: '0 12px 8px' }}>
        <Input
          prefix={<SearchOutlined />}
          placeholder="搜索对话..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          allowClear
        />
      </div>
      <List
        loading={loading}
        dataSource={filtered}
        style={{ flex: 1, overflow: 'auto', padding: '0 12px' }}
        renderItem={(item) => (
          <List.Item
            key={item.id}
            onClick={() => onSelect(item.id)}
            style={{
              cursor: 'pointer',
              padding: '8px 12px',
              borderRadius: 8,
              background: item.id === currentId ? '#e6f4ff' : 'transparent',
              marginBottom: 2,
            }}
            actions={[
              <Dropdown
                key="more"
                menu={{
                  items: [
                    {
                      key: 'rename',
                      icon: <EditOutlined />,
                      label: '重命名',
                      onClick: async () => {
                        const newTitle = prompt('新标题:', item.title);
                        if (newTitle) {
                          await conversationAPI.updateTitle(item.id, newTitle);
                          loadConvs();
                        }
                      },
                    },
                    {
                      key: 'delete',
                      icon: <DeleteOutlined />,
                      label: '删除',
                      danger: true,
                      onClick: () => {
                        onDelete(item.id);
                        setConvs((prev) => prev.filter((c) => c.id !== item.id));
                        message.success('已删除');
                      },
                    },
                  ],
                }}
              >
                <Button type="text" size="small">
                  ···
                </Button>
              </Dropdown>,
            ]}
          >
            <List.Item.Meta
              title={item.title}
              description={formatDate(item.updated_at)}
            />
          </List.Item>
        )}
      />
    </div>
  );
}
