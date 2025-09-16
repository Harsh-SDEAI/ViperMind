import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import lessonService, { LessonResponse, NavigationResponse } from '../../services/lessons';
import LessonContent from './LessonContent';
import LessonNavigation from './LessonNavigation';
import ProgressTracker from './ProgressTracker';
import LoadingSpinner from '../common/LoadingSpinner';

const LessonViewer: React.FC = () => {
  const { topicId } = useParams<{ topicId: string }>();
  const navigate = useNavigate();
  
  const [lesson, setLesson] = useState<LessonResponse | null>(null);
  const [navigation, setNavigation] = useState<{
    next?: NavigationResponse;
    previous?: NavigationResponse;
  }>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startTime] = useState(Date.now());
  const [isCompleted, setIsCompleted] = useState(false);

  useEffect(() => {
    if (topicId) {
      loadLesson(topicId);
      loadNavigation(topicId);
    }
  }, [topicId]);

  useEffect(() => {
    if (lesson) {
      setIsCompleted(lesson.user_progress.status === 'completed');
    }
  }, [lesson]);

  const loadLesson = async (id: string) => {
    try {
      setLoading(true);
      const lessonData = await lessonService.getLessonContent(id);
      setLesson(lessonData);
    } catch (err) {
      setError('Failed to load lesson content');
      console.error('Error loading lesson:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadNavigation = async (id: string) => {
    try {
      const [nextData, previousData] = await Promise.all([
        lessonService.getNextTopic(id),
        lessonService.getPreviousTopic(id)
      ]);
      
      setNavigation({
        next: nextData,
        previous: previousData
      });
    } catch (err) {
      console.error('Error loading navigation:', err);
    }
  };

  const handleMarkComplete = async () => {
    if (!topicId) return;

    try {
      const timeSpent = Math.floor((Date.now() - startTime) / 1000);
      
      await lessonService.updateProgress({
        topic_id: topicId,
        completed: true,
        time_spent: timeSpent
      });

      setIsCompleted(true);
      
      // Reload lesson to get updated progress
      await loadLesson(topicId);
      
    } catch (err) {
      console.error('Error marking lesson complete:', err);
    }
  };

  const handleNavigate = (targetTopicId: string) => {
    navigate(`/learn/topic/${targetTopicId}`);
  };

  const handleBackToCurriculum = () => {
    navigate('/curriculum');
  };

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error || !lesson) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <div className="text-center">
          <div className="text-red-600 text-lg font-medium mb-2">Error</div>
          <div className="text-gray-600">{error || 'Lesson not found'}</div>
          <button
            onClick={handleBackToCurriculum}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Curriculum
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={handleBackToCurriculum}
          className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Curriculum
        </button>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {lesson.topic_name}
            </h1>
            {lesson.is_generated && (
              <div className="flex items-center text-sm text-blue-600">
                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                AI-Generated Content
              </div>
            )}
          </div>
          
          <ProgressTracker
            progress={lesson.user_progress}
            isCompleted={isCompleted}
            onMarkComplete={handleMarkComplete}
          />
        </div>
      </div>

      {/* Lesson Content */}
      <div className="mb-8">
        <LessonContent content={lesson.lesson_content} />
      </div>

      {/* Navigation */}
      <div className="border-t pt-6">
        <LessonNavigation
          navigation={navigation}
          onNavigate={handleNavigate}
          isCompleted={isCompleted}
        />
      </div>
    </div>
  );
};

export default LessonViewer;