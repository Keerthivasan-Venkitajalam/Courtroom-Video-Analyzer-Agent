"""
timestamp_sync.py
Timestamp synchronization module for aligning video, transcript, and processor timecodes.
Implements shared epoch offset and linear drift correction.
"""
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from constants import EPOCH_OFFSET_US, get_unified_timestamp_us


@dataclass
class ComponentTimestamp:
    """Represents a timestamp from a specific component."""
    component: str
    timestamp_us: int
    local_time_us: int  # When this timestamp was recorded locally


@dataclass
class DriftReport:
    """Report on clock drift for a component."""
    component: str
    drift_us: int
    drift_rate_us_per_sec: float
    last_sync_us: int
    needs_correction: bool


class TimestampSynchronizer:
    """
    Manages timestamp synchronization across all system components.
    
    Components:
    - Vision Agent's local frame processor
    - Twelve Labs index
    - TurboPuffer text timestamps
    
    Ensures all timestamps align within 100ms accuracy.
    """
    
    def __init__(self):
        """Initialize timestamp synchronizer."""
        self.component_offsets: Dict[str, int] = {}
        self.last_sync_times: Dict[str, int] = {}
        self.drift_history: Dict[str, list] = {}
        self.sync_interval_us = 10_000_000  # 10 seconds
        
        # Initialize components
        self.components = [
            "frame_processor",
            "twelve_labs",
            "turbopuffer"
        ]
        
        for component in self.components:
            self.component_offsets[component] = 0
            self.last_sync_times[component] = get_unified_timestamp_us()
            self.drift_history[component] = []
        
        print("⏰ TimestampSynchronizer initialized")
        print(f"   Epoch offset: {EPOCH_OFFSET_US}μs")
        print(f"   Sync interval: {self.sync_interval_us / 1_000_000}s")
        print(f"   Accuracy target: ±100ms")
    
    def get_unified_timestamp(self) -> int:
        """
        Get current unified timestamp in microseconds.
        
        Returns:
            Current timestamp in microseconds since epoch
        """
        return get_unified_timestamp_us()
    
    def sync_component(self, component: str, component_timestamp_us: int) -> int:
        """
        Synchronize a component's timestamp with the unified clock.
        
        Args:
            component: Component name
            component_timestamp_us: Timestamp from the component
            
        Returns:
            Adjusted timestamp aligned with unified clock
        """
        if component not in self.components:
            print(f"⚠️  Unknown component: {component}")
            return component_timestamp_us
        
        # Get current unified time
        unified_time = self.get_unified_timestamp()
        
        # Calculate offset
        offset = unified_time - component_timestamp_us
        
        # Update component offset (exponential moving average for smoothing)
        alpha = 0.3  # Smoothing factor
        if self.component_offsets[component] == 0:
            self.component_offsets[component] = offset
        else:
            self.component_offsets[component] = int(
                alpha * offset + (1 - alpha) * self.component_offsets[component]
            )
        
        # Record sync time
        self.last_sync_times[component] = unified_time
        
        # Return adjusted timestamp
        adjusted = component_timestamp_us + self.component_offsets[component]
        
        return adjusted
    
    def detect_drift(self, component: str) -> Optional[DriftReport]:
        """
        Detect clock drift for a specific component.
        
        Args:
            component: Component name
            
        Returns:
            DriftReport if drift detected, None otherwise
        """
        if component not in self.components:
            return None
        
        current_time = self.get_unified_timestamp()
        last_sync = self.last_sync_times[component]
        time_since_sync = current_time - last_sync
        
        # Check if it's time to validate
        if time_since_sync < self.sync_interval_us:
            return None
        
        # Get current offset
        current_offset = self.component_offsets[component]
        
        # Calculate drift rate
        drift_rate = 0.0
        if len(self.drift_history[component]) > 0:
            prev_offset, prev_time = self.drift_history[component][-1]
            time_diff = (current_time - prev_time) / 1_000_000  # seconds
            if time_diff > 0:
                drift_rate = (current_offset - prev_offset) / time_diff
        
        # Record in history
        self.drift_history[component].append((current_offset, current_time))
        
        # Keep only last 100 entries
        if len(self.drift_history[component]) > 100:
            self.drift_history[component] = self.drift_history[component][-100:]
        
        # Check if correction needed (drift > 100ms)
        needs_correction = abs(current_offset) > 100_000  # 100ms in microseconds
        
        return DriftReport(
            component=component,
            drift_us=current_offset,
            drift_rate_us_per_sec=drift_rate,
            last_sync_us=last_sync,
            needs_correction=needs_correction
        )
    
    def correct_drift(self, component: str, drift_us: int) -> bool:
        """
        Apply drift correction to a component.
        
        Args:
            component: Component name
            drift_us: Drift amount in microseconds
            
        Returns:
            True if correction applied successfully
        """
        if component not in self.components:
            return False
        
        # Apply linear correction
        self.component_offsets[component] -= drift_us
        
        print(f"✅ Applied drift correction to {component}: {drift_us}μs")
        return True
    
    def validate_consistency(self) -> Dict[str, any]:
        """
        Validate timestamp consistency across all components.
        
        Returns:
            Consistency report dictionary
        """
        current_time = self.get_unified_timestamp()
        
        # Get all component timestamps (simulated)
        component_times = {}
        for component in self.components:
            # In real implementation, this would query each component
            # For now, use offset to simulate
            component_times[component] = current_time - self.component_offsets[component]
        
        # Calculate max discrepancy
        timestamps = list(component_times.values())
        if len(timestamps) > 1:
            max_discrepancy = max(timestamps) - min(timestamps)
        else:
            max_discrepancy = 0
        
        # Check if consistent (within 100ms)
        is_consistent = max_discrepancy <= 100_000  # 100ms in microseconds
        
        return {
            'timestamp': current_time,
            'components': component_times,
            'max_discrepancy_us': max_discrepancy,
            'max_discrepancy_ms': max_discrepancy / 1000,
            'is_consistent': is_consistent,
            'threshold_ms': 100
        }
    
    def log_discrepancy(self, component_a: str, component_b: str, 
                       discrepancy_us: int):
        """
        Log timestamp discrepancy exceeding 100ms.
        
        Args:
            component_a: First component name
            component_b: Second component name
            discrepancy_us: Discrepancy in microseconds
        """
        if abs(discrepancy_us) > 100_000:  # 100ms threshold
            timestamp = self.get_unified_timestamp()
            print(f"⚠️  TIMESTAMP DISCREPANCY DETECTED")
            print(f"   Time: {timestamp}")
            print(f"   Components: {component_a} ↔ {component_b}")
            print(f"   Discrepancy: {discrepancy_us / 1000:.2f}ms")
            print(f"   Threshold: 100ms")
    
    def get_sync_status(self) -> Dict[str, any]:
        """
        Get synchronization status for all components.
        
        Returns:
            Status dictionary
        """
        current_time = self.get_unified_timestamp()
        
        status = {
            'unified_time_us': current_time,
            'components': {}
        }
        
        for component in self.components:
            last_sync = self.last_sync_times[component]
            time_since_sync = (current_time - last_sync) / 1_000_000  # seconds
            
            status['components'][component] = {
                'offset_us': self.component_offsets[component],
                'offset_ms': self.component_offsets[component] / 1000,
                'last_sync_ago_s': time_since_sync,
                'drift_history_entries': len(self.drift_history[component])
            }
        
        return status


