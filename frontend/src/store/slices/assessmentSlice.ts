import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import assessmentService from '../../services/assessments';

// Import types from the service
import { Assessment, AssessmentResult, AssessmentHistory } from '../../services/assessments';

interface AssessmentState {
  currentAssessment: Assessment | null;
  currentQuestionIndex: number;
  userAnswers: Record<string, number>;
  timeRemaining: number;
  isSubmitting: boolean;
  results: AssessmentResult | null;
  assessmentHistory: AssessmentHistory[];
  loading: boolean;
  error: string | null;
  cache: Record<string, { assessment: Assessment; timestamp: number }>;
  cacheExpiry: number;
}

const initialState: AssessmentState = {
  currentAssessment: null,
  currentQuestionIndex: 0,
  userAnswers: {},
  timeRemaining: 0,
  isSubmitting: false,
  results: null,
  assessmentHistory: [],
  loading: false,
  error: null,
  cache: {},
  cacheExpiry: 30 * 60 * 1000, // 30 minutes
};

// Async thunks
export const generateAssessment = createAsyncThunk(
  'assessment/generate',
  async (
    { type, targetId }: { type: string; targetId: string },
    { getState, rejectWithValue }
  ) => {
    try {
      const state = getState() as { assessment: AssessmentState };
      const cacheKey = `${type}_${targetId}`;
      const now = Date.now();
      
      // Check cache first
      const cached = state.assessment.cache[cacheKey];
      if (cached && now - cached.timestamp < state.assessment.cacheExpiry) {
        return { assessment: cached.assessment, fromCache: true };
      }
      
      const response = await assessmentService.generateAssessment({
        target_id: targetId,
        assessment_type: type as 'quiz' | 'section_test' | 'level_final'
      });
      
      return { assessment: response, fromCache: false, cacheKey };
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to generate assessment');
    }
  }
);

export const submitAssessment = createAsyncThunk(
  'assessment/submit',
  async (
    { assessmentId, answers }: { assessmentId: string; answers: Record<string, number> },
    { rejectWithValue }
  ) => {
    try {
      const response = await assessmentService.submitAssessment({
        assessment_id: assessmentId,
        answers: Object.entries(answers).map(([questionId, selectedAnswer]) => ({
          question_id: questionId,
          selected_answer: selectedAnswer
        })),
        time_taken: 0 // This should be calculated properly
      });
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to submit assessment');
    }
  }
);

export const fetchAssessmentHistory = createAsyncThunk(
  'assessment/fetchHistory',
  async (_, { rejectWithValue }) => {
    try {
      const response = await assessmentService.getAssessmentHistory();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.message || 'Failed to fetch assessment history');
    }
  }
);

