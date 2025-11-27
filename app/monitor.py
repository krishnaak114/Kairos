"""
Core heartbeat monitoring engine.

Implements the main logic for detecting missed heartbeats and triggering alerts.
Designed for production use with comprehensive error handling, logging, and edge case coverage.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple
from collections import defaultdict
from pydantic import ValidationError

from app.models import (
    HeartbeatEvent,
    Alert,
    ValidationResult,
    MonitorConfig,
    MonitorResult
)

logger = logging.getLogger(__name__)


class HeartbeatMonitor:
    """
    Production-grade heartbeat monitoring system.
    
    Tracks service heartbeats and detects when services miss consecutive heartbeats,
    triggering alerts when thresholds are exceeded.
    
    Features:
        - Graceful handling of malformed data
        - Support for unordered events
        - Comprehensive validation and error reporting
        - Configurable intervals and thresholds
        - Per-service independent tracking
        - Production-ready logging and metrics
        
    Example:
        >>> config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        >>> monitor = HeartbeatMonitor(config)
        >>> events = load_events("events.json")
        >>> result = monitor.detect_alerts(events)
        >>> print(f"Detected {len(result.alerts)} alerts")
    """
    
    def __init__(self, config: MonitorConfig):
        """
        Initialize the monitor with configuration.
        
        Args:
            config: MonitorConfig object with interval and threshold settings
        """
        self.config = config
        self.interval = timedelta(seconds=config.expected_interval_seconds)
        self.tolerance = timedelta(seconds=config.tolerance_seconds)
        logger.info(
            f"Initialized HeartbeatMonitor: "
            f"interval={config.expected_interval_seconds}s, "
            f"allowed_misses={config.allowed_misses}, "
            f"tolerance={config.tolerance_seconds}s"
        )
    
    def detect_alerts(self, raw_events: List[dict]) -> MonitorResult:
        """
        Main entry point for alert detection.
        
        Processes raw event data, validates, sorts, and detects missed heartbeats
        for each service independently.
        
        Args:
            raw_events: List of raw event dictionaries from JSON
            
        Returns:
            MonitorResult containing alerts, validation stats, and metadata
            
        Example:
            >>> events = [
            ...     {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            ...     {"service": "email", "timestamp": "2025-08-04T10:01:00Z"}
            ... ]
            >>> result = monitor.detect_alerts(events)
        """
        start_time = datetime.now(timezone.utc)
        logger.info(f"Starting alert detection for {len(raw_events)} events")
        
        # Step 1: Validate and filter events
        valid_events, validation_result = self._validate_events(raw_events)
        logger.info(
            f"Validation complete: {validation_result.valid_events} valid, "
            f"{validation_result.invalid_events} invalid"
        )
        
        # Step 2: Group events by service
        services_map = self._group_by_service(valid_events)
        logger.info(f"Grouped into {len(services_map)} services: {list(services_map.keys())}")
        
        # Step 3: Detect alerts per service
        all_alerts: List[Alert] = []
        for service, events in services_map.items():
            service_alerts = self._detect_service_alerts(service, events)
            all_alerts.extend(service_alerts)
            if service_alerts:
                logger.warning(
                    f"Service '{service}' triggered {len(service_alerts)} alert(s)"
                )
        
        # Step 4: Build result
        end_time = datetime.now(timezone.utc)
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        result = MonitorResult(
            alerts=all_alerts,
            validation=validation_result,
            services_monitored=list(services_map.keys()),
            monitoring_duration_ms=duration_ms,
            timestamp=end_time
        )
        
        logger.info(
            f"Alert detection complete: {len(all_alerts)} alert(s) in {duration_ms:.2f}ms"
        )
        return result
    
    def _validate_events(self, raw_events: List[dict]) -> Tuple[List[HeartbeatEvent], ValidationResult]:
        """
        Validate and filter events, tracking all validation errors.
        
        Gracefully handles malformed events without crashing:
        - Missing service field
        - Missing timestamp field
        - Invalid timestamp format
        - Empty/null values
        
        Args:
            raw_events: Raw event dictionaries
            
        Returns:
            Tuple of (valid_events, validation_result)
        """
        valid_events: List[HeartbeatEvent] = []
        errors: List[str] = []
        skipped_reasons: Dict[str, int] = defaultdict(int)
        
        for idx, raw_event in enumerate(raw_events):
            try:
                # Pydantic will automatically validate
                event = HeartbeatEvent(**raw_event)
                valid_events.append(event)
            except ValidationError as e:
                # Parse validation error to categorize the issue
                reason = self._categorize_validation_error(e, raw_event)
                skipped_reasons[reason] += 1
                error_msg = f"Event {idx}: {reason} - {str(e.errors()[0]['msg'])}"
                errors.append(error_msg)
                logger.debug(f"Skipped event {idx}: {reason}")
            except Exception as e:
                # Catch any unexpected errors
                reason = "unexpected_error"
                skipped_reasons[reason] += 1
                error_msg = f"Event {idx}: Unexpected error - {str(e)}"
                errors.append(error_msg)
                logger.error(f"Unexpected error validating event {idx}: {e}")
        
        validation_result = ValidationResult(
            total_events=len(raw_events),
            valid_events=len(valid_events),
            invalid_events=len(raw_events) - len(valid_events),
            errors=errors,
            skipped_reasons=dict(skipped_reasons)
        )
        
        return valid_events, validation_result
    
    def _categorize_validation_error(self, error: ValidationError, raw_event: dict) -> str:
        """
        Categorize validation error for better observability.
        
        Args:
            error: Pydantic validation error
            raw_event: The raw event that failed
            
        Returns:
            Category string (e.g., 'missing_service', 'invalid_timestamp_format')
        """
        error_details = error.errors()[0]
        field = error_details.get('loc', ['unknown'])[0]
        error_type = error_details.get('type', '')
        
        # Check if field is missing
        if 'service' not in raw_event:
            return 'missing_service'
        if 'timestamp' not in raw_event:
            return 'missing_timestamp'
        
        # Check for null/empty values
        if raw_event.get('service') in [None, '']:
            return 'empty_service'
        if raw_event.get('timestamp') in [None, '']:
            return 'empty_timestamp'
        
        # Check for format issues
        if 'timestamp' in str(field) or 'datetime' in error_type:
            return 'invalid_timestamp_format'
        if 'service' in str(field):
            return 'invalid_service_format'
        
        return 'validation_error'
    
    def _group_by_service(self, events: List[HeartbeatEvent]) -> Dict[str, List[HeartbeatEvent]]:
        """
        Group validated events by service name.
        
        Args:
            events: List of validated HeartbeatEvent objects
            
        Returns:
            Dictionary mapping service names to their events
        """
        services: Dict[str, List[HeartbeatEvent]] = defaultdict(list)
        for event in events:
            services[event.service].append(event)
        return dict(services)
    
    def _detect_service_alerts(self, service: str, events: List[HeartbeatEvent]) -> List[Alert]:
        """
        Detect alerts for a single service.
        
        Algorithm:
        1. Sort events chronologically
        2. Track expected next heartbeat time
        3. Count consecutive misses
        4. Trigger alert when threshold reached
        5. Reset count on successful heartbeat
        
        Args:
            service: Service name
            events: List of heartbeat events for this service
            
        Returns:
            List of Alert objects (may be empty)
        """
        if not events:
            return []
        
        # Sort events chronologically
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        logger.debug(f"Processing {len(sorted_events)} events for service '{service}'")
        
        alerts: List[Alert] = []
        
        # Start tracking from first heartbeat
        last_heartbeat_time = sorted_events[0].timestamp
        consecutive_misses = 0
        
        # Process each subsequent heartbeat
        for current_event in sorted_events[1:]:
            expected_time = last_heartbeat_time + self.interval
            current_time = current_event.timestamp
            
            # Check if we've passed one or more expected heartbeat windows
            while expected_time + self.tolerance < current_time:
                # We missed an expected heartbeat
                consecutive_misses += 1
                logger.debug(
                    f"Service '{service}' missed heartbeat at {expected_time} "
                    f"(miss #{consecutive_misses})"
                )
                
                # Check if we've reached the alert threshold
                if consecutive_misses >= self.config.allowed_misses:
                    alert = Alert(
                        service=service,
                        alert_at=expected_time,
                        missed_count=consecutive_misses,
                        last_seen=last_heartbeat_time
                    )
                    alerts.append(alert)
                    logger.warning(
                        f"ALERT: Service '{service}' missed {consecutive_misses} "
                        f"consecutive heartbeats at {expected_time}"
                    )
                    
                    # Reset after alert (start tracking from this miss point)
                    consecutive_misses = 0
                    last_heartbeat_time = expected_time
                
                # Move to next expected window
                expected_time += self.interval
            
            # Heartbeat received - reset consecutive misses
            if consecutive_misses > 0:
                logger.debug(
                    f"Service '{service}' recovered after {consecutive_misses} miss(es)"
                )
            consecutive_misses = 0
            last_heartbeat_time = current_time
        
        # Check for trailing misses after the last heartbeat
        # Note: This is optional - depends on whether you want to alert
        # on ongoing outages or only completed outage windows
        # Commented out as per typical requirements, but available if needed
        
        return alerts
