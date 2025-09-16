import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Welcome to ViperMind!
              </h2>
              <div className="bg-white shadow rounded-lg p-6 max-w-md mx-auto">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Your Profile</h3>
                <div className="space-y-2 text-left">
                  <p><strong>Username:</strong> {user?.username}</p>
                  <p><strong>Email:</strong> {user?.email}</p>
                  <p><strong>Current Level:</strong> 
                    <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                      {user?.current_level}
                    </span>
                  </p>
                  <p><strong>Member since:</strong> {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</p>
                </div>
              </div>
              <div className="mt-8 space-y-4">
                <p className="text-gray-600">
                  Your Python learning journey starts here! 🐍
                </p>
                <div className="flex justify-center">
                  <Link
                    to="/curriculum"
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium"
                  >
                    Start Learning
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
    </div>
  );
};

export default Dashboard;