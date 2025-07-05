"""
📊 Advanced Monitoring & Metrics Collection System
Real-time performance monitoring with Prometheus integration

Features:
- Real-time performance metrics
- Prometheus integration
- Custom dashboards
- Alerting system
- Performance profiling
- Resource monitoring
- Auto-scaling triggers
"""

import time
import threading
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import psutil
import numpy as np
from collections import defaultdict, deque
import statistics

try:
    from prometheus_client import Counter, Histogram, Gauge, Summary, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logging.warning("Prometheus client not available, using basic metrics")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MetricEvent:
    """📊 Individual metric event"""
    timestamp: float
    metric_name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """📈 Performance snapshot at a point in time"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    processing_metrics: Dict[str, float]
    active_sessions: int
    request_rate: float
    error_rate: float
    response_time_p95: float


class MetricsCollector:
    """📊 Comprehensive metrics collection and monitoring"""
    
    def __init__(self, enable_prometheus: bool = True, collection_interval: float = 5.0):
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        self.collection_interval = collection_interval
        self.metrics_history: deque = deque(maxlen=10000)
        self.performance_snapshots: deque = deque(maxlen=1000)
        self.active_metrics: Dict[str, Any] = {}
        self.alert_thresholds: Dict[str, Dict] = {}
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.lock = threading.Lock()
        
        # Prometheus metrics
        if self.enable_prometheus:
            self.registry = CollectorRegistry()
            self._setup_prometheus_metrics()
        
        # Built-in metrics
        self._setup_builtin_metrics()
        
        # Start background collection
        self._start_background_collection()
        
        logger.info(f"📊 Metrics Collector initialized (Prometheus: {self.enable_prometheus})")
    
    def _setup_prometheus_metrics(self):
        """🔧 Setup Prometheus metrics"""
        if not self.enable_prometheus:
            return
        
        # Processing metrics
        self.processing_duration = Histogram(
            'holomorphic_processing_duration_seconds',
            'Time spent processing signals',
            ['operation_type', 'user_id'],
            registry=self.registry
        )
        
        self.processing_samples = Counter(
            'holomorphic_processing_samples_total',
            'Total samples processed',
            ['operation_type', 'user_id'],
            registry=self.registry
        )
        
        self.processing_errors = Counter(
            'holomorphic_processing_errors_total',
            'Total processing errors',
            ['error_type', 'operation_type'],
            registry=self.registry
        )
        
        # API metrics
        self.api_requests = Counter(
            'holomorphic_api_requests_total',
            'Total API requests',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.api_duration = Histogram(
            'holomorphic_api_request_duration_seconds',
            'API request duration',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # System metrics
        self.cpu_usage = Gauge(
            'holomorphic_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage = Gauge(
            'holomorphic_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self.registry
        )
        
        self.active_sessions = Gauge(
            'holomorphic_active_sessions',
            'Number of active user sessions',
            registry=self.registry
        )
        
        # Plugin metrics
        self.plugin_executions = Counter(
            'holomorphic_plugin_executions_total',
            'Total plugin executions',
            ['plugin_name', 'user_id'],
            registry=self.registry
        )
        
        self.plugin_duration = Histogram(
            'holomorphic_plugin_execution_duration_seconds',
            'Plugin execution duration',
            ['plugin_name'],
            registry=self.registry
        )
        
        # Security metrics
        self.auth_attempts = Counter(
            'holomorphic_auth_attempts_total',
            'Authentication attempts',
            ['result', 'user_type'],
            registry=self.registry
        )
        
        self.security_events = Counter(
            'holomorphic_security_events_total',
            'Security events',
            ['event_type', 'risk_level'],
            registry=self.registry
        )
    
    def _setup_builtin_metrics(self):
        """🔧 Setup built-in metrics tracking"""
        self.active_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_processing_time': 0.0,
            'total_samples_processed': 0,
            'average_response_time': 0.0,
            'requests_per_second': 0.0,
            'samples_per_second': 0.0,
            'error_rate': 0.0,
            'uptime_seconds': 0.0,
            'last_restart': time.time(),
            'peak_memory_usage': 0.0,
            'peak_cpu_usage': 0.0,
            'active_connections': 0,
            'cache_hit_rate': 0.0,
            'plugin_success_rate': 0.0
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'high_cpu': {'threshold': 80.0, 'duration': 300, 'severity': 'warning'},
            'high_memory': {'threshold': 85.0, 'duration': 300, 'severity': 'warning'},
            'high_error_rate': {'threshold': 5.0, 'duration': 60, 'severity': 'critical'},
            'low_performance': {'threshold': 0.5, 'duration': 300, 'severity': 'warning'},
            'no_requests': {'threshold': 0, 'duration': 600, 'severity': 'info'}
        }
    
    def _start_background_collection(self):
        """🔄 Start background metrics collection"""
        self.running = True
        self.executor.submit(self._system_metrics_loop)
        self.executor.submit(self._performance_analysis_loop)
        self.executor.submit(self._alert_monitoring_loop)
        logger.info("🔄 Background metrics collection started")
    
    def _system_metrics_loop(self):
        """📊 System metrics collection loop"""
        while self.running:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Update metrics
                with self.lock:
                    self.active_metrics['uptime_seconds'] = time.time() - self.active_metrics['last_restart']
                    self.active_metrics['peak_cpu_usage'] = max(self.active_metrics['peak_cpu_usage'], cpu_percent)
                    self.active_metrics['peak_memory_usage'] = max(self.active_metrics['peak_memory_usage'], memory.used)
                
                # Update Prometheus metrics
                if self.enable_prometheus:
                    self.cpu_usage.set(cpu_percent)
                    self.memory_usage.set(memory.used)
                
                # Create performance snapshot
                snapshot = PerformanceSnapshot(
                    timestamp=time.time(),
                    cpu_usage=cpu_percent,
                    memory_usage=memory.percent,
                    disk_usage=disk.percent,
                    network_io={'bytes_sent': network.bytes_sent, 'bytes_recv': network.bytes_recv},
                    processing_metrics={
                        'samples_per_second': self.active_metrics['samples_per_second'],
                        'requests_per_second': self.active_metrics['requests_per_second'],
                        'error_rate': self.active_metrics['error_rate']
                    },
                    active_sessions=self.active_metrics['active_connections'],
                    request_rate=self.active_metrics['requests_per_second'],
                    error_rate=self.active_metrics['error_rate'],
                    response_time_p95=self._calculate_p95_response_time()
                )
                
                with self.lock:
                    self.performance_snapshots.append(snapshot)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"System metrics collection error: {e}")
                time.sleep(self.collection_interval * 2)
    
    def _performance_analysis_loop(self):
        """📈 Performance analysis loop"""
        while self.running:
            try:
                self._analyze_performance_trends()
                self._update_derived_metrics()
                time.sleep(60)  # Analyze every minute
            except Exception as e:
                logger.error(f"Performance analysis error: {e}")
                time.sleep(120)
    
    def _alert_monitoring_loop(self):
        """🚨 Alert monitoring loop"""
        while self.running:
            try:
                self._check_alert_conditions()
                time.sleep(30)  # Check alerts every 30 seconds
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                time.sleep(60)
    
    def record_processing_event(self, samples_count: int, processing_time: float, 
                              user_id: str = "anonymous", operation_type: str = "process"):
        """📊 Record a signal processing event"""
        timestamp = time.time()
        
        # Update built-in metrics
        with self.lock:
            self.active_metrics['total_samples_processed'] += samples_count
            self.active_metrics['total_processing_time'] += processing_time
            
            # Calculate samples per second for this operation
            samples_per_second = samples_count / processing_time if processing_time > 0 else 0
            
            # Update running averages
            self._update_running_average('samples_per_second', samples_per_second)
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            self.processing_duration.labels(
                operation_type=operation_type,
                user_id=user_id
            ).observe(processing_time)
            
            self.processing_samples.labels(
                operation_type=operation_type,
                user_id=user_id
            ).inc(samples_count)
        
        # Store event
        event = MetricEvent(
            timestamp=timestamp,
            metric_name="processing_event",
            value=samples_per_second,
            labels={"user_id": user_id, "operation_type": operation_type},
            metadata={
                "samples_count": samples_count,
                "processing_time": processing_time,
                "samples_per_second": samples_per_second
            }
        )
        
        with self.lock:
            self.metrics_history.append(event)
        
        logger.debug(f"📊 Processing event recorded: {samples_count} samples in {processing_time:.3f}s")
    
    def record_api_request(self, method: str, endpoint: str, status_code: int, 
                          duration: float, user_id: str = "anonymous"):
        """🌐 Record an API request event"""
        timestamp = time.time()
        
        # Update built-in metrics
        with self.lock:
            self.active_metrics['total_requests'] += 1
            if 200 <= status_code < 400:
                self.active_metrics['successful_requests'] += 1
            else:
                self.active_metrics['failed_requests'] += 1
            
            # Update running averages
            self._update_running_average('average_response_time', duration)
            self._calculate_error_rate()
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            self.api_requests.labels(
                method=method,
                endpoint=endpoint,
                status_code=str(status_code)
            ).inc()
            
            self.api_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
        
        # Store event
        event = MetricEvent(
            timestamp=timestamp,
            metric_name="api_request",
            value=duration,
            labels={
                "method": method,
                "endpoint": endpoint,
                "status_code": str(status_code),
                "user_id": user_id
            },
            metadata={"duration": duration}
        )
        
        with self.lock:
            self.metrics_history.append(event)
    
    def record_plugin_execution(self, plugin_name: str, user_id: str = "anonymous", 
                              duration: float = 0.0, success: bool = True):
        """🔌 Record a plugin execution event"""
        timestamp = time.time()
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            self.plugin_executions.labels(
                plugin_name=plugin_name,
                user_id=user_id
            ).inc()
            
            if duration > 0:
                self.plugin_duration.labels(plugin_name=plugin_name).observe(duration)
        
        # Store event
        event = MetricEvent(
            timestamp=timestamp,
            metric_name="plugin_execution",
            value=duration,
            labels={
                "plugin_name": plugin_name,
                "user_id": user_id,
                "success": str(success)
            },
            metadata={"duration": duration, "success": success}
        )
        
        with self.lock:
            self.metrics_history.append(event)
    
    def record_security_event(self, event_type: str, risk_level: str = "low", 
                            user_id: str = None, success: bool = True):
        """🛡️ Record a security event"""
        timestamp = time.time()
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            self.security_events.labels(
                event_type=event_type,
                risk_level=risk_level
            ).inc()
            
            if event_type.startswith("auth_"):
                result = "success" if success else "failure"
                user_type = "authenticated" if user_id else "anonymous"
                self.auth_attempts.labels(result=result, user_type=user_type).inc()
        
        # Store event
        event = MetricEvent(
            timestamp=timestamp,
            metric_name="security_event",
            value=1.0,
            labels={
                "event_type": event_type,
                "risk_level": risk_level,
                "user_id": user_id or "anonymous",
                "success": str(success)
            },
            metadata={"success": success}
        )
        
        with self.lock:
            self.metrics_history.append(event)
    
    def record_error(self, error_type: str, error_message: str, 
                    operation_type: str = "unknown", user_id: str = "anonymous"):
        """❌ Record an error event"""
        timestamp = time.time()
        
        # Update Prometheus metrics
        if self.enable_prometheus:
            self.processing_errors.labels(
                error_type=error_type,
                operation_type=operation_type
            ).inc()
        
        # Store event
        event = MetricEvent(
            timestamp=timestamp,
            metric_name="error",
            value=1.0,
            labels={
                "error_type": error_type,
                "operation_type": operation_type,
                "user_id": user_id
            },
            metadata={"error_message": error_message}
        )
        
        with self.lock:
            self.metrics_history.append(event)
        
        logger.warning(f"❌ Error recorded: {error_type} - {error_message}")
    
    def record_benchmark_result(self, benchmark_results: Dict[str, Any]):
        """🏁 Record benchmark results"""
        timestamp = time.time()
        
        performance_achieved = benchmark_results.get('performance_achieved', 0)
        average_throughput = benchmark_results.get('average_throughput', 0)
        
        # Store event
        event = MetricEvent(
            timestamp=timestamp,
            metric_name="benchmark_result",
            value=performance_achieved,
            labels={"benchmark_type": "performance"},
            metadata=benchmark_results
        )
        
        with self.lock:
            self.metrics_history.append(event)
        
        logger.info(f"🏁 Benchmark recorded: {performance_achieved:.1f}% performance achieved")
    
    def _update_running_average(self, metric_name: str, new_value: float, window_size: int = 100):
        """📊 Update running average for a metric"""
        if metric_name not in self.active_metrics:
            self.active_metrics[metric_name] = new_value
            return
        
        # Simple exponential moving average
        alpha = 2.0 / (window_size + 1)
        self.active_metrics[metric_name] = (
            alpha * new_value + (1 - alpha) * self.active_metrics[metric_name]
        )
    
    def _calculate_error_rate(self):
        """📊 Calculate current error rate"""
        total = self.active_metrics['total_requests']
        failed = self.active_metrics['failed_requests']
        
        if total > 0:
            self.active_metrics['error_rate'] = (failed / total) * 100.0
        else:
            self.active_metrics['error_rate'] = 0.0
    
    def _calculate_p95_response_time(self) -> float:
        """📊 Calculate 95th percentile response time"""
        recent_events = [
            event for event in list(self.metrics_history)[-1000:]
            if event.metric_name == "api_request" and 
            event.timestamp > time.time() - 300  # Last 5 minutes
        ]
        
        if not recent_events:
            return 0.0
        
        response_times = [event.value for event in recent_events]
        return np.percentile(response_times, 95) if response_times else 0.0
    
    def _analyze_performance_trends(self):
        """📈 Analyze performance trends"""
        if len(self.performance_snapshots) < 10:
            return
        
        recent_snapshots = list(self.performance_snapshots)[-60:]  # Last hour
        
        # Calculate trends
        cpu_trend = self._calculate_trend([s.cpu_usage for s in recent_snapshots])
        memory_trend = self._calculate_trend([s.memory_usage for s in recent_snapshots])
        response_time_trend = self._calculate_trend([s.response_time_p95 for s in recent_snapshots])
        
        # Update active metrics
        with self.lock:
            self.active_metrics['cpu_trend'] = cpu_trend
            self.active_metrics['memory_trend'] = memory_trend
            self.active_metrics['response_time_trend'] = response_time_trend
    
    def _calculate_trend(self, values: List[float]) -> str:
        """📈 Calculate trend direction"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        if slope > 0.1:
            return "increasing"
        elif slope < -0.1:
            return "decreasing"
        else:
            return "stable"
    
    def _update_derived_metrics(self):
        """📊 Update derived metrics"""
        current_time = time.time()
        
        # Calculate requests per second (last 5 minutes)
        recent_requests = [
            event for event in list(self.metrics_history)[-1000:]
            if event.metric_name == "api_request" and 
            event.timestamp > current_time - 300
        ]
        
        if recent_requests:
            rps = len(recent_requests) / 300.0  # 5 minutes
            self.active_metrics['requests_per_second'] = rps
        
        # Calculate samples per second (last 5 minutes)
        recent_processing = [
            event for event in list(self.metrics_history)[-1000:]
            if event.metric_name == "processing_event" and 
            event.timestamp > current_time - 300
        ]
        
        if recent_processing:
            total_samples = sum(event.metadata.get('samples_count', 0) for event in recent_processing)
            sps = total_samples / 300.0  # 5 minutes
            self.active_metrics['samples_per_second'] = sps
    
    def _check_alert_conditions(self):
        """🚨 Check alert conditions"""
        current_time = time.time()
        
        for alert_name, config in self.alert_thresholds.items():
            try:
                if alert_name == 'high_cpu':
                    current_value = self.performance_snapshots[-1].cpu_usage if self.performance_snapshots else 0
                elif alert_name == 'high_memory':
                    current_value = self.performance_snapshots[-1].memory_usage if self.performance_snapshots else 0
                elif alert_name == 'high_error_rate':
                    current_value = self.active_metrics['error_rate']
                elif alert_name == 'low_performance':
                    current_value = self.active_metrics['samples_per_second'] / 6.48e6  # Ratio to target
                elif alert_name == 'no_requests':
                    current_value = self.active_metrics['requests_per_second']
                else:
                    continue
                
                # Check threshold
                threshold = config['threshold']
                if (alert_name in ['high_cpu', 'high_memory', 'high_error_rate'] and current_value > threshold) or \
                   (alert_name in ['low_performance', 'no_requests'] and current_value < threshold):
                    
                    self._trigger_alert(alert_name, current_value, config)
                    
            except Exception as e:
                logger.error(f"Alert check error for {alert_name}: {e}")
    
    def _trigger_alert(self, alert_name: str, current_value: float, config: Dict):
        """🚨 Trigger an alert"""
        logger.warning(f"🚨 ALERT: {alert_name} - Value: {current_value}, Threshold: {config['threshold']}")
        
        # Record alert as metric event
        event = MetricEvent(
            timestamp=time.time(),
            metric_name="alert",
            value=current_value,
            labels={
                "alert_name": alert_name,
                "severity": config['severity']
            },
            metadata={
                "threshold": config['threshold'],
                "duration": config['duration']
            }
        )
        
        with self.lock:
            self.metrics_history.append(event)
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """📊 Get all current metrics"""
        with self.lock:
            return {
                "timestamp": time.time(),
                "active_metrics": self.active_metrics.copy(),
                "recent_events": len(self.metrics_history),
                "performance_snapshots": len(self.performance_snapshots),
                "prometheus_enabled": self.enable_prometheus,
                "collection_interval": self.collection_interval,
                "uptime_seconds": self.active_metrics['uptime_seconds'],
                "system_status": self._get_system_status()
            }
    
    def get_performance_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """📈 Get performance summary for time window"""
        current_time = time.time()
        window_start = current_time - (time_window_minutes * 60)
        
        # Filter events in time window
        relevant_events = [
            event for event in list(self.metrics_history)
            if event.timestamp >= window_start
        ]
        
        # Filter snapshots in time window
        relevant_snapshots = [
            snapshot for snapshot in list(self.performance_snapshots)
            if snapshot.timestamp >= window_start
        ]
        
        if not relevant_snapshots:
            return {"error": "No data available for the specified time window"}
        
        # Calculate summary statistics
        cpu_values = [s.cpu_usage for s in relevant_snapshots]
        memory_values = [s.memory_usage for s in relevant_snapshots]
        response_times = [s.response_time_p95 for s in relevant_snapshots]
        
        return {
            "time_window_minutes": time_window_minutes,
            "data_points": len(relevant_snapshots),
            "cpu_usage": {
                "min": min(cpu_values),
                "max": max(cpu_values),
                "mean": statistics.mean(cpu_values),
                "median": statistics.median(cpu_values)
            },
            "memory_usage": {
                "min": min(memory_values),
                "max": max(memory_values),
                "mean": statistics.mean(memory_values),
                "median": statistics.median(memory_values)
            },
            "response_time_p95": {
                "min": min(response_times),
                "max": max(response_times),
                "mean": statistics.mean(response_times),
                "median": statistics.median(response_times)
            },
            "total_events": len(relevant_events),
            "error_events": len([e for e in relevant_events if e.metric_name == "error"]),
            "processing_events": len([e for e in relevant_events if e.metric_name == "processing_event"]),
            "api_requests": len([e for e in relevant_events if e.metric_name == "api_request"])
        }
    
    def get_prometheus_metrics(self) -> str:
        """📊 Get Prometheus metrics in exposition format"""
        if not self.enable_prometheus:
            return "# Prometheus not enabled\n"
        
        return generate_latest(self.registry).decode('utf-8')
    
    def _get_system_status(self) -> str:
        """📊 Get overall system status"""
        cpu_usage = self.performance_snapshots[-1].cpu_usage if self.performance_snapshots else 0
        memory_usage = self.performance_snapshots[-1].memory_usage if self.performance_snapshots else 0
        error_rate = self.active_metrics['error_rate']
        
        if error_rate > 10 or cpu_usage > 90 or memory_usage > 90:
            return "CRITICAL"
        elif error_rate > 5 or cpu_usage > 80 or memory_usage > 80:
            return "WARNING"
        elif error_rate > 1 or cpu_usage > 60 or memory_usage > 60:
            return "DEGRADED"
        else:
            return "HEALTHY"
    
    def export_metrics(self, format_type: str = "json", time_window_minutes: int = 60) -> str:
        """📤 Export metrics in various formats"""
        if format_type == "json":
            return json.dumps(self.get_performance_summary(time_window_minutes), indent=2)
        elif format_type == "prometheus":
            return self.get_prometheus_metrics()
        elif format_type == "csv":
            return self._export_csv(time_window_minutes)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _export_csv(self, time_window_minutes: int) -> str:
        """📤 Export metrics as CSV"""
        current_time = time.time()
        window_start = current_time - (time_window_minutes * 60)
        
        relevant_snapshots = [
            snapshot for snapshot in list(self.performance_snapshots)
            if snapshot.timestamp >= window_start
        ]
        
        if not relevant_snapshots:
            return "timestamp,cpu_usage,memory_usage,response_time_p95,request_rate,error_rate\n"
        
        csv_lines = ["timestamp,cpu_usage,memory_usage,response_time_p95,request_rate,error_rate"]
        
        for snapshot in relevant_snapshots:
            csv_lines.append(
                f"{snapshot.timestamp},{snapshot.cpu_usage},{snapshot.memory_usage},"
                f"{snapshot.response_time_p95},{snapshot.request_rate},{snapshot.error_rate}"
            )
        
        return "\n".join(csv_lines)
    
    def reset_metrics(self):
        """🔄 Reset all metrics (use with caution)"""
        with self.lock:
            self.metrics_history.clear()
            self.performance_snapshots.clear()
            self._setup_builtin_metrics()
        
        logger.warning("🔄 All metrics have been reset")
    
    def shutdown(self):
        """🛑 Shutdown metrics collector"""
        logger.info("🛑 Shutting down Metrics Collector...")
        self.running = False
        self.executor.shutdown(wait=True)
        logger.info("✅ Metrics Collector shutdown complete")


if __name__ == "__main__":
    # Test metrics collector
    collector = MetricsCollector()
    
    try:
        # Simulate some events
        collector.record_processing_event(10000, 0.1, "test_user", "benchmark")
        collector.record_api_request("POST", "/process", 200, 0.05, "test_user")
        collector.record_plugin_execution("TestPlugin", "test_user", 0.02, True)
        collector.record_security_event("auth_success", "low", "test_user", True)
        
        time.sleep(2)
        
        # Get metrics
        metrics = collector.get_all_metrics()
        print(json.dumps(metrics, indent=2))
        
        # Get performance summary
        summary = collector.get_performance_summary(5)
        print("\nPerformance Summary:")
        print(json.dumps(summary, indent=2))
        
    finally:
        collector.shutdown()