import { createSlice } from '@reduxjs/toolkit'

const uiSlice = createSlice({
  name: 'ui',
  initialState: {
    showTaskForm: false,
    editingTaskId: null,
    toastMessage: null,
  },
  reducers: {
    openTaskForm(state, action) {
      state.showTaskForm = true
      state.editingTaskId = action.payload ?? null
    },
    closeTaskForm(state) {
      state.showTaskForm = false
      state.editingTaskId = null
    },
    showToast(state, action) {
      state.toastMessage = action.payload
    },
    clearToast(state) {
      state.toastMessage = null
    },
  },
})

export const { openTaskForm, closeTaskForm, showToast, clearToast } = uiSlice.actions
export default uiSlice.reducer
