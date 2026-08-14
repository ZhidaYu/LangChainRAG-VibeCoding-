import { describe, it, expect, beforeEach, vi } from 'vitest'

vi.mock('../src/api/auth', () => ({
  authAPI: {
    login: vi.fn(),
    register: vi.fn(),
    me: vi.fn(),
    changePassword: vi.fn(),
  },
}))

vi.mock('../src/api/chat', () => ({
  conversationAPI: {
    list: vi.fn(),
    create: vi.fn(),
    getMessages: vi.fn(),
    delete: vi.fn(),
  },
}))

import { authAPI } from '../src/api/auth'
import { useAuthStore } from '../src/stores/authStore'
import { getAccessToken, getRefreshToken } from '../src/utils/token'

// Mock localStorage
const store: Record<string, string> = {}
beforeEach(() => {
  for (const key in store) delete store[key]
  vi.clearAllMocks()
  useAuthStore.setState({ user: null })
})
Object.defineProperty(globalThis, 'localStorage', {
  value: {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
  },
  writable: true,
})

const mockUser = {
  id: 'u-1',
  username: 'alice',
  role: 'user',
  is_active: 1,
  created_at: '2025-01-01T00:00:00',
}

describe('authStore', () => {
  it('should login and store tokens + user', async () => {
    vi.mocked(authAPI.login).mockResolvedValue({
      data: { access_token: 'acc-1', refresh_token: 'ref-1' },
    } as any)
    vi.mocked(authAPI.me).mockResolvedValue({ data: mockUser } as any)

    await useAuthStore.getState().login('alice', 'pw123456')

    expect(getAccessToken()).toBe('acc-1')
    expect(getRefreshToken()).toBe('ref-1')
    expect(useAuthStore.getState().user?.username).toBe('alice')
  })

  it('should not set user or tokens when login fails', async () => {
    vi.mocked(authAPI.login).mockRejectedValue(new Error('401'))

    await expect(
      useAuthStore.getState().login('alice', 'bad-password')
    ).rejects.toThrow('401')

    expect(useAuthStore.getState().user).toBeNull()
    expect(getAccessToken()).toBeNull()
  })

  it('should register and set user', async () => {
    vi.mocked(authAPI.register).mockResolvedValue({
      data: { access_token: 'acc-2', refresh_token: 'ref-2' },
    } as any)
    vi.mocked(authAPI.me).mockResolvedValue({ data: mockUser } as any)

    await useAuthStore.getState().register('alice', 'pw123456')

    expect(getAccessToken()).toBe('acc-2')
    expect(useAuthStore.getState().user).toEqual(mockUser)
  })

  it('should init without token do nothing', async () => {
    await useAuthStore.getState().init()

    expect(authAPI.me).not.toHaveBeenCalled()
    expect(useAuthStore.getState().user).toBeNull()
  })

  it('should init with token fetch current user', async () => {
    store['rag_access_token'] = 'acc-3'
    vi.mocked(authAPI.me).mockResolvedValue({ data: mockUser } as any)

    await useAuthStore.getState().init()

    expect(authAPI.me).toHaveBeenCalledTimes(1)
    expect(useAuthStore.getState().user?.username).toBe('alice')
  })

  it('should init clear tokens when me fails', async () => {
    store['rag_access_token'] = 'acc-3'
    store['rag_refresh_token'] = 'ref-3'
    vi.mocked(authAPI.me).mockRejectedValue(new Error('401'))

    await useAuthStore.getState().init()

    expect(useAuthStore.getState().user).toBeNull()
    expect(getAccessToken()).toBeNull()
    expect(getRefreshToken()).toBeNull()
  })

  it('should logout clear user and tokens', () => {
    store['rag_access_token'] = 'acc-4'
    store['rag_refresh_token'] = 'ref-4'
    useAuthStore.setState({ user: mockUser })

    useAuthStore.getState().logout()

    expect(useAuthStore.getState().user).toBeNull()
    expect(getAccessToken()).toBeNull()
    expect(getRefreshToken()).toBeNull()
  })

  it('should call changePassword API with given passwords', async () => {
    vi.mocked(authAPI.changePassword).mockResolvedValue({ data: {} } as any)

    await useAuthStore.getState().changePassword('old-pass', 'new-pass')

    expect(authAPI.changePassword).toHaveBeenCalledWith('old-pass', 'new-pass')
  })
})
