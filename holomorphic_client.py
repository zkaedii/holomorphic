"""
🧠 Holomorphic API Client Library
Easy-to-use Python client for Holomorphic Signal Processing API

Installation:
    pip install requests numpy

Usage:
    from holomorphic_client import HolomorphicClient

    # Initialize client
    client = HolomorphicClient("http://localhost:8000")

    # Register and login
    client.register("username", "email@example.com", "password")
    client.login("username", "password")

    # Generate and process signals
    signal = client.generate_signal("sine", 1000)
    result = client.process_signal(signal)

    # View statistics
    stats = client.get_stats()
    print(stats)
"""

import requests
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime
import json


class HolomorphicAPIError(Exception):
    """Custom exception for API errors"""
    pass


class HolomorphicClient:
    """
    Holomorphic Signal Processing API Client

    A comprehensive client for interacting with the Holomorphic API,
    providing methods for authentication, signal processing, and analytics.

    Attributes:
        base_url (str): Base URL of the API
        token (str): Authentication token
        timeout (int): Request timeout in seconds
    """

    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 30):
        """
        Initialize the Holomorphic API client

        Args:
            base_url: Base URL of the API (default: http://localhost:8000)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip("/")
        self.token = None
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        auth_required: bool = True
    ) -> requests.Response:
        """
        Make HTTP request to API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request body data
            params: Query parameters
            auth_required: Whether authentication is required

        Returns:
            Response object

        Raises:
            HolomorphicAPIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        headers = {}

        if auth_required and not self.token:
            raise HolomorphicAPIError("Authentication required. Please login first.")

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
                timeout=self.timeout
            )

            if response.status_code >= 400:
                try:
                    error_detail = response.json().get("detail", response.text)
                except:
                    error_detail = response.text

                raise HolomorphicAPIError(
                    f"API Error {response.status_code}: {error_detail}"
                )

            return response

        except requests.exceptions.RequestException as e:
            raise HolomorphicAPIError(f"Request failed: {str(e)}")

    # ========================================================================
    # AUTHENTICATION
    # ========================================================================

    def register(self, username: str, email: str, password: str) -> Dict:
        """
        Register a new user

        Args:
            username: Username (3-32 characters)
            email: Valid email address
            password: Password (minimum 8 characters)

        Returns:
            Registration response with user_id

        Raises:
            HolomorphicAPIError: If registration fails

        Example:
            >>> client.register("john_doe", "john@example.com", "SecurePass123!")
            {'message': 'User registered successfully', 'user_id': 1}
        """
        response = self._request(
            "POST",
            "/api/register",
            data={
                "username": username,
                "email": email,
                "password": password
            },
            auth_required=False
        )
        return response.json()

    def login(self, username: str, password: str) -> Dict:
        """
        Login user and store authentication token

        Args:
            username: Username
            password: Password

        Returns:
            Login response with token and expiry

        Raises:
            HolomorphicAPIError: If login fails

        Example:
            >>> client.login("john_doe", "SecurePass123!")
            {'token': 'eyJ...', 'expires_at': '2024-...', 'username': 'john_doe'}
        """
        response = self._request(
            "POST",
            "/api/login",
            data={"username": username, "password": password},
            auth_required=False
        )
        data = response.json()
        self.token = data["token"]
        return data

    def logout(self) -> Dict:
        """
        Logout current user and clear token

        Returns:
            Logout confirmation

        Example:
            >>> client.logout()
            {'message': 'Logged out successfully'}
        """
        response = self._request("POST", "/api/logout")
        self.token = None
        return response.json()

    def get_current_user(self) -> Dict:
        """
        Get current authenticated user information

        Returns:
            User information (id, username, email)

        Example:
            >>> client.get_current_user()
            {'id': 1, 'username': 'john_doe', 'email': 'john@example.com'}
        """
        response = self._request("GET", "/api/me")
        return response.json()

    # ========================================================================
    # SIGNAL PROCESSING
    # ========================================================================

    def process_signal(
        self,
        samples: Union[List[float], np.ndarray],
        harmonics: int = 5,
        noise: float = 0.1,
        feedback: float = 0.3
    ) -> Dict:
        """
        Process signal with holomorphic transformation

        Args:
            samples: Input signal (10-10000 samples)
            harmonics: Number of harmonic components (1-20, default: 5)
            noise: Noise level (0-1, default: 0.1)
            feedback: Feedback strength (0-1, default: 0.3)

        Returns:
            Processing results with output signal and metrics

        Example:
            >>> import numpy as np
            >>> signal = np.sin(np.linspace(0, 2*np.pi, 1000))
            >>> result = client.process_signal(signal, harmonics=10)
            >>> print(result['processing_time_ms'])
            5.23
        """
        # Convert numpy array to list if needed
        if isinstance(samples, np.ndarray):
            samples = samples.tolist()

        response = self._request(
            "POST",
            "/api/process",
            data={
                "samples": samples,
                "harmonics": harmonics,
                "noise": noise,
                "feedback": feedback
            }
        )
        return response.json()

    def generate_signal(
        self,
        signal_type: str,
        length: int = 1000
    ) -> np.ndarray:
        """
        Generate test signal

        Args:
            signal_type: Type of signal (sine, square, sawtooth, noise, chirp)
            length: Signal length (10-10000 samples, default: 1000)

        Returns:
            Generated signal as numpy array

        Example:
            >>> signal = client.generate_signal("sine", 1000)
            >>> print(signal.shape)
            (1000,)
        """
        response = self._request(
            "GET",
            f"/api/generate/{signal_type}",
            params={"length": length}
        )
        data = response.json()
        return np.array(data["samples"])

    # ========================================================================
    # ANALYTICS
    # ========================================================================

    def get_history(self, limit: int = 50) -> List[Dict]:
        """
        Get processing history for current user

        Args:
            limit: Maximum number of history items (default: 50)

        Returns:
            List of processing history entries

        Example:
            >>> history = client.get_history(limit=10)
            >>> print(f"Total processes: {len(history)}")
            Total processes: 10
        """
        response = self._request(
            "GET",
            "/api/history",
            params={"limit": limit}
        )
        return response.json()["history"]

    def get_stats(self) -> Dict:
        """
        Get user statistics

        Returns:
            User statistics including total processes, samples, and timing

        Example:
            >>> stats = client.get_stats()
            >>> print(f"Total processes: {stats['total_processes']}")
            >>> print(f"Avg time: {stats['avg_processing_time']:.2f}ms")
        """
        response = self._request("GET", "/api/stats")
        return response.json()

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated

        Returns:
            True if authenticated, False otherwise
        """
        return self.token is not None

    def create_test_signal(
        self,
        signal_type: str = "sine",
        frequency: float = 1.0,
        amplitude: float = 1.0,
        length: int = 1000,
        noise_level: float = 0.0
    ) -> np.ndarray:
        """
        Create custom test signal locally (no API call)

        Args:
            signal_type: Type of signal
            frequency: Signal frequency
            amplitude: Signal amplitude
            length: Signal length
            noise_level: Additive noise level

        Returns:
            Generated signal as numpy array
        """
        t = np.linspace(0, 2 * np.pi * frequency, length)

        if signal_type == "sine":
            signal = amplitude * np.sin(t)
        elif signal_type == "square":
            signal = amplitude * np.sign(np.sin(t))
        elif signal_type == "sawtooth":
            signal = amplitude * (2 * (t / (2 * np.pi) - np.floor(t / (2 * np.pi) + 0.5)))
        elif signal_type == "triangle":
            signal = amplitude * (2 * np.abs(2 * (t / (2 * np.pi) - np.floor(t / (2 * np.pi) + 0.5))) - 1)
        else:
            signal = amplitude * np.sin(t)

        if noise_level > 0:
            signal += np.random.normal(0, noise_level, length)

        return signal

    def batch_process(
        self,
        signals: List[Union[List[float], np.ndarray]],
        **kwargs
    ) -> List[Dict]:
        """
        Process multiple signals in batch

        Args:
            signals: List of signals to process
            **kwargs: Processing parameters (harmonics, noise, feedback)

        Returns:
            List of processing results

        Example:
            >>> signals = [client.generate_signal("sine", 500) for _ in range(5)]
            >>> results = client.batch_process(signals, harmonics=8)
            >>> avg_time = sum(r['processing_time_ms'] for r in results) / len(results)
        """
        results = []
        for signal in signals:
            result = self.process_signal(signal, **kwargs)
            results.append(result)
        return results

    def export_results(
        self,
        result: Dict,
        filename: str,
        format: str = "json"
    ):
        """
        Export processing results to file

        Args:
            result: Processing result dictionary
            filename: Output filename
            format: Export format (json, csv)

        Example:
            >>> result = client.process_signal(signal)
            >>> client.export_results(result, "output.json")
        """
        if format == "json":
            with open(filename, 'w') as f:
                json.dump(result, f, indent=2)
        elif format == "csv":
            import csv
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["sample_index", "value"])
                for i, value in enumerate(result["output"]):
                    writer.writerow([i, value])
        else:
            raise ValueError(f"Unsupported format: {format}")

    def __repr__(self) -> str:
        """String representation of client"""
        auth_status = "authenticated" if self.is_authenticated() else "not authenticated"
        return f"HolomorphicClient(base_url='{self.base_url}', {auth_status})"


# ============================================================================
# CONTEXT MANAGER SUPPORT
# ============================================================================

class HolomorphicSession:
    """
    Context manager for automatic login/logout

    Example:
        >>> with HolomorphicSession("http://localhost:8000", "user", "pass") as client:
        ...     result = client.process_signal(signal)
        ...     # Automatically logs out when done
    """

    def __init__(self, base_url: str, username: str, password: str):
        self.client = HolomorphicClient(base_url)
        self.username = username
        self.password = password

    def __enter__(self) -> HolomorphicClient:
        self.client.login(self.username, self.password)
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.client.logout()
        except:
            pass  # Ignore logout errors


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def quick_process(
    signal: Union[List[float], np.ndarray],
    username: str,
    password: str,
    base_url: str = "http://localhost:8000",
    **kwargs
) -> Dict:
    """
    Quick signal processing with automatic login/logout

    Args:
        signal: Input signal
        username: Username
        password: Password
        base_url: API base URL
        **kwargs: Processing parameters

    Returns:
        Processing results

    Example:
        >>> signal = np.sin(np.linspace(0, 2*np.pi, 1000))
        >>> result = quick_process(signal, "user", "pass", harmonics=10)
    """
    with HolomorphicSession(base_url, username, password) as client:
        return client.process_signal(signal, **kwargs)


# ============================================================================
# EXAMPLES
# ============================================================================

if __name__ == "__main__":
    # Example usage
    print("🧠 Holomorphic Client Library - Examples\n")

    # Initialize client
    client = HolomorphicClient("http://localhost:8000")
    print(f"Client: {client}\n")

    try:
        # Register (may fail if user exists)
        print("1. Registering user...")
        try:
            client.register("demo_user", "demo@example.com", "DemoPassword123!")
            print("   ✓ User registered\n")
        except HolomorphicAPIError as e:
            print(f"   ⚠ {e}\n")

        # Login
        print("2. Logging in...")
        client.login("demo_user", "DemoPassword123!")
        print("   ✓ Logged in\n")

        # Get user info
        print("3. Getting user info...")
        user = client.get_current_user()
        print(f"   User: {user['username']} ({user['email']})\n")

        # Generate signal
        print("4. Generating sine wave...")
        signal = client.generate_signal("sine", 1000)
        print(f"   ✓ Generated {len(signal)} samples\n")

        # Process signal
        print("5. Processing signal...")
        result = client.process_signal(signal, harmonics=10, noise=0.2)
        print(f"   Processing time: {result['processing_time_ms']:.2f}ms")
        print(f"   Throughput: {result['samples_per_second']:.0f} samples/sec\n")

        # Get statistics
        print("6. Getting statistics...")
        stats = client.get_stats()
        print(f"   Total processes: {stats['total_processes']}")
        print(f"   Total samples: {stats['total_samples']:,}")
        print(f"   Avg time: {stats['avg_processing_time']:.2f}ms\n")

        # Get history
        print("7. Getting history...")
        history = client.get_history(limit=5)
        print(f"   Found {len(history)} recent processes\n")

        # Logout
        print("8. Logging out...")
        client.logout()
        print("   ✓ Logged out\n")

        print("✅ All examples completed successfully!")

    except HolomorphicAPIError as e:
        print(f"❌ Error: {e}")
