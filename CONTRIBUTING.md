# Contributing to ViperMind

Thank you for your interest in contributing to ViperMind! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Submit bug fixes or new features
- **Documentation**: Improve or add documentation
- **Testing**: Help improve test coverage
- **Performance**: Optimize system performance
- **Security**: Identify and fix security issues

### Getting Started

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/vipermind.git
   cd vipermind
   ```

2. **Set Up Development Environment**
   ```bash
   # Copy environment configuration
   cp .env.example .env
   
   # Start development environment
   docker-compose up -d
   
   # Initialize database
   docker-compose exec backend python setup_database.py
   docker-compose exec backend python seed_curriculum.py
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-description
   ```

## 📋 Development Guidelines

### Code Standards

#### Python (Backend)
- **Formatting**: Use Black for code formatting
- **Linting**: Use Flake8 for linting
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Use Google-style docstrings
- **Testing**: Write tests for all new functionality

```python
def calculate_score(answers: List[Answer], total_questions: int) -> float:
    """Calculate assessment score based on correct answers.
    
    Args:
        answers: List of user answers
        total_questions: Total number of questions
        
    Returns:
        Score as percentage (0.0 to 100.0)
        
    Raises:
        ValueError: If total_questions is zero or negative
    """
    if total_questions <= 0:
        raise ValueError("Total questions must be positive")
    
    correct_answers = sum(1 for answer in answers if answer.is_correct)
    return (correct_answers / total_questions) * 100.0
```

#### TypeScript/React (Frontend)
- **Formatting**: Use Prettier for code formatting
- **Linting**: Use ESLint with TypeScript rules
- **Components**: Use functional components with hooks
- **Props**: Define proper TypeScript interfaces
- **Testing**: Use React Testing Library

```typescript
interface LessonViewerProps {
  topicId: string;
  onComplete: (score: number) => void;
  className?: string;
}

const LessonViewer: React.FC<LessonViewerProps> = ({
  topicId,
  onComplete,
  className = ''
}) => {
  // Component implementation
};
```

### Commit Message Format

Use conventional commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(assessment): add AI-powered question generation
fix(auth): resolve JWT token expiration issue
docs(api): update authentication documentation
test(curriculum): add integration tests for progress tracking
```

### Branch Naming

- `feature/description`: New features
- `bugfix/description`: Bug fixes
- `hotfix/description`: Critical fixes
- `docs/description`: Documentation updates
- `refactor/description`: Code refactoring

## 🧪 Testing

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test

# Integration tests
python backend/test_system_integration.py

# Performance tests
python backend/test_load_performance.py
```

### Test Coverage

- Maintain >90% test coverage for backend code
- Maintain >85% test coverage for frontend components
- Write integration tests for new API endpoints
- Include performance tests for critical paths

### Writing Tests

#### Backend Tests
```python
import pytest
from app.services.assessment import AssessmentService

class TestAssessmentService:
    def test_generate_quiz_success(self):
        """Test successful quiz generation."""
        service = AssessmentService()
        quiz = service.generate_quiz(topic_id="test-topic", user_id="test-user")
        
        assert quiz is not None
        assert len(quiz.questions) == 4
        assert all(len(q.options) == 4 for q in quiz.questions)
    
    def test_generate_quiz_invalid_topic(self):
        """Test quiz generation with invalid topic."""
        service = AssessmentService()
        
        with pytest.raises(ValueError):
            service.generate_quiz(topic_id="invalid", user_id="test-user")
```

#### Frontend Tests
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { LessonViewer } from './LessonViewer';

describe('LessonViewer', () => {
  it('renders lesson content correctly', () => {
    render(
      <LessonViewer 
        topicId="test-topic" 
        onComplete={jest.fn()} 
      />
    );
    
    expect(screen.getByText('Lesson Content')).toBeInTheDocument();
  });
  
  it('calls onComplete when lesson is finished', () => {
    const onComplete = jest.fn();
    render(
      <LessonViewer 
        topicId="test-topic" 
        onComplete={onComplete} 
      />
    );
    
    fireEvent.click(screen.getByText('Complete Lesson'));
    expect(onComplete).toHaveBeenCalledWith(100);
  });
});
```

## 🔍 Code Review Process

### Submitting Pull Requests

