# ViperMind Database Setup with pgAdmin

This guide shows how to set up the ViperMind database using pgAdmin interface.

## Step 1: Create Database in pgAdmin

1. **Open pgAdmin** and connect to your PostgreSQL server
2. **Right-click on "Databases"** in the left panel
3. **Select "Create" > "Database..."**
4. **Enter database details:**
   - Database name: `vipermind`
   - Owner: `postgres` (or your preferred user)
   - Encoding: `UTF8`
   - Template: `template1`
   - Collation: `Default`
   - Character type: `Default`
5. **Click "Save"** to create the database

## Step 2: Verify Database Connection

Update your environment variables to match your pgAdmin setup:

```bash
# Create a .env file in the backend directory
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=vipermind
POSTGRES_PORT=5432
SQLALCHEMY_DATABASE_URI=postgresql://postgres:your_password_here@localhost:5432/vipermind
```

## Step 3: Create Tables Using Python Scripts

Now that the database exists, we'll use our Python scripts to create the tables:

### Option A: Using the Complete Initialization Script
```bash
cd backend
python init_database.py
```

### Option B: Step-by-Step Approach
```bash
cd backend

# 1. Test the database connection first
python -c "from app.core.config import settings; print(f'Database URL: {settings.SQLALCHEMY_DATABASE_URI}')"

# 2. Test models work
python test_models.py

# 3. Create all tables and initialize data
python init_database.py
```

## Step 4: Verify Tables in pgAdmin

After running the initialization script:

1. **Refresh the database** in pgAdmin (right-click on "vipermind" > "Refresh")
2. **Expand the database** > "Schemas" > "public" > "Tables"
3. **You should see these tables:**
   - `users`
   - `levels`
   - `sections`
   - `topics`
   - `lesson_contents`
   - `remedial_contents`
   - `assessments`
   - `questions`
   - `answers`
   - `user_progress`
   - `level_progress`
   - `learning_analytics`

## Step 5: Verify Data was Inserted

You can run queries in pgAdmin to check the data:

1. **Right-click on the "vipermind" database**
2. **Select "Query Tool"**
3. **Run these verification queries:**

```sql
-- Check levels
SELECT * FROM levels ORDER BY "order";

-- Check sections
SELECT l.name as level_name, s.name as section_name, s.code 
FROM levels l 
JOIN sections s ON l.id = s.level_id 
ORDER BY l."order", s."order";

-- Check topics count
SELECT l.name as level_name, COUNT(t.id) as topic_count
FROM levels l
JOIN sections s ON l.id = s.level_id
JOIN topics t ON s.id = t.section_id
GROUP BY l.id, l.name
ORDER BY l."order";

-- Total curriculum structure
SELECT 
    COUNT(DISTINCT l.id) as levels,
    COUNT(DISTINCT s.id) as sections,
    COUNT(DISTINCT t.id) as topics
FROM levels l
LEFT JOIN sections s ON l.id = s.level_id
LEFT JOIN topics t ON s.id = t.section_id;
```

Expected results:
- **3 levels**: Beginner (B), Intermediate (I), Advanced (A)
- **12 sections**: 4 per level
- **30 topics**: Distributed across all sections

## Troubleshooting

### Connection Issues
If you get connection errors:

1. **Check PostgreSQL is running:**
   - In pgAdmin, ensure your server shows a green icon
   - Or check system services for PostgreSQL

2. **Verify connection details:**
   ```bash
   # Test connection manually
   psql -h localhost -U postgres -d vipermind
   ```

3. **Update password in .env file:**
   Make sure the password matches your PostgreSQL setup

### Permission Issues
If you get permission errors:

1. **Grant privileges to your user:**
   ```sql
   -- In pgAdmin Query Tool, run:
   GRANT ALL PRIVILEGES ON DATABASE vipermind TO postgres;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
   ```

### Import Errors
If Python scripts fail:

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Check Python path:**
   ```bash
   # Make sure you're in the backend directory
   pwd  # Should show .../vipermind/backend
   ```

## Alternative: Manual Table Creation

If the Python scripts don't work, you can create tables manually in pgAdmin:

1. **Open Query Tool** in pgAdmin
2. **Copy and paste the SQL from:** `backend/manual_table_creation.sql` (we'll create this file)
3. **Execute the SQL** to create all tables
4. **Run the data insertion queries** to populate curriculum data

## Next Steps

After successful database setup:

1. **Test the API connection:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   # Visit http://localhost:8000/docs to see the API documentation
   ```

2. **Verify database integration:**
   ```bash
   # Test that the API can connect to the database
   curl http://localhost:8000/health
   ```

3. **Ready for next task:** Authentication system implementation

## Database Schema Diagram

The database structure follows this hierarchy:
```
Users
├── UserProgress (tracks individual topic progress)
├── LevelProgress (tracks overall level progress)
├── Assessments
│   ├── Questions
│   └── Answers
└── LearningAnalytics

Curriculum
├── Levels (3: B, I, A)
│   └── Sections (4 per level)
│       └── Topics (2-3 per section)
│           ├── LessonContent
│           └── RemedialContent
```