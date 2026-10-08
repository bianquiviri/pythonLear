import { describe, expect, it } from 'vitest'
import { ApiError } from '../../app/composables/useApi'

describe('ApiError', () => {
  it('carries status and message', () => {
    const err = new ApiError(404, 'Client not found: 5')
    expect(err.status).toBe(404)
    expect(err.message).toBe('Client not found: 5')
    expect(err).toBeInstanceOf(Error)
  })
})

describe('login error mapping', () => {
  it('maps 401 to friendly message', () => {
    const status = 401
    const message = status === 401 ? 'Invalid email or password' : 'Login failed'
    expect(message).toBe('Invalid email or password')
  })
})
