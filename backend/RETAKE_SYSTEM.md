# Retake System and Attempt Management

## Overview

The ViperMind retake system provides intelligent attempt management for assessments with different rules based on assessment type. It tracks best scores, enforces attempt limits, and provides clear feedback to users about their retake eligibility.

## Features Implemented

### 1. Attempt Limits by Assessment Type

- **Quizzes**: Unlimited attempts to encourage learning
- **Section Tests**: 2 attempts total (1 initial + 1 retake)
- **Level Finals**: 2 attempts total (1 initial + 1 retake with review requirement)

### 2. Best Score Tracking

- Automatically tracks the highest score achieved across all attempts
- Displays best score and pass status in the RetakeManager component
- Updates progress tracking with best scores only

### 3. Retake Eligibility Logic

- **Quizzes**: Always eligible for retakes (unlimited)
- **Section Tests**: Eligible for retake if failed and haven't used all attempts
- **Level Finals**: Eligible for retake if failed, haven't used all attempts, and complete review

### 4. Pass Thresholds

- **Quizzes**: 70% required to pass
- **Section Tests**: 75% required to pass  
- **Level Finals**: 80% required to pass

## API Endpoints

### Get Remaining Attempts
```
GET /api/assessments/attempts/{target_id}?assessment_type={type}
```

Returns detailed information about attempts, including:
- Attempts used vs. maximum allowed
- Best score and pass status
- Retake eligibility
- Assessment history
- Review requirements (for level finals)

### Initiate Retake
```
POST /api/assessments/retake
```

Starts a new retake attempt with validation:
- Checks retake eligibility
- Enforces attempt limits
- Validates review completion (for level finals)

### Get Best Scores
```
GET /api/assessments/best-scores/{user_id}
```

Returns user's best scores across all assessments for progress tracking.

## Frontend Components

### RetakeManager Component

The `RetakeManager` component provides a comprehensive interface for:
- Displaying attempt history and best scores
- Showing retake eligibility and requirements
- Starting new attempts or retakes
- Providing clear feedback about attempt limits

**Props:**
- `targetId`: Assessment target (topic/section/level ID)
- `assessmentType`: Type of assessment ('quiz' | 'section_test' | 'level_final')
- `onRetakeStart`: Callback for starting a retake
- `onNewAttempt`: Callback for starting first attempt

### AssessmentLauncher Component

Integrates the RetakeManager with the assessment flow:
- Shows assessment guidelines and attempt limits
- Manages the transition between retake management and assessment taking
- Provides clear instructions for each assessment type

## Usage Examples

### 1. Quiz Retakes (Unlimited)

```typescript
// User can retake quizzes unlimited times
const retakeInfo = await assessmentService.getRemainingAttempts(topicId, 'quiz');
// retakeInfo.can_retake will always be true
// retakeInfo.max_attempts will be 999 (unlimited)
```

### 2. Section Test Retakes (Limited)

```typescript
// User gets one retake if they fail
const retakeInfo = await assessmentService.getRemainingAttempts(sectionId, 'section_test');
if (retakeInfo.can_retake && !retakeInfo.best_passed) {
  // User can retake the failed section test
  await assessmentService.initiateRetake({
    target_id: sectionId,
    assessment_type: 'section_test'
  });
}
```

### 3. Level Final Retakes (With Review)

```typescript
// User gets one retake with review requirement
const retakeInfo = await assessmentService.getRemainingAttempts(levelId, 'level_final');
if (retakeInfo.can_retake && retakeInfo.retake_requirements?.review_required) {
  // Show review requirement message
  console.log(retakeInfo.retake_requirements.message);
  // After review completion, allow retake
}
```

## Database Schema Updates

### Assessment Model Extensions

- `attempt_number`: Tracks which attempt this is (1, 2, etc.)
- `submitted_at`: When the assessment was completed
- Enhanced queries to filter only completed assessments

### Progress Model Integration

- `best_score`: Stores the highest score achieved
- `attempts`: Total number of attempts made
- `last_attempt_at`: Timestamp of most recent attempt

## Error Handling

### Common Error Scenarios

1. **Maximum Attempts Reached**
   ```json
   {
     "detail": "Maximum attempts (2) reached for this section_test"
   }
   ```

2. **Retake Not Allowed (Already Passed)**
   ```json
   {
     "detail": "Cannot retake a passed assessment."
   }
   ```

3. **Review Required**
   ```json
   {
     "retake_requirements": {
       "review_required": true,
       "message": "You must complete a review session before retaking the level final."
     }
   }
   ```

## Testing

### Unit Tests
Run the retake logic unit tests:
```bash
python backend/test_retake_logic.py
```

### Integration Tests
The full integration test requires a database connection:
```bash
python backend/test_retake_system.py
```

## Configuration

### Attempt Limits
Modify attempt limits in the assessment endpoints:

```python
max_attempts = {
    "quiz": 999,        # Unlimited
    "section_test": 2,  # 1 initial + 1 retake  
    "level_final": 2    # 1 initial + 1 retake
}
```

### Pass Thresholds
Adjust pass thresholds as needed:

```python
pass_thresholds = {
    "quiz": 70.0,
    "section_test": 75.0,
    "level_final": 80.0
}
```

## Future Enhancements

1. **Review System**: Implement actual review content and completion tracking
2. **Adaptive Retakes**: Adjust retake rules based on user performance patterns
3. **Remedial Content**: Generate targeted practice materials for failed assessments
4. **Analytics**: Track retake patterns to improve curriculum design
5. **Time Delays**: Add cooldown periods between retake attempts
6. **Partial Credit**: Implement partial scoring for complex assessments