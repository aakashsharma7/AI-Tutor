# 🚀 AI Tutor Application

A powerful AI-powered educational tutoring system that helps students learn and understand various topics through interactive sessions.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)

## 🌟 Overview
AI Tutor is an educational platform that leverages artificial intelligence to provide personalized tutoring experiences. The application consists of a modern frontend built with React and a robust backend powered by FastAPI.

## ✨ Features
- 🔐 Secure authentication with JWT and Google OAuth
- 🤖 AI-powered tutoring sessions
- 📝 Document analysis and assistance
- 💬 Interactive learning experience
- 📱 Responsive design for all devices
- 🔄 Real-time updates and caching

## 🛠️ Tech Stack

### Frontend
- ⚛️ React.js
- 🎨 Tailwind CSS
- 🔄 Redux for state management
- 📱 Responsive design
- 🔒 JWT authentication

### Backend
- 🐍 Python
- ⚡ FastAPI
- 🗄️ SQLAlchemy
- 🔐 JWT & OAuth2
- 🤖 Google Gemini AI
- 📦 PostgreSQL

## 📁 Project Structure

```
ai-tutor/
├── frontend/                 # Frontend React application
│   ├── public/              # Static files
│   ├── src/                 # Source files
│   │   ├── components/      # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── store/          # Redux store
│   │   └── utils/          # Utility functions
│   └── package.json        # Frontend dependencies
│
└── backend/                 # Backend FastAPI application
    ├── alembic/            # Database migrations
    ├── migrations/         # Migration versions
    ├── app.py             # Main application file
    ├── models.py          # Database models
    ├── schemas.py         # Pydantic schemas
    ├── database.py        # Database configuration
    └── requirements.txt   # Backend dependencies
```

## 🚀 Getting Started

### Prerequisites
- Node.js (v14 or higher)
- Python (v3.8 or higher)
- PostgreSQL

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```

## 🔑 Environment Variables

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/ai_tutor
SECRET_KEY=your_secret_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GEMINI_API_KEY=your_gemini_api_key
FRONTEND_URL=http://localhost:3000
```

## 📚 API Documentation

The API documentation is available at `/docs` when running the backend server. Key endpoints include:

- 🔐 `/token` - Authentication endpoint
- 👤 `/users/me` - Get current user info
- 🎓 `/tutor` - AI tutoring endpoint
- 📤 `/upload` - Document upload and analysis
- 🔍 `/health` - Health check endpoint

## 🚀 Deployment

### Frontend Deployment (Vercel)
```bash
cd frontend
vercel
```

### Backend Deployment
```bash
cd backend
# Configure your production environment variables
uvicorn app:app --host 0.0.0.0 --port 8000
```

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request. 