1. **Ensure Tests Pass**
   ```bash
   # Run all tests
   npm run test:all
   ```

2. **Update Documentation**
   - Update README if needed
   - Add/update API documentation
   - Update changelog

3. **Create Pull Request**
   - Use descriptive title
   - Include detailed description
   - Reference related issues
   - Add screenshots for UI changes

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests
- [ ] Updated existing tests

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

### Review Criteria

Reviewers will check for:
- **Functionality**: Does the code work as intended?
- **Code Quality**: Is the code clean and maintainable?
- **Performance**: Are there any performance implications?
- **Security**: Are there any security concerns?
- **Testing**: Is the code adequately tested?
- **Documentation**: Is the code properly documented?

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Reproduce the bug
3. Test with latest version
4. Gather system information

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g. macOS 12.0]
- Browser: [e.g. Chrome 95]
- Version: [e.g. 1.0.0]

**Screenshots**
If applicable, add screenshots

**Additional Context**
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other solutions you've considered

**Additional Context**
Mockups, examples, or references
```

## 🏗️ Architecture Guidelines

### Backend Architecture

- **FastAPI**: RESTful API design
- **LangGraph**: AI agent orchestration
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **Redis**: Caching layer

### Frontend Architecture

- **React**: Component-based UI
- **Redux Toolkit**: State management
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **React Router**: Navigation

### Database Design

- **PostgreSQL**: Primary database
- **Migrations**: Use Alembic for schema changes
- **Indexing**: Optimize query performance
- **Relationships**: Proper foreign key constraints

## 🔒 Security Guidelines

### Security Best Practices

- **Input Validation**: Validate all user inputs
- **Authentication**: Use JWT tokens properly
- **Authorization**: Check permissions for all actions
- **SQL Injection**: Use parameterized queries
- **XSS Prevention**: Sanitize user content
- **HTTPS**: Use HTTPS in production
- **Secrets**: Never commit secrets to git

### Reporting Security Issues

For security vulnerabilities:
1. **DO NOT** create public issues
2. Email security@vipermind.com
3. Include detailed description
4. Provide reproduction steps
5. Allow time for fix before disclosure

## 📚 Documentation

### Documentation Standards

- **API Documentation**: Use OpenAPI/Swagger
- **Code Comments**: Explain complex logic
- **README Updates**: Keep README current
- **Changelog**: Document all changes
- **Architecture Docs**: Explain design decisions

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Keep documentation up-to-date
- Test all examples

## 🎯 Performance Guidelines

### Performance Best Practices

- **Database**: Optimize queries and use indexes
- **Caching**: Use Redis for frequently accessed data
- **API**: Implement pagination for large datasets
- **Frontend**: Use lazy loading and code splitting
- **Images**: Optimize image sizes and formats

### Performance Testing

- Run performance tests for new features
- Monitor response times
- Check memory usage
- Test with realistic data volumes

## 🌍 Internationalization

### i18n Guidelines

- Use translation keys, not hardcoded strings
- Support RTL languages
- Consider cultural differences
- Test with different locales
- Use proper date/time formatting

## ♿ Accessibility

### Accessibility Standards

- Follow WCAG 2.1 AA guidelines
- Use semantic HTML elements
- Provide alt text for images
- Ensure keyboard navigation
- Test with screen readers
- Maintain color contrast ratios

## 📞 Getting Help

### Community Support

- **GitHub Discussions**: Ask questions and share ideas
- **Issues**: Report bugs and request features
- **Email**: contact@vipermind.com
- **Documentation**: Check docs/ directory

### Development Setup Help

If you need help setting up the development environment:

1. Check the README.md
2. Review docs/development/setup.md
3. Search existing issues
4. Create a new issue with "setup" label

## 🏆 Recognition

### Contributors

We recognize contributors in:
- README.md contributors section
- Release notes
- Annual contributor report
- Special recognition for significant contributions

### Contribution Types

We value all types of contributions:
- Code contributions
- Bug reports
- Documentation improvements
- Community support
- Testing and QA
- Design and UX feedback

## 📄 License

By contributing to ViperMind, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You

Thank you for contributing to ViperMind! Your efforts help make Python learning more accessible and effective for everyone.

---

**Questions?** Feel free to reach out to the maintainers or create an issue for clarification.