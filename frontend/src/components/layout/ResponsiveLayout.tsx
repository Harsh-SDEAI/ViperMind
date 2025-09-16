import React from 'react';
import { useResponsive } from '../../hooks/useResponsive';
import MobileNavigation from './MobileNavigation';
import Layout from './Layout';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
}

const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ children }) => {
  const { isMobile } = useResponsive();

  if (isMobile) {
    return (
      <div className="min-h-screen bg-gray-50">
        <MobileNavigation />
        <main className="pb-safe">
          {children}
        </main>
      </div>
    );
  }

  return <Layout>{children}</Layout>;
};

export default ResponsiveLayout;