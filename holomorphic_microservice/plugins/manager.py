"""
🔌 Plugin Management System
Dynamic plugin loading and execution with isolation
"""

import importlib
import importlib.util
import inspect
import json
import logging
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
import traceback
import uuid

import numpy as np
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginMetadata(BaseModel):
    """Plugin metadata model"""
    name: str = Field(..., description="Plugin name")
    version: str = Field("1.0.0", description="Plugin version")
    description: str = Field("", description="Plugin description")
    author: str = Field("", description="Plugin author")
    tags: List[str] = Field(default_factory=list, description="Plugin tags")
    dependencies: List[str] = Field(default_factory=list, description="Plugin dependencies")
    input_schema: Dict = Field(default_factory=dict, description="Input data schema")
    output_schema: Dict = Field(default_factory=dict, description="Output data schema")
    timeout_seconds: float = Field(30.0, description="Plugin execution timeout")
    memory_limit_mb: int = Field(512, description="Memory limit in MB")
    cpu_limit_percent: float = Field(50.0, description="CPU usage limit percentage")


class PluginBase:
    """🔌 Base class for all plugins"""
    
    def __init__(self):
        self.metadata = PluginMetadata(
            name=self.__class__.__name__,
            description="Base plugin class"
        )
        self.logger = logging.getLogger(f"plugin.{self.metadata.name}")
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin logic - must be implemented by subclasses"""
        raise NotImplementedError("Plugin must implement execute method")
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data"""
        return True
    
    def validate_output(self, result: Dict[str, Any]) -> bool:
        """Validate output data"""
        return True
    
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata"""
        return self.metadata


class SignalProcessingPlugin(PluginBase):
    """🌊 Signal processing plugin example"""
    
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="SignalProcessingPlugin",
            version="1.0.0",
            description="Advanced signal processing operations",
            author="iDeaKz",
            tags=["signal", "processing", "filter"],
            input_schema={
                "type": "object",
                "properties": {
                    "signal": {"type": "array", "items": {"type": "number"}},
                    "operation": {"type": "string", "enum": ["fft", "filter", "smooth"]},
                    "parameters": {"type": "object"}
                },
                "required": ["signal", "operation"]
            },
            timeout_seconds=60.0
        )
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute signal processing operation"""
        signal = np.array(data["signal"])
        operation = data["operation"]
        parameters = data.get("parameters", {})
        
        try:
            if operation == "fft":
                result = np.fft.fft(signal)
                return {
                    "processed_signal": result.tolist(),
                    "magnitude": np.abs(result).tolist(),
                    "phase": np.angle(result).tolist(),
                    "operation": operation
                }
            
            elif operation == "filter":
                # Simple moving average filter
                window = parameters.get("window", 5)
                filtered = np.convolve(signal, np.ones(window)/window, mode='same')
                return {
                    "processed_signal": filtered.tolist(),
                    "operation": operation,
                    "parameters": {"window": window}
                }
            
            elif operation == "smooth":
                # Gaussian smoothing
                sigma = parameters.get("sigma", 1.0)
                from scipy.ndimage import gaussian_filter1d
                smoothed = gaussian_filter1d(signal, sigma=sigma)
                return {
                    "processed_signal": smoothed.tolist(),
                    "operation": operation,
                    "parameters": {"sigma": sigma}
                }
            
            else:
                raise ValueError(f"Unknown operation: {operation}")
                
        except Exception as e:
            self.logger.error(f"Signal processing error: {e}")
            raise


