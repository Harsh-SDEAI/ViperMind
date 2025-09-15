from sqlalchemy.orm import Session
from app.models import Level, Section, Topic, LessonContent
from app.core.config import settings

def init_curriculum_data(db: Session) -> None:
    """Initialize the curriculum structure with all levels, sections, and topics"""
    
    # Check if data already exists
    if db.query(Level).first():
        return
    
    # Beginner Level (B)
    beginner_level = Level(
        name="Beginner",
        code="B",
        description="Introduction to Python programming fundamentals",
        order=1
    )
    db.add(beginner_level)
    db.flush()  # Get the ID
    
    # Beginner Sections
    b_sections = [
        {"name": "Python Basics", "code": "B1", "description": "Variables, data types, and basic operations", "order": 1},
        {"name": "Control Structures", "code": "B2", "description": "Conditionals and loops", "order": 2},
        {"name": "Functions and Modules", "code": "B3", "description": "Function definition and module usage", "order": 3},
        {"name": "Data Structures", "code": "B4", "description": "Lists, dictionaries, and basic data manipulation", "order": 4}
    ]
    
    for section_data in b_sections:
        section = Section(
            level_id=beginner_level.id,
            name=section_data["name"],
            code=section_data["code"],
            description=section_data["description"],
            order=section_data["order"]
        )
        db.add(section)
        db.flush()
        
        # Add topics for each section (2-3 topics per section for 10 total)
        if section_data["code"] == "B1":
            topics = [
                "Variables and Data Types",
                "Basic Input/Output",
                "String Operations"
            ]
        elif section_data["code"] == "B2":
            topics = [
                "If Statements",
                "For Loops",
                "While Loops"
            ]
        elif section_data["code"] == "B3":
            topics = [
                "Function Basics",
                "Parameters and Return Values"
            ]
        else:  # B4
            topics = [
                "Lists and Indexing",
                "Dictionaries"
            ]
        
        for i, topic_name in enumerate(topics):
            topic = Topic(
                section_id=section.id,
                name=topic_name,
                order=i + 1
            )
            db.add(topic)
    
    # Intermediate Level (I)
    intermediate_level = Level(
        name="Intermediate",
        code="I",
        description="Advanced Python concepts and object-oriented programming",
        order=2
    )
    db.add(intermediate_level)
    db.flush()
    
    # Intermediate Sections
    i_sections = [
        {"name": "Object-Oriented Programming", "code": "I1", "description": "Classes, objects, and inheritance", "order": 1},
        {"name": "Error Handling", "code": "I2", "description": "Exceptions and debugging", "order": 2},
        {"name": "File Operations", "code": "I3", "description": "Reading and writing files", "order": 3},
        {"name": "Advanced Data Structures", "code": "I4", "description": "Sets, tuples, and comprehensions", "order": 4}
    ]
    
    for section_data in i_sections:
        section = Section(
            level_id=intermediate_level.id,
            name=section_data["name"],
            code=section_data["code"],
            description=section_data["description"],
            order=section_data["order"]
        )
        db.add(section)
        db.flush()
        
        # Add topics for each section
        if section_data["code"] == "I1":
            topics = [
                "Classes and Objects",
                "Inheritance and Polymorphism",
                "Encapsulation"
            ]
        elif section_data["code"] == "I2":
            topics = [
                "Exception Handling",
                "Debugging Techniques"
            ]
        elif section_data["code"] == "I3":
            topics = [
                "File Reading and Writing",
                "Working with CSV and JSON"
            ]
        else:  # I4
            topics = [
                "Sets and Tuples",
                "List Comprehensions",
                "Dictionary Comprehensions"
            ]
        
        for i, topic_name in enumerate(topics):
            topic = Topic(
                section_id=section.id,
                name=topic_name,
                order=i + 1
            )
            db.add(topic)
    
    # Advanced Level (A)
    advanced_level = Level(
        name="Advanced",
        code="A",
        description="Advanced Python topics and real-world applications",
        order=3
    )
    db.add(advanced_level)
    db.flush()
    
    # Advanced Sections
    a_sections = [
        {"name": "Decorators and Generators", "code": "A1", "description": "Advanced function concepts", "order": 1},
        {"name": "Concurrency", "code": "A2", "description": "Threading and async programming", "order": 2},
        {"name": "Testing and Quality", "code": "A3", "description": "Unit testing and code quality", "order": 3},
        {"name": "Libraries and Frameworks", "code": "A4", "description": "Popular Python libraries", "order": 4}
    ]
    
    for section_data in a_sections:
        section = Section(
            level_id=advanced_level.id,
            name=section_data["name"],
            code=section_data["code"],
            description=section_data["description"],
            order=section_data["order"]
        )
        db.add(section)
        db.flush()
        
        # Add topics for each section
        if section_data["code"] == "A1":
            topics = [
                "Decorators",
                "Generators and Iterators"
            ]
        elif section_data["code"] == "A2":
            topics = [
                "Threading and Multiprocessing",
                "Async/Await Programming",
                "Concurrent Futures"
            ]
        elif section_data["code"] == "A3":
            topics = [
                "Unit Testing with pytest",
                "Code Quality and Linting"
            ]
        else:  # A4
            topics = [
                "NumPy and Pandas",
                "Web Development with Flask",
                "API Development"
            ]
        
        for i, topic_name in enumerate(topics):
            topic = Topic(
                section_id=section.id,
                name=topic_name,
                order=i + 1
            )
            db.add(topic)
    
    db.commit()

def create_indexes(db: Session) -> None:
    """Create database indexes for performance optimization"""
    # Indexes are defined in the models using index=True
    # Additional custom indexes can be created here if needed
    pass