import { describe, it, expect, beforeEach } from 'vitest'
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from '../src/utils/token'

// Mock localStorage
const store: Record<string, string> = {}
beforeEach(() => {
  for (const key in store) delete store[key]
})
Object.defineProperty(globalThis, 'localStorage', {
  value: {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
  },
  writable: true,
})

describe('Token Utilities', () => {
  it('should return null when no token stored', () => {
    expect(getAccessToken()).toBeNull()
    expect(getRefreshToken()).toBeNull()
  })

  it('should store and retrieve tokens', () => {
    setTokens('access-abc', 'refresh-xyz')
    expect(getAccessToken()).toBe('access-abc')
    expect(getRefreshToken()).toBe('refresh-xyz')
  })

  it('should clear tokens', () => {
    setTokens('access-abc', 'refresh-xyz')
    clearTokens()
    expect(getAccessToken()).toBeNull()
    expect(getRefreshToken()).toBeNull()
  })

  it('should overwrite old tokens', () => {
    setTokens('old-access', 'old-refresh')
    setTokens('new-access', 'new-refresh')
    expect(getAccessToken()).toBe('new-access')
    expect(getRefreshToken()).toBe('new-refresh')
  })
})
