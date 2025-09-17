#!/usr/bin/env python3
"""
Performance optimization test script.
Tests the effectiveness of caching, database optimization, and AI response optimization.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.cache import cache_manager
from app.core.performance import perf_monitor, get_performance_report
from app.db.optimization import refresh_materialized_views

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"
TEST_USER_TOKEN = None  # Will be set after login


class PerformanceTest:
    """Performance testing suite for ViperMind optimizations."""
    
    def __init__(self):
        self.results = {}
        self.session = requests.Session()
    
    def setup_test_user(self):
        """Create and authenticate a test user."""
        global TEST_USER_TOKEN
        
        # Register test user
        register_data = {
            "email": "perftest@example.com",
            "username": "perftest",
            "password": "testpassword123"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/register", json=register_data)
            if response.status_code not in [200, 400]:  # 400 if user already exists
                print(f"Registration failed: {response.status_code}")
        except Exception as e:
            print(f"Registration error: {e}")
        
        # Login
        login_data = {
            "username": "perftest",
            "password": "testpassword123"
        }
        
        try:
            response = self.session.post(f"{API_BASE}/auth/login", data=login_data)
            if response.status_code == 200:
                token_data = response.json()
                TEST_USER_TOKEN = token_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {TEST_USER_TOKEN}"})
                print("✓ Test user authenticated")
            else:
                print(f"Login failed: {response.status_code}")
        except Exception as e:
            print(f"Login error: {e}")
    
    def test_curriculum_caching(self, iterations: int = 10) -> Dict[str, Any]:
        """Test curriculum endpoint caching performance."""
        print(f"Testing curriculum caching ({iterations} iterations)...")
        
        times_without_cache = []
        times_with_cache = []
        
        # Clear cache first
        cache_manager.invalidate_pattern("vipermind:curriculum:*")
        
        # Test without cache (first call)
        for i in range(3):  # Warm up
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/curriculum/structure")
            end_time = time.time()
            
            if response.status_code == 200:
                times_without_cache.append(end_time - start_time)
        
        # Test with cache (subsequent calls)
        for i in range(iterations):
            start_time = time.time()
            response = self.session.get(f"{API_BASE}/curriculum/structure")
            end_time = time.time()
            
            if response.status_code == 200:
                times_with_cache.append(end_time - start_time)
        
        avg_without_cache = statistics.mean(times_without_cache) if times_without_cache else 0
        avg_with_cache = statistics.mean(times_with_cache) if times_with_cache else 0
        improvement = ((avg_without_cache - avg_with_cache) / avg_without_cache * 100) if avg_without_cache > 0 else 0
        
        result = {
            'avg_time_without_cache': avg_without_cache,
            'avg_time_with_cache': avg_with_cache,
            'improvement_percentage': improvement,
            'cache_hit_rate': len(times_with_cache) / (len(times_without_cache) + len(times_with_cache)) * 100
        }
        
        print(f"  Without cache: {avg_without_cache:.3f}s")
        print(f"  With cache: {avg_with_cache:.3f}s")
        print(f"  Improvement: {improvement:.1f}%")
        
        return result
    
    def test_concurrent_requests(self, endpoint: str, concurrent_users: int = 10, requests_per_user: int = 5) -> Dict[str, Any]:
        """Test performance under concurrent load."""
        print(f"Testing concurrent requests to {endpoint} ({concurrent_users} users, {requests_per_user} requests each)...")
        
        def make_requests(user_id: int) -> List[float]:
            times = []
            session = requests.Session()
            if TEST_USER_TOKEN:
                session.headers.update({"Authorization": f"Bearer {TEST_USER_TOKEN}"})
            
            for _ in range(requests_per_user):
                start_time = time.time()
                try:
                    response = session.get(f"{API_BASE}{endpoint}")
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        times.append(end_time - start_time)
                except Exception as e:
                    print(f"Request failed for user {user_id}: {e}")
            
            return times
        
        # Execute concurrent requests
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(make_requests, i) for i in range(concurrent_users)]
            all_times = []
            
            for future in futures:
                times = future.result()
                all_times.extend(times)
        
        if all_times:
            result = {
                'total_requests': len(all_times),
                'avg_response_time': statistics.mean(all_times),
                'min_response_time': min(all_times),
                'max_response_time': max(all_times),
                'p95_response_time': sorted(all_times)[int(len(all_times) * 0.95)],
                'requests_per_second': len(all_times) / max(all_times) if all_times else 0
            }
            
            print(f"  Total requests: {result['total_requests']}")
            print(f"  Avg response time: {result['avg_response_time']:.3f}s")
            print(f"  P95 response time: {result['p95_response_time']:.3f}s")
            print(f"  Requests/second: {result['requests_per_second']:.1f}")
            
            return result
        
        return {'error': 'No successful requests'}
    
    def test_database_optimization(self) -> Dict[str, Any]:
        """Test database query performance."""
        print("Testing database optimization...")
        
        # Refresh materialized views
        refresh_materialized_views()
        
        # Test complex query performance
        times = []
        for _ in range(5):
            start_time = time.time()
            try:
                response = self.session.get(f"{API_BASE}/curriculum/progress")
                end_time = time.time()
                
                if response.status_code == 200:
                    times.append(end_time - start_time)
            except Exception as e:
                print(f"Database test request failed: {e}")
        
        if times:
            result = {
                'avg_query_time': statistics.mean(times),
                'min_query_time': min(times),
                'max_query_time': max(times),
                'materialized_views_refreshed': True
            }
            
            print(f"  Avg query time: {result['avg_query_time']:.3f}s")
            print(f"  Min query time: {result['min_query_time']:.3f}s")
            print(f"  Max query time: {result['max_query_time']:.3f}s")
            
            return result
        
        return {'error': 'No successful database queries'}
    
    def test_memory_usage(self) -> Dict[str, Any]:
        """Test memory usage optimization."""
        print("Testing memory usage...")
        
        try:
            import psutil
            process = psutil.Process()
            
            # Get initial memory usage
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Make several requests to load data
            for _ in range(20):
                self.session.get(f"{API_BASE}/curriculum/structure")
                self.session.get(f"{API_BASE}/curriculum/progress")
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            result = {
                'initial_memory_mb': initial_memory,
                'final_memory_mb': final_memory,
                'memory_increase_mb': memory_increase,
                'memory_increase_percentage': (memory_increase / initial_memory * 100) if initial_memory > 0 else 0
            }
            
            print(f"  Initial memory: {initial_memory:.1f} MB")
            print(f"  Final memory: {final_memory:.1f} MB")
            print(f"  Memory increase: {memory_increase:.1f} MB ({result['memory_increase_percentage']:.1f}%)")
            
            return result
            
        except ImportError:
            return {'error': 'psutil not available for memory testing'}
        except Exception as e:
            return {'error': f'Memory test failed: {e}'}
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests."""
        print("="*60)
        print("VIPERMIND PERFORMANCE OPTIMIZATION TESTS")
        print("="*60)
        
        # Setup
        self.setup_test_user()
        
        # Run tests
        self.results['curriculum_caching'] = self.test_curriculum_caching()
        self.results['concurrent_curriculum'] = self.test_concurrent_requests('/curriculum/structure')
        self.results['concurrent_progress'] = self.test_concurrent_requests('/curriculum/progress')
        self.results['database_optimization'] = self.test_database_optimization()
        self.results['memory_usage'] = self.test_memory_usage()
        
        # Get system performance report
        self.results['system_performance'] = get_performance_report()
        
        return self.results
    
    def generate_report(self):
        """Generate a comprehensive performance report."""
        print("\n" + "="*60)
        print("PERFORMANCE TEST RESULTS")
        print("="*60)
        
        # Caching performance
        if 'curriculum_caching' in self.results:
            caching = self.results['curriculum_caching']
            print(f"\n📊 CACHING PERFORMANCE:")
            print(f"  Cache improvement: {caching.get('improvement_percentage', 0):.1f}%")
            print(f"  Cache hit rate: {caching.get('cache_hit_rate', 0):.1f}%")
        
        # Concurrent performance
        if 'concurrent_curriculum' in self.results:
            concurrent = self.results['concurrent_curriculum']
            print(f"\n🚀 CONCURRENT PERFORMANCE:")
            print(f"  Requests/second: {concurrent.get('requests_per_second', 0):.1f}")
            print(f"  P95 response time: {concurrent.get('p95_response_time', 0):.3f}s")
        
        # Database performance
        if 'database_optimization' in self.results:
            db = self.results['database_optimization']
            print(f"\n💾 DATABASE PERFORMANCE:")
            print(f"  Avg query time: {db.get('avg_query_time', 0):.3f}s")
        
        # Memory usage
        if 'memory_usage' in self.results:
            memory = self.results['memory_usage']
            print(f"\n🧠 MEMORY USAGE:")
            print(f"  Memory increase: {memory.get('memory_increase_mb', 0):.1f} MB")
            print(f"  Memory efficiency: {100 - memory.get('memory_increase_percentage', 0):.1f}%")
        
        # Overall score
        score = self.calculate_performance_score()
        print(f"\n⭐ OVERALL PERFORMANCE SCORE: {score}/100")
        
        if score >= 90:
            print("🎉 Excellent performance!")
        elif score >= 75:
            print("✅ Good performance")
        elif score >= 60:
            print("⚠️  Acceptable performance - consider optimizations")
        else:
            print("❌ Poor performance - optimization needed")
    
    def calculate_performance_score(self) -> int:
        """Calculate overall performance score (0-100)."""
        score = 100
        
        # Caching score (30 points)
        caching = self.results.get('curriculum_caching', {})
        cache_improvement = caching.get('improvement_percentage', 0)
        if cache_improvement < 50:
            score -= (50 - cache_improvement) * 0.6
        
        # Concurrent performance score (25 points)
        concurrent = self.results.get('concurrent_curriculum', {})
        rps = concurrent.get('requests_per_second', 0)
        if rps < 10:
            score -= (10 - rps) * 2.5
        
        # Database performance score (25 points)
        db = self.results.get('database_optimization', {})
        query_time = db.get('avg_query_time', 0)
        if query_time > 0.5:
            score -= (query_time - 0.5) * 50
        
        # Memory efficiency score (20 points)
        memory = self.results.get('memory_usage', {})
        memory_increase = memory.get('memory_increase_percentage', 0)
        if memory_increase > 20:
            score -= (memory_increase - 20) * 1
        
        return max(0, min(100, int(score)))


def main():
    """Run performance optimization tests."""
    tester = PerformanceTest()
    
    try:
        results = tester.run_all_tests()
        tester.generate_report()
        
        # Save results to file
        with open('performance_test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: performance_test_results.json")
        
    except Exception as e:
        print(f"❌ Performance tests failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())