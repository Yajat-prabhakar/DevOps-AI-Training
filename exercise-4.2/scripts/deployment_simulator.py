#!/usr/bin/env python3
"""
Deployment Simulation Scripts
Exercise 4.2: Intelligent Deployment Pipeline

This script simulates various deployment scenarios for testing.
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


class DeploymentSimulator:
    """Simulates deployment scenarios"""
    
    def __init__(self):
        self.strategies = ['rolling', 'canary', 'blue-green']
        self.running = False
        self.deployment_active = False
        self.current_strategy = None
    
    def start(self, duration: int = 300):
        """Start simulation"""
        self.running = True
        self.start_time = datetime.now()
        
        print(f"Starting deployment simulation")
        print(f"Duration: {duration} seconds")
        print(f"Strategies: {self.strategies}")
        
        # Start deployment simulation thread
        deployment_thread = threading.Thread(target=self._simulate_deployments, 
                                            args=(duration,))
        deployment_thread.daemon = True
        deployment_thread.start()
        
        # Main simulation loop
        try:
            for i in range(duration):
                if not self.running:
                    break
                
                # Generate metrics
                metrics = self._generate_metrics()
                
                # Print current values
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Strategy: {self.current_strategy or 'none'} | "
                      f"Status: {'ACTIVE' if self.deployment_active else 'idle'} | "
                      f"Success Rate: {metrics['success_rate']:.1%}",
                      end='', flush=True)
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nStopping simulation...")
        finally:
            self.running = False
    
    def _generate_metrics(self) -> Dict:
        """Generate current metric values"""
        return {
            'success_rate': random.uniform(0.85, 0.99),
            'rollback_rate': random.uniform(0.01, 0.1),
            'deployment_time': random.randint(10, 60),
            'timestamp': datetime.now().isoformat()
        }
    
    def _simulate_deployments(self, duration: int):
        """Simulate deployment scenarios"""
        while self.running and duration > 0:
            # Wait for random interval
            wait_time = random.randint(30, 90)
            time.sleep(wait_time)
            
            if not self.running:
                break
            
            # Choose strategy
            self.current_strategy = random.choice(self.strategies)
            self.deployment_active = True
            
            print(f"\n\n*** DEPLOYMENT STARTED: {self.current_strategy.upper()} ***")
            
            # Simulate deployment
            deployment_duration = random.randint(30, 120)
            
            for i in range(deployment_duration):
                if not self.running:
                    break
                
                # Simulate deployment progress
                progress = (i + 1) / deployment_duration * 100
                
                # Simulate different stages
                if progress < 20:
                    stage = "Building"
                elif progress < 40:
                    stage = "Testing"
                elif progress < 60:
                    stage = "Deploying"
                elif progress < 80:
                    stage = "Validating"
                else:
                    stage = "Finalizing"
                
                print(f"\r  Progress: {progress:.0f}% - {stage}", end='', flush=True)
                time.sleep(1)
            
            # Simulate deployment result
            success = random.choices([True, False], weights=[0.9, 0.1])[0]
            
            if success:
                print(f"\n*** DEPLOYMENT SUCCESSFUL ***")
            else:
                print(f"\n*** DEPLOYMENT FAILED - ROLLING BACK ***")
            
            self.deployment_active = False
            self.current_strategy = None
    
    def stop(self):
        """Stop simulation"""
        self.running = False


def run_scenario(strategy: str = 'canary', duration: int = 300):
    """Run a specific deployment scenario"""
    print("=" * 60)
    print("Deployment Simulation")
    print("=" * 60)
    
    # Create simulator
    simulator = DeploymentSimulator()
    
    # Print scenario info
    scenarios = {
        'rolling': {
            'description': 'Gradually replace instances',
            'risk_level': 'low',
            'rollback_time': 5,
            'downtime': 0
        },
        'canary': {
            'description': 'Deploy to small subset first',
            'risk_level': 'medium',
            'rollback_time': 2,
            'downtime': 0
        },
        'blue-green': {
            'description': 'Deploy to separate environment',
            'risk_level': 'high',
            'rollback_time': 1,
            'downtime': 0
        }
    }
    
    scenario_config = scenarios.get(strategy, scenarios['canary'])
    
    print(f"\nStrategy: {strategy}")
    print(f"Description: {scenario_config['description']}")
    print(f"Risk Level: {scenario_config['risk_level']}")
    print(f"Rollback Time: {scenario_config['rollback_time']} minutes")
    
    # Print instructions
    print("\n" + "=" * 60)
    print("INSTRUCTIONS:")
    print("1. Open Grafana dashboard in your browser")
    print("2. Watch for deployment metrics")
    print("3. Monitor the deployment in real-time")
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
        strategy = sys.argv[1]
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        run_scenario(strategy, duration)
    else:
        print("Usage: python deployment_simulator.py <strategy> [duration]")
        print("\nStrategies: rolling, canary, blue-green")
        sys.exit(1)


if __name__ == '__main__':
    main()
