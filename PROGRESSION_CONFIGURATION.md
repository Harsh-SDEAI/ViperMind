# Progression Configuration Guide

## Overview

You now have full control over all progression requirements in ViperMind. You can easily adjust section-wise and level-wise score requirements through multiple methods.

## Configuration Methods

### 1. Environment Variables (Recommended)
Edit the `.env.progression` file to set your preferred thresholds:

```bash
# Section requirements
SECTION_AVERAGE_REQUIREMENT=75.0    # Average quiz score needed to complete section
LEVEL_SECTION_AVERAGE_REQUIREMENT=75.0  # Section average needed for level advancement

# Level requirements  
LEVEL_FINAL_REQUIREMENT=80.0        # Level final score needed for advancement
LEVEL_FINAL_PASS_THRESHOLD=80.0     # Level final pass threshold
```

### 2. Management Script (Interactive)
Run the interactive configuration manager:

```bash
python manage_progression_config.py
```

This provides a user-friendly interface to:
- View current configuration
- Update specific thresholds
- Apply quick fixes (lower requirements)
- Reset to defaults

### 3. API Endpoints (Programmatic)
Use the REST API to manage configuration:

```bash
# Get current configuration
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/v1/progress/config

# Update configuration
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"section_average_requirement": 50.0}' \
     http://localhost:8000/api/v1/progress/config/update
```

## Key Configuration Parameters

### Section-Level Requirements
- **`section_average_requirement`**: Average quiz score needed to complete a section (default: 75%)
- **`section_test_requirement`**: Section test score needed (default: 75%)
- **`topic_quiz_requirement`**: Individual quiz score needed to complete topic (default: 70%)

### Level-Level Requirements
- **`level_section_average_requirement`**: Section average needed for level advancement (default: 75%)
- **`level_final_requirement`**: Level final score needed for advancement (default: 80%)

### Assessment Pass Thresholds
- **`quiz_pass_threshold`**: Score needed to pass a quiz (default: 70%)
- **`section_test_pass_threshold`**: Score needed to pass section test (default: 75%)
- **`level_final_pass_threshold`**: Score needed to pass level final (default: 80%)

## Quick Solutions for Your Issue

If you can't access intermediate level despite completing all beginner topics, try these quick fixes:

### Option 1: Lower Section Requirements
```bash
python manage_progression_config.py
# Choose option 3: "Quick fix - Lower section requirements to 50%"
```

### Option 2: Lower Level Final Requirements
```bash
python manage_progression_config.py
# Choose option 4: "Quick fix - Lower level final requirement to 60%"
```

### Option 3: Make Everything Easier
```bash
python manage_progression_config.py
# Choose option 6: "Make it easier (lower all thresholds)"
```

### Option 4: Direct Environment Variable Edit
Edit `.env.progression` and set:
```bash
SECTION_AVERAGE_REQUIREMENT=50.0
LEVEL_SECTION_AVERAGE_REQUIREMENT=50.0
LEVEL_FINAL_REQUIREMENT=60.0
```

Then restart the backend:
```bash
docker-compose restart backend
```

## Configuration Presets

### Easy Mode
- Quiz Pass: 50%
- Section Test Pass: 55%
- Level Final Pass: 60%
- Section Average Required: 55%
- Level Advancement: 60%

### Normal Mode (Default)
- Quiz Pass: 70%
- Section Test Pass: 75%
- Level Final Pass: 80%
- Section Average Required: 75%
- Level Advancement: 80%

### Hard Mode
- Quiz Pass: 85%
- Section Test Pass: 90%
- Level Final Pass: 95%
- Section Average Required: 90%
- Level Advancement: 95%

## Debugging Your Specific Issue

1. **Check current requirements**:
   ```bash
   python check_advancement_requirements.py
   ```

2. **Lower requirements if needed**:
   ```bash
   python manage_progression_config.py
   ```

3. **Verify the fix**:
   ```bash
   python check_advancement_requirements.py
   ```

## How Level Advancement Works

To advance from Beginner to Intermediate, you need:

1. **All beginner topics completed** with quiz scores
2. **All beginner sections** with average ≥ `section_average_requirement`
3. **Beginner level final** passed with score ≥ `level_final_requirement`

The system checks these requirements automatically when:
- You complete a quiz
- You pass a section test
- You pass a level final

## Troubleshooting

### Issue: "Section requires 75% average but I completed all topics"
**Solution**: You need quiz scores for all topics. Complete quizzes for all topics in the section.

### Issue: "Level final must be passed but I can't take it"
**Solution**: Complete all section tests first, then the level final becomes available.

### Issue: "Requirements are too strict"
**Solution**: Use the configuration manager to lower the thresholds to your preference.

## Advanced Configuration

You can also configure:
- **Attempt limits** for each assessment type
- **Requirement toggles** (require all topics, section tests, etc.)
- **Custom scoring algorithms** (by modifying the backend code)

The configuration system is designed to be flexible and allow you to customize the learning experience to your needs.