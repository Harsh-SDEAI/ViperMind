# Database Setup Guide

This guide explains how to set up the ViperMind database with all models and initial data.

## Database Models

The ViperMind platform uses the following main models:

### Core Models
- **User**: User accounts and authentication
- **Level**: Learning levels (Beginner, Intermediate, Advanced)
- **Section**: Sections within each level (4 per level)
- **Topic**: Individual topics within sections (30 total)
- **LessonContent**: Structured lesson content for each topic
- **RemedialContent**: Additional help content for struggling students

### Assessment Models
- **Assessment**: Quiz, section test, or level final assessments
- **Question**: Individual questions with multiple choice options
- **Answer**: User responses to questions

### Progress Tracking Models
- **UserProgress**: Individual topic progress for each user
- **LevelProgress**: Overall level progress and scoring
- **LearningAnalytics**: Detailed learning behavior tracking

## Database Initialization

### Method 1: Using Docker Compose (Recommended)
```bash
# Start the database service
docker-compose up -d db

# Run the initialization script
docker-compose exec backend python init_database.py
```

### Method 2: Manual Setup
```bash
# 1. Ensure PostgreSQL is running
# 2. Create the database
createdb vipermind

# 3. Set environment variables
export POSTGRES_SERVER=localhost
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=password
export POSTGRES_DB=vipermind

# 4. Install dependencies
pip install -r requirements.txt

# 5. Initialize the database
python init_database.py
```

### Method 3: Using Alembic Migrations
```bash
# Create initial migration
python create_initial_migration.py

# Apply migration
alembic upgrade head

# Initialize curriculum data
python -c "from app.db.init_db import init_curriculum_data; from app.db.base import SessionLocal; db = SessionLocal(); init_curriculum_data(db); db.close()"
```

## Database Structure

After initialization, the database will contain:

### Curriculum Structure
- **3 Levels**: Beginner (B), Intermediate (I), Advanced (A)
- **12 Sections**: 4 sections per level (B1-B4, I1-I4, A1-A4)
- **30 Topics**: Distributed across all sections

### Beginner Level Topics
- **B1 - Python Basics**: Variables, I/O, Strings
- **B2 - Control Structures**: If statements, For/While loops
- **B3 - Functions**: Function basics, Parameters
- **B4 - Data Structures**: Lists, Dictionaries

### Intermediate Level Topics
- **I1 - OOP**: Classes, Inheritance, Encapsulation
- **I2 - Error Handling**: Exceptions, Debugging
- **I3 - File Operations**: File I/O, CSV/JSON
- **I4 - Advanced Data**: Sets, Tuples, Comprehensions

### Advanced Level Topics
- **A1 - Advanced Functions**: Decorators, Generators
- **A2 - Concurrency**: Threading, Async programming
- **A3 - Testing**: Unit testing, Code quality
- **A4 - Libraries**: NumPy/Pandas, Flask, APIs

## Testing the Setup

Run the model test to verify everything works:
```bash
python test_models.py
```

## Database Indexes

The following indexes are automatically created for performance:
- User email and username (unique indexes)
- Assessment user_id and type
- Progress tracking by user_id, level_id, section_id, topic_id
- Learning analytics by user_id and timestamp

## Environment Variables

Required environment variables for database connection:
```bash
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=vipermind
SQLALCHEMY_DATABASE_URI=postgresql://postgres:password@localhost/vipermind
```

## Troubleshooting

### Common Issues

1. **Connection refused**: Ensure PostgreSQL is running
2. **Database does not exist**: Create the database first with `createdb vipermind`
3. **Permission denied**: Check PostgreSQL user permissions
4. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

### Resetting the Database
```bash
# Drop and recreate the database
dropdb vipermind
createdb vipermind
python init_database.py
```

### Checking Database Contents
```bash
# Connect to PostgreSQL
psql -d vipermind

# List all tables
\dt

# Check curriculum data
SELECT l.name, l.code, COUNT(s.id) as sections 
FROM levels l 
LEFT JOIN sections s ON l.id = s.level_id 
GROUP BY l.id, l.name, l.code 
ORDER BY l.order;
```