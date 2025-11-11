"""
🌐 Holomorphic Signal Processing API Server
FastAPI-based microservice with WebSocket support and plugin system
"""

import asyncio
import json
import logging
import time
import os
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Union

import numpy as np
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from ..core.engine import HolomorphicEngine, HolomorphicParameters, benchmark_holomorphic_engine
from ..plugins.manager import PluginManager
from ..monitoring.metrics import MetricsCollector
from ..security.auth import SecurityManager, verify_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

# Security
security = HTTPBearer()

# Global instances
engine: Optional[HolomorphicEngine] = None
plugin_manager: Optional[PluginManager] = None
metrics_collector: Optional[MetricsCollector] = None
security_manager: Optional[SecurityManager] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global engine, plugin_manager, metrics_collector, security_manager
    
    logger.info("🚀 Starting Holomorphic Signal Processing API...")
    
    # Initialize components
    params = HolomorphicParameters()
    engine = HolomorphicEngine(params)
    plugin_manager = PluginManager()
    metrics_collector = MetricsCollector()
    security_manager = SecurityManager()
    
    logger.info("✅ All components initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down API server...")
    if engine:
        engine.shutdown()
    if plugin_manager:
        plugin_manager.shutdown()
    if metrics_collector:
        metrics_collector.shutdown()
    
    logger.info("✅ Shutdown complete")


# FastAPI application
app = FastAPI(
    title="🧠 Holomorphic Signal Processing API",
    description="Revolutionary CPU-Optimized Real-Time Processing Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
# SECURITY FIX: Restrict CORS to specific origins only (configure via environment)
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # FIXED: No longer allows all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # FIXED: Explicit methods only
    allow_headers=["Content-Type", "Authorization"],  # FIXED: Explicit headers only
)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Pydantic models
class ProcessingRequest(BaseModel):
    """Signal processing request model"""
    samples: List[float] = Field(..., min_items=1, max_items=65536, description="Input signal samples")
    sampling_rate: Optional[float] = Field(6.48e6, gt=1000, le=1e8, description="Sampling rate in samples/second")
    control_input: Optional[List[float]] = Field(None, description="Optional control input")
    parameters: Optional[Dict] = Field(None, description="Optional processing parameters")
    
    @validator('samples')
    def validate_samples(cls, v):
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("All samples must be numeric")
        if any(abs(x) > 1e6 for x in v):
            raise ValueError("Sample values too large (max ±1e6)")
        return v


class ProcessingResponse(BaseModel):
    """Signal processing response model"""
    processed_signal: List[float] = Field(..., description="Processed signal output")
    performance_metrics: Dict = Field(..., description="Processing performance metrics")
    timestamp: float = Field(..., description="Processing timestamp")
    status: str = Field("success", description="Processing status")


class BenchmarkRequest(BaseModel):
    """Benchmark request model"""
    duration: float = Field(10.0, gt=0.1, le=300.0, description="Benchmark duration in seconds")
    batch_size: int = Field(8192, ge=64, le=65536, description="Batch size for processing")


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field("healthy", description="Service health status")
    timestamp: float = Field(..., description="Health check timestamp")
    performance: Dict = Field(..., description="Current performance metrics")
    components: Dict = Field(..., description="Component status")


class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str = Field(..., description="Message type")
    data: Dict = Field(..., description="Message data")
    timestamp: Optional[float] = Field(None, description="Message timestamp")


