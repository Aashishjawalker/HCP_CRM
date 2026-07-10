import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { sendChatMessage, createInteraction, getInteractions, updateInteraction, deleteInteraction, transcribeAudio } from '../api';

export const submitChatMessage = createAsyncThunk(
  'interactions/submitChatMessage',
  async (message, { rejectWithValue }) => {
    try {
      const data = await sendChatMessage(message);
      return data;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const submitTranscription = createAsyncThunk(
  'interactions/submitTranscription',
  async (audioBlob, { rejectWithValue, dispatch }) => {
    try {
      const text = await transcribeAudio(audioBlob);
      // Auto-submit transcribed text to the agent
      dispatch(submitChatMessage(text));
      return text;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const submitFormData = createAsyncThunk(
  'interactions/submitFormData',
  async (data, { rejectWithValue }) => {
    try {
      return await createInteraction(data);
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const fetchInteractions = createAsyncThunk(
  'interactions/fetchInteractions',
  async (_, { rejectWithValue }) => {
    try {
      return await getInteractions();
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const updateInteractionThunk = createAsyncThunk(
  'interactions/updateInteraction',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      return await updateInteraction(id, data);
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const deleteInteractionThunk = createAsyncThunk(
  'interactions/deleteInteraction',
  async (id, { rejectWithValue }) => {
    try {
      await deleteInteraction(id);
      return id;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);


const interactionSlice = createSlice({
  name: 'interactions',
  initialState: {
    list: [],
    loading: false,
    error: null,

    currentForm: {
      hcpName: '',
      interactionType: 'Meeting',
      date: '',
      time: '',
      attendees: '',
      topicsDiscussed: '',
      sentiment: 'Neutral',
      materialsShared: '',
    },

    chat: {
      messages: [
        { role: 'bot', text: 'Hi! Describe your interaction (e.g. "Met Dr. Sharma on Oct 15 at 3pm, discussed new product").' },
      ],
      loading: false,
    },

    submitSuccess: null,
    submitError: null,
    lastExtractedId: null, 
  },
  reducers: {
    updateFormField(state, action) {
      const { field, value } = action.payload;
      state.currentForm[field] = value;
    },

    setCurrentForm(state, action) {
      state.currentForm = { ...state.currentForm, ...action.payload };
    },

    addChatMessage(state, action) {
      state.chat.messages.push(action.payload);
    },

    clearFeedback(state) {
      state.submitSuccess = null;
      state.submitError = null;
    },

    resetForm(state) {
      state.currentForm = {
        hcpName: '',
        interactionType: 'Meeting',
        date: '',
        time: '',
        attendees: '',
        topicsDiscussed: '',
        sentiment: 'Neutral',
        materialsShared: '',
      };
      state.lastExtractedId = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(submitChatMessage.pending, (state) => {
        state.chat.loading = true;
        state.error = null;
      })
      .addCase(submitChatMessage.fulfilled, (state, action) => {
        state.chat.loading = false;
        const { response, formState } = action.payload;

        state.chat.messages.push({ role: 'bot', text: response });

        if (formState) {
          Object.keys(formState).forEach((key) => {
            if (key in state.currentForm && formState[key] !== null && formState[key] !== undefined) {
              state.currentForm[key] = formState[key];
            }
          });
        }

        if (action.payload.id) {
          state.lastExtractedId = action.payload.id;
        }

        state.submitSuccess = 'Chat processed successfully!';
      })
      .addCase(submitChatMessage.rejected, (state, action) => {
        state.chat.loading = false;
        state.error = action.payload || 'Failed to process chat message';
        state.chat.messages.push({
          role: 'bot',
          text: `Sorry, something went wrong: ${action.payload || 'Unknown error'}`,
        });
      });

    builder
      .addCase(submitTranscription.pending, (state) => {
        state.chat.loading = true;
      })
      .addCase(submitTranscription.fulfilled, (state) => {
        state.chat.loading = true; // keep loading — submitChatMessage is chained
      })
      .addCase(submitTranscription.rejected, (state, action) => {
        state.chat.loading = false;
        state.chat.messages.push({
          role: 'bot',
          text: `Transcription failed: ${action.payload || 'Unknown error'}`,
        });
      });

    builder
      .addCase(submitFormData.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.submitSuccess = null;
        state.submitError = null;
      })
      .addCase(submitFormData.fulfilled, (state) => {
        state.loading = false;
        state.submitSuccess = 'Interaction logged successfully!';
      })
      .addCase(submitFormData.rejected, (state, action) => {
        state.loading = false;
        state.submitError = action.payload || 'Failed to log interaction';
      });

    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload;
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to fetch interactions';
      });

    builder
      .addCase(updateInteractionThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateInteractionThunk.fulfilled, (state, action) => {
        state.loading = false;
        const updated = action.payload;
        const idx = state.list.findIndex((i) => i.id === updated.id);
        if (idx !== -1) {
          state.list[idx] = updated;
        } else {
          state.list.push(updated);
        }
        state.submitSuccess = 'Interaction updated successfully!';
      })
      .addCase(updateInteractionThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to update interaction';
      });

    builder
      .addCase(deleteInteractionThunk.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteInteractionThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.list = state.list.filter((i) => i.id !== action.payload);
        state.submitSuccess = `Deleted interaction #${action.payload}`;
      })
      .addCase(deleteInteractionThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to delete interaction';
      });
  },
});

export const {
  updateFormField,
  setCurrentForm,
  addChatMessage,
  clearFeedback,
  resetForm,
} = interactionSlice.actions;

export default interactionSlice.reducer;
