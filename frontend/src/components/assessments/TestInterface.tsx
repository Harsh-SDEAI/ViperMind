import React from 'react';
import AssessmentInterface from './AssessmentInterface';
import { useParams } from 'react-router-dom';

const TestInterface: React.FC = () => {
  const { testType } = useParams<{ testType: string }>();
  
  const assessmentType = testType === 'section' ? 'section_test' : 'level_final';
  
  return <AssessmentInterface assessmentType={assessmentType} />;
};

export default TestInterface;