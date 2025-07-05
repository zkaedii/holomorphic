"""
📊 Monitoring & Metrics Module
Real-time performance monitoring and alerting system
"""

from .metrics import MetricsCollector, MetricEvent, PerformanceSnapshot

__all__ = [
    "MetricsCollector",
    "MetricEvent", 
    "PerformanceSnapshot"
]

__version__ = "1.0.0"
__description__ = "Advanced monitoring and metrics collection"
__features__ = [
    "Real-time performance tracking",
    "Prometheus integration",
    "Custom alerting",
    "Performance profiling",
    "Export functionality"
]