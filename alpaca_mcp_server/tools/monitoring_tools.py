"""Monitoring Tools - MCP tools for hybrid trading service control

Provides MCP tool interface for Claude to control and interact with 
the genuine automated monitoring service.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
import os

from ..monitoring.hybrid_service import HybridTradingService, ServiceConfig, get_service_instance, set_service_instance
from ..monitoring.alert_system import test_alert_system


# Global service instance management
_service_instance: Optional[HybridTradingService] = None


async def start_hybrid_monitoring(
    check_interval: int = 2,
    signal_confidence_threshold: float = 0.75,
    max_concurrent_positions: int = 5,
    watchlist_size_limit: int = 20,
    enable_auto_alerts: bool = True,
    alert_channels: List[str] = None
) -> Dict:
    """
    Start the hybrid trading monitoring service.
    
    This tool starts genuine automated monitoring that runs independently
    of Claude, providing verifiable position tracking and signal detection.
    
    Args:
        check_interval: Seconds between monitoring cycles (default: 2)
        signal_confidence_threshold: Minimum confidence for signals (default: 0.75)
        max_concurrent_positions: Maximum positions to track (default: 5)
        watchlist_size_limit: Maximum watchlist size (default: 20)
        enable_auto_alerts: Enable automatic alerting (default: True)
        alert_channels: Alert channels ["file", "console", "desktop", "discord"]
    
    Returns:
        Service startup status and configuration
    """
    global _service_instance
    
    try:
        # Check if service is already running
        if _service_instance and _service_instance.active:
            return {
                "status": "error",
                "message": "Hybrid monitoring service is already active",
                "current_status": await _service_instance.get_status()
            }
        
        # Create service configuration
        config = ServiceConfig(
            check_interval=check_interval,
            signal_confidence_threshold=signal_confidence_threshold,
            max_concurrent_positions=max_concurrent_positions,
            watchlist_size_limit=watchlist_size_limit,
            enable_auto_alerts=enable_auto_alerts,
            alert_channels=alert_channels or ["file", "console"]
        )
        
        # Create and start service
        _service_instance = HybridTradingService(config)
        set_service_instance(_service_instance)
        
        result = await _service_instance.start_service()
        
        if result.get("status") == "success":
            # Test alert system
            await test_alert_system(_service_instance.alert_system)
            
            return {
                "status": "success",
                "message": "🚀 Hybrid monitoring service started successfully",
                "service_config": {
                    "check_interval": f"{check_interval} seconds",
                    "signal_threshold": f"{signal_confidence_threshold:.1%}",
                    "max_positions": max_concurrent_positions,
                    "watchlist_limit": watchlist_size_limit,
                    "alert_channels": config.alert_channels
                },
                "monitoring_info": {
                    "state_file": result.get("state_file"),
                    "log_file": "hybrid_monitoring.log",
                    "alerts_directory": "monitoring_data/alerts/"
                },
                "next_steps": [
                    "Add symbols to watchlist: add_symbols_to_watchlist(['AAPL', 'MSFT'])",
                    "Check status: get_hybrid_monitoring_status()",
                    "View signals: get_current_trading_signals()"
                ]
            }
        else:
            return result
            
    except Exception as e:
        logging.error(f"Error starting hybrid monitoring: {e}")
        return {
            "status": "error",
            "message": f"Failed to start monitoring service: {e}"
        }


async def stop_hybrid_monitoring() -> Dict:
    """
    Stop the hybrid trading monitoring service.
    
    Gracefully shuts down the monitoring service, saving state and
    sending final alerts.
    
    Returns:
        Service shutdown status and final statistics
    """
    global _service_instance
    
    try:
        if not _service_instance or not _service_instance.active:
            return {
                "status": "error",
                "message": "No active monitoring service to stop"
            }
        
        result = await _service_instance.stop_service()
        
        if result.get("status") == "success":
            return {
                "status": "success",
                "message": "🛑 Hybrid monitoring service stopped successfully",
                "final_statistics": {
                    "uptime_seconds": result.get("uptime_seconds", 0),
                    "total_checks": result.get("final_check_count", 0),
                    "total_errors": result.get("final_error_count", 0)
                }
            }
        else:
            return result
            
    except Exception as e:
        logging.error(f"Error stopping hybrid monitoring: {e}")
        return {
            "status": "error",
            "message": f"Failed to stop monitoring service: {e}"
        }


async def get_hybrid_monitoring_status() -> Dict:
    """
    Get current status of the hybrid monitoring service.
    
    Provides comprehensive status information including uptime,
    monitoring statistics, and current watchlist.
    
    Returns:
        Detailed service status information
    """
    global _service_instance
    
    try:
        if not _service_instance:
            return {
                "status": "inactive",
                "message": "No monitoring service instance found",
                "service_available": False
            }
        
        status = await _service_instance.get_status()
        
        # Get component statuses
        position_status = None
        signal_status = None
        alert_status = None
        
        if _service_instance.position_tracker:
            position_status = _service_instance.position_tracker.get_status()
        
        if _service_instance.signal_detector:
            signal_status = _service_instance.signal_detector.get_status()
        
        if _service_instance.alert_system:
            alert_status = _service_instance.alert_system.get_status()
        
        return {
            "status": "active" if status.active else "inactive",
            "service_status": {
                "active": status.active,
                "start_time": status.start_time.isoformat() if status.start_time else None,
                "last_check": status.last_check.isoformat() if status.last_check else None,
                "uptime_seconds": status.uptime_seconds,
                "check_count": status.check_count,
                "error_count": status.error_count
            },
            "monitoring_statistics": {
                "watchlist_size": status.watchlist_size,
                "active_positions": status.active_positions,
                "signals_detected_today": status.signals_detected_today
            },
            "component_status": {
                "position_tracker": position_status,
                "signal_detector": signal_status,
                "alert_system": alert_status
            },
            "current_watchlist": sorted(list(_service_instance.watchlist)) if _service_instance.watchlist else []
        }
        
    except Exception as e:
        logging.error(f"Error getting hybrid monitoring status: {e}")
        return {
            "status": "error",
            "message": f"Failed to get service status: {e}"
        }


async def verify_monitoring_active() -> Dict:
    """
    Verify that monitoring is actually running and provide proof.
    
    This tool provides verifiable evidence that genuine monitoring
    is taking place, addressing trust issues from manual monitoring.
    
    Returns:
        Verification data proving monitoring is active
    """
    global _service_instance
    
    try:
        if not _service_instance or not _service_instance.active:
            return {
                "monitoring_active": False,
                "verification_status": "FAILED",
                "message": "No active monitoring service detected",
                "proof": None
            }
        
        status = await _service_instance.get_status()
        
        # Gather proof of monitoring activity
        proof = {
            "service_running": status.active,
            "last_heartbeat": status.last_check.isoformat() if status.last_check else None,
            "total_monitoring_cycles": status.check_count,
            "uptime_seconds": status.uptime_seconds,
            "error_count": status.error_count,
            "watchlist_monitored": status.watchlist_size,
            "positions_tracked": status.active_positions,
            "log_file_exists": os.path.exists("hybrid_monitoring.log"),
            "state_file_exists": os.path.exists("monitoring_data/hybrid_service_state.json")
        }
        
        # Calculate monitoring health score
        health_score = 100
        if status.error_count > 0:
            health_score -= min(50, status.error_count * 5)  # -5 points per error, max -50
        
        if status.check_count == 0:
            health_score = 0
        
        verification_status = "VERIFIED" if health_score > 80 else "DEGRADED" if health_score > 50 else "POOR"
        
        return {
            "monitoring_active": True,
            "verification_status": verification_status,
            "health_score": health_score,
            "message": f"Monitoring verified: {status.check_count} cycles completed",
            "proof": proof,
            "recent_activity": {
                "signals_detected": status.signals_detected_today,
                "last_check_ago_seconds": (status.uptime_seconds - (status.last_check.timestamp() - status.start_time.timestamp())) if status.last_check and status.start_time else None
            }
        }
        
    except Exception as e:
        logging.error(f"Error verifying monitoring: {e}")
        return {
            "monitoring_active": False,
            "verification_status": "ERROR",
            "message": f"Verification failed: {e}",
            "proof": None
        }


async def add_symbols_to_watchlist(symbols: List[str]) -> Dict:
    """
    Add symbols to the monitoring watchlist.
    
    Args:
        symbols: List of stock symbols to add to monitoring
    
    Returns:
        Status of watchlist update
    """
    global _service_instance
    
    try:
        if not _service_instance or not _service_instance.active:
            return {
                "status": "error",
                "message": "No active monitoring service. Start monitoring first."
            }
        
        # Validate symbols
        clean_symbols = [symbol.upper().strip() for symbol in symbols if symbol.strip()]
        
        if not clean_symbols:
            return {
                "status": "error",
                "message": "No valid symbols provided"
            }
        
        result = await _service_instance.add_to_watchlist(clean_symbols)
        
        return {
            "status": result["status"],
            "message": f"Watchlist updated successfully" if result["status"] == "success" else result.get("message"),
            "added_symbols": result.get("added", []),
            "watchlist_size": result.get("watchlist_size", 0),
            "current_watchlist": result.get("current_watchlist", [])
        }
        
    except Exception as e:
        logging.error(f"Error adding symbols to watchlist: {e}")
        return {
            "status": "error",
            "message": f"Failed to add symbols: {e}"
        }


async def remove_symbols_from_watchlist(symbols: List[str]) -> Dict:
    """
    Remove symbols from the monitoring watchlist.
    
    Args:
        symbols: List of stock symbols to remove from monitoring
    
    Returns:
        Status of watchlist update
    """
    global _service_instance
    
    try:
        if not _service_instance or not _service_instance.active:
            return {
                "status": "error",
                "message": "No active monitoring service"
            }
        
        clean_symbols = [symbol.upper().strip() for symbol in symbols if symbol.strip()]
        
        if not clean_symbols:
            return {
                "status": "error",
                "message": "No valid symbols provided"
            }
        
        result = await _service_instance.remove_from_watchlist(clean_symbols)
        
        return {
            "status": result["status"],
            "message": "Watchlist updated successfully" if result["status"] == "success" else result.get("message"),
            "removed_symbols": result.get("removed", []),
            "watchlist_size": result.get("watchlist_size", 0),
            "current_watchlist": result.get("current_watchlist", [])
        }
        
    except Exception as e:
        logging.error(f"Error removing symbols from watchlist: {e}")
        return {
            "status": "error",
            "message": f"Failed to remove symbols: {e}"
        }


async def get_current_watchlist() -> Dict:
    """
    Get the current monitoring watchlist.
    
    Returns:
        Current watchlist and monitoring details
    """
    global _service_instance
    
    try:
        if not _service_instance:
            return {
                "status": "error",
                "message": "No monitoring service instance",
                "watchlist": []
            }
        
        watchlist = sorted(list(_service_instance.watchlist))
        
        return {
            "status": "success",
            "watchlist_size": len(watchlist),
            "watchlist": watchlist,
            "monitoring_active": _service_instance.active,
            "last_scan": _service_instance.signal_detector.last_scan.isoformat() if _service_instance.signal_detector and _service_instance.signal_detector.last_scan else None
        }
        
    except Exception as e:
        logging.error(f"Error getting watchlist: {e}")
        return {
            "status": "error",
            "message": f"Failed to get watchlist: {e}",
            "watchlist": []
        }


async def get_current_trading_signals() -> Dict:
    """
    Get current trading signals detected by the monitoring service.
    
    Returns:
        List of current trading signals with confidence scores
    """
    global _service_instance
    
    try:
        if not _service_instance or not _service_instance.active:
            return {
                "status": "error",
                "message": "No active monitoring service",
                "signals": []
            }
        
        signals = await _service_instance.get_current_signals()
        
        # Group signals by type for better organization
        signal_summary = {
            "fresh_trough": [],
            "fresh_peak": [],
            "other": []
        }
        
        for signal in signals:
            signal_type = signal.get("signal_type", "other")
            if signal_type in signal_summary:
                signal_summary[signal_type].append(signal)
            else:
                signal_summary["other"].append(signal)
        
        return {
            "status": "success",
            "total_signals": len(signals),
            "signals_by_type": {
                "buy_signals": len(signal_summary["fresh_trough"]),
                "sell_signals": len(signal_summary["fresh_peak"]),
                "other_signals": len(signal_summary["other"])
            },
            "all_signals": signals,
            "high_confidence_signals": [s for s in signals if s.get("confidence", 0) >= 0.8],
            "signal_summary": signal_summary
        }
        
    except Exception as e:
        logging.error(f"Error getting trading signals: {e}")
        return {
            "status": "error",
            "message": f"Failed to get signals: {e}",
            "signals": []
        }


async def get_monitoring_alerts(count: int = 10) -> Dict:
    """
    Get recent monitoring alerts.
    
    Args:
        count: Number of recent alerts to retrieve (default: 10)
    
    Returns:
        Recent alerts from the monitoring system
    """
    global _service_instance
    
    try:
        if not _service_instance or not _service_instance.alert_system:
            return {
                "status": "error",
                "message": "No active alert system",
                "alerts": []
            }
        
        recent_alerts = _service_instance.alert_system.get_recent_alerts(count)
        alert_status = _service_instance.alert_system.get_status()
        
        return {
            "status": "success",
            "alert_count": len(recent_alerts),
            "alerts_sent_today": alert_status["alerts_sent_today"],
            "active_channels": alert_status["active_channels"],
            "recent_alerts": recent_alerts
        }
        
    except Exception as e:
        logging.error(f"Error getting monitoring alerts: {e}")
        return {
            "status": "error",
            "message": f"Failed to get alerts: {e}",
            "alerts": []
        }