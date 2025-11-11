

# 🔗 Holomorphic API Integration Guide
**Complete guide for integrating with the Holomorphic Signal Processing API**

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [API Client Library](#api-client-library)
3. [Authentication](#authentication)
4. [Signal Processing](#signal-processing)
5. [Integration Testing](#integration-testing)
6. [Error Handling](#error-handling)
7. [Performance Optimization](#performance-optimization)
8. [Production Deployment](#production-deployment)
9. [Code Examples](#code-examples)

---

## 🚀 Quick Start

### Installation

```bash
# Install the API client library
pip install requests numpy

# Or install from requirements
pip install -r requirements.txt
```

### Basic Usage

```python
from holomorphic_client import HolomorphicClient

# Initialize client
client = HolomorphicClient("http://localhost:8000")

# Register and login
client.register("username", "email@example.com", "password")
client.login("username", "password")

# Generate and process signal
signal = client.generate_signal("sine", 1000)
result = client.process_signal(signal, harmonics=10)

print(f"Processing time: {result['processing_time_ms']:.2f}ms")
```

---

## 📚 API Client Library

### Features

✅ **Easy Authentication** - Automatic token management
✅ **Type Safety** - Full type hints and validation
✅ **Error Handling** - Comprehensive exception handling
✅ **Context Managers** - Automatic login/logout
✅ **Batch Processing** - Process multiple signals efficiently
✅ **Export Functions** - Save results to JSON/CSV

### Installation

```python
from holomorphic_client import HolomorphicClient, HolomorphicSession

# Initialize client
client = HolomorphicClient("http://localhost:8000")

# Or use context manager (auto login/logout)
with HolomorphicSession("http://localhost:8000", "user", "pass") as client:
    result = client.process_signal(signal)
```

### API Reference

#### `HolomorphicClient`

```python
class HolomorphicClient:
    def __init__(self, base_url: str, timeout: int = 30)
    def register(self, username: str, email: str, password: str) -> Dict
    def login(self, username: str, password: str) -> Dict
    def logout(self) -> Dict
    def get_current_user(self) -> Dict
    def process_signal(self, samples, harmonics=5, noise=0.1, feedback=0.3) -> Dict
    def generate_signal(self, signal_type: str, length: int = 1000) -> np.ndarray
    def get_history(self, limit: int = 50) -> List[Dict]
    def get_stats(self) -> Dict
    def batch_process(self, signals: List, **kwargs) -> List[Dict]
    def export_results(self, result: Dict, filename: str, format: str)
```

---

## 🔐 Authentication

### Register New User

```python
# Registration
response = client.register(
    username="john_doe",
    email="john@example.com",
    password="SecurePass123!"
)
# Returns: {'message': 'User registered successfully', 'user_id': 1}
```

**Requirements:**
- Username: 3-32 characters, alphanumeric + underscore
- Email: Valid email format
- Password: Minimum 8 characters

### Login

```python
# Login
response = client.login("john_doe", "SecurePass123!")
# Returns: {'token': 'eyJ...', 'expires_at': '2024-...', 'username': 'john_doe'}

# Token is automatically stored in client
assert client.is_authenticated() == True
```

### Logout

```python
# Logout
client.logout()
# Token is cleared automatically
```

### Token Management

```python
# Check authentication status
if client.is_authenticated():
    print("User is logged in")

# Manual token management
client.token = "your_token_here"  # Set token manually

# Tokens expire after 24 hours
```

---

## 🧠 Signal Processing

### Generate Test Signals

```python
# Available signal types: sine, square, sawtooth, noise, chirp

# Generate sine wave
signal = client.generate_signal("sine", 1000)

# Generate square wave
signal = client.generate_signal("square", 2000)

# Generate with specific length
signal = client.generate_signal("chirp", length=500)
```

### Process Signals

```python
# Basic processing
result = client.process_signal(signal)

# With custom parameters
result = client.process_signal(
    signal,
    harmonics=15,    # 1-20 harmonic components
    noise=0.2,       # 0-1 noise level
    feedback=0.4     # 0-1 feedback strength
)

# Access results
output_signal = result['output']                    # Processed signal
processing_time = result['processing_time_ms']      # Processing time
throughput = result['samples_per_second']           # Throughput
metrics = result['metrics']                         # Statistics

print(f"Mean: {metrics['mean']:.4f}")
print(f"Std:  {metrics['std']:.4f}")
print(f"Min:  {metrics['min']:.4f}")
print(f"Max:  {metrics['max']:.4f}")
```

### Batch Processing

```python
# Generate multiple signals
signals = [
    client.generate_signal("sine", 500),
    client.generate_signal("square", 500),
    client.generate_signal("chirp", 500)
]

# Batch process with same parameters
results = client.batch_process(signals, harmonics=10, noise=0.15)

# Analyze results
avg_time = sum(r['processing_time_ms'] for r in results) / len(results)
print(f"Average processing time: {avg_time:.2f}ms")
```

### Custom Signal Creation

```python
import numpy as np

# Create custom signal locally
t = np.linspace(0, 2*np.pi, 1000)
custom_signal = np.sin(t) + 0.5 * np.sin(2*t)

# Process custom signal
result = client.process_signal(custom_signal, harmonics=8)

# Or use client helper
custom_signal = client.create_test_signal(
    signal_type="sine",
    frequency=2.0,
    amplitude=0.8,
    length=1000,
    noise_level=0.1
)
```

---

## 📊 Analytics & History

### Get User Statistics

```python
stats = client.get_stats()

print(f"Total processes: {stats['total_processes']}")
print(f"Total samples: {stats['total_samples']:,}")
print(f"Average time: {stats['avg_processing_time']:.2f}ms")
print(f"Min time: {stats['min_processing_time']:.2f}ms")
print(f"Max time: {stats['max_processing_time']:.2f}ms")
```

### Get Processing History

```python
# Get last 50 processes
history = client.get_history(limit=50)

for item in history:
    print(f"Samples: {item['samples_count']:5d} | "
          f"Time: {item['processing_time_ms']:6.2f}ms | "
          f"Date: {item['created_at']}")
```

### Export Results

```python
result = client.process_signal(signal)

# Export to JSON
client.export_results(result, "output.json", format="json")

# Export to CSV
client.export_results(result, "output.csv", format="csv")
```

---

## 🧪 Integration Testing

### Run Integration Tests

```bash
# Run all integration tests
python integration_tests.py

# Verbose mode
python integration_tests.py --verbose

# Performance tests
python integration_tests.py --performance
```

### Test Coverage

The integration test suite covers:

✅ **Authentication Flow** - Registration, login, logout
✅ **Signal Generation** - All signal types
✅ **Signal Processing** - Various parameters
✅ **Input Validation** - Edge cases and errors
✅ **Analytics** - History and statistics
✅ **Concurrent Access** - Multi-user scenarios
✅ **Performance** - Response times and throughput
✅ **End-to-End** - Complete workflows

### Example Test

```python
from integration_tests import IntegrationTests

# Run specific test
tests = IntegrationTests(verbose=True)
tests.run_test("Authentication Test", tests.test_03_login_success)

# Run all tests
tests.run_all_tests()
```

---

## ⚠️ Error Handling

### Exception Handling

```python
from holomorphic_client import HolomorphicAPIError

try:
    client.login("user", "password")
    result = client.process_signal(signal)
except HolomorphicAPIError as e:
    print(f"API Error: {e}")
    # Handle error appropriately
```

### Common Errors

| Error Code | Meaning | Solution |
|------------|---------|----------|
| 400 | Bad Request | Check input validation |
| 401 | Unauthorized | Login required |
| 403 | Forbidden | Insufficient permissions |
| 422 | Validation Error | Check parameters |
| 500 | Server Error | Contact support |

### Retry Logic

```python
import time

def process_with_retry(client, signal, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.process_signal(signal)
        except HolomorphicAPIError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## ⚡ Performance Optimization

### Best Practices

1. **Reuse Client Instance**
   ```python
   # Good: Reuse client
   client = HolomorphicClient(base_url)
   for signal in signals:
       result = client.process_signal(signal)

   # Bad: Create new client each time
   for signal in signals:
       client = HolomorphicClient(base_url)
       client.login(user, pass)
       result = client.process_signal(signal)
   ```

2. **Batch Processing**
   ```python
   # Process multiple signals efficiently
   results = client.batch_process(signals, harmonics=10)
   ```

3. **Optimize Signal Length**
   ```python
   # Shorter signals process faster
   signal = client.generate_signal("sine", 500)  # Fast
   signal = client.generate_signal("sine", 10000)  # Slower
   ```

4. **Connection Pooling**
   ```python
   # Client uses requests.Session internally
   # Automatically reuses connections
   ```

### Performance Metrics

Typical performance on modern hardware:

| Operation | Time | Throughput |
|-----------|------|------------|
| Signal Generation | <1ms | N/A |
| Process 1000 samples | 5-10ms | ~100K samples/sec |
| Authentication | 50-100ms | N/A |
| Get History | 5-10ms | N/A |

---

## 🏭 Production Deployment

### Environment Configuration

```bash
# .env file
API_BASE_URL=https://api.holomorphic.example.com
API_TIMEOUT=30
MAX_RETRIES=3
```

```python
import os
from holomorphic_client import HolomorphicClient

# Use environment variables
client = HolomorphicClient(
    base_url=os.getenv("API_BASE_URL", "http://localhost:8000"),
    timeout=int(os.getenv("API_TIMEOUT", "30"))
)
```

### Production Checklist

- [ ] Use HTTPS endpoints
- [ ] Store credentials securely (environment variables, secrets manager)
- [ ] Implement proper error handling
- [ ] Add logging and monitoring
- [ ] Set appropriate timeouts
- [ ] Use connection pooling
- [ ] Implement retry logic
- [ ] Rate limit requests
- [ ] Cache results when appropriate
- [ ] Monitor API health

### Example Production Setup

```python
import os
import logging
from holomorphic_client import HolomorphicClient, HolomorphicAPIError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize client with production settings
client = HolomorphicClient(
    base_url=os.getenv("API_URL"),
    timeout=int(os.getenv("API_TIMEOUT", "30"))
)

# Login with credentials from environment
try:
    client.login(
        os.getenv("API_USERNAME"),
        os.getenv("API_PASSWORD")
    )
    logger.info("Successfully authenticated")
except HolomorphicAPIError as e:
    logger.error(f"Authentication failed: {e}")
    raise

# Process with error handling
def safe_process(signal):
    try:
        result = client.process_signal(signal)
        logger.info(f"Processed {len(signal)} samples in {result['processing_time_ms']:.2f}ms")
        return result
    except HolomorphicAPIError as e:
        logger.error(f"Processing failed: {e}")
        return None
```

---

## 💻 Code Examples

### Example 1: Simple Processing

```python
from holomorphic_client import HolomorphicClient
import numpy as np

client = HolomorphicClient()
client.login("user", "password")

# Generate signal
signal = np.sin(np.linspace(0, 2*np.pi, 1000))

# Process
result = client.process_signal(signal, harmonics=10)

print(f"Processing time: {result['processing_time_ms']:.2f}ms")
```

### Example 2: Parameter Sweep

```python
signal = client.generate_signal("sine", 1000)

for h in range(1, 21):
    result = client.process_signal(signal, harmonics=h)
    print(f"Harmonics {h:2d}: {result['processing_time_ms']:6.2f}ms")
```

### Example 3: Real-time Simulation

```python
import time

chunk_size = 500
num_chunks = 100

for i in range(num_chunks):
    # Generate chunk
    chunk = client.generate_signal("noise", chunk_size)

    # Process chunk
    start = time.time()
    result = client.process_signal(chunk, harmonics=5)
    latency = (time.time() - start) * 1000

    print(f"Chunk {i+1}: {latency:.2f}ms latency")
```

### Example 4: Multi-user Simulation

```python
from concurrent.futures import ThreadPoolExecutor

def user_workflow(user_id):
    client = HolomorphicClient()
    client.login(f"user{user_id}", f"password{user_id}")

    signal = client.generate_signal("sine", 1000)
    result = client.process_signal(signal)

    client.logout()
    return result

# Simulate 10 concurrent users
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(user_workflow, range(10)))

print(f"Processed {len(results)} signals concurrently")
```

---

## 📖 Additional Resources

### Documentation
- **API Reference**: http://localhost:8000/docs
- **Standalone App Guide**: `STANDALONE_APP_README.md`
- **Security Guide**: `SECURITY_AUDIT_REPORT.md`

### Example Scripts
- `examples/basic_usage.py` - Basic operations
- `examples/advanced_processing.py` - Advanced workflows
- `examples/visualization_example.py` - Signal visualization

### Testing
- `integration_tests.py` - Complete test suite
- `holomorphic_client.py` - API client library

### Support
- GitHub Issues: Report bugs and request features
- Email: support@holomorphic.ai
- Documentation: http://localhost:8000/docs

---

## 🎯 Quick Reference

### Authentication
```python
client.register(username, email, password)
client.login(username, password)
client.logout()
client.get_current_user()
```

### Processing
```python
signal = client.generate_signal(type, length)
result = client.process_signal(signal, harmonics, noise, feedback)
results = client.batch_process(signals, **params)
```

### Analytics
```python
history = client.get_history(limit)
stats = client.get_stats()
client.export_results(result, filename, format)
```

### Utilities
```python
client.is_authenticated()
client.create_test_signal(...)
```

---

**Ready to integrate? Start with `examples/basic_usage.py`!** 🚀
