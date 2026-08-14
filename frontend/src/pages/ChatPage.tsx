import { useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { message, Result, Button } from 'antd';
import ConversationList from '../components/chat/ConversationList';
import MessageBubble from '../components/chat/MessageBubble';
import ChatInput from '../components/chat/ChatInput';
import { useChatStore } from '../stores/chatStore';
import type { SourceMeta } from '../stores/chatStore';
import { useSSE } from '../hooks/useSSE';

export default function ChatPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { sendQuery } = useSSE();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    conversations,
    currentConvId,
    messages,
    streaming,
    streamingContent,
    sources,
    loadConversations,
    createConversation,
    selectConversation,
    deleteConversation,
    addMessage,
    setStreaming,
    appendStreamToken,
    setSources,
    resetStream,
  } = useChatStore();

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    if (id && id !== currentConvId) {
      selectConversation(id);
    }
  }, [id, currentConvId, selectConversation]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  const handleNew = useCallback(async () => {
    const newId = await createConversation();
    navigate(`/chat/${newId}`);
  }, [createConversation, navigate]);

  const handleSelect = useCallback(
    (convId: string) => {
      navigate(`/chat/${convId}`);
    },
    [navigate]
  );

  const handleDelete = useCallback(
    async (convId: string) => {
      await deleteConversation(convId);
      if (convId === currentConvId) {
        navigate('/chat');
      }
    },
    [deleteConversation, currentConvId, navigate]
  );

  const handleSend = useCallback(
    async (question: string) => {
      let convId = currentConvId;
      if (!convId) {
        const newId = await createConversation();
        convId = newId;
        navigate(`/chat/${newId}`);
      }

      // Add user message to UI
      addMessage({
        id: `temp-${Date.now()}`,
        conversation_id: convId,
        role: 'user',
        content: question,
        sources: '[]',
        created_at: new Date().toISOString(),
      });

      // Start streaming
      setStreaming(true);
      let fullSources: SourceMeta[] = [];

      await sendQuery(question, convId, {
        onToken: (token) => {
          appendStreamToken(token);
        },
        onSources: (srcs) => {
          fullSources = srcs;
          setSources(srcs);
        },
        onDone: () => {
          const answer = useChatStore.getState().streamingContent;
          addMessage({
            id: `temp-resp-${Date.now()}`,
            conversation_id: convId,
            role: 'assistant',
            content: answer,
            sources: JSON.stringify(fullSources),
            created_at: new Date().toISOString(),
          });
          resetStream();
          loadConversations();
        },
        onError: (err) => {
          message.error(err);
          setStreaming(false);
        },
      });
    },
    [
      currentConvId,
      createConversation,
      navigate,
      addMessage,
      setStreaming,
      appendStreamToken,
      setSources,
      resetStream,
      sendQuery,
      loadConversations,
    ]
  );

  return (
    <div style={{ display: 'flex', height: '100%' }}>
      {/* Sidebar */}
      <div style={{ width: 280, borderRight: '1px solid #f0f0f0', flexShrink: 0 }}>
        <ConversationList
          currentId={currentConvId}
          onSelect={handleSelect}
          onNew={handleNew}
          onDelete={handleDelete}
        />
      </div>

      {/* Main Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {!currentConvId ? (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Result
              icon={<span style={{ fontSize: 48 }}>💬</span>}
              title="向知识库提问，开始对话"
              extra={
                <Button type="primary" onClick={handleNew}>
                  开始新对话
                </Button>
              }
            />
          </div>
        ) : (
          <>
            <div style={{ flex: 1, overflow: 'auto', padding: '16px 24px' }}>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} message={msg} />
              ))}
              {streaming && streamingContent && (
                <MessageBubble isStreaming streamingContent={streamingContent} sources={sources} />
              )}
              <div ref={messagesEndRef} />
            </div>
            <ChatInput onSend={handleSend} disabled={streaming} />
          </>
        )}
      </div>
    </div>
  );
}
