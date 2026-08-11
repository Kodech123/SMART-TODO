import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import * as remindersApi from '../../api/remindersApi'

export const fetchReminders = createAsyncThunk('reminders/fetchAll', async (status = 'pending') =>
  remindersApi.listReminders({ status }),
)

export const snoozeReminder = createAsyncThunk('reminders/snooze', async ({ reminderId, minutes }, { dispatch }) => {
  const result = await remindersApi.snoozeReminder(reminderId, minutes)
  dispatch(fetchReminders())
  return result
})

const remindersSlice = createSlice({
  name: 'reminders',
  initialState: {
    items: [],
    isLoading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchReminders.pending, (state) => {
        state.isLoading = true
      })
      .addCase(fetchReminders.fulfilled, (state, action) => {
        state.isLoading = false
        state.items = action.payload.reminders
      })
      .addCase(fetchReminders.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.error.message
      })
  },
})

export default remindersSlice.reducer
