import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import * as authApi from '../../api/authApi'
import * as userApi from '../../api/userApi'

const TOKEN_STORAGE_KEY = 'dosmart_access_token'

export const registerUser = createAsyncThunk('auth/register', async ({ email, password, displayName }) => {
  const data = await authApi.register({ email, password, displayName })
  return { token: data.access_token, user: { user_id: data.user_id, email: data.email, display_name: data.display_name } }
})

export const loginUser = createAsyncThunk('auth/login', async ({ email, password }) => {
  const data = await authApi.login({ email, password })
  return data.access_token
})

export const fetchCurrentUser = createAsyncThunk('auth/fetchCurrentUser', async () => {
  const settings = await userApi.getSettings()
  return {
    user_id: settings.user_id,
    email: settings.email,
    display_name: settings.display_name,
  }
})

const initialState = {
  isAuthenticated: Boolean(localStorage.getItem(TOKEN_STORAGE_KEY)),
  user: null,
  token: localStorage.getItem(TOKEN_STORAGE_KEY),
  error: null,
  isLoading: false,
}

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout(state) {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
      state.isAuthenticated = false
      state.user = null
      state.token = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = true
        state.token = action.payload.token
        state.user = action.payload.user
        localStorage.setItem(TOKEN_STORAGE_KEY, action.payload.token)
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.error.message
      })
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true
        state.error = null
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false
        state.isAuthenticated = true
        state.token = action.payload
        localStorage.setItem(TOKEN_STORAGE_KEY, action.payload)
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.error.message
      })
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload
      })
  },
})

export const { logout } = authSlice.actions
export default authSlice.reducer
