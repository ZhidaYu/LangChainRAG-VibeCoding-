import { describe, it, expect, beforeEach, vi } from 'vitest'

vi.mock('../src/api/chat', () => ({
  conversationAPI: {
    list: vi.fn(),
    create: vi.fn(),
    getMessages: vi.fn(),
    delete: vi.fn(),
  },
}))

import { conversationAPI } from '../src/api/chat'
import { useChatStore } from '../src/stores/chatStore'

const makeConv = (id: string) => ({
  id,
  title: `会话${id}`,
  is_active: 1,
  created_at: '2025-01-01T00:00:00',
  updated_at: '2025-01-01T00:00:00',
})

const makeMsg = (id: string, content: string) => ({
  id,
  conversation_id: 'c1',
  role: 'assistant',
  content,
  sources: '[]',
  created_at: '2025-01-01T00:00:00',
})

describe('chatStore', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    useChatStore.getState().reset()
  })

  it('should load conversations', async () => {
    vi.mocked(conversationAPI.list).mockResolvedValue({
      data: [makeConv('c1'), makeConv('c2')],
    } as any)

    await useChatStore.getState().loadConversations()

    expect(useChatStore.getState().conversations).toHaveLength(2)
  })

  it('should create conversation and select it', async () => {
    vi.mocked(conversationAPI.create).mockResolvedValue({
      data: makeConv('c-new'),
    } as any)

    const id = await useChatStore.getState().createConversation()

    const s = useChatStore.getState()
    expect(id).toBe('c-new')
    expect(s.currentConvId).toBe('c-new')
    expect(s.conversations[0].id).toBe('c-new')
  })

  it('should select conversation and load messages', async () => {
    vi.mocked(conversationAPI.getMessages).mockResolvedValue({
      data: [makeMsg('m1', '你好')],
    } as any)

    await useChatStore.getState().selectConversation('c1')

    const s = useChatStore.getState()
    expect(s.currentConvId).toBe('c1')
    expect(s.messages).toHaveLength(1)
    expect(s.messages[0].content).toBe('你好')
  })

  it('should delete current conversation and clear messages', async () => {
    vi.mocked(conversationAPI.list).mockResolvedValue({
      data: [makeConv('c1')],
    } as any)
    await useChatStore.getState().loadConversations()
    useChatStore.setState({
      currentConvId: 'c1',
      messages: [makeMsg('m1', 'x')],
    })

    vi.mocked(conversationAPI.delete).mockResolvedValue({ data: {} } as any)
    await useChatStore.getState().deleteConversation('c1')

    const s = useChatStore.getState()
    expect(s.conversations).toHaveLength(0)
    expect(s.currentConvId).toBeNull()
    expect(s.messages).toHaveLength(0)
  })

  it('should delete non-current conversation keep current state', async () => {
    vi.mocked(conversationAPI.list).mockResolvedValue({
      data: [makeConv('c1'), makeConv('c2')],
    } as any)
    await useChatStore.getState().loadConversations()
    useChatStore.setState({
      currentConvId: 'c2',
      messages: [makeMsg('m1', 'x')],
    })

    vi.mocked(conversationAPI.delete).mockResolvedValue({ data: {} } as any)
    await useChatStore.getState().deleteConversation('c1')

    const s = useChatStore.getState()
    expect(s.currentConvId).toBe('c2')
    expect(s.messages).toHaveLength(1)
    expect(s.conversations.map((c) => c.id)).toEqual(['c2'])
  })

  it('should add messages', () => {
    useChatStore.getState().addMessage(makeMsg('m1', '第一条'))
    useChatStore.getState().addMessage(makeMsg('m2', '第二条'))

    expect(useChatStore.getState().messages).toHaveLength(2)
  })

  it('should track streaming state and append tokens', () => {
    const st = useChatStore.getState()
    st.setStreaming(true)
    st.appendStreamToken('你好')
    st.appendStreamToken('世界')

    expect(useChatStore.getState().streaming).toBe(true)
    expect(useChatStore.getState().streamingContent).toBe('你好世界')

    st.resetStream()
    expect(useChatStore.getState().streaming).toBe(false)
    expect(useChatStore.getState().streamingContent).toBe('')
  })

  it('should set sources', () => {
    const sources = [{ source_id: 1, file: 'a.txt', chunk_text: 't', score: 0.9 }]
    useChatStore.getState().setSources(sources)

    expect(useChatStore.getState().sources).toEqual(sources)
  })

  it('should reset to initial state', () => {
    useChatStore.setState({
      currentConvId: 'c1',
      messages: [makeMsg('m1', 'x')],
      streamingContent: 'abc',
    })

    useChatStore.getState().reset()

    const s = useChatStore.getState()
    expect(s.currentConvId).toBeNull()
    expect(s.messages).toHaveLength(0)
    expect(s.streamingContent).toBe('')
    expect(s.conversations).toHaveLength(0)
  })
})
