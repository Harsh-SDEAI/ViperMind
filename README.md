# ViperMind - AI-Powered Python Tutoring Platform

ViperMind is a comprehensive Python tutoring platform that provides structured learning through a three-level curriculum (Beginner, Intermediate, Advanced) powered by AI agents.

## Project Structure

```
vipermind/
├── backend/                 # Python FastAPI backend with LangGraph agents
│   ├── app/
│   │   ├── agents/         # LangGraph AI agents
│   │   ├── api/            # FastAPI routes
│   │   ├── core/           # Core configuration and security
│   │   ├── db/             # Database configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic services
│   │   └── utils/          # Utility functions
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend Docker configuration
├── frontend/               # React TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── store/          # Redux store configuration
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Utility functions
│   ├── package.json        # Node.js dependencies
│   └── Dockerfile         # Frontend Docker configuration
├── docker-compose.yml      # Multi-service Docker setup
└── README.md              # This file
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **LangGraph**: AI agent orchestration
- **OpenAI API**: GPT-4 for intelligent content generation
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe JavaScript
- **Redux Toolkit**: State management
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing

## Getting Started

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd vipermind
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=your-openai-api-key-here
```

4. Start the development environment:
```bash
docker-compose up -d
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development

To run individual services for development:

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

## Features

- **Structured Learning**: Three-level curriculum (Beginner, Intermediate, Advanced)
- **AI-Powered Content**: Dynamic lesson generation and personalized explanations
- **Adaptive Assessments**: AI-generated questions based on user performance
- **Progress Tracking**: Comprehensive progress monitoring and analytics
- **Responsive Design**: Works across desktop and mobile devices

## License

This project is licensed under the MIT License.