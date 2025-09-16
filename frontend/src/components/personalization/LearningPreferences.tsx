import React, { useState, useEffect } from 'react';
import personalizationService, { UserProfile, LearningStyleUpdate } from '../../services/personalization';

interface LearningPreferencesProps {
  onUpdate?: (profile: UserProfile) => void;
  className?: string;
}

const LearningPreferences: React.FC<LearningPreferencesProps> = ({
  onUpdate,
  className = ''
}) => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Form state
  const [interests, setInterests] = useState<string[]>([]);
  const [preferredExamples, setPreferredExamples] = useState('general');
  const [learningPace, setLearningPace] = useState('moderate');
  const [newInterest, setNewInterest] = useState('');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      const profileData = await personalizationService.getUserProfile();
      setProfile(profileData);
      
      // Update form state
      setInterests(profileData.interests || []);
      setLearningPace(profileData.learning_pace || 'moderate');
      
      // Extract preferred examples from personalization data
      const personalData = profileData.adaptation_strategies || {};
      setPreferredExamples(personalData.preferred_examples || 'general');
      
    } catch (err) {
      setError('Failed to load learning preferences');
      console.error('Error loading profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const analyzeLearningStyle = async () => {
    try {
      setAnalyzing(true);
      setError(null);
      
      const result = await personalizationService.analyzeLearningStyle();
      
      if (result.success) {
        setSuccessMessage('Learning style analysis completed! Your profile has been updated.');
        await loadProfile(); // Reload profile with new data
        
        if (onUpdate && profile) {
          onUpdate(profile);
        }
      } else {
        setError(result.error || 'Analysis failed');
      }
    } catch (err) {
      setError('Error analyzing learning style');
      console.error('Error analyzing:', err);
    } finally {
      setAnalyzing(false);
    }
  };

  const savePreferences = async () => {
    try {
      setSaving(true);
      setError(null);
      setSuccessMessage(null);

      const preferences: LearningStyleUpdate = {
        interests,
        preferred_examples: preferredExamples,
        learning_pace_preference: learningPace
      };

      const result = await personalizationService.updateLearningPreferences(preferences);
      
      if (result.success) {
        setSuccessMessage('Learning preferences updated successfully!');
        await loadProfile(); // Reload profile
        
        if (onUpdate && profile) {
          onUpdate(profile);
        }
      } else {
        setError('Failed to update preferences');
      }
    } catch (err) {
      setError('Error saving preferences');
      console.error('Error saving:', err);
    } finally {
      setSaving(false);
    }
  };

  const addInterest = () => {
    if (newInterest.trim() && !interests.includes(newInterest.trim())) {
      setInterests([...interests, newInterest.trim()]);
      setNewInterest('');
    }
  };

  const removeInterest = (interest: string) => {
    setInterests(interests.filter(i => i !== interest));
  };

  const getLearningStyleIcon = (style: string) => {
    switch (style) {
      case 'visual': return '👁️';
      case 'auditory': return '👂';
      case 'kinesthetic': return '✋';
      case 'reading_writing': return '📝';
      default: return '🧠';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg border p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg border ${className}`}>
      {/* Header */}
      <div className="p-6 border-b">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Learning Preferences</h2>
            <p className="text-gray-600 mt-1">Customize your learning experience</p>
          </div>
          
          <button
            onClick={analyzeLearningStyle}
            disabled={analyzing}
            className={`flex items-center px-4 py-2 rounded-lg transition-colors ${
              analyzing 
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                : 'bg-purple-600 text-white hover:bg-purple-700'
            }`}
          >
            <svg className={`w-4 h-4 mr-2 ${analyzing ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            {analyzing ? 'Analyzing...' : 'AI Analysis'}
          </button>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Current Learning Style */}
        {profile && (
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-3">Current Learning Profile</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-blue-700">Learning Style:</span>
                <div className="flex items-center mt-1">
                  <span className="mr-2">{getLearningStyleIcon(profile.primary_learning_style)}</span>
                  <span className="font-medium text-blue-900 capitalize">
                    {profile.primary_learning_style.replace('_', ' ')}
                  </span>
                </div>
              </div>
              
              <div>
                <span className="text-blue-700">Content Preference:</span>
                <div className="font-medium text-blue-900 mt-1 capitalize">
                  {profile.content_preference.replace('_', ' ')}
                </div>
              </div>
              
              <div>
                <span className="text-blue-700">Learning Pace:</span>
                <div className="font-medium text-blue-900 mt-1 capitalize">
                  {profile.learning_pace}
                </div>
              </div>
              
              <div>
                <span className="text-blue-700">Confidence:</span>
                <div className={`font-medium mt-1 ${getConfidenceColor(profile.learning_style_confidence)}`}>
                  {Math.round(profile.learning_style_confidence * 100)}%
                </div>
              </div>
            </div>
            
            {profile.last_analysis_date && (
              <div className="text-xs text-blue-600 mt-3">
                Last analyzed: {new Date(profile.last_analysis_date).toLocaleDateString()}
              </div>
            )}
          </div>
        )}

        {/* Interests */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Your Interests
            <span className="text-gray-500 font-normal ml-1">(helps personalize examples)</span>
          </label>
          
          <div className="flex flex-wrap gap-2 mb-3">
            {interests.map((interest, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
              >
                {interest}
                <button
                  onClick={() => removeInterest(interest)}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          
          <div className="flex space-x-2">
            <input
              type="text"
              value={newInterest}
              onChange={(e) => setNewInterest(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addInterest()}
              placeholder="Add an interest (e.g., games, science, web development)"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              onClick={addInterest}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Add
            </button>
          </div>
        </div>

        {/* Preferred Examples */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Preferred Example Context
          </label>
          <select
            value={preferredExamples}
            onChange={(e) => setPreferredExamples(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="general">General Programming</option>
            <option value="games">Game Development</option>
            <option value="web">Web Development</option>
            <option value="data">Data Science</option>
            <option value="automation">Automation & Scripts</option>
            <option value="science">Scientific Computing</option>
            <option value="business">Business Applications</option>
          </select>
        </div>

        {/* Learning Pace */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Learning Pace Preference
          </label>
          <div className="space-y-2">
            {[
              { value: 'fast', label: 'Fast', description: 'Quick overviews, minimal repetition' },
              { value: 'moderate', label: 'Moderate', description: 'Balanced pace with good explanations' },
              { value: 'thorough', label: 'Thorough', description: 'Detailed explanations, lots of examples' }
            ].map((option) => (
              <label key={option.value} className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="radio"
                  name="learningPace"
                  value={option.value}
                  checked={learningPace === option.value}
                  onChange={(e) => setLearningPace(e.target.value)}
                  className="mt-1 text-blue-600 focus:ring-blue-500"
                />
                <div>
                  <div className="font-medium text-gray-900">{option.label}</div>
                  <div className="text-sm text-gray-600">{option.description}</div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Messages */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-red-600 text-sm">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <p className="text-green-600 text-sm">{successMessage}</p>
          </div>
        )}

        {/* Save Button */}
        <div className="flex justify-end pt-4 border-t">
          <button
            onClick={savePreferences}
            disabled={saving}
            className={`px-6 py-2 rounded-lg font-medium transition-colors ${
              saving 
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {saving ? 'Saving...' : 'Save Preferences'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default LearningPreferences;