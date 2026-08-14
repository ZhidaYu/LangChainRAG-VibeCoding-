import { Card, Tag } from 'antd';
import { FileTextOutlined } from '@ant-design/icons';
import type { SourceMeta } from '../../stores/chatStore';

export default function CitationCard({ source }: { source: SourceMeta }) {
  const scorePercent = Math.round(source.score * 100);

  return (
    <Card
      size="small"
      title={
        <span>
          <FileTextOutlined style={{ marginRight: 4 }} />
          Source {source.source_id}: {source.file}
        </span>
      }
      extra={<Tag color={scorePercent > 80 ? 'green' : 'orange'}>相关度 {scorePercent}%</Tag>}
      style={{ marginBottom: 8, background: '#fafafa' }}
    >
      <p style={{ margin: 0, color: '#666', fontSize: 13 }}>&ldquo;{source.chunk_text}&rdquo;</p>
    </Card>
  );
}
