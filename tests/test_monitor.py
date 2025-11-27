"""
Comprehensive test suite for HeartbeatMonitor.

Tests all required cases plus additional edge cases for production readiness:
1. Working alert case
2. Near-miss case (no alert)
3. Unordered input
4. Malformed events
5. Multiple services
6. Edge cases (empty input, single event, etc.)
"""

import pytest
from datetime import datetime
from app.models import MonitorConfig
from app.monitor import HeartbeatMonitor


class TestRequiredCases:
    """Required test cases from the assignment."""
    
    def test_alert_triggered(self):
        """
        Test Case 1: Working alert case.
        
        Service sends heartbeats at 10:00, 10:01, then nothing until 10:05.
        Expected: Alert at 10:05 (after missing 10:02, 10:03, 10:04)
        """
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            # Misses at 10:02, 10:03, 10:04
            {"service": "email", "timestamp": "2025-08-04T10:05:00Z"}
        ]
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        # Assertions
        assert result.validation.valid_events == 3
        assert result.validation.invalid_events == 0
        assert len(result.alerts) == 1
        
        alert = result.alerts[0]
        assert alert.service == "email"
        assert alert.missed_count == 3
        # Alert triggered at the 3rd miss (10:04), not when recovery arrives (10:05)
        assert alert.alert_at == datetime.fromisoformat("2025-08-04T10:04:00+00:00")
        assert alert.last_seen == datetime.fromisoformat("2025-08-04T10:01:00+00:00")
    
    def test_near_miss_no_alert(self):
        """
        Test Case 2: Near-miss case (only 2 misses, no alert).
        
        Service sends heartbeats at 10:00, 10:01, then recovers at 10:04.
        Expected: No alert (only missed 10:02 and 10:03 = 2 misses)
        """
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            # Misses at 10:02, 10:03 (only 2)
            {"service": "email", "timestamp": "2025-08-04T10:04:00Z"}
        ]
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        # Assertions
        assert result.validation.valid_events == 3
        assert len(result.alerts) == 0  # No alert - only 2 misses
    
    def test_unordered_input(self):
        """
        Test Case 3: Unordered input.
        
        Events arrive out of chronological order but should still
        trigger alert after sorting.
        """
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:05:00Z"},  # Out of order
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:10:00Z"},  # Another one
        ]
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        # Should still detect the alert after sorting
        assert result.validation.valid_events == 4
        assert len(result.alerts) == 2  # Two separate alert periods
    
    def test_malformed_events(self):
        """
        Test Case 4: Malformed events.
        
        System should gracefully skip events with:
        - Missing service field
        - Missing timestamp field
        - Invalid timestamp format
        - Empty/null values
        """
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},  # Valid
            {"service": "email"},  # Missing timestamp
            {"timestamp": "2025-08-04T10:01:00Z"},  # Missing service
            {"service": "email", "timestamp": "not-a-real-timestamp"},  # Invalid format
            {"service": "", "timestamp": "2025-08-04T10:02:00Z"},  # Empty service
            {"service": "email", "timestamp": "2025-08-04T10:03:00Z"},  # Valid
        ]
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        
        # Should not crash
        result = monitor.detect_alerts(events)
        
        # Assertions
        assert result.validation.total_events == 6
        assert result.validation.valid_events == 2  # Only 2 valid events
        assert result.validation.invalid_events == 4
        assert len(result.validation.errors) == 4
        
        # Check skipped reasons are tracked
        assert result.validation.skipped_reasons["missing_timestamp"] == 1
        assert result.validation.skipped_reasons["missing_service"] == 1
        assert result.validation.skipped_reasons["invalid_timestamp_format"] == 1
        assert result.validation.skipped_reasons["empty_service"] == 1


class TestMultipleServices:
    """Test scenarios with multiple services."""
    
    def test_multiple_services_independent_tracking(self):
        """
        Each service should be tracked independently.
        
        email: triggers alert
        sms: no alert (healthy)
        push: triggers alert
        """
        events = [
            # Email: will trigger alert
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:05:00Z"},  # 3 misses
            
            # SMS: healthy (no alert)
            {"service": "sms", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "sms", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "sms", "timestamp": "2025-08-04T10:02:00Z"},
            {"service": "sms", "timestamp": "2025-08-04T10:03:00Z"},
            
            # Push: will trigger alert
            {"service": "push", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "push", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "push", "timestamp": "2025-08-04T10:05:00Z"},  # 3 misses
        ]
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        # Assertions
        assert len(result.services_monitored) == 3
        assert set(result.services_monitored) == {"email", "sms", "push"}
        assert len(result.alerts) == 2  # Only email and push trigger alerts
        
        alert_services = {alert.service for alert in result.alerts}
        assert alert_services == {"email", "push"}


