"""
tests/unit/test_timestamp_alignment.py
Unit tests for TimestampSynchronizer.
"""
import time
import pytest

from backend.core.timestamp_sync import TimestampSynchronizer


class TestTimestampSynchronizer:

    def test_get_unified_timestamp_is_recent(self):
        sync = TimestampSynchronizer()
        now_us = int(time.time() * 1_000_000)
        ts = sync.get_unified_timestamp()
        # Should be within 1 second of wall clock
        assert abs(ts - now_us) < 1_000_000, f"Timestamp drift too large: {abs(ts - now_us)} µs"

    def test_sync_known_component(self):
        sync = TimestampSynchronizer()
        base = sync.get_unified_timestamp()
        adjusted = sync.sync_component("turbopuffer", base - 50_000)
        assert isinstance(adjusted, int)
        assert adjusted > 0

    def test_sync_unknown_component_passthrough(self):
        sync = TimestampSynchronizer()
        ts = int(time.time() * 1_000_000)
        result = sync.sync_component("nonexistent_component", ts)
        assert result == ts, "Unknown components should be passed through unchanged"

    def test_validate_consistency_returns_dict(self):
        sync = TimestampSynchronizer()
        report = sync.validate_consistency()
        assert "is_consistent" in report
        assert "max_discrepancy_ms" in report
        assert "threshold_ms" in report
        assert isinstance(report["is_consistent"], bool)

    def test_fresh_sync_is_consistent(self):
        """A freshly initialised synchroniser should report consistency."""
        sync = TimestampSynchronizer()
        report = sync.validate_consistency()
        assert report["is_consistent"] is True

    def test_drift_detection_too_soon(self):
        """drift detection should return None if called immediately."""
        sync = TimestampSynchronizer()
        report = sync.detect_drift("frame_processor")
        # sync_interval is 10 s; called immediately → should be None
        assert report is None

    def test_correct_drift_modifies_offset(self):
        sync = TimestampSynchronizer()
        sync.sync_component("twelve_labs", sync.get_unified_timestamp() - 200_000)
        before = sync.component_offsets["twelve_labs"]
        sync.correct_drift("twelve_labs", 50_000)
        after = sync.component_offsets["twelve_labs"]
        assert after == before - 50_000

    def test_get_sync_status_all_components(self):
        sync = TimestampSynchronizer()
        status = sync.get_sync_status()
        assert "unified_time_us" in status
        assert "components" in status
        for comp in ["frame_processor", "twelve_labs", "turbopuffer"]:
            assert comp in status["components"]
