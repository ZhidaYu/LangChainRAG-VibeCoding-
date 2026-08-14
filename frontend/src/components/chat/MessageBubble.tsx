import { useState } from 'react';
import { Typography, Collapse, Space } from 'antd';
import { UserOutlined, RobotOutlined, CaretRightOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import CitationCard from './CitationCard';
import type { Message } from '../../api/chat';
import type { SourceMeta } from '../../stores/chatStore';

const { Text } = Typography;

interface Props {
  message?: Message;
  streamingContent?: string;
  sources?: SourceMeta[];
  isStreaming?: boolean;
}

export default function MessageBubble({ message, streamingContent, sources = [], isStreaming }: Props) {
  const isUser = message?.role === 'user';
  const content = message?.content || streamingContent || '';
  const parsedSources: SourceMeta[] = message?.sources
    ? (() => { try { return JSON.parse(message.sources); } catch { return []; } })()
    : sources;

  const [showSources, setShowSources] = useState(false);

  return (
    <div style={{ display: 'flex', marginBottom: 16, flexDirection: isUser ? 'row-reverse' : 'row' }}>
      <div
        style={{
          width: 36,
          height: 36,
          borderRadius: '50%',
          background: isUser ? '#1677ff' : '#52c41a',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: isUser ? '0 0 0 12px' : '0 12px 0 0',
          flexShrink: 0,
        }}
      >
        {isUser ? (
          <UserOutlined style={{ color: '#fff' }} />
        ) : (
          <RobotOutlined style={{ color: '#fff' }} />
        )}
      </div>
      <div style={{ maxWidth: '70%' }}>
        <div
          style={{
            padding: '10px 16px',
            borderRadius: 12,
            background: isUser ? '#e6f4ff' : '#f6ffed',
            lineHeight: 1.7,
          }}
        >
          {isUser ? (
            <Text>{content}</Text>
          ) : (
            <div>
              <ReactMarkdown>{content}</ReactMarkdown>
              {isStreaming && <span className="cursor-blink">▌</span>}
            </div>
          )}
        </div>
        {!isUser && parsedSources.length > 0 && !isStreaming && (
          <div style={{ marginTop: 8 }}>
            <a onClick={() => setShowSources(!showSources)} style={{ fontSize: 12 }}>
              <CaretRightOutlined rotate={showSources ? 90 : 0} />
              {showSources ? '收起' : '查看'} {parsedSources.length} 个引用来源
            </a>
            {showSources && (
              <div style={{ marginTop: 8 }}>
                {parsedSources.map((s) => (
                  <CitationCard key={s.source_id} source={s} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
