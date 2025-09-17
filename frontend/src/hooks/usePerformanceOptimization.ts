import { useEffect, useCallback, useRef } from 'react';
import { useDispatch } from 'react-redux';
import { invalidateCache as invalidateCurriculumCache } from '../store/slices/curriculumSlice';
import { invalidateCache as invalidateAssessmentCache } from '../store/slices/assessmentSlice';

interface PerformanceMetrics {
  renderTime: number;
  memoryUsage: number;
  cacheHitRate: number;
}

export const usePerformanceOptimization = () => {
  const dispatch = useDispatch();
  const metricsRef = useRef<PerformanceMetrics[]>([]);
  const renderStartTime = useRef<number>(0);

  // Measure component render time
  const startRenderMeasurement = useCallback(() => {
    renderStartTime.current = performance.now();
  }, []);

  const endRenderMeasurement = useCallback((componentName: string) => {
    const renderTime = performance.now() - renderStartTime.current;
    
    // Log slow renders
    if (renderTime > 100) {
      console.warn(`Slow render detected in ${componentName}: ${renderTime.toFixed(2)}ms`);
    }
    
    // Store metrics
    metricsRef.current.push({
      renderTime,
      memoryUsage: getMemoryUsage(),
      cacheHitRate: 0, // Will be calculated separately
    });
    
    // Keep only last 100 measurements
    if (metricsRef.current.length > 100) {
      metricsRef.current = metricsRef.current.slice(-100);
    }
  }, []);

  // Get memory usage (if available)
  const getMemoryUsage = useCallback((): number => {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      return memory.usedJSHeapSize / memory.totalJSHeapSize * 100;
    }
    return 0;
  }, []);

  // Optimize images with lazy loading
  const optimizeImage = useCallback((src: string, options?: { 
    width?: number; 
    height?: number; 
    quality?: number;
  }) => {
    const { width, height, quality = 80 } = options || {};
    
    // Create optimized image URL (this would typically use a CDN or image service)
    let optimizedSrc = src;
    
    if (width || height) {
      const params = new URLSearchParams();
      if (width) params.append('w', width.toString());
      if (height) params.append('h', height.toString());
      params.append('q', quality.toString());
      
      optimizedSrc = `${src}?${params.toString()}`;
    }
    
    return optimizedSrc;
  }, []);

  // Debounce function for performance
  const debounce = useCallback(<T extends (...args: any[]) => any>(
    func: T,
    delay: number
  ): ((...args: Parameters<T>) => void) => {
    let timeoutId: NodeJS.Timeout;
    
    return (...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    };
  }, []);

  // Throttle function for performance
  const throttle = useCallback(<T extends (...args: any[]) => any>(
    func: T,
    delay: number
  ): ((...args: Parameters<T>) => void) => {
    let lastCall = 0;
    
    return (...args: Parameters<T>) => {
      const now = Date.now();
      if (now - lastCall >= delay) {
        lastCall = now;
        func(...args);
      }
    };
  }, []);

  // Memoize expensive calculations
  const memoize = useCallback(<T extends (...args: any[]) => any>(
    func: T,
    keyGenerator?: (...args: Parameters<T>) => string
  ) => {
    const cache = new Map<string, ReturnType<T>>();
    
    return (...args: Parameters<T>): ReturnType<T> => {
      const key = keyGenerator ? keyGenerator(...args) : JSON.stringify(args);
      
      if (cache.has(key)) {
        return cache.get(key)!;
      }
      
      const result = func(...args);
      cache.set(key, result);
      
      // Limit cache size
      if (cache.size > 100) {
        const firstKey = cache.keys().next().value;
        cache.delete(firstKey);
      }
      
      return result;
    };
  }, []);

  // Preload critical resources
  const preloadResource = useCallback((url: string, type: 'script' | 'style' | 'image' | 'fetch') => {
    if (type === 'fetch') {
      // Preload data
      fetch(url, { method: 'HEAD' }).catch(() => {
        // Ignore errors for preloading
      });
    } else {
      // Preload assets
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = url;
      
      switch (type) {
        case 'script':
          link.as = 'script';
          break;
        case 'style':
          link.as = 'style';
          break;
        case 'image':
          link.as = 'image';
          break;
      }
      
      document.head.appendChild(link);
    }
  }, []);

  // Clean up old cache entries
  const cleanupCache = useCallback(() => {
    // Clear curriculum cache if it's older than 5 minutes
    const curriculumCacheTime = localStorage.getItem('curriculum_cache_time');
    if (curriculumCacheTime) {
      const cacheAge = Date.now() - parseInt(curriculumCacheTime);
      if (cacheAge > 5 * 60 * 1000) {
        dispatch(invalidateCurriculumCache());
        localStorage.removeItem('curriculum_cache_time');
      }
    }
    
    // Clear assessment cache if it's older than 30 minutes
    const assessmentCacheTime = localStorage.getItem('assessment_cache_time');
    if (assessmentCacheTime) {
      const cacheAge = Date.now() - parseInt(assessmentCacheTime);
      if (cacheAge > 30 * 60 * 1000) {
        dispatch(invalidateAssessmentCache());
        localStorage.removeItem('assessment_cache_time');
      }
    }
  }, [dispatch]);

  // Monitor performance metrics
  const getPerformanceMetrics = useCallback(() => {
    const metrics = metricsRef.current;
    if (metrics.length === 0) return null;
    
    const avgRenderTime = metrics.reduce((sum, m) => sum + m.renderTime, 0) / metrics.length;
    const avgMemoryUsage = metrics.reduce((sum, m) => sum + m.memoryUsage, 0) / metrics.length;
    const slowRenders = metrics.filter(m => m.renderTime > 100).length;
    
    return {
      averageRenderTime: avgRenderTime,
      averageMemoryUsage: avgMemoryUsage,
      slowRenderCount: slowRenders,
      totalMeasurements: metrics.length,
      performanceScore: calculatePerformanceScore(avgRenderTime, avgMemoryUsage, slowRenders)
    };
  }, []);

  // Calculate performance score (0-100)
  const calculatePerformanceScore = (avgRenderTime: number, avgMemoryUsage: number, slowRenders: number): number => {
    let score = 100;
    
    // Penalize slow render times
    if (avgRenderTime > 50) score -= Math.min(30, (avgRenderTime - 50) / 2);
    
    // Penalize high memory usage
    if (avgMemoryUsage > 70) score -= Math.min(20, (avgMemoryUsage - 70) / 2);
    
    // Penalize frequent slow renders
    const slowRenderRate = slowRenders / metricsRef.current.length;
    if (slowRenderRate > 0.1) score -= Math.min(25, slowRenderRate * 100);
    
    return Math.max(0, Math.round(score));
  };

  // Set up performance monitoring
  useEffect(() => {
    // Clean up cache on mount
    cleanupCache();
    
    // Set up periodic cache cleanup
    const cleanupInterval = setInterval(cleanupCache, 60000); // Every minute
    
    // Monitor memory usage
    const memoryInterval = setInterval(() => {
      const memoryUsage = getMemoryUsage();
      if (memoryUsage > 90) {
        console.warn(`High memory usage detected: ${memoryUsage.toFixed(1)}%`);
      }
    }, 30000); // Every 30 seconds
    
    return () => {
      clearInterval(cleanupInterval);
      clearInterval(memoryInterval);
    };
  }, [cleanupCache, getMemoryUsage]);

  // Intersection Observer for lazy loading
  const createIntersectionObserver = useCallback((
    callback: (entries: IntersectionObserverEntry[]) => void,
    options?: IntersectionObserverInit
  ) => {
    if (!('IntersectionObserver' in window)) {
      // Fallback for browsers without IntersectionObserver
      return {
        observe: () => {},
        unobserve: () => {},
        disconnect: () => {}
      };
    }
    
    return new IntersectionObserver(callback, {
      rootMargin: '50px',
      threshold: 0.1,
      ...options
    });
  }, []);

  return {
    startRenderMeasurement,
    endRenderMeasurement,
    optimizeImage,
    debounce,
    throttle,
    memoize,
    preloadResource,
    cleanupCache,
    getPerformanceMetrics,
    createIntersectionObserver,
  };
};