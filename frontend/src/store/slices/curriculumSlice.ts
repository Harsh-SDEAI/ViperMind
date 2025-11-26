import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import curriculumService from '../../services/curriculum';

// Import types from the service
import { Topic, Section, Level } from '../../services/curriculum';

interface CurriculumState {
  levels: Level[];
  currentLevel: Level | null;
  currentSection: Section | null;
  currentTopic: Topic | null;
  loading: boolean;
  error: string | null;
  lastFetched: number | null;
  cacheExpiry: number;
}

const initialState: CurriculumState = {
  levels: [],
  currentLevel: null,
  currentSection: null,
  currentTopic: null,
  loading: false,
  error: null,
  lastFetched: null,
  cacheExpiry: 5 * 60 * 1000, // 5 minutes
};

// Async thunks with caching
export const fetchCurriculumStructure = createAsyncThunk(
  'curriculum/fetchStructure',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { curriculum: CurriculumState };
      const now = Date.now();
      
      // Check if we have cached data that's still valid
      if (
        state.curriculum.levels.length > 0 &&
        state.curriculum.lastFetched &&
        now - state.curriculum.lastFetched < state.curriculum.cacheExpiry
      ) {
        return { levels: state.curriculum.levels, fromCache: true };
      }
      
      const response = await curriculumService.getCurriculumStructure();
      return { levels: response.levels, fromCache: false };
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch curriculum structure');
    }
  }
);

export const fetchCurriculumWithProgress = createAsyncThunk(
  'curriculum/fetchWithProgress',
  async (_, { rejectWithValue }) => {
    try {
      const response = await curriculumService.getCurriculumWithProgress();
      return response.levels;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch curriculum with progress');
    }
  }
);

export const fetchLevelDetails = createAsyncThunk(
  'curriculum/fetchLevelDetails',
  async (levelId: string, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { curriculum: CurriculumState };
      
      // Check if we already have this level in cache
      const cachedLevel = state.curriculum.levels.find(level => level.id === levelId);
      if (cachedLevel && cachedLevel.sections.length > 0) {
        return { level: cachedLevel, fromCache: true };
      }
      
      const response = await curriculumService.getLevelDetails(levelId);
      return { level: response, fromCache: false };
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch level details');
    }
  }
);

const curriculumSlice = createSlice({
  name: 'curriculum',
  initialState,
  reducers: {
    setCurrentLevel: (state, action: PayloadAction<Level | null>) => {
      state.currentLevel = action.payload;
    },
    setCurrentSection: (state, action: PayloadAction<Section | null>) => {
      state.currentSection = action.payload;
    },
    setCurrentTopic: (state, action: PayloadAction<Topic | null>) => {
      state.currentTopic = action.payload;
    },
    updateTopicProgress: (state, action: PayloadAction<{ topicId: string; progress: Partial<Topic> }>) => {
      const { topicId, progress } = action.payload;
      
      // Update in levels array
      state.levels.forEach(level => {
        level.sections.forEach(section => {
          const topic = section.topics.find(t => t.id === topicId);
          if (topic) {
            Object.assign(topic, progress);
          }
        });
      });
      
      // Update current topic if it matches
      if (state.currentTopic && state.currentTopic.id === topicId) {
        Object.assign(state.currentTopic, progress);
      }
    },
    clearError: (state) => {
      state.error = null;
    },
    invalidateCache: (state) => {
      state.lastFetched = null;
    },
    refreshAfterLevelAdvancement: (state) => {
      // Force refresh by invalidating cache and clearing current data
      state.lastFetched = null;
      state.levels = [];
      state.currentLevel = null;
      state.currentSection = null;
      state.currentTopic = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch curriculum structure
      .addCase(fetchCurriculumStructure.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCurriculumStructure.fulfilled, (state, action) => {
        state.loading = false;
        state.levels = action.payload.levels;
        if (!action.payload.fromCache) {
          state.lastFetched = Date.now();
        }
      })
      .addCase(fetchCurriculumStructure.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch curriculum with progress
      .addCase(fetchCurriculumWithProgress.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCurriculumWithProgress.fulfilled, (state, action) => {
        state.loading = false;
        state.levels = action.payload;
        state.lastFetched = Date.now();
      })
      .addCase(fetchCurriculumWithProgress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch level details
      .addCase(fetchLevelDetails.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchLevelDetails.fulfilled, (state, action) => {
        state.loading = false;
        const { level } = action.payload;
        
        // Update or add level in the levels array
        const existingIndex = state.levels.findIndex(l => l.id === level.id);
        if (existingIndex >= 0) {
          state.levels[existingIndex] = level;
        } else {
          state.levels.push(level);
          state.levels.sort((a, b) => a.order - b.order);
        }
        
        state.currentLevel = level;
      })
      .addCase(fetchLevelDetails.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  setCurrentLevel,
  setCurrentSection,
  setCurrentTopic,
  updateTopicProgress,
  clearError,
  invalidateCache,
  refreshAfterLevelAdvancement,
} = curriculumSlice.actions;

// Selectors with memoization
export const selectCurriculumLevels = (state: { curriculum: CurriculumState }) => state.curriculum.levels;
export const selectCurrentLevel = (state: { curriculum: CurriculumState }) => state.curriculum.currentLevel;
export const selectCurrentSection = (state: { curriculum: CurriculumState }) => state.curriculum.currentSection;
export const selectCurrentTopic = (state: { curriculum: CurriculumState }) => state.curriculum.currentTopic;
export const selectCurriculumLoading = (state: { curriculum: CurriculumState }) => state.curriculum.loading;
export const selectCurriculumError = (state: { curriculum: CurriculumState }) => state.curriculum.error;

export const selectLevelById = (levelId: string) => (state: { curriculum: CurriculumState }) =>
  state.curriculum.levels.find(level => level.id === levelId);

export const selectSectionById = (sectionId: string) => (state: { curriculum: CurriculumState }) => {
  for (const level of state.curriculum.levels) {
    const section = level.sections.find(s => s.id === sectionId);
    if (section) return section;
  }
  return null;
};

export const selectTopicById = (topicId: string) => (state: { curriculum: CurriculumState }) => {
  for (const level of state.curriculum.levels) {
    for (const section of level.sections) {
      const topic = section.topics.find(t => t.id === topicId);
      if (topic) return topic;
    }
  }
  return null;
};

export const selectUserProgress = (state: { curriculum: CurriculumState }) => {
  const totalTopics = state.curriculum.levels.reduce(
    (total, level) => total + level.sections.reduce(
      (sectionTotal, section) => sectionTotal + section.topics.length, 0
    ), 0
  );
  
  const completedTopics = state.curriculum.levels.reduce(
    (total, level) => total + level.sections.reduce(
      (sectionTotal, section) => sectionTotal + section.topics.filter(
        topic => topic.is_completed
      ).length, 0
    ), 0
  );
  
  return {
    totalTopics,
    completedTopics,
    progressPercentage: totalTopics > 0 ? (completedTopics / totalTopics) * 100 : 0,
  };
};

export default curriculumSlice.reducer;