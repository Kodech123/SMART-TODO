import { configureStore } from '@reduxjs/toolkit'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import authReducer from '../features/auth/authSlice'
import categoriesReducer from '../features/categories/categoriesSlice'
import remindersReducer from '../features/reminders/remindersSlice'
import tasksReducer from '../features/tasks/tasksSlice'
import uiReducer from '../features/ui/uiSlice'

export function buildTestStore(preloadedState = {}) {
  return configureStore({
    reducer: {
      auth: authReducer,
      tasks: tasksReducer,
      reminders: remindersReducer,
      categories: categoriesReducer,
      ui: uiReducer,
    },
    preloadedState,
  })
}

export function renderWithProviders(ui, { preloadedState = {}, store = buildTestStore(preloadedState) } = {}) {
  function Wrapper({ children }) {
    return (
      <Provider store={store}>
        <MemoryRouter>{children}</MemoryRouter>
      </Provider>
    )
  }
  return { store, ...render(ui, { wrapper: Wrapper }) }
}
