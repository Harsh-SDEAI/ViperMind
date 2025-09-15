-- ViperMind Database Manual Table Creation
-- Run this SQL in pgAdmin Query Tool if Python scripts don't work

-- Create ENUM types first
CREATE TYPE user_level AS ENUM ('beginner', 'intermediate', 'advanced');
CREATE TYPE assessment_type AS ENUM ('quiz', 'section_test', 'level_final');
CREATE TYPE difficulty_level AS ENUM ('easy', 'medium', 'hard');
CREATE TYPE progress_status AS ENUM ('locked', 'available', 'in_progress', 'completed');

-- Create UUID extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    password_hash VARCHAR NOT NULL,
    current_level user_level DEFAULT 'beginner',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Levels table
CREATE TABLE levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR NOT NULL,
    code VARCHAR(1) UNIQUE NOT NULL,
    description TEXT,
    "order" INTEGER NOT NULL
);

-- Sections table
CREATE TABLE sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    level_id UUID NOT NULL REFERENCES levels(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    code VARCHAR(2) NOT NULL,
    description TEXT,
    "order" INTEGER NOT NULL
);

-- Topics table
CREATE TABLE topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_id UUID NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    "order" INTEGER NOT NULL
);

-- Lesson contents table
CREATE TABLE lesson_contents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    why_it_matters TEXT NOT NULL,
    key_ideas TEXT[] NOT NULL,
    examples JSONB,
    pitfalls TEXT[] NOT NULL,
    recap TEXT NOT NULL
);

-- Remedial contents table
CREATE TABLE remedial_contents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    explanation TEXT NOT NULL,
    practice_exercises JSONB,
    additional_resources JSONB
);

-- Assessments table
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type assessment_type NOT NULL,
    target_id UUID NOT NULL,
    score FLOAT,
    passed BOOLEAN,
    attempt_number INTEGER DEFAULT 1,
    completed_at TIMESTAMP WITH TIME ZONE,
    ai_generated BOOLEAN DEFAULT true,
    difficulty_level difficulty_level DEFAULT 'medium',
    personalization_factors JSONB,
    ai_feedback TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for assessments
CREATE INDEX idx_assessments_user_id ON assessments(user_id);
CREATE INDEX idx_assessments_type ON assessments(type);
CREATE INDEX idx_assessments_target_id ON assessments(target_id);

-- Questions table
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    options TEXT[] NOT NULL,
    correct_answer INTEGER NOT NULL,
    explanation TEXT,
    difficulty difficulty_level DEFAULT 'medium',
    ai_generated BOOLEAN DEFAULT true,
    generation_prompt TEXT,
    concept_tags VARCHAR[],
    code_snippet TEXT,
    "order" INTEGER NOT NULL
);

-- Answers table
CREATE TABLE answers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    selected_option INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    time_taken INTEGER,
    confidence_level VARCHAR,
    ai_hint_used BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User progress table
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    level_id UUID NOT NULL REFERENCES levels(id) ON DELETE CASCADE,
    section_id UUID NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    status progress_status DEFAULT 'locked',
    best_score FLOAT,
    attempts INTEGER DEFAULT 0,
    last_attempt_at TIMESTAMP WITH TIME ZONE,
    unlocked_at TIMESTAMP WITH TIME ZONE,
    learning_velocity FLOAT,
    struggle_areas VARCHAR[],
    strength_areas VARCHAR[],
    recommended_difficulty VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for user_progress
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX idx_user_progress_topic_id ON user_progress(topic_id);
CREATE UNIQUE INDEX idx_user_progress_unique ON user_progress(user_id, topic_id);

-- Level progress table
CREATE TABLE level_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    level_id UUID NOT NULL REFERENCES levels(id) ON DELETE CASCADE,
    topic_quiz_average FLOAT DEFAULT 0.0,
    section_test_average FLOAT DEFAULT 0.0,
    level_final_score FLOAT,
    overall_score FLOAT DEFAULT 0.0,
    is_unlocked BOOLEAN DEFAULT false,
    is_completed BOOLEAN DEFAULT false,
    can_advance BOOLEAN DEFAULT false,
    ai_insights JSONB,
    predicted_completion_time INTEGER,
    personalized_recommendations VARCHAR[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for level_progress
CREATE INDEX idx_level_progress_user_id ON level_progress(user_id);
CREATE INDEX idx_level_progress_level_id ON level_progress(level_id);
CREATE UNIQUE INDEX idx_level_progress_unique ON level_progress(user_id, level_id);

-- Learning analytics table
CREATE TABLE learning_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    activity_type VARCHAR NOT NULL,
    topic_id UUID REFERENCES topics(id),
    time_spent INTEGER,
    performance_metrics JSONB,
    ai_observations JSONB,
    engagement_score FLOAT
);

-- Create indexes for learning_analytics
CREATE INDEX idx_learning_analytics_user_id ON learning_analytics(user_id);
CREATE INDEX idx_learning_analytics_timestamp ON learning_analytics(timestamp);
CREATE INDEX idx_learning_analytics_activity_type ON learning_analytics(activity_type);

-- Insert initial curriculum data
INSERT INTO levels (name, code, description, "order") VALUES
('Beginner', 'B', 'Introduction to Python programming fundamentals', 1),
('Intermediate', 'I', 'Advanced Python concepts and object-oriented programming', 2),
('Advanced', 'A', 'Advanced Python topics and real-world applications', 3);

-- Get level IDs for sections
DO $$
DECLARE
    beginner_id UUID;
    intermediate_id UUID;
    advanced_id UUID;