class TestEdgeCases:
    """Additional edge cases for production readiness."""
    
    def test_empty_input(self):
        """Handle empty event list without crashing."""
        events = []
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        assert result.validation.total_events == 0
        assert result.validation.valid_events == 0
        assert len(result.alerts) == 0
    
    def test_single_event(self):
        """Single event should not trigger alert."""
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"}
        ]
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        assert result.validation.valid_events == 1
        assert len(result.alerts) == 0
    
    def test_exact_threshold(self):
        """Test exactly at threshold (3 misses)."""
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:05:00Z"},  # Exactly 3 misses
        ]
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        assert len(result.alerts) == 1
        assert result.alerts[0].missed_count == 3
    
    def test_recovery_after_alert(self):
        """Service can recover after triggering an alert."""
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:05:00Z"},  # Alert here
            {"service": "email", "timestamp": "2025-08-04T10:06:00Z"},  # Recovery
            {"service": "email", "timestamp": "2025-08-04T10:07:00Z"},
        ]
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        assert len(result.alerts) == 1  # Only one alert, then recovery
    
    def test_multiple_alert_periods(self):
        """Service can trigger multiple alerts in different time windows."""
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:05:00Z"},  # First alert
            {"service": "email", "timestamp": "2025-08-04T10:06:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:10:00Z"},  # Second alert
        ]
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        assert len(result.alerts) == 2  # Two separate alert periods
    
    def test_different_intervals(self):
        """Test with different interval configurations."""
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:05:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:25:00Z"},  # 4 intervals of 5min
        ]
        
        # 5-minute intervals
        config = MonitorConfig(expected_interval_seconds=300, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        assert len(result.alerts) == 1
    
    def test_case_insensitive_service_names(self):
        """Service names should be normalized to lowercase."""
        events = [
            {"service": "EMAIL", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "Email", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:05:00Z"},
        ]
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        # All should be treated as the same service
        assert len(result.services_monitored) == 1
        assert result.services_monitored[0] == "email"
        assert len(result.alerts) == 1


class TestRealWorldData:
    """Test with the actual provided dataset."""
    
    def test_provided_dataset(self):
        """
        Test with the actual provided events.json data.
        
        Based on manual analysis:
        - email: 10:00, 10:01, 10:02, [miss 10:03, 10:04, 10:05], 10:06, 10:07...
        - sms: healthy with few gaps
        - push: 10:00, 10:01, 10:02, [miss 10:03, 10:04, 10:05], 10:06...
        """
        import json
        from pathlib import Path
        
        # Load the actual data file
        data_file = Path(__file__).parent.parent / "data" / "events.json"
        with open(data_file) as f:
            events = json.load(f)
        
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=3)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        # Validation checks
        assert result.validation.total_events == 29
        assert result.validation.valid_events == 26  # 3 malformed events
        assert result.validation.invalid_events == 3
        
        # Alert checks (based on manual analysis of the data)
        assert len(result.alerts) >= 1  # At least push service should alert
        
        # Check that malformed events were properly categorized
        assert "missing_timestamp" in result.validation.skipped_reasons
        assert "missing_service" in result.validation.skipped_reasons
        assert "invalid_timestamp_format" in result.validation.skipped_reasons


class TestConfiguration:
    """Test different configuration scenarios."""
    
    def test_different_allowed_misses(self):
        """Test with different allowed_misses thresholds."""
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:05:00Z"},  # 3 misses
        ]
        
        # Test with allowed_misses=2 (should alert)
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=2)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        assert len(result.alerts) == 1
        
        # Test with allowed_misses=4 (should not alert)
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=4)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        assert len(result.alerts) == 0
    
    def test_tolerance_window(self):
        """Test tolerance window for late heartbeats."""
        events = [
            {"service": "email", "timestamp": "2025-08-04T10:00:00Z"},
            {"service": "email", "timestamp": "2025-08-04T10:01:05Z"},  # 5 seconds late
            {"service": "email", "timestamp": "2025-08-04T10:02:05Z"},
        ]
        
        # With tolerance: should not trigger alerts
        config = MonitorConfig(expected_interval_seconds=60, allowed_misses=1, tolerance_seconds=10)
        monitor = HeartbeatMonitor(config)
        result = monitor.detect_alerts(events)
        
        # With tolerance, late heartbeats should be accepted
        assert len(result.alerts) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
