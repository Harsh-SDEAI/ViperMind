#!/usr/bin/env python3
"""
Seed script to populate the database with curriculum data
"""

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models.curriculum import Level, Section, Topic, LessonContent

def create_curriculum_data():
    """Create the complete curriculum structure"""
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_levels = db.query(Level).count()
        if existing_levels > 0:
            print("Curriculum data already exists. Skipping seed.")
            return
        
        print("Creating curriculum structure...")
        
        # Create Beginner Level (B)
        beginner_level = Level(
            name="Beginner",
            code="B",
            description="Introduction to Python programming fundamentals",
            order=1
        )
        db.add(beginner_level)
        db.flush()
        
        # Beginner Sections
        b1_section = Section(
            level_id=beginner_level.id,
            name="Python Basics",
            code="B1",
            description="Core Python concepts and syntax",
            order=1
        )
        db.add(b1_section)
        db.flush()
        
        b2_section = Section(
            level_id=beginner_level.id,
            name="Data Structures",
            code="B2",
            description="Lists, dictionaries, and basic data manipulation",
            order=2
        )
        db.add(b2_section)
        db.flush()
        
        # B1 Topics
        b1_topics = [
            ("Variables and Data Types", 1),
            ("Basic Operations", 2),
            ("Input and Output", 3),
            ("Conditional Statements", 4),
            ("Loops", 5)
        ]
        
        for topic_name, order in b1_topics:
            topic = Topic(
                section_id=b1_section.id,
                name=topic_name,
                order=order
            )
            db.add(topic)
        
        # B2 Topics
        b2_topics = [
            ("Lists", 1),
            ("Dictionaries", 2),
            ("Tuples and Sets", 3),
            ("String Manipulation", 4),
            ("List Comprehensions", 5)
        ]
        
        for topic_name, order in b2_topics:
            topic = Topic(
                section_id=b2_section.id,
                name=topic_name,
                order=order
            )
            db.add(topic)
        
        # Create Intermediate Level (I)
        intermediate_level = Level(
            name="Intermediate",
            code="I",
            description="Functions, modules, and object-oriented programming",
            order=2
        )
        db.add(intermediate_level)
        db.flush()
        
        # Intermediate Sections
        i1_section = Section(
            level_id=intermediate_level.id,
            name="Functions and Modules",
            code="I1",
            description="Creating reusable code with functions and modules",
            order=1
        )
        db.add(i1_section)
        db.flush()
        
        i2_section = Section(
            level_id=intermediate_level.id,
            name="Object-Oriented Programming",
            code="I2",
            description="Classes, objects, and inheritance",
            order=2
        )
        db.add(i2_section)
        db.flush()
        
        # I1 Topics
        i1_topics = [
            ("Defining Functions", 1),
            ("Function Parameters", 2),
            ("Return Values", 3),
            ("Scope and Namespaces", 4),
            ("Modules and Packages", 5)
        ]
        
        for topic_name, order in i1_topics:
            topic = Topic(
                section_id=i1_section.id,
                name=topic_name,
                order=order
            )
            db.add(topic)
        
        # I2 Topics
        i2_topics = [
            ("Classes and Objects", 1),
            ("Attributes and Methods", 2),
            ("Inheritance", 3),
            ("Polymorphism", 4),
            ("Special Methods", 5)
        ]
        
        for topic_name, order in i2_topics:
            topic = Topic(
                section_id=i2_section.id,
                name=topic_name,
                order=order
            )
            db.add(topic)
        
        # Create Advanced Level (A)
        advanced_level = Level(
            name="Advanced",
            code="A",
            description="Advanced Python concepts and real-world applications",
            order=3
        )
        db.add(advanced_level)
        db.flush()
        
        # Advanced Sections
        a1_section = Section(
            level_id=advanced_level.id,
            name="Advanced Concepts",
            code="A1",
            description="Decorators, generators, and advanced features",
            order=1
        )
        db.add(a1_section)
        db.flush()
        
        a2_section = Section(
            level_id=advanced_level.id,
            name="Libraries and Frameworks",
            code="A2",
            description="Working with popular Python libraries",
            order=2
        )
        db.add(a2_section)
        db.flush()
        
        # A1 Topics
        a1_topics = [
            ("Decorators", 1),
            ("Generators and Iterators", 2),
            ("Context Managers", 3),
            ("Exception Handling", 4),
            ("File I/O", 5)
        ]
        
        for topic_name, order in a1_topics:
            topic = Topic(
                section_id=a1_section.id,
                name=topic_name,
                order=order
            )
            db.add(topic)
        
        # A2 Topics
        a2_topics = [
            ("Working with APIs", 1),
            ("Data Analysis with Pandas", 2),
            ("Web Development Basics", 3),
            ("Testing and Debugging", 4),
            ("Project Structure", 5)
        ]
        
        for topic_name, order in a2_topics:
            topic = Topic(
                section_id=a2_section.id,
                name=topic_name,
                order=order
            )
            db.add(topic)
        
        db.commit()
        print("✅ Curriculum structure created successfully!")
        
        # Print summary
        levels = db.query(Level).count()
        sections = db.query(Section).count()
        topics = db.query(Topic).count()
        
        print(f"📊 Created: {levels} levels, {sections} sections, {topics} topics")
        
    except Exception as e:
        print(f"❌ Error creating curriculum: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_curriculum_data()