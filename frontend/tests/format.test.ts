import { describe, it, expect } from 'vitest'
import { formatFileSize, formatDate } from '../src/utils/format'

describe('formatFileSize', () => {
  it('should format bytes', () => {
    expect(formatFileSize(500)).toBe('500 B')
  })

  it('should format KB', () => {
    expect(formatFileSize(2048)).toBe('2.0 KB')
  })

  it('should format MB', () => {
    expect(formatFileSize(2097152)).toBe('2.0 MB')
  })

  it('should handle zero', () => {
    expect(formatFileSize(0)).toBe('0 B')
  })
})

describe('formatDate', () => {
  it('should show today for current date', () => {
    const today = new Date().toISOString()
    expect(formatDate(today)).toBe('今天')
  })

  it('should show yesterday', () => {
    const yesterday = new Date(Date.now() - 86400000).toISOString()
    expect(formatDate(yesterday)).toBe('昨天')
  })

  it('should show locale date for old dates', () => {
    const old = new Date('2024-01-01').toISOString()
    const result = formatDate(old)
    expect(result).toContain('2024')
  })
})
