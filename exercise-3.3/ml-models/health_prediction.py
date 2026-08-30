#!/usr/bin/env python3
"""
ML Model for Infrastructure Health Prediction
Exercise 3.3: Infrastructure Health Prediction

This script simulates infrastructure health prediction and maintenance scheduling.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import sys
from typing import Dict, List, Tuple


class InfrastructureSimulator:
    """Simulates infrastructure metrics"""
    
    def __init__(self):
        self.components = {
            'cpu': {'base': 50, 'trend': 0.1, 'noise': 5},
            'memory': {'base': 60, 'trend': 0.05, 'noise': 3},
            'disk': {'base': 70, 'trend': 0.02, 'noise': 2},
            'network': {'base': 30, 'trend': 0.1, 'noise': 10},
            'security': {'base': 90, 'trend': -0.01, 'noise': 5}
        }
    
    def generate(self, periods: int = 24 * 30) -> pd.DataFrame:
        """Generate infrastructure metrics"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                             periods=periods, freq='h')
        
        data = {'timestamp': dates}
        
        for component, config in self.components.items():
            # Base value
            base = config['base']
            
            # Trend
            trend = config['trend'] * np.arange(periods)
            
            # Noise
            noise = np.random.normal(0, config['noise'], periods)
            
            # Combine
            values = base + trend + noise
            values = np.maximum(0, np.minimum(100, values))
            
            data[f'{component}_usage'] = values
        
        return pd.DataFrame(data)


