#!/usr/bin/env python3
"""
Load testing and performance validation for ViperMind.
Tests system performance under various load conditions.
"""

import asyncio
import aiohttp
import time
import statistics
import json
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
import sys
from pathlib import Path
import threading

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Test configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class LoadTester:
    """Load testing suite for ViperMind system."""
    
    def __init__(self):
        self.results = {}
        self.test_users = []
        
    async def setup_test_users(self, count: int = 50):
        """Create test users for load testing."""
        print(f"👥 Setting up {count} test users...")
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for i in range(count):
                username = f"load_test_user_{i}"
                user_data = {
                    "email": f"loadtest{i}@example.com",
                    "username": username,
                    "password": "loadtest123"
                }
                
                # Register user
                try:
                    async with session.post(f"{API_BASE}/auth/register", json=user_data) as response:
                        pass  # May fail if user exists, that's ok
                except:
                    pass
                
                # Login to get token
                login_data = aiohttp.FormData()
                login_data.add_field('username', username)
                login_data.add_field('password', 'loadtest123')
                
                try:
                    async with session.post(f"{API_BASE}/auth/login", data=login_data) as response:
                        if response.status == 200:
                            token_data = await response.json()
                            self.test_users.append({
                                "username": username,
                                "token": token_data["access_token"]
                            })
                except Exception as e:
                    print(f"Failed to login user {username}: {e}")
        
        print(f"✅ Created {len(self.test_users)} test users")
    
    async def test_api_endpoint_load(self, endpoint: str, method: str = "GET", 
                                   concurrent_users: int = 10, 
                                   requests_per_user: int = 10,
                                   auth_required: bool = True) -> Dict[str, Any]:
        """Test load on a specific API endpoint."""
        
        print(f"🔥 Load testing {method} {endpoint} with {concurrent_users} users, {requests_per_user} requests each")
        
        results = {
            "endpoint": endpoint,
            "method": method,
            "concurrent_users": concurrent_users,
            "requests_per_user": requests_per_user,
            "total_requests": concurrent_users * requests_per_user,
            "response_times": [],
            "status_codes": {},
            "errors": [],
            "start_time": time.time()
        }
        
        async def make_request(session: aiohttp.ClientSession, user_index: int) -> List[Dict[str, Any]]:
            """Make requests for a single user."""
            user_results = []
            
            # Get user token if auth required
            headers = {}
            if auth_required and user_index < len(self.test_users):
                headers["Authorization"] = f"Bearer {self.test_users[user_index]['token']}"
            
            for request_num in range(requests_per_user):
                request_start = time.time()
                
                try:
                    if method.upper() == "GET":
                        async with session.get(f"{API_BASE}{endpoint}", headers=headers) as response:
                            status = response.status
                            await response.text()  # Consume response
                    elif method.upper() == "POST":
                        async with session.post(f"{API_BASE}{endpoint}", headers=headers, json={}) as response:
                            status = response.status
                            await response.text()
                    
                    response_time = time.time() - request_start
                    
                    user_results.append({
                        "response_time": response_time,
                        "status_code": status,
                        "user_index": user_index,
                        "request_num": request_num
                    })
                    
                except Exception as e:
                    response_time = time.time() - request_start
                    user_results.append({
                        "response_time": response_time,
                        "status_code": 0,
                        "error": str(e),
                        "user_index": user_index,
                        "request_num": request_num
                    })
            
            return user_results
        
        # Execute concurrent requests
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=100)
        ) as session:
            tasks = [make_request(session, i) for i in range(concurrent_users)]
            all_results = await asyncio.gather(*tasks)
        
        # Process results
        for user_results in all_results:
            for result in user_results:
                results["response_times"].append(result["response_time"])
                
                status_code = result["status_code"]
                if status_code in results["status_codes"]:
                    results["status_codes"][status_code] += 1
                else:
                    results["status_codes"][status_code] = 1
                
                if "error" in result:
                    results["errors"].append(result["error"])
        
        # Calculate statistics
        results["end_time"] = time.time()
        results["total_duration"] = results["end_time"] - results["start_time"]
        
        if results["response_times"]:
            results["avg_response_time"] = statistics.mean(results["response_times"])
            results["min_response_time"] = min(results["response_times"])
            results["max_response_time"] = max(results["response_times"])
            results["median_response_time"] = statistics.median(results["response_times"])
            
            # Calculate percentiles
            sorted_times = sorted(results["response_times"])
            results["p95_response_time"] = sorted_times[int(len(sorted_times) * 0.95)]
            results["p99_response_time"] = sorted_times[int(len(sorted_times) * 0.99)]
        
        # Calculate throughput
        successful_requests = results["status_codes"].get(200, 0)
        results["requests_per_second"] = successful_requests / results["total_duration"] if results["total_duration"] > 0 else 0
        results["success_rate"] = (successful_requests / results["total_requests"]) * 100 if results["total_requests"] > 0 else 0
        
        return results
    
    async def test_user_workflow_load(self, concurrent_users: int = 20) -> Dict[str, Any]:
        """Test load with realistic user workflows."""
        
        print(f"👤 Testing user workflow load with {concurrent_users} concurrent users")
        
        results = {
            "concurrent_users": concurrent_users,
            "workflows_completed": 0,
            "workflows_failed": 0,
            "workflow_times": [],
            "operation_times": {},
            "errors": [],
            "start_time": time.time()
        }
        
        async def simulate_user_workflow(session: aiohttp.ClientSession, user_index: int) -> Dict[str, Any]:
            """Simulate a complete user workflow."""
            workflow_start = time.time()
            workflow_result = {
                "user_index": user_index,
                "success": False,
                "operations": {},
                "total_time": 0,
                "errors": []
            }
            
            try:
                # Get user token
                if user_index < len(self.test_users):
                    headers = {"Authorization": f"Bearer {self.test_users[user_index]['token']}"}
                else:
                    headers = {}
                
                # 1. Get curriculum structure
                op_start = time.time()
                async with session.get(f"{API_BASE}/curriculum/structure") as response:
                    curriculum_time = time.time() - op_start
                    workflow_result["operations"]["curriculum"] = {
                        "time": curriculum_time,
                        "status": response.status
                    }
                    
                    if response.status == 200:
                        curriculum_data = await response.json()
                    else:
                        raise Exception(f"Curriculum request failed: {response.status}")
                
                # 2. Get progress dashboard
                op_start = time.time()
                async with session.get(f"{API_BASE}/progress/dashboard", headers=headers) as response:
                    dashboard_time = time.time() - op_start
                    workflow_result["operations"]["dashboard"] = {
                        "time": dashboard_time,
                        "status": response.status
                    }
                    
                    if response.status != 200:
                        raise Exception(f"Dashboard request failed: {response.status}")
                
                # 3. Get lesson content
                if curriculum_data.get("levels"):
                    first_topic_id = curriculum_data["levels"][0]["sections"][0]["topics"][0]["id"]
                    
                    op_start = time.time()
                    async with session.get(f"{API_BASE}/lessons/{first_topic_id}", headers=headers) as response:
                        lesson_time = time.time() - op_start
                        workflow_result["operations"]["lesson"] = {
                            "time": lesson_time,
                            "status": response.status
                        }
                        
                        if response.status != 200:
                            raise Exception(f"Lesson request failed: {response.status}")
                
                # 4. Generate quiz
                op_start = time.time()
                async with session.post(f"{API_BASE}/assessments/generate-quiz/{first_topic_id}", headers=headers) as response:
                    quiz_time = time.time() - op_start
                    workflow_result["operations"]["quiz_generation"] = {
                        "time": quiz_time,
                        "status": response.status
                    }
                    
                    if response.status == 200:
                        quiz_data = await response.json()
                        
                        # 5. Submit quiz
                        if quiz_data.get("success") and quiz_data.get("assessment"):
                            assessment = quiz_data["assessment"]
                            answers = {q["id"]: 0 for q in assessment["questions"]}
                            
                            submission_data = {
                                "assessment_id": assessment["id"],
                                "answers": answers,
                                "time_taken": 60
                            }
                            
                            op_start = time.time()
                            async with session.post(f"{API_BASE}/assessments/submit", 
                                                  json=submission_data, headers=headers) as response:
                                submit_time = time.time() - op_start
                                workflow_result["operations"]["quiz_submission"] = {
                                    "time": submit_time,
                                    "status": response.status
                                }
                                
                                if response.status != 200:
                                    raise Exception(f"Quiz submission failed: {response.status}")
                
                workflow_result["success"] = True
                
            except Exception as e:
                workflow_result["errors"].append(str(e))
            
            workflow_result["total_time"] = time.time() - workflow_start
            return workflow_result
        
        # Execute concurrent workflows
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60),
            connector=aiohttp.TCPConnector(limit=100)
        ) as session:
            tasks = [simulate_user_workflow(session, i) for i in range(concurrent_users)]
            workflow_results = await asyncio.gather(*tasks)
        
        # Process results
        for workflow_result in workflow_results:
            if workflow_result["success"]:
                results["workflows_completed"] += 1
            else:
                results["workflows_failed"] += 1
            
            results["workflow_times"].append(workflow_result["total_time"])
            results["errors"].extend(workflow_result["errors"])
            
            # Aggregate operation times
            for op_name, op_data in workflow_result["operations"].items():
                if op_name not in results["operation_times"]:
                    results["operation_times"][op_name] = []
                results["operation_times"][op_name].append(op_data["time"])
        
        # Calculate statistics
        results["end_time"] = time.time()
        results["total_duration"] = results["end_time"] - results["start_time"]
        results["success_rate"] = (results["workflows_completed"] / concurrent_users) * 100
        
        if results["workflow_times"]:
            results["avg_workflow_time"] = statistics.mean(results["workflow_times"])
            results["max_workflow_time"] = max(results["workflow_times"])
            results["min_workflow_time"] = min(results["workflow_times"])
        
        # Calculate operation statistics
        for op_name, times in results["operation_times"].items():
            if times:
                results["operation_times"][op_name] = {
                    "avg": statistics.mean(times),
                    "min": min(times),
                    "max": max(times),
                    "count": len(times)
                }
        
        return results
    
    async def test_database_load(self) -> Dict[str, Any]:
        """Test database performance under load."""
        
        print("💾 Testing database load performance")
        
        # Test multiple concurrent database-heavy operations
        endpoints_to_test = [
            ("/curriculum/progress", "GET", True),
            ("/progress/dashboard", "GET", True),
            ("/assessments/history", "GET", True)
        ]
        
        results = {
            "database_tests": {},
            "overall_performance": {}
        }
        
        for endpoint, method, auth_required in endpoints_to_test:
            test_result = await self.test_api_endpoint_load(
                endpoint=endpoint,
                method=method,
                concurrent_users=15,
                requests_per_user=5,
                auth_required=auth_required
            )
            
            results["database_tests"][endpoint] = test_result
        
        # Calculate overall database performance
        all_response_times = []
        total_requests = 0
        successful_requests = 0
        
        for test_result in results["database_tests"].values():
            all_response_times.extend(test_result["response_times"])
            total_requests += test_result["total_requests"]
            successful_requests += test_result["status_codes"].get(200, 0)
        
        if all_response_times:
            results["overall_performance"] = {
                "avg_response_time": statistics.mean(all_response_times),
                "p95_response_time": sorted(all_response_times)[int(len(all_response_times) * 0.95)],
                "success_rate": (successful_requests / total_requests) * 100,
                "total_requests": total_requests
            }
        
        return results
    
    async def run_comprehensive_load_tests(self) -> Dict[str, Any]:
        """Run comprehensive load testing suite."""
        
        print("🚀 Starting comprehensive load testing...")
        print("=" * 60)
        
        # Setup test users
        await self.setup_test_users(50)
        
        test_results = {
            "timestamp": time.time(),
            "test_environment": "load_test",
            "tests": {}
        }
        
        try:
            # Test individual endpoints
            print("\n📡 Testing individual API endpoints...")
            
            endpoint_tests = [
                ("/monitoring/status", "GET", False, 20, 5),
                ("/curriculum/structure", "GET", False, 15, 8),
                ("/curriculum/progress", "GET", True, 10, 10),
                ("/progress/dashboard", "GET", True, 10, 8)
            ]
            
            for endpoint, method, auth_required, users, requests in endpoint_tests:
                test_result = await self.test_api_endpoint_load(
                    endpoint=endpoint,
                    method=method,
                    concurrent_users=users,
                    requests_per_user=requests,
                    auth_required=auth_required
                )
                test_results["tests"][f"endpoint_{endpoint.replace('/', '_')}"] = test_result
            
            # Test user workflows
            print("\n👥 Testing user workflow load...")
            workflow_result = await self.test_user_workflow_load(concurrent_users=25)
            test_results["tests"]["user_workflows"] = workflow_result
            
            # Test database load
            print("\n💾 Testing database load...")
            database_result = await self.test_database_load()
            test_results["tests"]["database_load"] = database_result
            
            # Generate summary
            test_results["summary"] = self._generate_load_test_summary(test_results)
            
        except Exception as e:
            test_results["error"] = str(e)
            print(f"❌ Load testing failed: {e}")
        
        return test_results
    
    def _generate_load_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of load test results."""
        
        summary = {
            "overall_performance": "unknown",
            "total_requests": 0,
            "avg_response_time": 0,
            "success_rate": 0,
            "performance_score": 0,
            "recommendations": []
        }
        
        all_response_times = []
        total_requests = 0
        successful_requests = 0
        
        # Aggregate results from all tests
        for test_name, test_result in results["tests"].items():
            if "response_times" in test_result:
                all_response_times.extend(test_result["response_times"])
                total_requests += test_result.get("total_requests", 0)
                successful_requests += test_result.get("status_codes", {}).get(200, 0)
            elif "workflows_completed" in test_result:
                total_requests += test_result.get("concurrent_users", 0)
                successful_requests += test_result.get("workflows_completed", 0)
        
        if all_response_times and total_requests > 0:
            summary["avg_response_time"] = statistics.mean(all_response_times)
            summary["success_rate"] = (successful_requests / total_requests) * 100
            summary["total_requests"] = total_requests
            
            # Calculate performance score (0-100)
            score = 100
            
            # Penalize slow response times
            if summary["avg_response_time"] > 2.0:
                score -= min(30, (summary["avg_response_time"] - 2.0) * 10)
            
            # Penalize low success rates
            if summary["success_rate"] < 95:
                score -= (95 - summary["success_rate"]) * 2
            
            summary["performance_score"] = max(0, score)
            
            # Determine overall performance
            if summary["performance_score"] >= 90:
                summary["overall_performance"] = "excellent"
            elif summary["performance_score"] >= 75:
                summary["overall_performance"] = "good"
            elif summary["performance_score"] >= 60:
                summary["overall_performance"] = "acceptable"
            else:
                summary["overall_performance"] = "poor"
            
            # Generate recommendations
            if summary["avg_response_time"] > 1.0:
                summary["recommendations"].append("Consider optimizing database queries")
            if summary["success_rate"] < 95:
                summary["recommendations"].append("Investigate error causes and improve error handling")
            if summary["performance_score"] < 80:
                summary["recommendations"].append("Consider scaling infrastructure")
        
        return summary


async def main():
    """Run load testing suite."""
    print("🔥 Starting ViperMind Load Testing Suite")
    print("=" * 60)
    
    tester = LoadTester()
    
    try:
        results = await tester.run_comprehensive_load_tests()
        
        # Print results
        print("\n" + "=" * 60)
        print("📊 LOAD TESTING RESULTS")
        print("=" * 60)
        
        summary = results.get("summary", {})
        
        print(f"Overall Performance: {summary.get('overall_performance', 'unknown').upper()}")
        print(f"Performance Score: {summary.get('performance_score', 0):.1f}/100")
        print(f"Total Requests: {summary.get('total_requests', 0)}")
        print(f"Average Response Time: {summary.get('avg_response_time', 0):.3f}s")
        print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
        
        # Recommendations
        recommendations = summary.get("recommendations", [])
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  • {rec}")
        
        # Save results
        with open("load_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: load_test_results.json")
        
        # Return appropriate exit code
        performance_score = summary.get("performance_score", 0)
        return 0 if performance_score >= 70 else 1
        
    except Exception as e:
        print(f"❌ Load testing failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))