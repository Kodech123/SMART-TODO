import { configureStore } from '@reduxjs/toolkit'
import authReducer from '../features/auth/authSlice'
import categoriesReducer from '../features/categories/categoriesSlice'
import remindersReducer from '../features/reminders/remindersSlice'
import tasksReducer from '../features/tasks/tasksSlice'
import uiReducer from '../features/ui/uiSlice'

export const store = configureStore({
  reducer: {
    auth: authReducer,
    tasks: tasksReducer,
    reminders: remindersReducer,
    categories: categoriesReducer,
    ui: uiReducer,
  },
})