class HealthPredictor:
    """Predicts infrastructure health"""
    
    def __init__(self):
        self.model = None
    
    def fit(self, df: pd.DataFrame) -> None:
        """Fit the model"""
        # Simple linear regression for each component
        self.model = {}
        
        for col in df.columns:
            if col == 'timestamp':
                continue
            
            values = df[col].values
            x = np.arange(len(values))
            
            # Fit linear regression
            coeffs = np.polyfit(x, values, 1)
            
            self.model[col] = {
                'coeffs': coeffs,
                'mean': values.mean(),
                'std': values.std()
            }
    
    def predict(self, hours: int = 24) -> pd.DataFrame:
        """Predict future health"""
        if self.model is None:
            raise ValueError("Model not fitted")
        
        future_dates = pd.date_range(start=datetime.now(), periods=hours, freq='h')
        
        predictions = {'timestamp': future_dates}
        
        for col, model in self.model.items():
            x = np.arange(len(future_dates))
            
            # Predict using linear model
            pred = np.polyval(model['coeffs'], x)
            
            predictions[f'{col}_predicted'] = pred
            predictions[f'{col}_lower'] = pred - 2 * model['std']
            predictions[f'{col}_upper'] = pred + 2 * model['std']
        
        return pd.DataFrame(predictions)
    
    def calculate_health_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate health scores"""
        df = df.copy()
        
        # Health score = 100 - usage
        for col in df.columns:
            if col == 'timestamp':
                continue
            
            if '_usage' in col:
                component = col.replace('_usage', '')
                df[f'{component}_health'] = 100 - df[col]
        
        # Overall health score (weighted)
        df['overall_health'] = (
            df.get('cpu_health', 50) * 0.2 +
            df.get('memory_health', 50) * 0.2 +
            df.get('disk_health', 50) * 0.3 +
            df.get('network_health', 50) * 0.2 +
            df.get('security_health', 50) * 0.1
        )
        
        return df


class MaintenanceScheduler:
    """Schedules maintenance based on health predictions"""
    
    def __init__(self):
        self.thresholds = {
            'disk_critical': 90,
            'disk_warning': 80,
            'network_critical': 80,
            'network_warning': 70,
            'cpu_critical': 90,
            'cpu_warning': 80,
            'memory_critical': 90,
            'memory_warning': 80,
            'security_critical': 50,
            'security_warning': 60
        }
    
    def schedule(self, predictions: pd.DataFrame) -> List[Dict]:
        """Schedule maintenance based on predictions"""
        maintenance = []
        
        # Check each component
        for component in ['cpu', 'memory', 'disk', 'network', 'security']:
            if f'{component}_predicted' in predictions.columns:
                max_predicted = predictions[f'{component}_predicted'].max()
                
                # Determine priority
                if max_predicted > self.thresholds.get(f'{component}_critical', 90):
                    priority = 'critical'
                    action = f'Schedule immediate {component} maintenance'
                elif max_predicted > self.thresholds.get(f'{component}_warning', 80):
                    priority = 'warning'
                    action = f'Schedule {component} maintenance within 7 days'
                else:
                    continue
                
                # Find when threshold will be exceeded
                threshold = self.thresholds.get(f'{component}_warning', 80)
                exceed_idx = predictions[predictions[f'{component}_predicted'] > threshold].index
                
                if len(exceed_idx) > 0:
                    days_until = (exceed_idx[0] - predictions.index[0]) / 24
                else:
                    days_until = 30  # Default to 30 days
                
                maintenance.append({
                    'component': component,
                    'priority': priority,
                    'action': action,
                    'current_usage': float(predictions[f'{component}_predicted'].iloc[0]),
                    'predicted_usage': float(max_predicted),
                    'days_until_threshold': float(days_until)
                })
        
        return maintenance


class CostOptimizer:
    """Generates cost optimization recommendations"""
    
    def __init__(self):
        self.hourly_costs = {
            'cpu': 0.05,  # $0.05 per core per hour
            'memory': 0.01,  # $0.01 per GB per hour
            'disk': 0.001,  # $0.001 per GB per hour
            'network': 0.01  # $0.01 per GB transferred
        }
    
    def analyze(self, metrics: Dict) -> List[Dict]:
        """Analyze costs and generate recommendations"""
        recommendations = []
        
        # Check CPU utilization
        cpu_usage = metrics.get('cpu', 0)
        if cpu_usage < 30:
            recommendations.append({
                'component': 'cpu',
                'current_usage': cpu_usage,
                'recommendation': 'Consider right-sizing CPU resources',
                'potential_savings': f'${self.hourly_costs["cpu"] * 4 * 24 * 30:.2f}/month'
            })
        
        # Check memory utilization
        memory_usage = metrics.get('memory', 0)
        if memory_usage < 40:
            recommendations.append({
                'component': 'memory',
                'current_usage': memory_usage,
                'recommendation': 'Consider right-sizing memory resources',
                'potential_savings': f'${self.hourly_costs["memory"] * 16 * 24 * 30:.2f}/month'
            })
        
        # Check disk utilization
        disk_usage = metrics.get('disk', 0)
        if disk_usage < 50:
            recommendations.append({
                'component': 'disk',
                'current_usage': disk_usage,
                'recommendation': 'Consider deleting unused data or snapshots',
                'potential_savings': f'${self.hourly_costs["disk"] * 100 * 24 * 30:.2f}/month'
            })
        
        return recommendations


class ReportGenerator:
    """Generates infrastructure health reports"""
    
    def generate(self, metrics: Dict, predictions: pd.DataFrame, 
                 maintenance: List[Dict], cost_recommendations: List[Dict]) -> Dict:
        """Generate comprehensive report"""
        report = {
            'summary': {
                'timestamp': datetime.now().isoformat(),
                'overall_health_score': float(metrics.get('overall_health', 0)),
                'components': {}
            },
            'health_scores': {},
            'predictions': {},
            'maintenance_schedule': maintenance,
            'cost_recommendations': cost_recommendations
        }
        
        # Add component health scores
        for component in ['cpu', 'memory', 'disk', 'network', 'security']:
            if f'{component}_health' in metrics:
                report['health_scores'][component] = {
                    'score': float(metrics[f'{component}_health']),
                    'usage': float(metrics.get(f'{component}_usage', 0))
                }
        
        # Add predictions
        if predictions is not None and len(predictions) > 0:
            for col in predictions.columns:
                if '_predicted' in col:
                    component = col.replace('_predicted', '')
                    report['predictions'][component] = {
                        'predicted_values': predictions[col].tolist(),
                        'max_predicted': float(predictions[col].max()),
                        'min_predicted': float(predictions[col].min())
                    }
        
        return report


def main():
    """Main function"""
    print("=" * 60)
    print("Exercise 3.3: Infrastructure Health Prediction")
    print("=" * 60)
    
    # Generate infrastructure metrics
    print("\n1. Generating infrastructure metrics...")
    simulator = InfrastructureSimulator()
    df = simulator.generate(periods=24 * 30)  # 30 days of hourly data
    print(f"   Generated {len(df)} data points")
    
    # Calculate health scores
    print("\n2. Calculating health scores...")
    predictor = HealthPredictor()
    df_health = predictor.calculate_health_score(df)
    
    current_health = df_health.iloc[-1]
    print(f"   Current health scores:")
    print(f"     - CPU: {current_health.get('cpu_health', 0):.1f}/100")
    print(f"     - Memory: {current_health.get('memory_health', 0):.1f}/100")
    print(f"     - Disk: {current_health.get('disk_health', 0):.1f}/100")
    print(f"     - Network: {current_health.get('network_health', 0):.1f}/100")
    print(f"     - Security: {current_health.get('security_health', 0):.1f}/100")
    print(f"     - Overall: {current_health.get('overall_health', 0):.1f}/100")
    
    # Train predictor
    print("\n3. Training health predictor...")
    predictor.fit(df_health)
    print("   Model trained")
    
    # Predict future health
    print("\n4. Predicting future health...")
    predictions = predictor.predict(hours=24 * 7)  # 7 days
    print(f"   Predicted {len(predictions)} hours")
    
    # Schedule maintenance
    print("\n5. Scheduling maintenance...")
    scheduler = MaintenanceScheduler()
    maintenance = scheduler.schedule(predictions)
    print(f"   Scheduled {len(maintenance)} maintenance tasks:")
    for task in maintenance:
        print(f"     - [{task['priority'].upper()}] {task['action']}")
    
    # Analyze costs
    print("\n6. Analyzing costs...")
    optimizer = CostOptimizer()
    current_metrics = {
        'cpu': float(current_health.get('cpu_usage', 0)),
        'memory': float(current_health.get('memory_usage', 0)),
        'disk': float(current_health.get('disk_usage', 0)),
        'network': float(current_health.get('network_usage', 0))
    }
    cost_recommendations = optimizer.analyze(current_metrics)
    print(f"   Generated {len(cost_recommendations)} cost recommendations:")
    for rec in cost_recommendations:
        print(f"     - {rec['recommendation']}")
    
    # Generate report
    print("\n7. Generating report...")
    report_generator = ReportGenerator()
    report = report_generator.generate(
        current_health.to_dict(),
        predictions,
        maintenance,
        cost_recommendations
    )
    
    with open('infrastructure_health_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print("   Report saved to infrastructure_health_report.json")
    
    # Save predictions
    predictions.to_csv('health_predictions.csv', index=False)
    print("   Predictions saved to health_predictions.csv")
    
    print("\n" + "=" * 60)
    print("Infrastructure Health Prediction Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
