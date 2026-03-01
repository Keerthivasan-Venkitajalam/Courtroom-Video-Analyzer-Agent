"""
timestamp_sync.py
Timestamp synchronisation across video, transcript, and processor timecodes.
Implements shared epoch offset and exponential-moving-average drift correction.
"""
import time
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass

from backend.core.logging_config import get_logger
from backend.core.constants import EPOCH_OFFSET_US, get_unified_timestamp_us

logger = get_logger(__name__)


@dataclass
class ComponentTimestamp:
    """Timestamp recorded by a specific component."""
    component: str
    timestamp_us: int
    local_time_us: int  # Wall-clock time when this was recorded


@dataclass
class DriftReport:
    """Clock-drift report for a single component."""
    component: str
    drift_us: int
    drift_rate_us_per_sec: float
    last_sync_us: int
    needs_correction: bool


class TimestampSynchronizer:
    """
    Manages timestamp synchronisation across all system components:
    - Vision Agent's local frame processor
    - Twelve Labs index
    - TurboPuffer text timestamps

    Ensures all timestamps align within 100 ms accuracy.
    """

    # Threshold below which drift correction is not needed
    DRIFT_THRESHOLD_US: int = 100_000   # 100 ms in µs
    MAX_DRIFT_HISTORY: int = 100

    def __init__(self) -> None:
        self.component_offsets: Dict[str, int] = {}
        self.last_sync_times: Dict[str, int] = {}
        self.drift_history: Dict[str, List[Tuple[int, int]]] = {}
        self.sync_interval_us: int = 10_000_000  # 10 seconds

        self.components: List[str] = ["frame_processor", "twelve_labs", "turbopuffer"]

        for component in self.components:
            self.component_offsets[component] = 0
            self.last_sync_times[component] = get_unified_timestamp_us()
            self.drift_history[component] = []

        logger.info(
            "TimestampSynchronizer initialised | epoch_offset=%dµs | sync_interval=%.1fs | target=±100ms",
            EPOCH_OFFSET_US,
            self.sync_interval_us / 1_000_000,
        )

    def get_unified_timestamp(self) -> int:
        """Return the current unified timestamp in microseconds."""
        return get_unified_timestamp_us()

    def sync_component(self, component: str, component_timestamp_us: int) -> int:
        """
        Synchronise a component timestamp with the unified clock.

        Args:
            component: One of 'frame_processor', 'twelve_labs', 'turbopuffer'.
            component_timestamp_us: Raw timestamp from the component (µs).

        Returns:
            Adjusted timestamp aligned with the unified clock.
        """
        if component not in self.components:
            logger.warning("sync_component: unknown component '%s'", component)
            return component_timestamp_us

        unified_time = self.get_unified_timestamp()
        offset = unified_time - component_timestamp_us

        # Exponential moving average for offset smoothing (α = 0.3)
        alpha = 0.3
        if self.component_offsets[component] == 0:
            self.component_offsets[component] = offset
        else:
            self.component_offsets[component] = int(
                alpha * offset + (1 - alpha) * self.component_offsets[component]
            )

        self.last_sync_times[component] = unified_time
        return component_timestamp_us + self.component_offsets[component]

    def detect_drift(self, component: str) -> Optional[DriftReport]:
        """
        Detect clock drift for a specific component.

        Returns a DriftReport if enough time has elapsed since the last sync,
        otherwise returns None.
        """
        if component not in self.components:
            return None

        current_time = self.get_unified_timestamp()
        last_sync = self.last_sync_times[component]

        if (current_time - last_sync) < self.sync_interval_us:
            return None  # Too soon to check again

        current_offset = self.component_offsets[component]
        drift_rate = 0.0

        if self.drift_history[component]:
            prev_offset, prev_time = self.drift_history[component][-1]
            time_diff = (current_time - prev_time) / 1_000_000  # → seconds
            if time_diff > 0:
                drift_rate = (current_offset - prev_offset) / time_diff

        self.drift_history[component].append((current_offset, current_time))

        # Keep history bounded
        if len(self.drift_history[component]) > self.MAX_DRIFT_HISTORY:
            self.drift_history[component] = self.drift_history[component][-self.MAX_DRIFT_HISTORY:]

        needs_correction = abs(current_offset) > self.DRIFT_THRESHOLD_US

        return DriftReport(
            component=component,
            drift_us=current_offset,
            drift_rate_us_per_sec=drift_rate,
            last_sync_us=last_sync,
            needs_correction=needs_correction,
        )

    def correct_drift(self, component: str, drift_us: int) -> bool:
        """
        Apply a linear drift correction to a component.

        Args:
            component: Target component.
            drift_us: Drift magnitude in microseconds.

        Returns:
            True if the correction was applied.
        """
        if component not in self.components:
            return False

        self.component_offsets[component] -= drift_us
        logger.info("Applied drift correction | component=%s drift=%dµs", component, drift_us)
        return True

    def validate_consistency(self) -> Dict[str, Any]:
        """
        Validate timestamp consistency across all components.

        Returns a report dict with max discrepancy and a boolean flag.
        """
        current_time = self.get_unified_timestamp()

        # Simulate component times using stored offsets
        component_times: Dict[str, int] = {
            c: current_time - self.component_offsets[c]
            for c in self.components
        }

        timestamps = list(component_times.values())
        max_discrepancy = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0
        is_consistent = max_discrepancy <= self.DRIFT_THRESHOLD_US

        return {
            "timestamp": current_time,
            "components": component_times,
            "max_discrepancy_us": max_discrepancy,
            "max_discrepancy_ms": max_discrepancy / 1000,
            "is_consistent": is_consistent,
            "threshold_ms": self.DRIFT_THRESHOLD_US / 1000,
        }

    def log_discrepancy(
        self, component_a: str, component_b: str, discrepancy_us: int
    ) -> None:
        """Log a timestamp discrepancy that exceeds 100 ms."""
        if abs(discrepancy_us) > self.DRIFT_THRESHOLD_US:
            logger.warning(
                "Timestamp discrepancy | %s ↔ %s | %.2f ms (threshold 100 ms)",
                component_a,
                component_b,
                discrepancy_us / 1000,
            )

    def get_sync_status(self) -> Dict[str, Any]:
        """Return synchronisation status for all components."""
        current_time = self.get_unified_timestamp()

        return {
            "unified_time_us": current_time,
            "components": {
                c: {
                    "offset_us": self.component_offsets[c],
                    "offset_ms": self.component_offsets[c] / 1000,
                    "last_sync_ago_s": (current_time - self.last_sync_times[c]) / 1_000_000,
                    "drift_history_entries": len(self.drift_history[c]),
                }
                for c in self.components
            },
        }


if __name__ == "__main__":
    from backend.core.logging_config import configure_logging
    configure_logging()

    sync = TimestampSynchronizer()
    base = sync.get_unified_timestamp()

    # Simulate drift for each component
    drifts = {"frame_processor": 0, "twelve_labs": -50_000, "turbopuffer": 75_000}
    for comp, drift in drifts.items():
        adjusted = sync.sync_component(comp, base + drift)
        logger.info("%s | original=%d adjusted=%d diff=%dµs", comp, base + drift, adjusted, adjusted - (base + drift))

    consistency = sync.validate_consistency()
    logger.info(
        "Consistency | max_discrepancy=%.2f ms | consistent=%s",
        consistency["max_discrepancy_ms"],
        consistency["is_consistent"],
    )
