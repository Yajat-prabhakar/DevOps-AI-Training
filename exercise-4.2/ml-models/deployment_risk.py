#!/usr/bin/env python3
"""
ML Model for Deployment Risk Prediction
Exercise 4.2: Intelligent Deployment Pipeline

This script predicts deployment risk and recommends deployment strategies.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import sys
from typing import Dict, List, Tuple


class DeploymentSimulator:
    """Simulates deployment metrics"""
    
    def __init__(self):
        self.deployment_history = []
    
    def generate_history(self, n_deployments: int = 100) -> pd.DataFrame:
        """Generate deployment history"""
        deployments = []
        
        for i in range(n_deployments):
            deployment = {
                'deployment_id': f"DEP-{i:04d}",
                'timestamp': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                'strategy': random.choice(['rolling', 'canary', 'blue-green']),
                'risk_score': random.uniform(0, 100),
                'files_changed': random.randint(1, 50),
                'lines_added': random.randint(10, 1000),
                'lines_removed': random.randint(0, 500),
                'test_coverage': random.uniform(0.5, 1.0),
                'previous_failures': random.randint(0, 5),
                'success': random.choices([True, False], weights=[0.9, 0.1])[0],
                'rollback': random.choices([False, True], weights=[0.95, 0.05])[0],
                'performance_impact': random.choice(['none', 'low', 'medium', 'high']),
                'duration_minutes': random.randint(10, 120)
            }
            deployments.append(deployment)
        
        return pd.DataFrame(deployments)


class DeploymentRiskPredictor:
    """Predicts deployment risk using ML"""
    
    def __init__(self):
        self.model = None
    
    def fit(self, df: pd.DataFrame) -> None:
        """Fit the model"""
        # Simple logistic regression simulation
        features = ['risk_score', 'files_changed', 'lines_added', 'lines_removed', 
                    'test_coverage', 'previous_failures']
        
        X = df[features].values
        y = df['success'].astype(int).values
        
        # Normalize features
        self.mean = X.mean(axis=0)
        self.std = X.std(axis=0)
        X_norm = (X - self.mean) / self.std
        
        # Simple linear model
        self.weights = np.linalg.lstsq(X_norm, y, rcond=None)[0]
        
        self.model = {
            'weights': self.weights,
            'mean': self.mean,
            'std': self.std
        }
    
    def predict(self, deployment_metrics: Dict) -> Dict:
        """Predict deployment risk"""
        if self.model is None:
            raise ValueError("Model not fitted")
        
        features = [
            deployment_metrics.get('risk_score', 50),
            deployment_metrics.get('files_changed', 10),
            deployment_metrics.get('lines_added', 100),
            deployment_metrics.get('lines_removed', 50),
            deployment_metrics.get('test_coverage', 0.8),
            deployment_metrics.get('previous_failures', 0)
        ]
        
        # Normalize
        X = np.array(features)
        X_norm = (X - self.model['mean']) / self.model['std']
        
        # Predict
        success_prob = np.dot(X_norm, self.model['weights'])
        success_prob = 1 / (1 + np.exp(-success_prob))  # Sigmoid
        
        # Calculate risk score
        risk_score = (1 - success_prob) * 100
        
        # Determine strategy
        if risk_score < 30:
            strategy = 'rolling'
        elif risk_score < 60:
            strategy = 'canary'
        else:
            strategy = 'blue-green'
        
        return {
            'success_probability': float(success_prob),
            'risk_score': float(risk_score),
            'recommended_strategy': strategy,
            'rollback_probability': float(1 - success_prob),
            'performance_impact': self._predict_performance_impact(deployment_metrics)
        }
    
    def _predict_performance_impact(self, metrics: Dict) -> str:
        """Predict performance impact"""
        risk_score = metrics.get('risk_score', 50)
        
        if risk_score < 20:
            return 'none'
        elif risk_score < 40:
            return 'low'
        elif risk_score < 70:
            return 'medium'
        else:
            return 'high'


class DeploymentStrategyOptimizer:
    """Optimizes deployment strategy"""
    
    def __init__(self):
        self.strategies = {
            'rolling': {
                'description': 'Gradually replace instances',
                'risk_threshold': 30,
                'rollback_time': 5,
                'downtime': 0
            },
            'canary': {
                'description': 'Deploy to small subset first',
                'risk_threshold': 60,
                'rollback_time': 2,
                'downtime': 0
            },
            'blue-green': {
                'description': 'Deploy to separate environment',
                'risk_threshold': 100,
                'rollback_time': 1,
                'downtime': 0
            }
        }
    
    def optimize(self, risk_score: float, 
                 deployment_metrics: Dict) -> Dict:
        """Optimize deployment strategy"""
        # Determine optimal strategy
        if risk_score < 30:
            strategy = 'rolling'
        elif risk_score < 60:
            strategy = 'canary'
        else:
            strategy = 'blue-green'
        
        # Get strategy details
        strategy_details = self.strategies[strategy]
        
        # Generate optimization recommendations
        recommendations = self._generate_recommendations(
            strategy, risk_score, deployment_metrics
        )
        
        return {
            'strategy': strategy,
            'description': strategy_details['description'],
            'rollback_time': strategy_details['rollback_time'],
            'downtime': strategy_details['downtime'],
            'recommendations': recommendations
        }
    
    def _generate_recommendations(self, strategy: str, risk_score: float,
                                 metrics: Dict) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if strategy == 'canary':
            recommendations.append('Monitor canary for 15 minutes')
            recommendations.append('Check error rate and latency')
            recommendations.append('Validate user experience')
        
        elif strategy == 'blue-green':
            recommendations.append('Run full test suite in green environment')
            recommendations.append('Validate all endpoints')
            recommendations.append('Check database migrations')
        
        if risk_score > 50:
            recommendations.append('Consider additional testing')
            recommendations.append('Review code changes')
            recommendations.append('Notify stakeholders')
        
        return recommendations


class PerformanceAnalyzer:
    """Analyzes deployment performance"""
    
    def __init__(self):
        self.baselines = {
            'latency_p95': 0.5,
            'error_rate': 0.01,
            'throughput': 1000,
            'availability': 0.999
        }
    
    def analyze(self, current_metrics: Dict, 
                baseline_metrics: Dict) -> Dict:
        """Analyze deployment performance"""
        analysis = {}
        
        # Compare latency
        current_latency = current_metrics.get('latency_p95', 0)
        baseline_latency = baseline_metrics.get('latency_p95', self.baselines['latency_p95'])
        latency_change = (current_latency - baseline_latency) / baseline_latency
        
        analysis['latency'] = {
            'current': current_latency,
            'baseline': baseline_latency,
            'change': latency_change,
            'status': 'normal' if abs(latency_change) < 0.1 else 'degraded'
        }
        
        # Compare error rate
        current_error_rate = current_metrics.get('error_rate', 0)
        baseline_error_rate = baseline_metrics.get('error_rate', self.baselines['error_rate'])
        error_rate_change = current_error_rate - baseline_error_rate
        
        analysis['error_rate'] = {
            'current': current_error_rate,
            'baseline': baseline_error_rate,
            'change': error_rate_change,
            'status': 'normal' if error_rate_change < 0.01 else 'degraded'
        }
        
        # Compare throughput
        current_throughput = current_metrics.get('throughput', 0)
        baseline_throughput = baseline_metrics.get('throughput', self.baselines['throughput'])
        throughput_change = (current_throughput - baseline_throughput) / baseline_throughput
        
        analysis['throughput'] = {
            'current': current_throughput,
            'baseline': baseline_throughput,
            'change': throughput_change,
            'status': 'normal' if abs(throughput_change) < 0.1 else 'degraded'
        }
        
        # Overall assessment
        statuses = [analysis[metric]['status'] for metric in analysis]
        if all(status == 'normal' for status in statuses):
            analysis['overall'] = 'healthy'
        elif any(status == 'degraded' for status in statuses):
            analysis['overall'] = 'degraded'
        else:
            analysis['overall'] = 'critical'
        
        return analysis


class DeploymentReporter:
    """Generates deployment reports"""
    
    def generate(self, deployment_metrics: Dict, risk_prediction: Dict,
                 strategy_optimization: Dict, performance_analysis: Dict) -> Dict:
        """Generate deployment report"""
        report = {
            'summary': {
                'deployment_id': deployment_metrics.get('deployment_id', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'strategy': strategy_optimization['strategy'],
                'risk_score': risk_prediction['risk_score'],
                'success_probability': risk_prediction['success_probability'],
                'performance_status': performance_analysis['overall']
            },
            'risk_assessment': risk_prediction,
            'strategy': strategy_optimization,
            'performance_analysis': performance_analysis,
            'recommendations': strategy_optimization['recommendations']
        }
        
        return report


def main():
    """Main function"""
    print("=" * 60)
    print("Exercise 4.2: Intelligent Deployment Pipeline")
    print("=" * 60)
    
    # Generate deployment history
    print("\n1. Generating deployment history...")
    simulator = DeploymentSimulator()
    history = simulator.generate_history(n_deployments=100)
    print(f"   Generated {len(history)} deployments")
    
    # Train risk predictor
    print("\n2. Training deployment risk predictor...")
    predictor = DeploymentRiskPredictor()
    predictor.fit(history)
    print("   Model trained")
    
    # Simulate new deployment
    print("\n3. Simulating new deployment...")
    new_deployment = {
        'deployment_id': 'DEP-NEW-001',
        'risk_score': 45,
        'files_changed': 15,
        'lines_added': 250,
        'lines_removed': 50,
        'test_coverage': 0.85,
        'previous_failures': 1
    }
    print(f"   Deployment: {new_deployment['deployment_id']}")
    print(f"   Risk Score: {new_deployment['risk_score']}")
    
    # Predict risk
    print("\n4. Predicting deployment risk...")
    risk_prediction = predictor.predict(new_deployment)
    print(f"   Success Probability: {risk_prediction['success_probability']:.1%}")
    print(f"   Risk Score: {risk_prediction['risk_score']:.1f}")
    print(f"   Recommended Strategy: {risk_prediction['recommended_strategy']}")
    
    # Optimize strategy
    print("\n5. Optimizing deployment strategy...")
    optimizer = DeploymentStrategyOptimizer()
    strategy_optimization = optimizer.optimize(
        risk_prediction['risk_score'],
        new_deployment
    )
    print(f"   Strategy: {strategy_optimization['strategy']}")
    print(f"   Description: {strategy_optimization['description']}")
    print(f"   Rollback Time: {strategy_optimization['rollback_time']} minutes")
    
    # Analyze performance
    print("\n6. Analyzing deployment performance...")
    analyzer = PerformanceAnalyzer()
    current_metrics = {
        'latency_p95': 0.45,
        'error_rate': 0.008,
        'throughput': 1050
    }
    baseline_metrics = {
        'latency_p95': 0.5,
        'error_rate': 0.01,
        'throughput': 1000
    }
    performance_analysis = analyzer.analyze(current_metrics, baseline_metrics)
    print(f"   Performance Status: {performance_analysis['overall']}")
    
    # Generate report
    print("\n7. Generating deployment report...")
    reporter = DeploymentReporter()
    report = reporter.generate(
        new_deployment,
        risk_prediction,
        strategy_optimization,
        performance_analysis
    )
    
    with open('deployment_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print("   Report saved to deployment_report.json")
    
    print("\n" + "=" * 60)
    print("Intelligent Deployment Pipeline Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
