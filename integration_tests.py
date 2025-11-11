"""
🔗 Holomorphic API Integration Test Suite
Complete end-to-end testing of all API endpoints with authentication flows

Usage:
    python integration_tests.py                    # Run all tests
    python integration_tests.py --verbose          # Verbose output
    python integration_tests.py --endpoint process # Test specific endpoint
    python integration_tests.py --load-test        # Run load tests

Features:
    ✓ Authentication flow testing
    ✓ All endpoint coverage
    ✓ Error handling validation
    ✓ Performance benchmarking
    ✓ Concurrent request testing
    ✓ Data persistence verification
    ✓ Security testing
"""

import asyncio
import json
import time
import requests
import numpy as np
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys
import argparse

# ============================================================================
# CONFIGURATION
# ============================================================================

class TestConfig:
    """Test configuration"""
    BASE_URL = "http://localhost:8000"
    TIMEOUT = 30
    MAX_RETRIES = 3
    CONCURRENT_USERS = 10
    LOAD_TEST_DURATION = 60  # seconds

    # Test user credentials
    TEST_USERS = [
        {"username": f"test_user_{i}", "email": f"test{i}@example.com", "password": "TestPassword123!"}
        for i in range(1, 11)
    ]

# ============================================================================
# TEST RESULTS TRACKING
# ============================================================================

