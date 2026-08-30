#!/usr/bin/env python3
"""
Infrastructure Health Scenario Simulator
Exercise 3.3: Infrastructure Health Prediction

This script simulates various infrastructure health scenarios for testing.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import time
import threading
import random
import json
from typing import Dict, List
import sys


class InfrastructureSimulator:
    """Simulates infrastructure health scenarios"""
    
    def __init__(self):
        self.base_values = {
            'cpu': 50,
            'memory': 60,
            'disk': 70,
            'network': 30,
            'security': 90
        }
        self.running = False
        self.scenario_active = False
        self.scenario_type = None
    
    def start(self, duration: int = 300):
        """Start simulation"""
        self.running = True
        self.start_time = datetime.now()
        
        print(f"Starting infrastructure health simulation")
        print(f"Duration: {duration} seconds")
        print(f"Base values: {self.base_values}")
        
        # Start scenario injection thread
        scenario_thread = threading.Thread(target=self._inject_scenarios, 
                                          args=(duration,))
        scenario_thread.daemon = True
        scenario_thread.start()
        
        # Main simulation loop
        try:
            for i in range(duration):
                if not self.running:
                    break
                
                # Generate metrics
                metrics = self._generate_metrics()
                
                # Print current values
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                      f"CPU: {metrics['cpu']:.1f}% | "
                      f"Memory: {metrics['memory']:.1f}% | "
                      f"Disk: {metrics['disk']:.1f}% | "
                      f"Network: {metrics['network']:.1f}% | "
                      f"Scenario: {'ACTIVE' if self.scenario_active else 'none'}",
                      end='', flush=True)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nStopping simulation...")
        finally:
            self.running = False
    
    def _generate_metrics(self) -> Dict:
        """Generate current metric values"""
        metrics = {}
        
        for component, base in self.base_values.items():
            value = base
            
            # Apply scenario effects
            if self.scenario_active and self.scenario_type:
                if self.scenario_type == 'disk_exhaustion' and component == 'disk':
                    value *= np.random.uniform(1.5, 2.0)
                elif self.scenario_type == 'memory_leak' and component == 'memory':
                    value *= np.random.uniform(1.3, 1.8)
                elif self.scenario_type == 'cpu_spike' and component == 'cpu':
                    value *= np.random.uniform(1.5, 2.5)
                elif self.scenario_type == 'network_congestion' and component == 'network':
                    value *= np.random.uniform(1.5, 2.0)
                elif self.scenario_type == 'security_breach' and component == 'security':
                    value *= np.random.uniform(0.3, 0.6)
            
            # Add noise
            value += np.random.normal(0, 2)
            
            # Clamp to 0-100
            value = max(0, min(100, value))
            
            metrics[component] = value
        
        return metrics
    
    def _inject_scenarios(self, duration: int):
        """Randomly inject infrastructure scenarios"""
        while self.running and duration > 0:
            # Wait for random interval
            wait_time = random.randint(30, 90)
            time.sleep(wait_time)
            
            if not self.running:
                break
            
            # Choose scenario type
            scenario_types = [
                'disk_exhaustion',
                'memory_leak',
                'cpu_spike',
                'network_congestion',
                'security_breach'
            ]
            self.scenario_type = random.choice(scenario_types)
            self.scenario_active = True
            
            print(f"\n\n*** INFRASTRUCTURE SCENARIO: {self.scenario_type.upper()} ***")
            
            # Scenario duration
            scenario_duration = random.randint(10, 60)
            time.sleep(scenario_duration)
            
            self.scenario_active = False
            self.scenario_type = None
            
            print(f"*** SCENARIO CLEARED ***\n")
    
    def stop(self):
        """Stop simulation"""
        self.running = False


def run_scenario(scenario: str = 'disk_exhaustion', duration: int = 300):
    """Run a specific infrastructure scenario"""
    print("=" * 60)
    print("Infrastructure Health Scenario Simulator")
    print("=" * 60)
    
    # Create simulator
    simulator = InfrastructureSimulator()
    
    # Print scenario info
    scenarios = {
        'disk_exhaustion': {
            'description': 'Disk space running low',
            'severity': 'critical',
            'expected_alert': 'DiskExhaustionPredicted',
            'expected_action': 'Clean up disk space or add more storage'
        },
        'memory_leak': {
            'description': 'Memory usage increasing due to leak',
            'severity': 'warning',
            'expected_alert': 'MemoryExhaustionPredicted',
            'expected_action': 'Investigate memory usage, consider adding more memory'
        },
        'cpu_spike': {
            'description': 'CPU usage spike due to runaway process',
            'severity': 'warning',
            'expected_alert': 'CpuSaturationPredicted',
            'expected_action': 'Investigate process list, check for DDoS'
        },
        'network_congestion': {
            'description': 'Network traffic spike causing congestion',
            'severity': 'warning',
            'expected_alert': 'NetworkSaturationPredicted',
            'expected_action': 'Investigate source, consider upgrading network'
        },
        'security_breach': {
            'description': 'Security incident detected',
            'severity': 'critical',
            'expected_alert': 'HighFailedLogins',
            'expected_action': 'Review security, check for unauthorized access'
        }
    }
    
    scenario_config = scenarios.get(scenario, scenarios['disk_exhaustion'])
    
    print(f"\nScenario: {scenario_config['description']}")
    print(f"Severity: {scenario_config['severity']}")
    print(f"Expected Alert: {scenario_config['expected_alert']}")
    print(f"Expected Action: {scenario_config['expected_action']}")
    
    # Print instructions
    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("1. Open Grafana dashboard in your browser")
    print("2. Watch for infrastructure health alerts")
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
        run_scenario(scenario, duration)
    else:
        print("Usage: python infrastructure_simulator.py <scenario> [duration]")
        print("\nScenarios: disk_exhaustion, memory_leak, cpu_spike, network_congestion, security_breach")
        sys.exit(1)


if __name__ == '__main__':
    main()