class MathematicalPlugin(PluginBase):
    """🧮 Mathematical operations plugin"""
    
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="MathematicalPlugin",
            version="1.0.0",
            description="Advanced mathematical operations and analysis",
            author="iDeaKz",
            tags=["math", "analysis", "statistics"],
            input_schema={
                "type": "object",
                "properties": {
                    "data": {"type": "array", "items": {"type": "number"}},
                    "operation": {"type": "string", "enum": ["stats", "correlation", "regression"]},
                    "parameters": {"type": "object"}
                },
                "required": ["data", "operation"]
            }
        )
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mathematical operation"""
        input_data = np.array(data["data"])
        operation = data["operation"]
        parameters = data.get("parameters", {})
        
        try:
            if operation == "stats":
                return {
                    "mean": float(np.mean(input_data)),
                    "std": float(np.std(input_data)),
                    "min": float(np.min(input_data)),
                    "max": float(np.max(input_data)),
                    "median": float(np.median(input_data)),
                    "var": float(np.var(input_data)),
                    "operation": operation
                }
            
            elif operation == "correlation":
                # Auto-correlation
                correlation = np.correlate(input_data, input_data, mode='full')
                return {
                    "correlation": correlation[correlation.size // 2:].tolist(),
                    "peak_correlation": float(np.max(correlation)),
                    "operation": operation
                }
            
            elif operation == "regression":
                # Linear regression
                x = np.arange(len(input_data))
                coeffs = np.polyfit(x, input_data, 1)
                fitted = np.polyval(coeffs, x)
                r_squared = 1 - np.sum((input_data - fitted) ** 2) / np.sum((input_data - np.mean(input_data)) ** 2)
                
                return {
                    "slope": float(coeffs[0]),
                    "intercept": float(coeffs[1]),
                    "fitted_values": fitted.tolist(),
                    "r_squared": float(r_squared),
                    "operation": operation
                }
            
            else:
                raise ValueError(f"Unknown operation: {operation}")
                
        except Exception as e:
            self.logger.error(f"Mathematical operation error: {e}")
            raise


class PluginManager:
    """🔌 Plugin Manager with dynamic loading and execution"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, PluginBase] = {}
        self.plugin_metadata: Dict[str, PluginMetadata] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.execution_stats: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        
        # Create plugin directory if it doesn't exist
        self.plugin_dir.mkdir(exist_ok=True)
        
        # Load built-in plugins
        self._load_builtin_plugins()
        
        # Load external plugins
        self._load_external_plugins()
        
        logger.info(f"🔌 Plugin Manager initialized with {len(self.plugins)} plugins")
    
    def _load_builtin_plugins(self):
        """Load built-in plugins"""
        builtin_plugins = [
            SignalProcessingPlugin,
            MathematicalPlugin
        ]
        
        for plugin_class in builtin_plugins:
            try:
                plugin_instance = plugin_class()
                self._register_plugin(plugin_instance)
                logger.info(f"✅ Loaded built-in plugin: {plugin_instance.metadata.name}")
            except Exception as e:
                logger.error(f"❌ Failed to load built-in plugin {plugin_class.__name__}: {e}")
    
    def _load_external_plugins(self):
        """Load plugins from plugin directory"""
        for plugin_file in self.plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
            
            try:
                self._load_plugin_from_file(plugin_file)
            except Exception as e:
                logger.error(f"❌ Failed to load plugin from {plugin_file}: {e}")
    
    def _load_plugin_from_file(self, plugin_file: Path):
        """Load a single plugin from file"""
        spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load plugin spec from {plugin_file}")
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find plugin classes in the module
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, PluginBase) and 
                obj != PluginBase):
                
                plugin_instance = obj()
                self._register_plugin(plugin_instance)
                logger.info(f"✅ Loaded external plugin: {plugin_instance.metadata.name}")
    
    def _register_plugin(self, plugin: PluginBase):
        """Register a plugin instance"""
        with self.lock:
            metadata = plugin.get_metadata()
            self.plugins[metadata.name] = plugin
            self.plugin_metadata[metadata.name] = metadata
            self.execution_stats[metadata.name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_execution_time": 0.0,
                "average_execution_time": 0.0,
                "last_execution": None
            }
    
    def list_plugins(self) -> Dict[str, Dict]:
        """List all available plugins"""
        with self.lock:
            return {
                name: {
                    "metadata": metadata.dict(),
                    "stats": self.execution_stats[name].copy()
                }
                for name, metadata in self.plugin_metadata.items()
            }
    
    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """Get detailed information about a specific plugin"""
        with self.lock:
            if plugin_name not in self.plugins:
                return None
            
            return {
                "metadata": self.plugin_metadata[plugin_name].dict(),
                "stats": self.execution_stats[plugin_name].copy(),
                "available": True
            }
    
    def execute_plugin(self, plugin_name: str, data: Dict[str, Any], timeout: Optional[float] = None) -> Dict[str, Any]:
        """Execute a plugin with the given data"""
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin '{plugin_name}' not found")
        
        plugin = self.plugins[plugin_name]
        metadata = self.plugin_metadata[plugin_name]
        execution_timeout = timeout or metadata.timeout_seconds
        
        # Generate execution ID
        execution_id = str(uuid.uuid4())
        
        logger.info(f"🔌 Executing plugin '{plugin_name}' (ID: {execution_id})")
        
        try:
            # Validate input
            if not plugin.validate_input(data):
                raise ValueError("Input validation failed")
            
            # Execute plugin with timeout
            future = self.executor.submit(self._execute_plugin_safe, plugin, data, execution_id)
            
            start_time = time.time()
            result = future.result(timeout=execution_timeout)
            execution_time = time.time() - start_time
            
            # Validate output
            if not plugin.validate_output(result):
                raise ValueError("Output validation failed")
            
            # Update statistics
            self._update_plugin_stats(plugin_name, execution_time, success=True)
            
            # Add execution metadata to result
            result.update({
                "execution_id": execution_id,
                "plugin_name": plugin_name,
                "execution_time_seconds": execution_time,
                "timestamp": time.time(),
                "status": "success"
            })
            
            logger.info(f"✅ Plugin '{plugin_name}' executed successfully in {execution_time:.3f}s")
            
            return result
            
        except TimeoutError:
            error_msg = f"Plugin '{plugin_name}' execution timed out after {execution_timeout}s"
            logger.error(error_msg)
            self._update_plugin_stats(plugin_name, execution_timeout, success=False)
            raise RuntimeError(error_msg)
        
        except Exception as e:
            error_msg = f"Plugin '{plugin_name}' execution failed: {str(e)}"
            logger.error(error_msg)
            self._update_plugin_stats(plugin_name, 0.0, success=False)
            raise RuntimeError(error_msg)
    
    def _execute_plugin_safe(self, plugin: PluginBase, data: Dict[str, Any], execution_id: str) -> Dict[str, Any]:
        """Safely execute plugin with error handling"""
        try:
            return plugin.execute(data)
        except Exception as e:
            logger.error(f"Plugin execution error (ID: {execution_id}): {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _update_plugin_stats(self, plugin_name: str, execution_time: float, success: bool):
        """Update plugin execution statistics"""
        with self.lock:
            stats = self.execution_stats[plugin_name]
            stats["total_executions"] += 1
            stats["last_execution"] = time.time()
            
            if success:
                stats["successful_executions"] += 1
                stats["total_execution_time"] += execution_time
                stats["average_execution_time"] = (
                    stats["total_execution_time"] / stats["successful_executions"]
                )
            else:
                stats["failed_executions"] += 1
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a specific plugin"""
        if plugin_name not in self.plugins:
            return False
        
        try:
            # Remove existing plugin
            with self.lock:
                del self.plugins[plugin_name]
                del self.plugin_metadata[plugin_name]
                del self.execution_stats[plugin_name]
            
            # Reload external plugins
            self._load_external_plugins()
            
            return plugin_name in self.plugins
            
        except Exception as e:
            logger.error(f"Failed to reload plugin '{plugin_name}': {e}")
            return False
    
    def get_execution_stats(self) -> Dict[str, Dict]:
        """Get execution statistics for all plugins"""
        with self.lock:
            return {
                name: stats.copy()
                for name, stats in self.execution_stats.items()
            }
    
    def shutdown(self):
        """Shutdown the plugin manager"""
        logger.info("🛑 Shutting down Plugin Manager...")
        self.executor.shutdown(wait=True)
        logger.info("✅ Plugin Manager shutdown complete")


# Example plugin file template
PLUGIN_TEMPLATE = '''"""
🔌 Custom Plugin Template
Generated by Holomorphic Signal Processing System
"""

import numpy as np
from typing import Dict, Any
from holomorphic_microservice.plugins.manager import PluginBase, PluginMetadata


class CustomPlugin(PluginBase):
    """🔧 Custom plugin implementation"""
    
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="CustomPlugin",
            version="1.0.0",
            description="Custom plugin description",
            author="Your Name",
            tags=["custom", "example"],
            input_schema={
                "type": "object",
                "properties": {
                    "data": {"type": "array", "items": {"type": "number"}},
                    "operation": {"type": "string"}
                },
                "required": ["data", "operation"]
            }
        )
    
    def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom plugin logic"""
        input_data = np.array(data["data"])
        operation = data["operation"]
        
        # Implement your custom logic here
        result = input_data * 2  # Example operation
        
        return {
            "processed_data": result.tolist(),
            "operation": operation,
            "custom_field": "Custom plugin executed successfully"
        }
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data"""
        required_fields = ["data", "operation"]
        return all(field in data for field in required_fields)
'''


def create_plugin_template(plugin_name: str, output_dir: str = "plugins") -> str:
    """Create a new plugin template file"""
    output_path = Path(output_dir) / f"{plugin_name.lower()}_plugin.py"
    output_path.parent.mkdir(exist_ok=True)
    
    # Customize template
    customized_template = PLUGIN_TEMPLATE.replace("CustomPlugin", f"{plugin_name}Plugin")
    customized_template = customized_template.replace("Custom plugin description", f"{plugin_name} plugin implementation")
    
    # Write template file
    with open(output_path, 'w') as f:
        f.write(customized_template)
    
    logger.info(f"📝 Created plugin template: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    # Test plugin manager
    manager = PluginManager()
    
    # List available plugins
    plugins = manager.list_plugins()
    print("Available plugins:")
    for name, info in plugins.items():
        print(f"  - {name}: {info['metadata']['description']}")
    
    # Test signal processing plugin
    try:
        test_signal = [np.sin(2 * np.pi * i / 100) for i in range(200)]
        result = manager.execute_plugin("SignalProcessingPlugin", {
            "signal": test_signal,
            "operation": "fft"
        })
        print(f"\nSignal processing result: {len(result['processed_signal'])} samples processed")
    except Exception as e:
        print(f"Plugin execution failed: {e}")
    
    # Create example plugin template
    create_plugin_template("Example")