# Dependency injection
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token and get current user"""
    try:
        # SECURITY FIX: Use global security_manager instance instead of creating new one
        if not security_manager:
            raise HTTPException(status_code=503, detail="Security manager not available")

        payload = security_manager.verify_token(credentials.credentials)
        return payload
    except Exception as e:
        logger.warning(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


# Health check endpoints
@app.get("/health", response_model=HealthResponse)
@limiter.limit("60/minute")
async def health_check(request: Request, current_user=Depends(get_current_user)):
    """🏥 Health check endpoint - SECURITY: Now requires authentication"""
    try:
        components_status = {
            "engine": "healthy" if engine and engine.performance_metrics else "degraded",
            "plugin_manager": "healthy" if plugin_manager else "unhealthy",
            "metrics_collector": "healthy" if metrics_collector else "unhealthy",
            "security_manager": "healthy" if security_manager else "unhealthy"
        }

        # SECURITY FIX: Limit detailed performance info to admins only
        performance = {}
        if current_user.get("security_level") == "admin":
            performance = engine.get_performance_metrics() if engine else {}

        return HealthResponse(
            status="healthy" if all(status == "healthy" for status in components_status.values()) else "degraded",
            timestamp=time.time(),
            performance=performance,
            components=components_status
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.get("/metrics")
@limiter.limit("30/minute")
async def get_metrics(request: Request, current_user=Depends(get_current_user)):
    """📊 Get system metrics - SECURITY: Now requires authentication"""
    try:
        # SECURITY FIX: Only admins can view system metrics
        if current_user.get("security_level") not in ["admin", "system"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions to view metrics")

        if not metrics_collector:
            raise HTTPException(status_code=503, detail="Metrics collector not available")

        return metrics_collector.get_all_metrics()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


# Core processing endpoints
@app.post("/process", response_model=ProcessingResponse)
@limiter.limit("100/minute")
async def process_signal(request: Request, processing_request: ProcessingRequest, current_user=Depends(get_current_user)):
    """🧠 Process signal using holomorphic engine"""
    try:
        if not engine:
            raise HTTPException(status_code=503, detail="Processing engine not available")

        # Convert input samples to numpy array
        samples = np.array(processing_request.samples)
        control_input = np.array(processing_request.control_input) if processing_request.control_input else None

        # Generate time array
        dt = 1.0 / processing_request.sampling_rate
        t_array = np.arange(len(samples)) * dt

        # Process signal
        start_time = time.perf_counter()
        processed_signal = engine.process_holomorphic_signal(t_array, control_input)
        processing_time = time.perf_counter() - start_time

        # Get performance metrics
        performance_metrics = engine.get_performance_metrics()
        performance_metrics["api_processing_time_ms"] = processing_time * 1000

        # Update metrics collector
        if metrics_collector:
            metrics_collector.record_processing_event(
                samples_count=len(samples),
                processing_time=processing_time,
                user_id=current_user.get("user_id", "unknown")
            )

        return ProcessingResponse(
            processed_signal=processed_signal.tolist(),
            performance_metrics=performance_metrics,
            timestamp=time.time(),
            status="success"
        )

    except HTTPException:
        raise
    except Exception as e:
        # SECURITY FIX: Don't expose internal error details to clients
        logger.error(f"Signal processing failed: {e}")
        if metrics_collector:
            metrics_collector.record_error("processing_error", "Internal processing error")
        raise HTTPException(status_code=500, detail="Processing failed")


@app.post("/benchmark")
@limiter.limit("5/minute")
async def run_benchmark(request: Request, benchmark_request: BenchmarkRequest, current_user=Depends(get_current_user)):
    """🏁 Run performance benchmark"""
    try:
        logger.info(f"🏁 Starting benchmark for user {current_user.get('user_id', 'unknown')}")

        # Run benchmark in background task
        results = benchmark_holomorphic_engine(duration=benchmark_request.duration)

        # Update metrics
        if metrics_collector:
            metrics_collector.record_benchmark_result(results)

        return {
            "benchmark_results": results,
            "timestamp": time.time(),
            "status": "completed"
        }

    except HTTPException:
        raise
    except Exception as e:
        # SECURITY FIX: Don't expose internal error details
        logger.error(f"Benchmark failed: {e}")
        if metrics_collector:
            metrics_collector.record_error("benchmark_error", "Benchmark error")
        raise HTTPException(status_code=500, detail="Benchmark failed")


# Plugin management endpoints
@app.get("/plugins")
@limiter.limit("30/minute")
async def list_plugins(request, current_user=Depends(get_current_user)):
    """🔌 List available plugins"""
    try:
        if not plugin_manager:
            raise HTTPException(status_code=503, detail="Plugin manager not available")
        
        return plugin_manager.list_plugins()
    except Exception as e:
        logger.error(f"Plugin listing failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to list plugins")


@app.post("/plugins/{plugin_name}/execute")
@limiter.limit("50/minute")
async def execute_plugin(request: Request, plugin_name: str, data: Dict, current_user=Depends(get_current_user)):
    """🔌 Execute a specific plugin"""
    try:
        if not plugin_manager:
            raise HTTPException(status_code=503, detail="Plugin manager not available")

        result = plugin_manager.execute_plugin(plugin_name, data)

        if metrics_collector:
            metrics_collector.record_plugin_execution(plugin_name, current_user.get("user_id", "unknown"))

        return {
            "plugin_name": plugin_name,
            "result": result,
            "timestamp": time.time(),
            "status": "success"
        }

    except HTTPException:
        raise
    except Exception as e:
        # SECURITY FIX: Don't expose internal error details
        logger.error(f"Plugin execution failed: {e}")
        if metrics_collector:
            metrics_collector.record_error("plugin_error", f"{plugin_name}: Plugin execution error")
        raise HTTPException(status_code=500, detail="Plugin execution failed")


# WebSocket endpoint for real-time streaming
@app.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    """🌊 Real-time signal processing stream - SECURITY: Authentication required via query param"""
    # SECURITY FIX: Require authentication for WebSocket connections
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return

    try:
        # Verify token
        if not security_manager:
            await websocket.close(code=1011, reason="Security manager unavailable")
            return

        user_payload = security_manager.verify_token(token)
        logger.info(f"🌊 WebSocket connection established for user {user_payload.get('user_id')}")
    except Exception as e:
        logger.warning(f"WebSocket authentication failed: {e}")
        await websocket.close(code=1008, reason="Invalid authentication token")
        return

    await websocket.accept()

    try:
        while True:
            # Receive message
            message_data = await websocket.receive_text()
            message = WebSocketMessage.parse_raw(message_data)
            
            if message.type == "process":
                # Process signal in real-time
                samples = np.array(message.data.get("samples", []))
                if len(samples) == 0:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "data": {"message": "No samples provided"},
                        "timestamp": time.time()
                    }))
                    continue
                
                # Generate time array and process
                dt = 1.0 / message.data.get("sampling_rate", 6.48e6)
                t_array = np.arange(len(samples)) * dt
                
                if engine:
                    processed_signal = engine.process_holomorphic_signal(t_array)
                    performance_metrics = engine.get_performance_metrics()
                    
                    # Send response
                    response = {
                        "type": "processed_signal",
                        "data": {
                            "processed_signal": processed_signal.tolist(),
                            "performance_metrics": performance_metrics
                        },
                        "timestamp": time.time()
                    }
                    
                    await websocket.send_text(json.dumps(response))
                else:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "data": {"message": "Processing engine not available"},
                        "timestamp": time.time()
                    }))
            
            elif message.type == "ping":
                # Respond to ping with pong
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "data": {"message": "Server is alive"},
                    "timestamp": time.time()
                }))
            
            else:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "data": {"message": f"Unknown message type: {message.type}"},
                    "timestamp": time.time()
                }))
                
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "data": {"message": f"Server error: {str(e)}"},
                "timestamp": time.time()
            }))
        except:
            pass


# Static HTML demo page
@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """🎮 Interactive demo page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🧠 Holomorphic Signal Processing Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #1a1a1a; color: #fff; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 40px; }
            .demo-section { margin: 20px 0; padding: 20px; background: #2a2a2a; border-radius: 8px; }
            button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background: #45a049; }
            .metrics { background: #333; padding: 10px; border-radius: 4px; margin: 10px 0; }
            #chart { width: 100%; height: 400px; background: #fff; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 Holomorphic Signal Processing Engine</h1>
                <h2>Revolutionary CPU-Optimized Real-Time Processing</h2>
                <p><strong>Performance Target: 6.48M samples/second</strong></p>
            </div>
            
            <div class="demo-section">
                <h3>🚀 Performance Benchmark</h3>
                <button onclick="runBenchmark()">Run 10-Second Benchmark</button>
                <div id="benchmark-results" class="metrics"></div>
            </div>
            
            <div class="demo-section">
                <h3>🧠 Signal Processing Demo</h3>
                <button onclick="processTestSignal()">Process Test Signal</button>
                <div id="processing-results" class="metrics"></div>
                <canvas id="chart"></canvas>
            </div>
            
            <div class="demo-section">
                <h3>🌊 Real-Time Streaming</h3>
                <button onclick="connectWebSocket()" id="ws-button">Connect WebSocket</button>
                <div id="ws-status" class="metrics">Disconnected</div>
                <div id="stream-metrics" class="metrics"></div>
            </div>
        </div>
        
        <script>
            let ws = null;
            
            async function runBenchmark() {
                const resultDiv = document.getElementById('benchmark-results');
                resultDiv.innerHTML = '<p>🏁 Running benchmark...</p>';
                
                try {
                    const response = await fetch('/benchmark', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ duration: 10.0, batch_size: 8192 })
                    });
                    
                    const data = await response.json();
                    const results = data.benchmark_results;
                    
                    resultDiv.innerHTML = `
                        <h4>📊 Benchmark Results</h4>
                        <p><strong>Performance:</strong> ${(results.average_throughput/1e6).toFixed(2)}M samples/sec</p>
                        <p><strong>Target Achievement:</strong> ${results.performance_achieved.toFixed(1)}%</p>
                        <p><strong>Status:</strong> ${results.status}</p>
                        <p><strong>Total Samples:</strong> ${results.total_samples.toLocaleString()}</p>
                        <p><strong>Processing Time:</strong> ${results.total_time_seconds.toFixed(2)}s</p>
                    `;
                } catch (error) {
                    resultDiv.innerHTML = `<p>❌ Error: ${error.message}</p>`;
                }
            }
            
            async function processTestSignal() {
                const resultDiv = document.getElementById('processing-results');
                resultDiv.innerHTML = '<p>🧠 Processing signal...</p>';
                
                // Generate test signal
                const samples = Array.from({length: 1000}, (_, i) => Math.sin(2 * Math.PI * i / 100) + 0.1 * Math.random());
                
                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            samples: samples,
                            sampling_rate: 100000
                        })
                    });
                    
                    const data = await response.json();
                    const metrics = data.performance_metrics;
                    
                    resultDiv.innerHTML = `
                        <h4>🔬 Processing Results</h4>
                        <p><strong>Samples Processed:</strong> ${metrics.samples_processed}</p>
                        <p><strong>Processing Time:</strong> ${metrics.processing_time_ms.toFixed(3)}ms</p>
                        <p><strong>Throughput:</strong> ${(metrics.samples_per_second/1e6).toFixed(2)}M samples/sec</p>
                        <p><strong>Performance Ratio:</strong> ${(metrics.performance_ratio * 100).toFixed(1)}%</p>
                    `;
                    
                    // Simple visualization
                    drawSignal(data.processed_signal.slice(0, 200));
                    
                } catch (error) {
                    resultDiv.innerHTML = `<p>❌ Error: ${error.message}</p>`;
                }
            }
            
            function drawSignal(signal) {
                const canvas = document.getElementById('chart');
                const ctx = canvas.getContext('2d');
                canvas.width = canvas.offsetWidth;
                canvas.height = 400;
                
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.strokeStyle = '#4CAF50';
                ctx.lineWidth = 2;
                
                ctx.beginPath();
                const scaleX = canvas.width / signal.length;
                const scaleY = canvas.height / 4;
                const offsetY = canvas.height / 2;
                
                for (let i = 0; i < signal.length; i++) {
                    const x = i * scaleX;
                    const y = offsetY - signal[i] * scaleY;
                    
                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                
                ctx.stroke();
            }
            
            function connectWebSocket() {
                const button = document.getElementById('ws-button');
                const statusDiv = document.getElementById('ws-status');
                const metricsDiv = document.getElementById('stream-metrics');
                
                if (ws) {
                    ws.close();
                    ws = null;
                    button.textContent = 'Connect WebSocket';
                    statusDiv.innerHTML = 'Disconnected';
                    return;
                }
                
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/stream`);
                
                ws.onopen = () => {
                    statusDiv.innerHTML = '🌊 Connected';
                    button.textContent = 'Disconnect WebSocket';
                    
                    // Send ping every 5 seconds
                    setInterval(() => {
                        if (ws && ws.readyState === WebSocket.OPEN) {
                            ws.send(JSON.stringify({
                                type: 'ping',
                                data: {},
                                timestamp: Date.now() / 1000
                            }));
                        }
                    }, 5000);
                };
                
                ws.onmessage = (event) => {
                    const message = JSON.parse(event.data);
                    if (message.type === 'processed_signal') {
                        const metrics = message.data.performance_metrics;
                        metricsDiv.innerHTML = `
                            <h4>🌊 Stream Metrics</h4>
                            <p><strong>Throughput:</strong> ${(metrics.samples_per_second/1e6).toFixed(2)}M samples/sec</p>
                            <p><strong>Latency:</strong> ${metrics.processing_time_ms.toFixed(3)}ms</p>
                        `;
                    }
                };
                
                ws.onclose = () => {
                    statusDiv.innerHTML = 'Disconnected';
                    button.textContent = 'Connect WebSocket';
                    ws = null;
                };
                
                ws.onerror = (error) => {
                    statusDiv.innerHTML = `❌ Error: ${error.message}`;
                };
            }
        </script>
    </body>
    </html>
    """


# HolomorphicAPI class for external use
class HolomorphicAPI:
    """🌐 Holomorphic API wrapper class"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.app = app
    
    def run(self, **kwargs):
        """🚀 Run the API server"""
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=True,
            **kwargs
        )
        server = uvicorn.Server(config)
        server.run()


if __name__ == "__main__":
    # Run development server
    api = HolomorphicAPI()
    api.run(reload=True)