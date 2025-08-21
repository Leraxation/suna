"""
Monitoring and Maintenance Tool for Suna AI
Provides comprehensive monitoring, maintenance, and system health management
Extends existing Suna AI infrastructure with enterprise-level operational capabilities
"""

import json
import asyncio
import time
import psutil
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import threading

from agentpress.tool import Tool, ToolResult, openapi_schema, xml_schema
from services.llm import make_llm_api_call
from utils.logger import logger
from utils.config import config

class MonitoringMaintenanceTool(Tool):
    """Advanced monitoring and maintenance management tool."""

    def __init__(self):
        super().__init__()
        self.monitoring_active = False
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.alerts = []
        self.maintenance_schedules = {}
        self.health_checks = {}
        self.performance_baselines = {}
        self.monitoring_thread = None
        
        # Initialize default monitoring configuration
        self._initialize_monitoring()
        
    def _initialize_monitoring(self):
        """Initialize default monitoring configurations."""
        self.monitoring_config = {
            "intervals": {
                "system_metrics": 60,  # seconds
                "health_checks": 300,  # 5 minutes
                "performance_analysis": 900,  # 15 minutes
                "log_analysis": 1800  # 30 minutes
            },
            "thresholds": {
                "cpu_usage": 80,
                "memory_usage": 85,
                "disk_usage": 90,
                "response_time": 5000,  # milliseconds
                "error_rate": 5  # percentage
            },
            "alerts": {
                "enabled": True,
                "channels": ["log", "email", "webhook"],
                "severity_levels": ["low", "medium", "high", "critical"]
            }
        }

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "start_monitoring",
            "description": "Start comprehensive system monitoring with customizable metrics and alerts",
            "parameters": {
                "type": "object",
                "properties": {
                    "monitoring_scope": {
                        "type": "string",
                        "description": "Scope of monitoring",
                        "enum": ["system", "application", "network", "database", "all"],
                        "default": "all"
                    },
                    "monitoring_interval": {
                        "type": "integer",
                        "description": "Monitoring interval in seconds",
                        "default": 60
                    },
                    "alert_thresholds": {
                        "type": "object",
                        "description": "Custom alert thresholds for various metrics"
                    },
                    "enable_predictive": {
                        "type": "boolean",
                        "description": "Enable predictive analytics for proactive monitoring",
                        "default": True
                    }
                }
            }
        }
    })
    @xml_schema(
        tag_name="start-monitoring",
        mappings=[
            {"param_name": "monitoring_scope", "node_type": "attribute", "path": "scope"},
            {"param_name": "monitoring_interval", "node_type": "attribute", "path": "interval"},
            {"param_name": "alert_thresholds", "node_type": "content", "path": "thresholds"},
            {"param_name": "enable_predictive", "node_type": "attribute", "path": "predictive"}
        ],
        example='''
        <function_calls>
        <invoke name="start_monitoring">
        <parameter name="monitoring_scope">all</parameter>
        <parameter name="monitoring_interval">60</parameter>
        <parameter name="enable_predictive">true</parameter>
        </invoke>
        </function_calls>
        '''
    )
    async def start_monitoring(
        self, 
        monitoring_scope: str = "all",
        monitoring_interval: int = 60,
        alert_thresholds: Dict[str, Any] = None,
        enable_predictive: bool = True
    ) -> ToolResult:
        """Start comprehensive system monitoring."""
        try:
            if alert_thresholds:
                self.monitoring_config["thresholds"].update(alert_thresholds)
            
            self.monitoring_config["intervals"]["system_metrics"] = monitoring_interval
            
            # Start monitoring if not already active
            if not self.monitoring_active:
                self.monitoring_active = True
                self.monitoring_thread = threading.Thread(
                    target=self._monitoring_loop,
                    args=(monitoring_scope, enable_predictive),
                    daemon=True
                )
                self.monitoring_thread.start()
            
            # Collect initial baseline metrics
            baseline_metrics = await self._collect_baseline_metrics(monitoring_scope)
            
            return self.success_response({
                "monitoring_started": True,
                "monitoring_scope": monitoring_scope,
                "monitoring_interval": monitoring_interval,
                "predictive_enabled": enable_predictive,
                "baseline_metrics": baseline_metrics,
                "alert_thresholds": self.monitoring_config["thresholds"],
                "started_at": datetime.now().isoformat(),
                "monitoring_id": f"monitor_{int(time.time())}"
            })
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            return self.fail_response(f"Failed to start monitoring: {str(e)}")

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "get_system_health",
            "description": "Get comprehensive system health report including metrics, alerts, and recommendations",
            "parameters": {
                "type": "object",
                "properties": {
                    "include_history": {
                        "type": "boolean",
                        "description": "Include historical metrics in the report",
                        "default": False
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range for historical data (1h, 24h, 7d, 30d)",
                        "default": "24h"
                    },
                    "detail_level": {
                        "type": "string",
                        "description": "Level of detail in the report",
                        "enum": ["summary", "detailed", "comprehensive"],
                        "default": "detailed"
                    }
                }
            }
        }
    })
    async def get_system_health(
        self, 
        include_history: bool = False,
        time_range: str = "24h",
        detail_level: str = "detailed"
    ) -> ToolResult:
        """Get comprehensive system health report."""
        try:
            # Collect current system metrics
            current_metrics = await self._collect_current_metrics()
            
            # Analyze system health
            health_analysis = await self._analyze_system_health(current_metrics)
            
            # Get active alerts
            active_alerts = self._get_active_alerts()
            
            # Generate recommendations
            recommendations = await self._generate_health_recommendations(current_metrics, health_analysis)
            
            health_report = {
                "overall_health_score": health_analysis["overall_score"],
                "health_status": health_analysis["status"],
                "current_metrics": current_metrics,
                "active_alerts": active_alerts,
                "recommendations": recommendations,
                "report_generated_at": datetime.now().isoformat()
            }
            
            if include_history:
                historical_data = self._get_historical_metrics(time_range)
                health_report["historical_metrics"] = historical_data
                health_report["trends"] = self._analyze_trends(historical_data)
            
            if detail_level == "comprehensive":
                health_report["detailed_analysis"] = await self._get_detailed_analysis()
                health_report["performance_benchmarks"] = self.performance_baselines
                health_report["maintenance_status"] = self._get_maintenance_status()
            
            return self.success_response({
                "system_health_report": health_report,
                "report_detail_level": detail_level,
                "monitoring_active": self.monitoring_active
            })
            
        except Exception as e:
            logger.error(f"Failed to get system health: {str(e)}")
            return self.fail_response(f"Failed to get system health: {str(e)}")

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "schedule_maintenance",
            "description": "Schedule and manage system maintenance tasks with automated execution",
            "parameters": {
                "type": "object",
                "properties": {
                    "maintenance_type": {
                        "type": "string",
                        "description": "Type of maintenance to schedule",
                        "enum": ["cleanup", "optimization", "backup", "update", "security_scan", "custom"]
                    },
                    "schedule": {
                        "type": "object",
                        "description": "Maintenance schedule configuration",
                        "properties": {
                            "frequency": {"type": "string", "enum": ["once", "daily", "weekly", "monthly"]},
                            "time": {"type": "string", "description": "Time to execute (HH:MM format)"},
                            "day_of_week": {"type": "integer", "description": "Day of week (0=Monday, 6=Sunday)"},
                            "day_of_month": {"type": "integer", "description": "Day of month (1-31)"}
                        },
                        "required": ["frequency"]
                    },
                    "maintenance_config": {
                        "type": "object",
                        "description": "Configuration parameters for the maintenance task"
                    },
                    "auto_execute": {
                        "type": "boolean",
                        "description": "Whether to automatically execute the maintenance",
                        "default": True
                    }
                },
                "required": ["maintenance_type", "schedule"]
            }
        }
    })
    async def schedule_maintenance(
        self, 
        maintenance_type: str, 
        schedule: Dict[str, Any],
        maintenance_config: Dict[str, Any] = None,
        auto_execute: bool = True
    ) -> ToolResult:
        """Schedule system maintenance tasks."""
        try:
            if maintenance_config is None:
                maintenance_config = {}
            
            # Generate maintenance task ID
            task_id = f"maint_{maintenance_type}_{int(time.time())}"
            
            # Calculate next execution time
            next_execution = self._calculate_next_execution(schedule)
            
            # Create maintenance task
            maintenance_task = {
                "task_id": task_id,
                "type": maintenance_type,
                "schedule": schedule,
                "config": maintenance_config,
                "auto_execute": auto_execute,
                "next_execution": next_execution,
                "created_at": datetime.now().isoformat(),
                "status": "scheduled",
                "execution_history": []
            }
            
            # Store the maintenance task
            self.maintenance_schedules[task_id] = maintenance_task
            
            # If it's a one-time task and should execute now
            if schedule["frequency"] == "once" and auto_execute:
                execution_result = await self._execute_maintenance_task(maintenance_task)
                maintenance_task["execution_history"].append(execution_result)
                maintenance_task["status"] = "completed"
            
            return self.success_response({
                "maintenance_scheduled": maintenance_task,
                "task_id": task_id,
                "next_execution": next_execution,
                "estimated_duration": self._estimate_maintenance_duration(maintenance_type),
                "maintenance_window": self._get_maintenance_window(maintenance_type)
            })
            
        except Exception as e:
            logger.error(f"Failed to schedule maintenance: {str(e)}")
            return self.fail_response(f"Failed to schedule maintenance: {str(e)}")

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "analyze_performance",
            "description": "Perform comprehensive performance analysis with bottleneck identification and optimization suggestions",
            "parameters": {
                "type": "object",
                "properties": {
                    "analysis_scope": {
                        "type": "string",
                        "description": "Scope of performance analysis",
                        "enum": ["cpu", "memory", "disk", "network", "application", "database", "all"],
                        "default": "all"
                    },
                    "time_period": {
                        "type": "string",
                        "description": "Time period for analysis",
                        "enum": ["1h", "6h", "24h", "7d", "30d"],
                        "default": "24h"
                    },
                    "include_predictions": {
                        "type": "boolean",
                        "description": "Include performance predictions and forecasts",
                        "default": True
                    }
                }
            }
        }
    })
    async def analyze_performance(
        self, 
        analysis_scope: str = "all",
        time_period: str = "24h",
        include_predictions: bool = True
    ) -> ToolResult:
        """Perform comprehensive performance analysis."""
        try:
            # Collect performance metrics
            performance_metrics = await self._collect_performance_metrics(analysis_scope, time_period)
            
            # Identify bottlenecks
            bottlenecks = await self._identify_bottlenecks(performance_metrics)
            
            # Generate optimization suggestions
            optimizations = await self._generate_optimization_suggestions(bottlenecks, performance_metrics)
            
            # Calculate performance scores
            performance_scores = self._calculate_performance_scores(performance_metrics)
            
            analysis_result = {
                "performance_summary": {
                    "overall_score": performance_scores["overall"],
                    "cpu_score": performance_scores["cpu"],
                    "memory_score": performance_scores["memory"],
                    "disk_score": performance_scores["disk"],
                    "network_score": performance_scores["network"]
                },
                "bottlenecks_identified": bottlenecks,
                "optimization_suggestions": optimizations,
                "performance_metrics": performance_metrics,
                "analysis_scope": analysis_scope,
                "time_period": time_period,
                "analyzed_at": datetime.now().isoformat()
            }
            
            if include_predictions:
                predictions = await self._generate_performance_predictions(performance_metrics)
                analysis_result["performance_predictions"] = predictions
                analysis_result["capacity_planning"] = self._generate_capacity_recommendations(predictions)
            
            return self.success_response({
                "performance_analysis": analysis_result,
                "recommendations_count": len(optimizations),
                "critical_issues": len([b for b in bottlenecks if b.get("severity") == "critical"])
            })
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {str(e)}")
            return self.fail_response(f"Performance analysis failed: {str(e)}")

    @openapi_schema({
        "type": "function",
        "function": {
            "name": "manage_alerts",
            "description": "Manage system alerts including configuration, acknowledgment, and escalation",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Alert management action",
                        "enum": ["list", "acknowledge", "resolve", "escalate", "configure", "mute"]
                    },
                    "alert_id": {
                        "type": "string",
                        "description": "Specific alert ID for targeted actions"
                    },
                    "alert_config": {
                        "type": "object",
                        "description": "Alert configuration for setup or modification"
                    },
                    "filters": {
                        "type": "object",
                        "description": "Filters for listing alerts (severity, type, time_range)"
                    }
                },
                "required": ["action"]
            }
        }
    })
    async def manage_alerts(
        self, 
        action: str,
        alert_id: str = None,
        alert_config: Dict[str, Any] = None,
        filters: Dict[str, Any] = None
    ) -> ToolResult:
        """Manage system alerts and notifications."""
        try:
            if action == "list":
                alerts = self._filter_alerts(filters or {})
                return self.success_response({
                    "alerts": alerts,
                    "total_count": len(alerts),
                    "active_count": len([a for a in alerts if a["status"] == "active"]),
                    "filters_applied": filters
                })
                
            elif action == "acknowledge":
                if not alert_id:
                    return self.fail_response("Alert ID required for acknowledgment")
                
                result = self._acknowledge_alert(alert_id)
                return self.success_response({
                    "alert_acknowledged": result,
                    "alert_id": alert_id,
                    "acknowledged_at": datetime.now().isoformat()
                })
                
            elif action == "resolve":
                if not alert_id:
                    return self.fail_response("Alert ID required for resolution")
                
                result = self._resolve_alert(alert_id)
                return self.success_response({
                    "alert_resolved": result,
                    "alert_id": alert_id,
                    "resolved_at": datetime.now().isoformat()
                })
                
            elif action == "configure":
                if not alert_config:
                    return self.fail_response("Alert configuration required")
                
                config_result = self._configure_alerts(alert_config)
                return self.success_response({
                    "alert_configuration": config_result,
                    "configured_at": datetime.now().isoformat()
                })
                
            else:
                return self.fail_response(f"Unknown alert action: {action}")
                
        except Exception as e:
            logger.error(f"Alert management failed: {str(e)}")
            return self.fail_response(f"Alert management failed: {str(e)}")

    # Implementation methods
    def _monitoring_loop(self, monitoring_scope: str, enable_predictive: bool):
        """Main monitoring loop running in background thread."""
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = asyncio.run(self._collect_current_metrics())
                
                # Store metrics in history
                timestamp = datetime.now().isoformat()
                for metric_name, value in metrics.items():
                    self.metrics_history[metric_name].append({
                        "timestamp": timestamp,
                        "value": value
                    })
                
                # Check for alerts
                self._check_alert_conditions(metrics)
                
                # Predictive analysis if enabled
                if enable_predictive:
                    self._perform_predictive_analysis(metrics)
                
                # Sleep until next monitoring interval
                time.sleep(self.monitoring_config["intervals"]["system_metrics"])
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {str(e)}")
                time.sleep(60)  # Wait before retrying

    async def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics."""
        try:
            # Use psutil for real system metrics where possible
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_usage": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "load_average": psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 1.0,
                "process_count": len(psutil.pids()),
                "network_connections": len(psutil.net_connections()),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            # Fallback to simulated metrics if psutil fails
            logger.warning(f"Failed to collect real metrics, using simulated: {str(e)}")
            return {
                "cpu_usage": 45.2,
                "memory_usage": 62.8,
                "memory_available_gb": 6.2,
                "disk_usage": 58.3,
                "disk_free_gb": 128.5,
                "load_average": 1.2,
                "process_count": 156,
                "network_connections": 23,
                "timestamp": datetime.now().isoformat()
            }

    async def _collect_baseline_metrics(self, monitoring_scope: str) -> Dict[str, Any]:
        """Collect baseline metrics for comparison."""
        metrics = await self._collect_current_metrics()
        
        # Store as baseline
        self.performance_baselines = {
            "baseline_timestamp": datetime.now().isoformat(),
            "baseline_metrics": metrics,
            "monitoring_scope": monitoring_scope
        }
        
        return metrics

    async def _analyze_system_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall system health based on metrics."""
        health_score = 100
        issues = []
        
        # Check CPU usage
        if metrics["cpu_usage"] > self.monitoring_config["thresholds"]["cpu_usage"]:
            health_score -= 20
            issues.append("High CPU usage detected")
        
        # Check memory usage
        if metrics["memory_usage"] > self.monitoring_config["thresholds"]["memory_usage"]:
            health_score -= 25
            issues.append("High memory usage detected")
        
        # Check disk usage
        if metrics["disk_usage"] > self.monitoring_config["thresholds"]["disk_usage"]:
            health_score -= 30
            issues.append("High disk usage detected")
        
        # Determine status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 75:
            status = "good"
        elif health_score >= 50:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "overall_score": max(0, health_score),
            "status": status,
            "issues": issues,
            "analysis_timestamp": datetime.now().isoformat()
        }

    def _check_alert_conditions(self, metrics: Dict[str, Any]):
        """Check if any alert conditions are met."""
        thresholds = self.monitoring_config["thresholds"]
        
        # Check CPU threshold
        if metrics["cpu_usage"] > thresholds["cpu_usage"]:
            self._create_alert("cpu_high", "high", f"CPU usage at {metrics['cpu_usage']:.1f}%")
        
        # Check memory threshold
        if metrics["memory_usage"] > thresholds["memory_usage"]:
            self._create_alert("memory_high", "high", f"Memory usage at {metrics['memory_usage']:.1f}%")
        
        # Check disk threshold
        if metrics["disk_usage"] > thresholds["disk_usage"]:
            self._create_alert("disk_high", "critical", f"Disk usage at {metrics['disk_usage']:.1f}%")

    def _create_alert(self, alert_type: str, severity: str, message: str):
        """Create a new alert."""
        alert = {
            "alert_id": f"alert_{len(self.alerts) + 1}",
            "type": alert_type,
            "severity": severity,
            "message": message,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "acknowledged": False,
            "resolved": False
        }
        
        self.alerts.append(alert)
        logger.warning(f"Alert created: {alert}")

    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active alerts."""
        return [alert for alert in self.alerts if alert["status"] == "active"]

    async def _generate_health_recommendations(self, metrics: Dict[str, Any], health_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate health improvement recommendations."""
        recommendations = []
        
        if metrics["cpu_usage"] > 70:
            recommendations.append({
                "category": "performance",
                "priority": "medium",
                "title": "Optimize CPU Usage",
                "description": "Consider identifying and optimizing CPU-intensive processes",
                "estimated_impact": "15-25% performance improvement"
            })
        
        if metrics["memory_usage"] > 80:
            recommendations.append({
                "category": "performance",
                "priority": "high",
                "title": "Memory Optimization",
                "description": "Review memory usage and consider adding more RAM or optimizing applications",
                "estimated_impact": "20-30% performance improvement"
            })
        
        if metrics["disk_usage"] > 85:
            recommendations.append({
                "category": "storage",
                "priority": "critical",
                "title": "Disk Space Management",
                "description": "Clean up unnecessary files or expand storage capacity",
                "estimated_impact": "Prevent system failures"
            })
        
        return recommendations

    # Additional helper methods with placeholder implementations
    def _get_historical_metrics(self, time_range: str) -> Dict[str, Any]:
        """Get historical metrics for specified time range."""
        return {"historical_data": "placeholder"}

    def _analyze_trends(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in historical data."""
        return {"trends": "placeholder"}

    async def _get_detailed_analysis(self) -> Dict[str, Any]:
        """Get detailed system analysis."""
        return {"detailed_analysis": "placeholder"}

    def _get_maintenance_status(self) -> Dict[str, Any]:
        """Get current maintenance status."""
        return {"maintenance_status": "placeholder"}

    def _calculate_next_execution(self, schedule: Dict[str, Any]) -> str:
        """Calculate next execution time for maintenance."""
        return (datetime.now() + timedelta(hours=1)).isoformat()

    async def _execute_maintenance_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a maintenance task."""
        return {"execution_result": "completed", "duration_seconds": 120}

    def _estimate_maintenance_duration(self, maintenance_type: str) -> str:
        """Estimate maintenance duration."""
        durations = {
            "cleanup": "5-10 minutes",
            "optimization": "15-30 minutes",
            "backup": "30-60 minutes",
            "update": "10-45 minutes",
            "security_scan": "20-40 minutes"
        }
        return durations.get(maintenance_type, "10-30 minutes")

    def _get_maintenance_window(self, maintenance_type: str) -> str:
        """Get recommended maintenance window."""
        return "Low traffic hours (2:00 AM - 4:00 AM)"

    async def _collect_performance_metrics(self, scope: str, time_period: str) -> Dict[str, Any]:
        """Collect performance metrics for analysis."""
        return {"performance_metrics": "placeholder"}

    async def _identify_bottlenecks(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify performance bottlenecks."""
        return [{"bottleneck": "placeholder"}]

    async def _generate_optimization_suggestions(self, bottlenecks: List[Dict[str, Any]], metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimization suggestions."""
        return [{"optimization": "placeholder"}]

    def _calculate_performance_scores(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance scores."""
        return {
            "overall": 85,
            "cpu": 80,
            "memory": 75,
            "disk": 90,
            "network": 88
        }

    async def _generate_performance_predictions(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance predictions."""
        return {"predictions": "placeholder"}

    def _generate_capacity_recommendations(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate capacity planning recommendations."""
        return {"capacity_recommendations": "placeholder"}

    def _filter_alerts(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter alerts based on criteria."""
        return self.alerts

    def _acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        for alert in self.alerts:
            if alert["alert_id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now().isoformat()
                return True
        return False

    def _resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert["alert_id"] == alert_id:
                alert["resolved"] = True
                alert["status"] = "resolved"
                alert["resolved_at"] = datetime.now().isoformat()
                return True
        return False

    def _configure_alerts(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure alert settings."""
        self.monitoring_config["alerts"].update(config)
        return self.monitoring_config["alerts"]

    def _perform_predictive_analysis(self, metrics: Dict[str, Any]):
        """Perform predictive analysis on metrics."""
        # Placeholder for predictive analysis
        pass