def test_timestamp_sync():
    """Test timestamp synchronization functionality."""
    print("=" * 60)
    print("TIMESTAMP SYNCHRONIZATION TEST")
    print("=" * 60)
    
    # Initialize synchronizer
    sync = TimestampSynchronizer()
    
    # Test 1: Get unified timestamp
    print("\n[Test 1] Unified Timestamp")
    unified = sync.get_unified_timestamp()
    print(f"  Unified time: {unified}μs")
    print(f"  Human readable: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(unified / 1_000_000))}")
    
    # Test 2: Sync components with simulated drift
    print("\n[Test 2] Component Synchronization")
    
    # Simulate component timestamps with drift
    base_time = unified
    component_times = {
        'frame_processor': base_time,
        'twelve_labs': base_time - 50_000,  # 50ms behind
        'turbopuffer': base_time + 75_000   # 75ms ahead
    }
    
    for component, timestamp in component_times.items():
        adjusted = sync.sync_component(component, timestamp)
        drift = adjusted - timestamp
        print(f"  {component}:")
        print(f"    Original: {timestamp}μs")
        print(f"    Adjusted: {adjusted}μs")
        print(f"    Drift: {drift / 1000:.2f}ms")
    
    # Test 3: Validate consistency
    print("\n[Test 3] Consistency Validation")
    consistency = sync.validate_consistency()
    print(f"  Max discrepancy: {consistency['max_discrepancy_ms']:.2f}ms")
    print(f"  Is consistent: {'✅' if consistency['is_consistent'] else '❌'}")
    print(f"  Threshold: {consistency['threshold_ms']}ms")
    
    # Test 4: Detect drift
    print("\n[Test 4] Drift Detection")
    time.sleep(0.1)  # Small delay
    
    for component in sync.components:
        drift_report = sync.detect_drift(component)
        if drift_report:
            print(f"  {component}:")
            print(f"    Drift: {drift_report.drift_us / 1000:.2f}ms")
            print(f"    Rate: {drift_report.drift_rate_us_per_sec:.2f}μs/s")
            print(f"    Needs correction: {'⚠️  Yes' if drift_report.needs_correction else '✅ No'}")
    
    # Test 5: Log discrepancy
    print("\n[Test 5] Discrepancy Logging")
    sync.log_discrepancy('twelve_labs', 'turbopuffer', 125_000)  # 125ms discrepancy
    
    # Test 6: Get sync status
    print("\n[Test 6] Synchronization Status")
    status = sync.get_sync_status()
    print(f"  Unified time: {status['unified_time_us']}μs")
    for component, info in status['components'].items():
        print(f"  {component}:")
        print(f"    Offset: {info['offset_ms']:.2f}ms")
        print(f"    Last sync: {info['last_sync_ago_s']:.2f}s ago")
    
    print("\n✅ Timestamp synchronization test complete!")


if __name__ == "__main__":
    test_timestamp_sync()