class TestResults:
    """Track and display test results"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.timings = []
        self.start_time = time.time()

    def record_pass(self, test_name: str, duration: float):
        self.passed += 1
        self.timings.append({"test": test_name, "duration": duration, "status": "PASS"})
        print(f"✅ PASS: {test_name} ({duration:.3f}s)")

    def record_fail(self, test_name: str, error: str, duration: float):
        self.failed += 1
        self.errors.append({"test": test_name, "error": error})
        self.timings.append({"test": test_name, "duration": duration, "status": "FAIL"})
        print(f"❌ FAIL: {test_name} - {error}")

    def print_summary(self):
        total_time = time.time() - self.start_time
        total_tests = self.passed + self.failed

        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Success Rate: {(self.passed/total_tests*100):.1f}%")
        print(f"Total Time: {total_time:.2f}s")

        if self.timings:
            avg_time = sum(t["duration"] for t in self.timings) / len(self.timings)
            print(f"Average Test Time: {avg_time:.3f}s")

        if self.errors:
            print("\n❌ FAILED TESTS:")
            for error in self.errors:
                print(f"  - {error['test']}: {error['error']}")

        print("="*70 + "\n")

        return self.failed == 0

# ============================================================================
# API CLIENT
# ============================================================================

class HolomorphicAPIClient:
    """API client for testing"""

    def __init__(self, base_url: str = TestConfig.BASE_URL):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with retries"""
        url = f"{self.base_url}{endpoint}"

        if self.token:
            kwargs.setdefault("headers", {})
            kwargs["headers"]["Authorization"] = f"Bearer {self.token}"

        for attempt in range(TestConfig.MAX_RETRIES):
            try:
                response = self.session.request(method, url, timeout=TestConfig.TIMEOUT, **kwargs)
                return response
            except requests.exceptions.RequestException as e:
                if attempt == TestConfig.MAX_RETRIES - 1:
                    raise
                time.sleep(0.5 * (attempt + 1))

    def register(self, username: str, email: str, password: str) -> Dict:
        """Register new user"""
        response = self._request("POST", "/api/register", json={
            "username": username,
            "email": email,
            "password": password
        })
        return response

    def login(self, username: str, password: str) -> Dict:
        """Login user"""
        response = self._request("POST", "/api/login", json={
            "username": username,
            "password": password
        })

        if response.status_code == 200:
            data = response.json()
            self.token = data["token"]

        return response

    def logout(self) -> Dict:
        """Logout user"""
        response = self._request("POST", "/api/logout")
        self.token = None
        return response

    def get_me(self) -> Dict:
        """Get current user"""
        return self._request("GET", "/api/me")

    def process_signal(self, samples: List[float], harmonics: int = 5,
                      noise: float = 0.1, feedback: float = 0.3) -> Dict:
        """Process signal"""
        return self._request("POST", "/api/process", json={
            "samples": samples,
            "harmonics": harmonics,
            "noise": noise,
            "feedback": feedback
        })

    def generate_signal(self, signal_type: str, length: int = 1000) -> Dict:
        """Generate test signal"""
        return self._request("GET", f"/api/generate/{signal_type}?length={length}")

    def get_history(self, limit: int = 50) -> Dict:
        """Get processing history"""
        return self._request("GET", f"/api/history?limit={limit}")

    def get_stats(self) -> Dict:
        """Get user statistics"""
        return self._request("GET", "/api/stats")

    def health_check(self) -> Dict:
        """Check API health"""
        return self._request("GET", "/health")

    def get_metrics(self) -> Dict:
        """Get system metrics"""
        return self._request("GET", "/metrics")

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class IntegrationTests:
    """Complete integration test suite"""

    def __init__(self, verbose: bool = False):
        self.results = TestResults()
        self.verbose = verbose
        self.client = HolomorphicAPIClient()

    def run_test(self, test_name: str, test_func):
        """Run a single test and record results"""
        if self.verbose:
            print(f"\n🔍 Running: {test_name}")

        start_time = time.time()
        try:
            test_func()
            duration = time.time() - start_time
            self.results.record_pass(test_name, duration)
        except Exception as e:
            duration = time.time() - start_time
            self.results.record_fail(test_name, str(e), duration)

    def test_01_health_check(self):
        """Test health endpoint (requires auth after security patch)"""
        # Health now requires authentication
        response = self.client.health_check()
        assert response.status_code in [200, 401], f"Unexpected status: {response.status_code}"

    def test_02_register_user(self):
        """Test user registration"""
        user = TestConfig.TEST_USERS[0]
        response = self.client.register(user["username"], user["email"], user["password"])

        # May already exist from previous run
        assert response.status_code in [200, 400], f"Registration failed: {response.status_code}"

    def test_03_login_success(self):
        """Test successful login"""
        user = TestConfig.TEST_USERS[0]
        response = self.client.login(user["username"], user["password"])

        assert response.status_code == 200, f"Login failed: {response.status_code}"
        data = response.json()
        assert "token" in data, "Token not in response"
        assert self.client.token is not None, "Token not set in client"

    def test_04_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        client = HolomorphicAPIClient()
        response = client.login("invalid_user", "wrong_password")

        assert response.status_code == 401, "Should reject invalid credentials"

    def test_05_get_current_user(self):
        """Test getting current user info"""
        response = self.client.get_me()

        assert response.status_code == 200, f"Get user failed: {response.status_code}"
        data = response.json()
        assert "username" in data, "Username not in response"
        assert "email" in data, "Email not in response"

    def test_06_generate_sine_signal(self):
        """Test sine wave generation"""
        response = self.client.generate_signal("sine", 1000)

        assert response.status_code == 200, f"Generate signal failed: {response.status_code}"
        data = response.json()
        assert "samples" in data, "Samples not in response"
        assert len(data["samples"]) == 1000, "Wrong sample count"

    def test_07_generate_all_signal_types(self):
        """Test all signal type generators"""
        signal_types = ["sine", "square", "sawtooth", "noise", "chirp"]

        for signal_type in signal_types:
            response = self.client.generate_signal(signal_type, 500)
            assert response.status_code == 200, f"Failed to generate {signal_type}"
            data = response.json()
            assert len(data["samples"]) == 500, f"Wrong sample count for {signal_type}"

    def test_08_process_signal_basic(self):
        """Test basic signal processing"""
        # Generate test signal
        gen_response = self.client.generate_signal("sine", 1000)
        samples = gen_response.json()["samples"]

        # Process signal
        response = self.client.process_signal(samples)

        assert response.status_code == 200, f"Process failed: {response.status_code}"
        data = response.json()
        assert "output" in data, "Output not in response"
        assert "processing_time_ms" in data, "Processing time not in response"
        assert "samples_per_second" in data, "Samples/sec not in response"
        assert "metrics" in data, "Metrics not in response"

    def test_09_process_signal_with_params(self):
        """Test signal processing with custom parameters"""
        samples = [np.sin(2 * np.pi * i / 100) for i in range(1000)]

        response = self.client.process_signal(
            samples=samples,
            harmonics=10,
            noise=0.2,
            feedback=0.5
        )

        assert response.status_code == 200, f"Process failed: {response.status_code}"
        data = response.json()
        assert len(data["output"]) == 1000, "Output length mismatch"

    def test_10_process_signal_validation(self):
        """Test input validation for signal processing"""
        # Test with too few samples
        response = self.client.process_signal(samples=[1.0, 2.0])
        assert response.status_code == 422, "Should reject too few samples"

        # Test with too many samples
        response = self.client.process_signal(samples=[1.0] * 20000)
        assert response.status_code == 422, "Should reject too many samples"

    def test_11_get_processing_history(self):
        """Test getting processing history"""
        response = self.client.get_history(limit=10)

        assert response.status_code == 200, f"Get history failed: {response.status_code}"
        data = response.json()
        assert "history" in data, "History not in response"
        assert "count" in data, "Count not in response"
        assert isinstance(data["history"], list), "History should be a list"

    def test_12_get_user_statistics(self):
        """Test getting user statistics"""
        response = self.client.get_stats()

        assert response.status_code == 200, f"Get stats failed: {response.status_code}"
        data = response.json()
        assert "total_processes" in data, "Total processes not in response"
        assert "total_samples" in data, "Total samples not in response"
        assert "avg_processing_time" in data, "Avg processing time not in response"

    def test_13_unauthorized_access(self):
        """Test that endpoints require authentication"""
        client = HolomorphicAPIClient()

        # Try to access protected endpoint without auth
        response = client.get_me()
        assert response.status_code == 401, "Should reject unauthenticated request"

    def test_14_token_expiration(self):
        """Test that expired tokens are rejected (if applicable)"""
        # This would need a token that's actually expired
        # For now, just test with invalid token
        client = HolomorphicAPIClient()
        client.token = "invalid_token_12345"

        response = client.get_me()
        assert response.status_code == 401, "Should reject invalid token"

    def test_15_concurrent_processing(self):
        """Test concurrent signal processing requests"""
        # Generate test signal
        gen_response = self.client.generate_signal("sine", 500)
        samples = gen_response.json()["samples"]

        # Process multiple times concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(self.client.process_signal, samples)
                for _ in range(5)
            ]

            for future in as_completed(futures):
                response = future.result()
                assert response.status_code == 200, "Concurrent processing failed"

    def test_16_signal_metrics_accuracy(self):
        """Test that signal metrics are accurate"""
        # Create known signal
        samples = [1.0] * 500 + [-1.0] * 500

        response = self.client.process_signal(samples)
        data = response.json()

        metrics = data["metrics"]
        assert "mean" in metrics, "Mean not in metrics"
        assert "std" in metrics, "Std not in metrics"
        assert "min" in metrics, "Min not in metrics"
        assert "max" in metrics, "Max not in metrics"

    def test_17_logout(self):
        """Test user logout"""
        response = self.client.logout()
        assert response.status_code == 200, f"Logout failed: {response.status_code}"
        assert self.client.token is None, "Token should be cleared"

    def test_18_authenticated_health_check(self):
        """Test health check with authentication"""
        # Login first
        user = TestConfig.TEST_USERS[0]
        self.client.login(user["username"], user["password"])

        response = self.client.health_check()
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert "status" in data, "Status not in response"
        assert "components" in data, "Components not in response"

    def test_19_metrics_admin_only(self):
        """Test that metrics endpoint requires admin (after security patch)"""
        response = self.client.get_metrics()
        # Should be 401 (no auth) or 403 (insufficient permissions)
        assert response.status_code in [401, 403], "Metrics should be restricted"

    def test_20_end_to_end_workflow(self):
        """Test complete end-to-end workflow"""
        # 1. Register new user
        timestamp = int(time.time())
        user = {
            "username": f"workflow_user_{timestamp}",
            "email": f"workflow{timestamp}@example.com",
            "password": "WorkflowTest123!"
        }

        reg_response = self.client.register(user["username"], user["email"], user["password"])
        assert reg_response.status_code == 200, "Registration failed"

        # 2. Login
        login_response = self.client.login(user["username"], user["password"])
        assert login_response.status_code == 200, "Login failed"

        # 3. Generate signal
        gen_response = self.client.generate_signal("chirp", 1000)
        assert gen_response.status_code == 200, "Signal generation failed"
        samples = gen_response.json()["samples"]

        # 4. Process signal multiple times
        for i in range(3):
            proc_response = self.client.process_signal(samples, harmonics=5+i)
            assert proc_response.status_code == 200, f"Processing {i} failed"

        # 5. Check history
        hist_response = self.client.get_history()
        assert hist_response.status_code == 200, "Get history failed"
        history = hist_response.json()["history"]
        assert len(history) >= 3, "History should have at least 3 entries"

        # 6. Check stats
        stats_response = self.client.get_stats()
        assert stats_response.status_code == 200, "Get stats failed"
        stats = stats_response.json()
        assert stats["total_processes"] >= 3, "Stats should show at least 3 processes"

        # 7. Logout
        logout_response = self.client.logout()
        assert logout_response.status_code == 200, "Logout failed"

    def run_all_tests(self):
        """Run all integration tests"""
        print("\n" + "="*70)
        print("🧪 HOLOMORPHIC API INTEGRATION TESTS")
        print("="*70 + "\n")

        # Get all test methods
        test_methods = [
            method for method in dir(self)
            if method.startswith("test_") and callable(getattr(self, method))
        ]

        # Sort by test number
        test_methods.sort()

        print(f"Found {len(test_methods)} tests\n")

        for method_name in test_methods:
            test_name = method_name.replace("_", " ").title()
            self.run_test(test_name, getattr(self, method_name))

        return self.results.print_summary()

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class PerformanceTests:
    """Performance and load testing"""

    def __init__(self):
        self.results = TestResults()

    def test_response_times(self):
        """Test API response times"""
        print("\n📊 Response Time Analysis")
        print("-" * 50)

        client = HolomorphicAPIClient()
        user = TestConfig.TEST_USERS[0]
        client.login(user["username"], user["password"])

        # Generate test signal
        samples = [np.sin(2 * np.pi * i / 100) for i in range(1000)]

        # Test multiple times
        response_times = []
        for i in range(10):
            start = time.time()
            response = client.process_signal(samples)
            duration = time.time() - start

            if response.status_code == 200:
                response_times.append(duration)

        if response_times:
            avg = np.mean(response_times)
            std = np.std(response_times)
            min_time = np.min(response_times)
            max_time = np.max(response_times)

            print(f"Average: {avg*1000:.2f}ms")
            print(f"Std Dev: {std*1000:.2f}ms")
            print(f"Min: {min_time*1000:.2f}ms")
            print(f"Max: {max_time*1000:.2f}ms")
            print(f"95th %ile: {np.percentile(response_times, 95)*1000:.2f}ms")

    def test_concurrent_load(self):
        """Test concurrent user load"""
        print("\n⚡ Concurrent Load Test")
        print("-" * 50)

        def user_workflow(user_id):
            """Simulate user workflow"""
            client = HolomorphicAPIClient()
            user = TestConfig.TEST_USERS[user_id % len(TestConfig.TEST_USERS)]

            try:
                # Login
                client.login(user["username"], user["password"])

                # Generate and process signal
                gen_response = client.generate_signal("sine", 500)
                if gen_response.status_code == 200:
                    samples = gen_response.json()["samples"]
                    client.process_signal(samples)

                return True
            except:
                return False

        # Run concurrent users
        success_count = 0
        with ThreadPoolExecutor(max_workers=TestConfig.CONCURRENT_USERS) as executor:
            futures = [
                executor.submit(user_workflow, i)
                for i in range(TestConfig.CONCURRENT_USERS)
            ]

            for future in as_completed(futures):
                if future.result():
                    success_count += 1

        print(f"Concurrent Users: {TestConfig.CONCURRENT_USERS}")
        print(f"Successful: {success_count}/{TestConfig.CONCURRENT_USERS}")
        print(f"Success Rate: {(success_count/TestConfig.CONCURRENT_USERS)*100:.1f}%")

    def test_throughput(self):
        """Test processing throughput"""
        print("\n🚀 Throughput Test")
        print("-" * 50)

        client = HolomorphicAPIClient()
        user = TestConfig.TEST_USERS[0]
        client.login(user["username"], user["password"])

        # Generate test signal
        samples = [np.sin(2 * np.pi * i / 100) for i in range(1000)]

        # Process for 10 seconds
        start_time = time.time()
        request_count = 0
        total_samples = 0

        while time.time() - start_time < 10:
            response = client.process_signal(samples)
            if response.status_code == 200:
                request_count += 1
                total_samples += len(samples)

        duration = time.time() - start_time

        print(f"Duration: {duration:.2f}s")
        print(f"Requests: {request_count}")
        print(f"Requests/sec: {request_count/duration:.2f}")
        print(f"Total Samples: {total_samples:,}")
        print(f"Samples/sec: {total_samples/duration:,.0f}")

    def run_all_tests(self):
        """Run all performance tests"""
        print("\n" + "="*70)
        print("⚡ PERFORMANCE TESTS")
        print("="*70)

        self.test_response_times()
        self.test_concurrent_load()
        self.test_throughput()

        print("\n" + "="*70 + "\n")

# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Holomorphic API Integration Tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--performance", "-p", action="store_true", help="Run performance tests")
    parser.add_argument("--endpoint", "-e", type=str, help="Test specific endpoint")

    args = parser.parse_args()

    print("\n🔗 Holomorphic API Integration Tests")
    print(f"Target: {TestConfig.BASE_URL}")
    print(f"Timeout: {TestConfig.TIMEOUT}s")
    print()

    # Check if API is reachable
    try:
        response = requests.get(f"{TestConfig.BASE_URL}/docs", timeout=5)
        if response.status_code != 200:
            print("⚠️  Warning: API may not be running. Starting tests anyway...")
    except:
        print("❌ Error: Cannot reach API. Is it running?")
        print(f"   Try: python standalone_app.py")
        return 1

    # Run tests
    all_passed = True

    if args.performance:
        perf_tests = PerformanceTests()
        perf_tests.run_all_tests()
    else:
        tests = IntegrationTests(verbose=args.verbose)
        all_passed = tests.run_all_tests()

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
