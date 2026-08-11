import { beforeEach, describe, expect, it, vi } from 'vitest'
import * as authApi from '../../api/authApi'
import * as userApi from '../../api/userApi'
import reducer, { fetchCurrentUser, loginUser, logout, registerUser } from './authSlice'

vi.mock('../../api/authApi')
vi.mock('../../api/userApi')

describe('authSlice', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('has the expected initial state when no token is stored', () => {
    const state = reducer(undefined, { type: '@@INIT' })
    expect(state.isAuthenticated).toBe(false)
    expect(state.user).toBeNull()
  })

  it('registerUser.fulfilled marks the user authenticated and stores the token', async () => {
    authApi.register.mockResolvedValue({
      user_id: 1,
      email: 'a@example.com',
      display_name: 'Alice',
      access_token: 'tok123',
    })

    const action = await registerUser({ email: 'a@example.com', password: 'pw', displayName: 'Alice' })(
      vi.fn(),
      () => ({}),
      undefined,
    )
    const state = reducer(undefined, action)

    expect(state.isAuthenticated).toBe(true)
    expect(state.token).toBe('tok123')
    expect(state.user.display_name).toBe('Alice')
    expect(localStorage.getItem('dosmart_access_token')).toBe('tok123')
  })

  it('loginUser.rejected records the error and does not authenticate', async () => {
    authApi.login.mockRejectedValue(new Error('Invalid email or password'))

    const action = await loginUser({ email: 'a@example.com', password: 'wrong' })(vi.fn(), () => ({}), undefined)
    const state = reducer(undefined, action)

    expect(state.isAuthenticated).toBe(false)
    expect(state.error).toBe('Invalid email or password')
  })

  it('fetchCurrentUser.fulfilled populates the user', async () => {
    userApi.getSettings.mockResolvedValue({ user_id: 2, email: 'b@example.com', display_name: 'Bob' })

    const action = await fetchCurrentUser()(vi.fn(), () => ({}), undefined)
    const state = reducer(undefined, action)

    expect(state.user).toEqual({ user_id: 2, email: 'b@example.com', display_name: 'Bob' })
  })

  it('logout clears authentication state and storage', () => {
    localStorage.setItem('dosmart_access_token', 'tok123')
    const loggedInState = { isAuthenticated: true, token: 'tok123', user: { user_id: 1 }, error: null, isLoading: false }

    const state = reducer(loggedInState, logout())

    expect(state.isAuthenticated).toBe(false)
    expect(state.token).toBeNull()
    expect(localStorage.getItem('dosmart_access_token')).toBeNull()
  })
})
