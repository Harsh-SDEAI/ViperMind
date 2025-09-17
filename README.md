# ViperMind - AI-Powered Python Tutoring Platform

ViperMind is a comprehensive Python tutoring platform that provides structured learning through a three-level curriculum (Beginner, Intermediate, Advanced). The system delivers lessons, assessments, and progress tracking through a web-based interface with an AI agent backend managing all educational content and user progression.

## 🌟 Features

### 🎓 Comprehensive Learning System
- **Structured Curriculum**: 30 topics across 3 levels (Beginner, Intermediate, Advanced)
- **AI-Generated Content**: Personalized lessons, assessments, and explanations
- **Progressive Learning**: Unlock system with clear advancement criteria
- **Multiple Assessment Types**: Quizzes, section tests, and level finals

### 🤖 AI-Powered Intelligence
- **LangGraph Agent Architecture**: Sophisticated AI workflow management
- **Personalized Tutoring**: Adaptive content based on learning patterns
- **Dynamic Question Generation**: AI-created assessments tailored to user performance
- **Intelligent Hints**: Contextual help when students struggle

### 📊 Advanced Progress Tracking
- **Detailed Analytics**: Comprehensive learning insights and performance metrics
- **Smart Recommendations**: AI-powered suggestions for improvement
- **Remedial Support**: Targeted help for struggling areas
- **Achievement System**: Motivational progress indicators

### 🔧 Technical Excellence
- **High Performance**: Redis caching and database optimization
- **Error Resilience**: Comprehensive fallback systems
- **Mobile Responsive**: Optimized for all device types
- **Production Ready**: Docker deployment with monitoring

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: High-performance Python web framework
- **LangGraph**: AI agent orchestration and workflow management
- **OpenAI GPT-4**: Intelligent content generation
- **PostgreSQL**: Robust data persistence
- **Redis**: High-speed caching layer
- **SQLAlchemy**: Advanced ORM with optimized queries

### Frontend Stack
- **React 18**: Modern UI framework with TypeScript
- **Redux Toolkit**: Efficient state management with caching
- **Tailwind CSS**: Responsive design system
- **Axios**: Optimized API communication

### Infrastructure
- **Docker**: Containerized deployment
- **Nginx**: Reverse proxy and load balancing
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)
- OpenAI API key

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/vipermind.git
   cd vipermind
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment**
   ```bash
   docker-compose up -d
   ```

4. **Initialize the database**
   ```bash
   docker-compose exec backend python setup_database.py
   docker-compose exec backend python seed_curriculum.py
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Production Deployment

1. **Prepare production environment**
   ```bash
   cp .env.production .env
   # Update .env with your production values
   ```

2. **Deploy with the deployment script**
   ```bash
   ./scripts/deploy.sh production
   ```

3. **Verify deployment**
   ```bash
   curl http://localhost/api/v1/monitoring/status
   ```

## 📚 Documentation

### API Documentation
- **Interactive Docs**: Available at `/docs` endpoint
- **OpenAPI Spec**: Available at `/openapi.json`
- **Postman Collection**: `docs/api/ViperMind.postman_collection.json`

### User Guides
- **Student Guide**: `docs/user-guide/student-guide.md`
- **Admin Guide**: `docs/user-guide/admin-guide.md`
- **API Reference**: `docs/api/README.md`

### Developer Documentation
- **Setup Guide**: `docs/development/setup.md`
- **Architecture Overview**: `docs/development/architecture.md`
- **Contributing Guidelines**: `CONTRIBUTING.md`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Deployment environment | `development` | No |
| `POSTGRES_USER` | Database username | `postgres` | Yes |
| `POSTGRES_PASSWORD` | Database password | - | Yes |
| `POSTGRES_DB` | Database name | `vipermind` | Yes |
| `REDIS_HOST` | Redis hostname | `localhost` | No |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes |
| `SECRET_KEY` | JWT secret key | - | Yes |

### Performance Tuning

The system includes several performance optimizations:

- **Redis Caching**: Curriculum content and AI responses
- **Database Indexing**: Optimized queries for progress tracking
- **Connection Pooling**: Efficient database connections
- **CDN Ready**: Static asset optimization

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
python backend/test_integration_user_journeys.py

# Performance tests
python backend/test_performance_optimization.py
```

### Test Coverage
- Backend: >90% unit test coverage
- Frontend: >85% component test coverage
- Integration: All critical user journeys
- Performance: Load testing up to 100 concurrent users

## 📊 Monitoring

### Health Checks
- **System Status**: `/api/v1/monitoring/status`
- **Detailed Health**: `/api/v1/monitoring/health`
- **Metrics**: `/api/v1/monitoring/metrics`

### Monitoring Stack
- **Prometheus**: Metrics collection at `:9090`
- **Grafana**: Dashboards at `:3001`
- **Application Logs**: Structured JSON logging
- **Error Tracking**: Comprehensive error handling

## 🔒 Security

### Security Features
- **JWT Authentication**: Secure token-based auth
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: API endpoint protection
- **HTTPS Enforcement**: SSL/TLS encryption
- **Security Headers**: XSS and CSRF protection

### Security Best Practices
- Regular dependency updates
- Secure environment variable handling
- Database connection encryption
- API endpoint authentication
- Input sanitization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards
- **Python**: Black formatting, Flake8 linting
- **TypeScript**: ESLint, Prettier formatting
- **Commits**: Conventional commit messages
- **Documentation**: Update docs for new features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check the `docs/` directory
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Email**: support@vipermind.com

### Troubleshooting
- **Common Issues**: `docs/troubleshooting.md`
- **Performance Issues**: `docs/performance-tuning.md`
- **Deployment Issues**: `docs/deployment-troubleshooting.md`

## 🎯 Roadmap

### Upcoming Features
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Mobile app development
- [ ] Integration with external LMS
- [ ] Advanced AI personalization

### Version History
- **v1.0.0**: Initial release with core features
- **v1.1.0**: Performance optimizations and caching
- **v1.2.0**: Enhanced error handling and monitoring

---

**ViperMind** - Empowering Python learning through AI-driven education.

Made with ❤️ by the ViperMind Team