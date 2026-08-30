#!/usr/bin/env python3
"""
Anomaly Injection Simulator
Exercise 3.1: Enterprise Anomaly Detection System

This script simulates various types of anomalies for testing
anomaly detection systems.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import time
import threading
import random
from typing import Dict, List, Optional
import sys


class MetricsSimulator:
    """Simulates metrics that can be exported to Prometheus"""
    
    def __init__(self, base_value: float = 50.0, port: int = 8000):
        self.base_value = base_value
        self.port = port
        self.running = False
        self.anomaly_active = False
        self.anomaly_type = None
        self.anomaly_start = None
        
    def start(self, duration: int = 300):
        """Start simulating metrics"""
        self.running = True
        self.start_time = datetime.now()
        
        print(f"Starting metrics simulation on port {self.port}")
        print(f"Duration: {duration} seconds")
        print(f"Base value: {self.base_value}")
        
        # Start anomaly injection thread
        anomaly_thread = threading.Thread(target=self._inject_anomalies, 
                                         args=(duration,))
        anomaly_thread.daemon = True
        anomaly_thread.start()
        
        # Main simulation loop
        try:
            for i in range(duration):
                if not self.running:
                    break
                
                # Generate metrics
                metrics = self._generate_metrics()
                
                # Print current values (simulating Prometheus scrape)
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                      f"CPU: {metrics['cpu']:.1f}% | "
                      f"Memory: {metrics['memory']:.1f}% | "
                      f"Disk I/O: {metrics['disk_io']:.1f} MB/s | "
                      f"Network: {metrics['network']:.1f} MB/s | "
                      f"Anomaly: {'ACTIVE' if self.anomaly_active else 'none'}",
                      end='', flush=True)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nStopping simulation...")
        finally:
            self.running = False
    
    def _generate_metrics(self) -> Dict:
        """Generate current metric values"""
        base = self.base_value
        noise = np.random.normal(0, 5)
        
        # Apply anomaly if active
        if self.anomaly_active and self.anomaly_type:
            if self.anomaly_type == 'cpu_spike':
                base *= np.random.uniform(2, 4)
            elif self.anomaly_type == 'memory_leak':
                base *= np.random.uniform(1.5, 2.5)
            elif self.anomaly_type == 'disk_thrash':
                base *= np.random.uniform(3, 5)
            elif self.anomaly_type == 'network_flood':
                base *= np.random.uniform(4, 6)
        
        # Add seasonal pattern
        hour = datetime.now().hour
        seasonal = 10 * np.sin(2 * np.pi * hour / 24)
        
        # Add weekly pattern
        weekday = datetime.now().weekday()
        weekly = 5 * np.sin(2 * np.pi * weekday / 7)
        
        return {
            'cpu': max(0, min(100, base + noise + seasonal + weekly)),
            'memory': max(0, min(100, base * 0.8 + noise + seasonal)),
            'disk_io': max(0, base * 0.5 + noise * 0.5),
            'network': max(0, base * 0.3 + noise * 0.3),
            'timestamp': datetime.now().isoformat()
        }
    
    def _inject_anomalies(self, duration: int):
        """Randomly inject anomalies during simulation"""
        while self.running and duration > 0:
            # Wait for random interval
            wait_time = random.randint(30, 120)
            time.sleep(wait_time)
            
            if not self.running:
                break
            
            # Choose anomaly type
            anomaly_types = [
                'cpu_spike',
                'memory_leak', 
                'disk_thrash',
                'network_flood'
            ]
            self.anomaly_type = random.choice(anomaly_types)
            self.anomaly_active = True
            self.anomaly_start = datetime.now()
            
            print(f"\n\n*** ANOMALY DETECTED: {self.anomaly_type.upper()} ***")
            
            # Anomaly duration
            anomaly_duration = random.randint(10, 60)
            time.sleep(anomaly_duration)
            
            self.anomaly_active = False
            self.anomaly_type = None
            
            print(f"*** ANOMALY CLEARED ***\n")
    
    def stop(self):
        """Stop simulation"""
        self.running = False


class PrometheusExporter:
    """Exports metrics in Prometheus format"""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.metrics = {}
    
    def update(self, metrics: Dict):
        """Update metrics"""
        self.metrics = metrics
    
    def format_metrics(self) -> str:
        """Format metrics in Prometheus text format"""
        lines = []
        
        # CPU metric
        lines.append('# HELP cpu_usage_percent Current CPU usage percentage')
        lines.append('# TYPE cpu_usage_percent gauge')
        lines.append(f'cpu_usage_percent {self.metrics.get("cpu", 0):.2f}')
        
        # Memory metric
        lines.append('# HELP memory_usage_percent Current memory usage percentage')
        lines.append('# TYPE memory_usage_percent gauge')
        lines.append(f'memory_usage_percent {self.metrics.get("memory", 0):.2f}')
        
        # Disk I/O metric
        lines.append('# HELP disk_io_mbps Current disk I/O in MB/s')
        lines.append('# TYPE disk_io_mbps gauge')
        lines.append(f'disk_io_mbps {self.metrics.get("disk_io", 0):.2f}')
        
        # Network metric
        lines.append('# HELP network_mbps Current network traffic in MB/s')
        lines.append('# TYPE network_mbps gauge')
        lines.append(f'network_mbps {self.metrics.get("network", 0):.2f}')
        
        # Anomaly score
        lines.append('# HELP anomaly_score Current anomaly score')
        lines.append('# TYPE anomaly_score gauge')
        lines.append(f'anomaly_score {self.metrics.get("anomaly_score", 0):.2f}')
        
        # Timestamp
        lines.append('# HELP metric_timestamp Timestamp of last update')
        lines.append('# TYPE metric_timestamp gauge')
        lines.append(f'metric_timestamp {self.metrics.get("timestamp", 0)}')
        
        return '\n'.join(lines)


class AnomalyScenario:
    """Defines specific anomaly scenarios"""
    
    @staticmethod
    def cpu_spike() -> Dict:
        """CPU spike scenario"""
        return {
            'type': 'cpu_spike',
            'description': 'Sudden CPU spike due to runaway process',
            'severity': 'critical',
            'duration': 60,
            'multiplier': 3.0,
            'expected_alert': 'HighCpuAnomalyScore',
            'expected_action': 'Investigate process list, check for DDoS'
        }
    
    @staticmethod
    def memory_leak() -> Dict:
        """Memory leak scenario"""
        return {
            'type': 'memory_leak',
            'description': 'Gradual memory increase due to leak',
            'severity': 'warning',
            'duration': 300,
            'multiplier': 1.5,
            'expected_alert': 'MemoryLeakDetected',
            'expected_action': 'Profile application, check for memory leaks'
        }
    
    @staticmethod
    def disk_thrash() -> Dict:
        """Disk thrashing scenario"""
        return {
            'type': 'disk_thrash',
            'description': 'High disk I/O due to excessive reads/writes',
            'severity': 'warning',
            'duration': 120,
            'multiplier': 4.0,
            'expected_alert': 'HighDiskIoAnomalyScore',
            'expected_action': 'Check for heavy I/O operations'
        }
    
    @staticmethod
    def network_flood() -> Dict:
        """Network flood scenario"""
        return {
            'type': 'network_flood',
            'description': 'Network traffic spike',
            'severity': 'critical',
            'duration': 90,
            'multiplier': 5.0,
            'expected_alert': 'HighNetworkAnomalyScore',
            'expected_action': 'Investigate source, check for DDoS'
        }
    
    @staticmethod
    def cascading_failure() -> List[Dict]:
        """Cascading failure scenario"""
        return [
            {
                'type': 'cpu_spike',
                'severity': 'warning',
                'duration': 60,
                'multiplier': 2.0,
                'delay': 0
            },
            {
                'type': 'memory_leak',
                'severity': 'warning',
                'duration': 120,
                'multiplier': 1.5,
                'delay': 30
            },
            {
                'type': 'disk_thrash',
                'severity': 'critical',
                'duration': 180,
                'multiplier': 3.0,
                'delay': 60
            },
            {
                'type': 'network_flood',
                'severity': 'critical',
                'duration': 240,
                'multiplier': 4.0,
                'delay': 90
            }
        ]


def run_simulation(scenario: str = 'cpu_spike', duration: int = 300):
    """Run a specific anomaly scenario"""
    print("=" * 60)
    print("Anomaly Injection Simulator")
    print("=" * 60)
    
    # Create simulator
    simulator = MetricsSimulator(base_value=50, port=8000)
    
    # Print scenario info
    if scenario == 'cpu_spike':
        scenario_config = AnomalyScenario.cpu_spike()
    elif scenario == 'memory_leak':
        scenario_config = AnomalyScenario.memory_leak()
    elif scenario == 'disk_thrash':
        scenario_config = AnomalyScenario.disk_thrash()
    elif scenario == 'network_flood':
        scenario_config = AnomalyScenario.network_flood()
    else:
        scenario_config = AnomalyScenario.cpu_spike()
    
    print(f"\nScenario: {scenario_config['description']}")
    print(f"Severity: {scenario_config['severity']}")
    print(f"Duration: {scenario_config['duration']} seconds")
    print(f"Multiplier: {scenario_config['multiplier']}x")
    print(f"Expected Alert: {scenario_config['expected_alert']}")
    print(f"Expected Action: {scenario_config['expected_action']}")
    
    # Print instructions
    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("1. Open Grafana dashboard in your browser")
    print("2. Watch for anomaly detection alerts")
    print("3. Monitor the metrics in real-time")
    print("4. Press Ctrl+C to stop simulation")
    print("=" * 60)
    
    try:
        simulator.start(duration)
    except KeyboardInterrupt:
        simulator.stop()
        print("\nSimulation stopped.")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        scenario = sys.argv[1]
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    else:
        print("Usage: python anomaly_simulator.py <scenario> [duration]")
        print("Scenarios: cpu_spike, memory_leak, disk_thrash, network_flood")
        print("Duration: seconds (default: 300)")
        sys.exit(1)
    
    run_simulation(scenario, duration)


if __name__ == '__main__':
    main()
