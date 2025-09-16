import { useState, useEffect } from 'react';

interface BreakpointConfig {
  sm: number;
  md: number;
  lg: number;
  xl: number;
  '2xl': number;
}

const breakpoints: BreakpointConfig = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
};

export interface ResponsiveState {
  width: number;
  height: number;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isSmall: boolean;
  isMedium: boolean;
  isLarge: boolean;
  isXLarge: boolean;
  is2XLarge: boolean;
  orientation: 'portrait' | 'landscape';
}

export const useResponsive = (): ResponsiveState => {
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1024,
    height: typeof window !== 'undefined' ? window.innerHeight : 768,
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const { width, height } = windowSize;

  return {
    width,
    height,
    isMobile: width < breakpoints.md,
    isTablet: width >= breakpoints.md && width < breakpoints.lg,
    isDesktop: width >= breakpoints.lg,
    isSmall: width >= breakpoints.sm,
    isMedium: width >= breakpoints.md,
    isLarge: width >= breakpoints.lg,
    isXLarge: width >= breakpoints.xl,
    is2XLarge: width >= breakpoints['2xl'],
    orientation: height > width ? 'portrait' : 'landscape',
  };
};

export const useBreakpoint = (breakpoint: keyof BreakpointConfig): boolean => {
  const { width } = useResponsive();
  return width >= breakpoints[breakpoint];
};

export default useResponsive;