const assessmentSlice = createSlice({
  name: 'assessment',
  initialState,
  reducers: {
    setCurrentQuestion: (state, action: PayloadAction<number>) => {
      state.currentQuestionIndex = action.payload;
    },
    answerQuestion: (state, action: PayloadAction<{ questionId: string; answer: number }>) => {
      const { questionId, answer } = action.payload;
      state.userAnswers[questionId] = answer;
    },
    setTimeRemaining: (state, action: PayloadAction<number>) => {
      state.timeRemaining = action.payload;
    },
    decrementTime: (state) => {
      if (state.timeRemaining > 0) {
        state.timeRemaining -= 1;
      }
    },
    nextQuestion: (state) => {
      if (state.currentAssessment && state.currentQuestionIndex < state.currentAssessment.questions.length - 1) {
        state.currentQuestionIndex += 1;
      }
    },
    previousQuestion: (state) => {
      if (state.currentQuestionIndex > 0) {
        state.currentQuestionIndex -= 1;
      }
    },
    resetAssessment: (state) => {
      state.currentAssessment = null;
      state.currentQuestionIndex = 0;
      state.userAnswers = {};
      state.timeRemaining = 0;
      state.results = null;
      state.error = null;
    },
    clearError: (state) => {
      state.error = null;
    },
    invalidateCache: (state, action: PayloadAction<string | undefined>) => {
      if (action.payload) {
        delete state.cache[action.payload];
      } else {
        state.cache = {};
      }
    },
  },
  extraReducers: (builder) => {
    builder
      // Generate assessment
      .addCase(generateAssessment.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(generateAssessment.fulfilled, (state, action) => {
        state.loading = false;
        const { assessment, fromCache, cacheKey } = action.payload;
        
        state.currentAssessment = assessment;
        state.currentQuestionIndex = 0;
        state.userAnswers = {};
        
        // Set timer from assessment time limit
        state.timeRemaining = assessment.time_limit * 60; // Convert minutes to seconds
        
        // Cache the assessment if not from cache
        if (!fromCache && cacheKey) {
          state.cache[cacheKey] = {
            assessment,
            timestamp: Date.now(),
          };
        }
      })
      .addCase(generateAssessment.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Submit assessment
      .addCase(submitAssessment.pending, (state) => {
        state.isSubmitting = true;
        state.error = null;
      })
      .addCase(submitAssessment.fulfilled, (state, action) => {
        state.isSubmitting = false;
        state.results = action.payload;
        
        // Note: AssessmentResult and AssessmentHistory are different types
        // We should fetch the updated history separately rather than trying to convert types
        
        // Clear cache for this assessment type/target
        if (state.currentAssessment) {
          const cacheKey = `${state.currentAssessment.assessment_type}_${state.currentAssessment.target_id}`;
          delete state.cache[cacheKey];
        }
      })
      .addCase(submitAssessment.rejected, (state, action) => {
        state.isSubmitting = false;
        state.error = action.payload as string;
      })
      
      // Fetch assessment history
      .addCase(fetchAssessmentHistory.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchAssessmentHistory.fulfilled, (state, action) => {
        state.loading = false;
        state.assessmentHistory = action.payload;
      })
      .addCase(fetchAssessmentHistory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  setCurrentQuestion,
  answerQuestion,
  setTimeRemaining,
  decrementTime,
  nextQuestion,
  previousQuestion,
  resetAssessment,
  clearError,
  invalidateCache,
} = assessmentSlice.actions;

// Selectors
export const selectCurrentAssessment = (state: { assessment: AssessmentState }) => state.assessment.currentAssessment;
export const selectCurrentQuestion = (state: { assessment: AssessmentState }) => {
  const { currentAssessment, currentQuestionIndex } = state.assessment;
  return currentAssessment?.questions[currentQuestionIndex] || null;
};
export const selectCurrentQuestionIndex = (state: { assessment: AssessmentState }) => state.assessment.currentQuestionIndex;
export const selectUserAnswers = (state: { assessment: AssessmentState }) => state.assessment.userAnswers;
export const selectTimeRemaining = (state: { assessment: AssessmentState }) => state.assessment.timeRemaining;
export const selectIsSubmitting = (state: { assessment: AssessmentState }) => state.assessment.isSubmitting;
export const selectAssessmentResults = (state: { assessment: AssessmentState }) => state.assessment.results;
export const selectAssessmentHistory = (state: { assessment: AssessmentState }) => state.assessment.assessmentHistory;
export const selectAssessmentLoading = (state: { assessment: AssessmentState }) => state.assessment.loading;
export const selectAssessmentError = (state: { assessment: AssessmentState }) => state.assessment.error;

export const selectAssessmentProgress = (state: { assessment: AssessmentState }) => {
  const { currentAssessment, userAnswers } = state.assessment;
  if (!currentAssessment) return { answered: 0, total: 0, percentage: 0 };
  
  const answered = Object.keys(userAnswers).length;
  const total = currentAssessment.questions.length;
  const percentage = total > 0 ? (answered / total) * 100 : 0;
  
  return { answered, total, percentage };
};

export const selectCanSubmit = (state: { assessment: AssessmentState }) => {
  const { currentAssessment, userAnswers } = state.assessment;
  if (!currentAssessment) return false;
  
  return Object.keys(userAnswers).length === currentAssessment.questions.length;
};

export default assessmentSlice.reducer;