#!/usr/bin/env python3
"""
Performance Scenario Simulator
Exercise 3.2: Application Performance Intelligence

This script simulates various performance scenarios for testing.
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


class PerformanceSimulator:
    """Simulates application performance metrics"""
    
    def __init__(self):
        self.base_latency = 0.1  # 100ms
        self.base_error_rate = 0.01  # 1%
        self.base_throughput = 1000  # rps
        self.running = False
        self.scenario_active = False
        self.scenario_type = None
    
    def start(self, duration: int = 300):
        """Start simulation"""
        self.running = True
        self.start_time = datetime.now()
        
        print(f"Starting performance simulation")
        print(f"Duration: {duration} seconds")
        print(f"Base latency: {self.base_latency * 1000:.0f}ms")
        print(f"Base error rate: {self.base_error_rate:.1%}")
        print(f"Base throughput: {self.base_throughput} rps")
        
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
                      f"Latency: {metrics['latency'] * 1000:.0f}ms | "
                      f"Errors: {metrics['error_rate']:.1%} | "
                      f"Throughput: {metrics['throughput']:.0f} rps | "
                      f"Scenario: {'ACTIVE' if self.scenario_active else 'none'}",
                      end='', flush=True)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nStopping simulation...")
        finally:
            self.running = False
    
    def _generate_metrics(self) -> Dict:
        """Generate current metric values"""
        latency = self.base_latency
        error_rate = self.base_error_rate
        throughput = self.base_throughput
        
        # Apply scenario effects
        if self.scenario_active and self.scenario_type:
            if self.scenario_type == 'latency_spike':
                latency *= np.random.uniform(3, 5)
            elif self.scenario_type == 'error_spike':
                error_rate *= np.random.uniform(5, 10)
            elif self.scenario_type == 'throughput_drop':
                throughput *= np.random.uniform(0.2, 0.5)
            elif self.scenario_type == 'cascading_failure':
                latency *= np.random.uniform(2, 4)
                error_rate *= np.random.uniform(3, 6)
                throughput *= np.random.uniform(0.3, 0.7)
        
        # Add noise
        latency += np.random.normal(0, 0.01)
        error_rate += np.random.normal(0, 0.005)
        throughput += np.random.normal(0, 50)
        
        return {
            'latency': max(0.01, latency),
            'error_rate': max(0, min(1, error_rate)),
            'throughput': max(100, throughput),
            'timestamp': datetime.now().isoformat()
        }
    
    def _inject_scenarios(self, duration: int):
        """Randomly inject performance scenarios"""
        while self.running and duration > 0:
            # Wait for random interval
            wait_time = random.randint(30, 90)
            time.sleep(wait_time)
            
            if not self.running:
                break
            
            # Choose scenario type
            scenario_types = [
                'latency_spike',
                'error_spike',
                'throughput_drop',
                'cascading_failure'
            ]
            self.scenario_type = random.choice(scenario_types)
            self.scenario_active = True
            
            print(f"\n\n*** PERFORMANCE SCENARIO: {self.scenario_type.upper()} ***")
            
            # Scenario duration
            scenario_duration = random.randint(10, 60)
            time.sleep(scenario_duration)
            
            self.scenario_active = False
            self.scenario_type = None
            
            print(f"*** SCENARIO CLEARED ***\n")
    
    def stop(self):
        """Stop simulation"""
        self.running = False


class LoadGenerator:
    """Generates load for performance testing"""
    
    def __init__(self):
        self.endpoints = [
            '/api/users',
            '/api/products',
            '/api/orders',
            '/api/search',
            '/api/recommendations'
        ]
    
    def generate_load(self, duration: int = 60, 
                     rps: int = 100) -> pd.DataFrame:
        """Generate load test data"""
        timestamps = []
        endpoints = []
        latencies = []
        status_codes = []
        
        start_time = datetime.now()
        
        for i in range(duration * rps):
            if (datetime.now() - start_time).total_seconds() >= duration:
                break
            
            # Random endpoint
            endpoint = random.choice(self.endpoints)
            
            # Random latency (with scenario effects)
            latency = np.random.exponential(0.1)  # 100ms average
            
            # Random status code (mostly 200, some errors)
            status = random.choices(
                [200, 201, 400, 404, 500, 503],
                weights=[70, 10, 5, 5, 7, 3]
            )[0]
            
            timestamps.append(datetime.now())
            endpoints.append(endpoint)
            latencies.append(latency)
            status_codes.append(status)
            
            # Sleep to maintain target RPS
            time.sleep(1 / rps)
        
        return pd.DataFrame({
            'timestamp': timestamps,
            'endpoint': endpoints,
            'latency': latencies,
            'status_code': status_codes
        })


def run_scenario(scenario: str = 'latency_spike', duration: int = 300):
    """Run a specific performance scenario"""
    print("=" * 60)
    print("Performance Scenario Simulator")
    print("=" * 60)
    
    # Create simulator
    simulator = PerformanceSimulator()
    
    # Print scenario info
    scenarios = {
        'latency_spike': {
            'description': 'Sudden increase in response latency',
            'severity': 'warning',
            'expected_alert': 'HighLatencyP95',
            'expected_action': 'Check database queries, optimize slow endpoints'
        },
        'error_spike': {
            'description': 'Increase in HTTP error rates',
            'severity': 'critical',
            'expected_alert': 'HighErrorRate',
            'expected_action': 'Check application logs, investigate errors'
        },
        'throughput_drop': {
            'description': 'Decrease in request throughput',
            'severity': 'warning',
            'expected_alert': 'LowThroughput',
            'expected_action': 'Check load balancer, verify service health'
        },
        'cascading_failure': {
            'description': 'Multiple performance issues occurring together',
            'severity': 'critical',
            'expected_alert': 'CriticalPerformanceHealth',
            'expected_action': 'Immediate investigation required'
        }
    }
    
    scenario_config = scenarios.get(scenario, scenarios['latency_spike'])
    
    print(f"\nScenario: {scenario_config['description']}")
    print(f"Severity: {scenario_config['severity']}")
    print(f"Expected Alert: {scenario_config['expected_alert']}")
    print(f"Expected Action: {scenario_config['expected_action']}")
    
    # Print instructions
    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("1. Open Grafana dashboard in your browser")
    print("2. Watch for performance alerts")
    print("3. Monitor the metrics in real-time")
    print("4. Press Ctrl+C to stop simulation")
    print("=" * 60)
    
    try:
        simulator.start(duration)
    except KeyboardInterrupt:
        simulator.stop()
        print("\nSimulation stopped.")


def run_load_test(duration: int = 60, rps: int = 100):
    """Run load test"""
    print("=" * 60)
    print("Load Test Generator")
    print("=" * 60)
    
    print(f"\nDuration: {duration} seconds")
    print(f"Target RPS: {rps}")
    
    generator = LoadGenerator()
    
    print("\nGenerating load...")
    df = generator.generate_load(duration=duration, rps=rps)
    
    # Analyze results
    print("\nLoad Test Results:")
    print(f"  Total requests: {len(df)}")
    print(f"  Average latency: {df['latency'].mean() * 1000:.0f}ms")
    print(f"  p95 latency: {df['latency'].quantile(0.95) * 1000:.0f}ms")
    print(f"  p99 latency: {df['latency'].quantile(0.99) * 1000:.0f}ms")
    print(f"  Error rate: {(df['status_code'] >= 400).mean():.1%}")
    
    # Save results
    df.to_csv('load_test_results.csv', index=False)
    print("\nResults saved to load_test_results.csv")
    
    # Generate report
    report = {
        'summary': {
            'total_requests': len(df),
            'average_latency': float(df['latency'].mean()),
            'p95_latency': float(df['latency'].quantile(0.95)),
            'p99_latency': float(df['latency'].quantile(0.99)),
            'error_rate': float((df['status_code'] >= 400).mean())
        },
        'endpoint_breakdown': df.groupby('endpoint').agg({
            'latency': ['mean', 'std'],
            'status_code': lambda x: (x >= 400).mean()
        }).to_dict()
    }
    
    with open('load_test_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print("Report saved to load_test_report.json")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == 'load':
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            rps = int(sys.argv[3]) if len(sys.argv) > 3 else 100
            run_load_test(duration, rps)
        else:
            scenario = sys.argv[1]
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 300
            run_scenario(scenario, duration)
    else:
        print("Usage:")
        print("  python performance_simulator.py <scenario> [duration]")
        print("  python performance_simulator.py load [duration] [rps]")
        print("\nScenarios: latency_spike, error_spike, throughput_drop, cascading_failure")
        sys.exit(1)


if __name__ == '__main__':
    main()
