import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import * as categoriesApi from '../../api/categoriesApi'

export const fetchCategories = createAsyncThunk('categories/fetchAll', async () => categoriesApi.listCategories())

const categoriesSlice = createSlice({
  name: 'categories',
  initialState: {
    items: [],
    isLoading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchCategories.pending, (state) => {
        state.isLoading = true
      })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.isLoading = false
        state.items = action.payload
      })
      .addCase(fetchCategories.rejected, (state, action) => {
        state.isLoading = false
        state.error = action.error.message
      })
  },
})

export default categoriesSlice.reducer
