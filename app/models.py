"""
Pydantic models for HeartbeatMonitor.

Type-safe data models with automatic validation following production best practices.
All models include comprehensive validation, examples, and error handling.
"""

from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class HeartbeatEvent(BaseModel):
    """
    Represents a single heartbeat event from a service.
    
    This model provides automatic validation for incoming events,
    gracefully rejecting malformed data without crashing the system.
    
    Attributes:
        service: Service name (e.g., 'email', 'sms', 'push')
        timestamp: ISO 8601 formatted timestamp in UTC
        
    Examples:
        >>> event = HeartbeatEvent(
        ...     service="email",
        ...     timestamp="2025-08-04T10:00:00Z"
        ... )
        >>> event.service
        'email'
    """
    
    service: str = Field(
        ...,
        description="Service identifier",
        min_length=1,
        max_length=100,
        pattern=r'^[a-zA-Z0-9_-]+$'
    )
    timestamp: datetime = Field(
        ...,
        description="Heartbeat timestamp in ISO 8601 format (UTC)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "service": "email",
                    "timestamp": "2025-08-04T10:00:00Z"
                }
            ]
        }
    )
    
    @field_validator('service', mode='before')
    @classmethod
    def validate_service(cls, v: str) -> str:
        """Ensure service name is not empty and properly formatted."""
        if not v or not v.strip():
            raise ValueError("Service name cannot be empty")
        return v.strip().lower()  # Normalize to lowercase


class Alert(BaseModel):
    """
    Represents an alert triggered by missed heartbeats.
    
    Attributes:
        service: Service that triggered the alert
        alert_at: Timestamp when the alert was triggered (after N consecutive misses)
        missed_count: Number of consecutive heartbeats missed
        last_seen: Timestamp of the last successful heartbeat
        
    Examples:
        >>> alert = Alert(
        ...     service="email",
        ...     alert_at="2025-08-04T10:05:00Z",
        ...     missed_count=3,
        ...     last_seen="2025-08-04T10:02:00Z"
        ... )
    """
    
    service: str = Field(..., description="Service identifier")
    alert_at: datetime = Field(..., description="Timestamp when alert was triggered")
    missed_count: int = Field(..., description="Number of consecutive misses", ge=1)
    last_seen: datetime = Field(..., description="Last successful heartbeat timestamp")
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "service": "email",
                    "alert_at": "2025-08-04T10:05:00Z",
                    "missed_count": 3,
                    "last_seen": "2025-08-04T10:02:00Z"
                }
            ]
        }
    )


class ValidationResult(BaseModel):
    """
    Results of event validation and filtering.
    
    Tracks statistics about processed events including valid, invalid,
    and malformed events for observability and debugging.
    
    Attributes:
        total_events: Total number of input events
        valid_events: Number of successfully validated events
        invalid_events: Number of events that failed validation
        errors: List of validation error messages
        skipped_reasons: Breakdown of why events were skipped
    """
    
    total_events: int = Field(..., description="Total input events", ge=0)
    valid_events: int = Field(..., description="Successfully validated events", ge=0)
    invalid_events: int = Field(..., description="Failed validation", ge=0)
    errors: List[str] = Field(
        default_factory=list,
        description="Validation error messages"
    )
    skipped_reasons: dict[str, int] = Field(
        default_factory=dict,
        description="Breakdown of skipped events by reason"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "total_events": 29,
                    "valid_events": 26,
                    "invalid_events": 3,
                    "errors": [
                        "Missing service field at index 13",
                        "Invalid timestamp 'not-a-real-timestamp' at index 12"
                    ],
                    "skipped_reasons": {
                        "missing_service": 1,
                        "missing_timestamp": 1,
                        "invalid_timestamp_format": 1
                    }
                }
            ]
        }
    )


class MonitorConfig(BaseModel):
    """
    Configuration for the HeartbeatMonitor.
    
    Controls monitoring behavior including intervals, thresholds,
    and operational parameters.
    
    Attributes:
        expected_interval_seconds: Expected time between heartbeats
        allowed_misses: Number of consecutive misses before alert
        tolerance_seconds: Grace period for late heartbeats (optional)
        timezone: Timezone for timestamp handling (default: UTC)
        
    Examples:
        >>> config = MonitorConfig(
        ...     expected_interval_seconds=60,
        ...     allowed_misses=3
        ... )
    """
    
    expected_interval_seconds: int = Field(
        ...,
        description="Expected interval between heartbeats",
        ge=1,
        le=86400  # Max 24 hours
    )
    allowed_misses: int = Field(
        ...,
        description="Consecutive misses before alert",
        ge=1,
        le=100
    )
    tolerance_seconds: int = Field(
        default=0,
        description="Grace period for late heartbeats",
        ge=0
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone for timestamp processing"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "expected_interval_seconds": 60,
                    "allowed_misses": 3,
                    "tolerance_seconds": 5,
                    "timezone": "UTC"
                }
            ]
        }
    )


class MonitorResult(BaseModel):
    """
    Complete result of monitoring operation.
    
    Combines validation results, detected alerts, and monitoring statistics
    for comprehensive reporting.
    
    Attributes:
        alerts: List of triggered alerts
        validation: Validation statistics
        services_monitored: List of unique services processed
        monitoring_duration_ms: Time taken to process (milliseconds)
        timestamp: When monitoring was performed
    """
    
    alerts: List[Alert] = Field(
        default_factory=list,
        description="Triggered alerts"
    )
    validation: ValidationResult = Field(
        ...,
        description="Validation results"
    )
    services_monitored: List[str] = Field(
        default_factory=list,
        description="Unique services processed"
    )
    monitoring_duration_ms: float = Field(
        ...,
        description="Processing time in milliseconds",
        ge=0
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Monitoring execution timestamp"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "alerts": [
                        {
                            "service": "push",
                            "alert_at": "2025-08-04T10:05:00Z",
                            "missed_count": 3,
                            "last_seen": "2025-08-04T10:02:00Z"
                        }
                    ],
                    "validation": {
                        "total_events": 29,
                        "valid_events": 26,
                        "invalid_events": 3,
                        "errors": [],
                        "skipped_reasons": {}
                    },
                    "services_monitored": ["email", "sms", "push"],
                    "monitoring_duration_ms": 12.5,
                    "timestamp": "2025-11-27T10:00:00Z"
                }
            ]
        }
    )


class HealthCheckResponse(BaseModel):
    """Health check response for monitoring the monitor (meta!)."""
    
    status: Literal["healthy", "degraded", "unhealthy"] = Field(
        ...,
        description="Service health status"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )
    version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    uptime_seconds: Optional[float] = Field(
        None,
        description="Service uptime in seconds"
    )
