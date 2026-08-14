import { useEffect, useState, useCallback } from 'react';
import {
  Table, Button, Upload, Modal, Select, Tag, Space, Card, Statistic, Row, Col, message, Popconfirm
} from 'antd';
import { UploadOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { knowledgeAPI } from '../../api/knowledge';
import type { KnowledgeDocument, KBStats } from '../../api/knowledge';
import { formatFileSize, formatDate } from '../../utils/format';

export default function KnowledgePage() {
  const [docs, setDocs] = useState<KnowledgeDocument[]>([]);
  const [stats, setStats] = useState<KBStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [category, setCategory] = useState('');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [mounted, setMounted] = useState(false);

  const loadDocs = useCallback(async () => {
    setLoading(true);
    try {
      const [docsRes, statsRes] = await Promise.all([knowledgeAPI.list(), knowledgeAPI.stats()]);
      setDocs(docsRes.data);
      setStats(statsRes.data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!mounted) {
      setMounted(true);
      loadDocs();
    }
  }, [mounted, loadDocs]);

  const handleUpload = async () => {
    if (!uploadFile) return;
    setUploading(true);
    try {
      await knowledgeAPI.upload(uploadFile, category);
      message.success('文档上传成功');
      setUploadOpen(false);
      setUploadFile(null);
      setCategory('');
      loadDocs();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await knowledgeAPI.delete(id);
      message.success('已删除');
      loadDocs();
    } catch {
      message.error('删除失败');
    }
  };

  const statusColors: Record<string, string> = {
    processing: 'processing',
    indexed: 'success',
    failed: 'error',
  };

  const columns = [
    { title: '文件名', dataIndex: 'filename', key: 'filename', ellipsis: true },
    { title: '类型', dataIndex: 'file_type', key: 'type', width: 80 },
    { title: '大小', dataIndex: 'file_size', key: 'size', width: 100, render: (v: number) => formatFileSize(v) },
    { title: '分类', dataIndex: 'product_category', key: 'category', width: 100, render: (v: string | null) => v || '-' },
    { title: '分块数', dataIndex: 'chunk_count', key: 'chunks', width: 80 },
    { title: '状态', dataIndex: 'status', key: 'status', width: 100, render: (v: string) => <Tag color={statusColors[v]}>{v}</Tag> },
    { title: '时间', dataIndex: 'created_at', key: 'date', width: 120, render: (v: string) => formatDate(v) },
    {
      title: '操作', key: 'actions', width: 80,
      render: (_: unknown, r: KnowledgeDocument) => (
        <Popconfirm title="确认删除？" onConfirm={() => handleDelete(r.id)}>
          <Button type="text" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      ),
    },
  ];

  return (
    <div style={{ padding: 24 }}>
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}><Card><Statistic title="总文档数" value={stats?.total_documents || 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="总分块数" value={stats?.total_chunks || 0} /></Card></Col>
        <Col span={6}><Card><Statistic title="已索引" value={stats?.by_status?.indexed || 0} valueStyle={{ color: '#3f8600' }} /></Card></Col>
        <Col span={6}><Card><Statistic title="失败" value={stats?.by_status?.failed || 0} valueStyle={{ color: '#cf1322' }} /></Card></Col>
      </Row>

      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<UploadOutlined />} onClick={() => setUploadOpen(true)}>上传文档</Button>
        <Button icon={<ReloadOutlined />} onClick={loadDocs}>刷新</Button>
      </Space>

      <Table columns={columns} dataSource={docs} rowKey="id" loading={loading} pagination={{ pageSize: 20 }} />

      <Modal
        title="上传知识文档"
        open={uploadOpen}
        onOk={handleUpload}
        onCancel={() => { setUploadOpen(false); setUploadFile(null); }}
        confirmLoading={uploading}
      >
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8 }}>产品分类</div>
          <Select
            style={{ width: '100%' }}
            placeholder="选择产品分类（可选）"
            allowClear
            value={category || undefined}
            onChange={(v) => setCategory(v || '')}
            options={[
              { label: '手机', value: '手机' },
              { label: '电脑', value: '电脑' },
              { label: '家电', value: '家电' },
              { label: '服装', value: '服装' },
              { label: '食品', value: '食品' },
              { label: '其他', value: '其他' },
            ]}
          />
        </div>
        <Upload
          beforeUpload={(file) => { setUploadFile(file); return false; }}
          maxCount={1}
          onRemove={() => setUploadFile(null)}
          accept=".pdf,.docx,.txt,.md,.csv,.xlsx"
        >
          <Button icon={<UploadOutlined />}>选择文件</Button>
        </Upload>
      </Modal>
    </div>
  );
}
