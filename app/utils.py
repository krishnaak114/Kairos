"""
Utility functions for the Heartbeat Monitor.

Provides helper functions for file I/O, logging configuration,
and common operations.
"""

import json
import logging
from pathlib import Path
from typing import List, Any
from datetime import datetime


def setup_logging(level: str = "INFO", log_file: str = None) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        
    Example:
        >>> setup_logging(level="DEBUG", log_file="monitor.log")
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format=log_format,
        handlers=handlers
    )
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("pydantic").setLevel(logging.WARNING)


def load_events_from_file(file_path: str) -> List[dict]:
    """
    Load heartbeat events from JSON file.
    
    Args:
        file_path: Path to JSON file containing events
        
    Returns:
        List of event dictionaries
        
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
        
    Example:
        >>> events = load_events_from_file("data/events.json")
        >>> len(events)
        29
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Events file not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        events = json.load(f)
    
    if not isinstance(events, list):
        raise ValueError(f"Expected JSON array, got {type(events).__name__}")
    
    return events


def save_alerts_to_file(alerts: List[Any], output_path: str) -> None:
    """
    Save alerts to JSON file.
    
    Args:
        alerts: List of Alert objects
        output_path: Path where to save the JSON output
        
    Example:
        >>> save_alerts_to_file(result.alerts, "output/alerts.json")
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert Alert objects to dict
    alerts_data = [alert.model_dump(mode='json') for alert in alerts]
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(alerts_data, f, indent=2, default=str)


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "1.5s", "125ms")
        
    Example:
        >>> format_duration(0.125)
        '125.0ms'
        >>> format_duration(1.5)
        '1.5s'
    """
    if seconds < 1:
        return f"{seconds * 1000:.1f}ms"
    else:
        return f"{seconds:.1f}s"


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime in ISO 8601 format.
    
    Args:
        dt: Datetime object
        
    Returns:
        ISO 8601 formatted string
        
    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2025, 8, 4, 10, 0, 0)
        >>> format_timestamp(dt)
        '2025-08-04T10:00:00Z'
    """
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


def print_summary(result: Any) -> None:
    """
    Print a human-readable summary of monitoring results.
    
    Args:
        result: MonitorResult object
        
    Example:
        >>> print_summary(monitor_result)
        ===== Heartbeat Monitor Results =====
        Total Events: 29
        Valid Events: 26
        Invalid Events: 3
        Alerts Triggered: 1
        =====================================
    """
    print("\n" + "=" * 50)
    print("       Heartbeat Monitor Results")
    print("=" * 50)
    print(f"Total Events:     {result.validation.total_events}")
    print(f"Valid Events:     {result.validation.valid_events}")
    print(f"Invalid Events:   {result.validation.invalid_events}")
    print(f"Services:         {', '.join(result.services_monitored)}")
    print(f"Alerts Triggered: {len(result.alerts)}")
    print(f"Processing Time:  {format_duration(result.monitoring_duration_ms / 1000)}")
    print("=" * 50)
    
    if result.validation.invalid_events > 0:
        print("\nSkipped Events Breakdown:")
        for reason, count in result.validation.skipped_reasons.items():
            print(f"  - {reason}: {count}")
    
    if result.alerts:
        print(f"\n🚨 Alerts Detected ({len(result.alerts)}):")
        for idx, alert in enumerate(result.alerts, 1):
            print(f"\n  Alert #{idx}:")
            print(f"    Service:      {alert.service}")
            print(f"    Alert At:     {format_timestamp(alert.alert_at)}")
            print(f"    Missed Count: {alert.missed_count}")
            print(f"    Last Seen:    {format_timestamp(alert.last_seen)}")
    else:
        print("\n✅ No alerts detected - all services healthy!")
    
    print("\n" + "=" * 50 + "\n")