BEGIN
    SELECT id INTO beginner_id FROM levels WHERE code = 'B';
    SELECT id INTO intermediate_id FROM levels WHERE code = 'I';
    SELECT id INTO advanced_id FROM levels WHERE code = 'A';

    -- Insert Beginner sections
    INSERT INTO sections (level_id, name, code, description, "order") VALUES
    (beginner_id, 'Python Basics', 'B1', 'Variables, data types, and basic operations', 1),
    (beginner_id, 'Control Structures', 'B2', 'Conditionals and loops', 2),
    (beginner_id, 'Functions and Modules', 'B3', 'Function definition and module usage', 3),
    (beginner_id, 'Data Structures', 'B4', 'Lists, dictionaries, and basic data manipulation', 4);

    -- Insert Intermediate sections
    INSERT INTO sections (level_id, name, code, description, "order") VALUES
    (intermediate_id, 'Object-Oriented Programming', 'I1', 'Classes, objects, and inheritance', 1),
    (intermediate_id, 'Error Handling', 'I2', 'Exceptions and debugging', 2),
    (intermediate_id, 'File Operations', 'I3', 'Reading and writing files', 3),
    (intermediate_id, 'Advanced Data Structures', 'I4', 'Sets, tuples, and comprehensions', 4);

    -- Insert Advanced sections
    INSERT INTO sections (level_id, name, code, description, "order") VALUES
    (advanced_id, 'Decorators and Generators', 'A1', 'Advanced function concepts', 1),
    (advanced_id, 'Concurrency', 'A2', 'Threading and async programming', 2),
    (advanced_id, 'Testing and Quality', 'A3', 'Unit testing and code quality', 3),
    (advanced_id, 'Libraries and Frameworks', 'A4', 'Popular Python libraries', 4);
END $$;

-- Insert topics for each section
DO $$
DECLARE
    section_record RECORD;
    topic_names TEXT[];
    topic_name TEXT;
    topic_order INTEGER;
BEGIN
    -- Beginner topics
    FOR section_record IN SELECT id, code FROM sections WHERE code LIKE 'B%' ORDER BY "order" LOOP
        CASE section_record.code
            WHEN 'B1' THEN topic_names := ARRAY['Variables and Data Types', 'Basic Input/Output', 'String Operations'];
            WHEN 'B2' THEN topic_names := ARRAY['If Statements', 'For Loops', 'While Loops'];
            WHEN 'B3' THEN topic_names := ARRAY['Function Basics', 'Parameters and Return Values'];
            WHEN 'B4' THEN topic_names := ARRAY['Lists and Indexing', 'Dictionaries'];
        END CASE;
        
        topic_order := 1;
        FOREACH topic_name IN ARRAY topic_names LOOP
            INSERT INTO topics (section_id, name, "order") VALUES (section_record.id, topic_name, topic_order);
            topic_order := topic_order + 1;
        END LOOP;
    END LOOP;

    -- Intermediate topics
    FOR section_record IN SELECT id, code FROM sections WHERE code LIKE 'I%' ORDER BY "order" LOOP
        CASE section_record.code
            WHEN 'I1' THEN topic_names := ARRAY['Classes and Objects', 'Inheritance and Polymorphism', 'Encapsulation'];
            WHEN 'I2' THEN topic_names := ARRAY['Exception Handling', 'Debugging Techniques'];
            WHEN 'I3' THEN topic_names := ARRAY['File Reading and Writing', 'Working with CSV and JSON'];
            WHEN 'I4' THEN topic_names := ARRAY['Sets and Tuples', 'List Comprehensions', 'Dictionary Comprehensions'];
        END CASE;
        
        topic_order := 1;
        FOREACH topic_name IN ARRAY topic_names LOOP
            INSERT INTO topics (section_id, name, "order") VALUES (section_record.id, topic_name, topic_order);
            topic_order := topic_order + 1;
        END LOOP;
    END LOOP;

    -- Advanced topics
    FOR section_record IN SELECT id, code FROM sections WHERE code LIKE 'A%' ORDER BY "order" LOOP
        CASE section_record.code
            WHEN 'A1' THEN topic_names := ARRAY['Decorators', 'Generators and Iterators'];
            WHEN 'A2' THEN topic_names := ARRAY['Threading and Multiprocessing', 'Async/Await Programming', 'Concurrent Futures'];
            WHEN 'A3' THEN topic_names := ARRAY['Unit Testing with pytest', 'Code Quality and Linting'];
            WHEN 'A4' THEN topic_names := ARRAY['NumPy and Pandas', 'Web Development with Flask', 'API Development'];
        END CASE;
        
        topic_order := 1;
        FOREACH topic_name IN ARRAY topic_names LOOP
            INSERT INTO topics (section_id, name, "order") VALUES (section_record.id, topic_name, topic_order);
            topic_order := topic_order + 1;
        END LOOP;
    END LOOP;
END $$;

-- Verification queries
SELECT 'Database setup complete!' as status;

SELECT 
    l.name as level_name,
    l.code as level_code,
    COUNT(DISTINCT s.id) as sections_count,
    COUNT(DISTINCT t.id) as topics_count
FROM levels l
LEFT JOIN sections s ON l.id = s.level_id
LEFT JOIN topics t ON s.id = t.section_id
GROUP BY l.id, l.name, l.code, l."order"
ORDER BY l."order";

SELECT 'Total curriculum structure:' as info,
    COUNT(DISTINCT l.id) as total_levels,
    COUNT(DISTINCT s.id) as total_sections,
    COUNT(DISTINCT t.id) as total_topics
FROM levels l
LEFT JOIN sections s ON l.id = s.level_id
LEFT JOIN topics t ON s.id = t.section_id;