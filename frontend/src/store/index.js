import { configureStore } from '@reduxjs/toolkit';
import interactionReducer from './interactionSlice';

const store = configureStore({
  reducer: {
    interactions: interactionReducer,
  },
});

export default store;
