# Level Progression Fix

## Problem Analysis

The issue was that after completing a level (passing the level final exam), the next level was not getting unlocked automatically. This prevented users from progressing through the curriculum.

## Root Causes Identified

### 1. **Level Advancement Logic Only Triggered for Quizzes**
In `backend/app/api/api_v1/endpoints/assessments.py`, the level advancement check was only executed for quiz assessments:

```python
if assessment.type == AssessmentType.QUIZ:
    # ... quiz logic ...
    if passed:
        unlocks = _check_and_update_unlocks(str(current_user.id), db)
        level_advancement = _check_level_advancement(str(current_user.id), db)
```

This meant that when a user passed a level final exam, the system never checked if they should advance to the next level.

### 2. **Incomplete Level Progress Update**
The level progress update logic had a flawed database query:

```python
level_progress = db.query(LevelProgress).filter(
    LevelProgress.user_id == current_user.id,
    LevelProgress.level_id == assessment.target_id if assessment.type == AssessmentType.LEVEL_FINAL else None
).first()
```

For section tests, this would query with `level_id == None`, making the query ineffective.

### 3. **Missing Cache Invalidation**
The frontend curriculum cache wasn't being invalidated when level advancement occurred, so users wouldn't see the newly unlocked level immediately.

## Solutions Implemented

### 1. **Fixed Level Advancement Trigger**
Moved the level advancement check outside the quiz-specific block so it runs for all passed assessments:

```python
# Check for unlocks and level advancement for all passed assessments
if passed:
    unlocks = _check_and_update_unlocks(str(current_user.id), db)
    level_advancement = _check_level_advancement(str(current_user.id), db)
    
    # Update next steps if content was unlocked
    if unlocks:
        next_steps["unlocked_content"] = unlocks
    if level_advancement.get("can_advance"):
        next_steps["level_advancement"] = level_advancement
```

### 2. **Fixed Level Progress Update Logic**
Separated the logic for level finals and section tests with proper database queries:

```python
if assessment.type == AssessmentType.LEVEL_FINAL:
    # Get or create level progress for level final
    level_progress = db.query(LevelProgress).filter(
        LevelProgress.user_id == current_user.id,
        LevelProgress.level_id == assessment.target_id
    ).first()
    
    if not level_progress:
        level_progress = LevelProgress(
            user_id=current_user.id,
            level_id=assessment.target_id,
            is_unlocked=True
        )
        db.add(level_progress)
    
    # Update level final score
    if level_progress.level_final_score is None or score > level_progress.level_final_score:
        level_progress.level_final_score = score
        level_progress.is_completed = passed
        level_progress.can_advance = passed

elif assessment.type == AssessmentType.SECTION_TEST:
    # For section tests, we need to find the level from the section
    section = db.query(Section).filter(Section.id == assessment.target_id).first()
    if section:
        level_progress = db.query(LevelProgress).filter(
            LevelProgress.user_id == current_user.id,
            LevelProgress.level_id == section.level_id
        ).first()
        
        # ... proper section test handling ...
```

### 3. **Added Cache Invalidation**
Added cache invalidation when level advancement occurs:

```python
# Invalidate curriculum cache if level advancement occurred
if passed and next_steps.get("level_advancement", {}).get("can_advance"):
    from app.core.cache import cache_manager, CacheKeys
    cache_key = cache_manager._generate_key(CacheKeys.PROGRESS, f"curriculum:{current_user.id}")
    cache_manager.delete(cache_key)
```

### 4. **Enhanced Frontend State Management**
Added a new action to refresh curriculum data after level advancement:

```typescript
refreshAfterLevelAdvancement: (state) => {
  // Force refresh by invalidating cache and clearing current data
  state.lastFetched = null;
  state.levels = [];
  state.currentLevel = null;
  state.currentSection = null;
  state.currentTopic = null;
},
```

## Level Advancement Requirements

For a user to advance to the next level, they must meet these criteria (as defined in `_check_level_advancement`):

1. **All sections in current level completed** with 75%+ average
2. **Level final exam passed** with 80%+ score
3. **Next level exists** (can't advance beyond Advanced level)

When these conditions are met:
- User's `current_level` field is updated
- Next level is unlocked in `LevelProgress` table
- First topic of next level becomes available
- Frontend cache is invalidated to show changes immediately

## Testing

A test script (`test_level_progression.py`) has been created to verify the fix works correctly. The script:

1. Creates/logs in a test user
2. Simulates completing a level final exam
3. Verifies that level advancement occurs
4. Checks that the next level is unlocked

## Files Modified

### Backend
- `backend/app/api/api_v1/endpoints/assessments.py` - Fixed level advancement logic
- `backend/app/api/api_v1/endpoints/progress.py` - Added cache invalidation

### Frontend
- `frontend/src/store/slices/curriculumSlice.ts` - Added refresh action

## Verification Steps

To verify the fix works:

1. **Start the application**:
   ```bash
   docker-compose up -d
   ```

2. **Run the test script**:
   ```bash
   python test_level_progression.py
   ```

3. **Manual testing**:
   - Register a new user
   - Complete all beginner topics and section tests
   - Take and pass the beginner level final (80%+)
   - Verify intermediate level becomes unlocked
   - Check that user's profile shows "intermediate" level

## Expected Behavior After Fix

1. **When user passes level final**: Level advancement check runs automatically
2. **If requirements met**: User advances to next level and it becomes unlocked
3. **Frontend updates**: Curriculum refreshes to show newly available content
4. **Immediate feedback**: User sees success message and next steps
5. **Persistent state**: Level advancement persists across sessions

The fix ensures that level progression works seamlessly, providing users with a smooth learning experience as they advance through the curriculum.