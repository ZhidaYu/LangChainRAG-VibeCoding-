import { useCallback } from 'react';
import { getAccessToken } from '../utils/token';

interface SSECallbacks {
  onToken: (token: string) => void;
  onSources: (sources: any[]) => void;
  onDone: () => void;
  onError: (error: string) => void;
}

export function useSSE() {
  const sendQuery = useCallback(
    async (question: string, conversationId: string, callbacks: SSECallbacks) => {
      const token = getAccessToken();
      if (!token) return;

      try {
        const response = await fetch('http://localhost:8000/api/chat/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            question,
            conversation_id: conversationId,
          }),
        });

        if (!response.ok) {
          const err = await response.json();
          callbacks.onError(err.detail || '请求失败');
          return;
        }

        const reader = response.body?.getReader();
        if (!reader) {
          callbacks.onError('无法读取响应流');
          return;
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.slice(6).trim();
              if (!dataStr) continue;
              try {
                const data = JSON.parse(dataStr);
                if (data.type === 'token') {
                  callbacks.onToken(data.content);
                } else if (data.type === 'sources') {
                  callbacks.onSources(data.sources || []);
                } else if (data.type === 'done') {
                  callbacks.onDone();
                } else if (data.type === 'error') {
                  callbacks.onError(data.detail || '未知错误');
                }
              } catch {
                // Skip malformed JSON lines
              }
            }
          }
        }
      } catch (err: any) {
        callbacks.onError(err.message || '网络错误');
      }
    },
    []
  );

  return { sendQuery };
}
