import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoginForm from './components/auth/LoginForm';
import RegisterForm from './components/auth/RegisterForm';
import Dashboard from './components/Dashboard';
import CurriculumOverview from './components/curriculum/CurriculumOverview';
import LessonViewer from './components/lessons/LessonViewer';
import QuizInterface from './components/assessments/QuizInterface';
import TestInterface from './components/assessments/TestInterface';
import Layout from './components/layout/Layout';
import './App.css';

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<LoginForm />} />
          <Route path="/register" element={<RegisterForm />} />
          
          {/* Protected routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Layout>
                  <Dashboard />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/curriculum"
            element={
              <ProtectedRoute>
                <Layout>
                  <CurriculumOverview />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/learn/topic/:topicId"
            element={
              <ProtectedRoute>
                <Layout>
                  <LessonViewer />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/quiz/:targetId"
            element={
              <ProtectedRoute>
                <Layout>
                  <QuizInterface />
                </Layout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/test/:testType/:targetId"
            element={
              <ProtectedRoute>
                <Layout>
                  <TestInterface />
                </Layout>
              </ProtectedRoute>
            }
          />
          
          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/curriculum" replace />} />
          
          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </AuthProvider>
  );
}

export default App;