#!/usr/bin/env python3
"""
ML Model for Traffic Prediction and Scaling Recommendations
Exercise 3.2: Application Performance Intelligence

This script simulates traffic prediction and automated scaling recommendations.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import sys
from typing import Dict, List, Tuple


class TrafficSimulator:
    """Simulates traffic patterns for prediction"""
    
    def __init__(self):
        self.base_traffic = 1000  # requests per second
        self.daily_pattern = 0.3  # 30% variation
        self.weekly_pattern = 0.2  # 20% variation
        self.noise = 0.1  # 10% random noise
    
    def generate(self, periods: int = 24 * 7) -> pd.DataFrame:
        """Generate traffic data"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), 
                             periods=periods, freq='h')
        
        # Daily pattern (peak during business hours)
        hour = np.array([d.hour for d in dates])
        daily = self.base_traffic * self.daily_pattern * np.sin(
            2 * np.pi * (hour - 6) / 24
        )
        
        # Weekly pattern (higher on weekdays)
        weekday = np.array([d.weekday() for d in dates])
        weekly = self.base_traffic * self.weekly_pattern * np.where(
            weekday < 5, 1, 0.7
        )
        
        # Random noise
        noise = np.random.normal(0, self.base_traffic * self.noise, periods)
        
        # Combine
        traffic = self.base_traffic + daily + weekly + noise
        traffic = np.maximum(traffic, 0)  # No negative traffic
        
        return pd.DataFrame({
            'timestamp': dates,
            'traffic': traffic,
            'hour': hour,
            'weekday': weekday
        })


class TrafficPredictor:
    """Predicts future traffic using ML"""
    
    def __init__(self):
        self.model = None
    
    def fit(self, df: pd.DataFrame) -> None:
        """Fit the model"""
        # Simple regression model
        X = df[['hour', 'weekday']].values
        y = df['traffic'].values
        
        # Add polynomial features
        X_poly = np.column_stack([
            X,
            X[:, 0] ** 2,
            X[:, 1] ** 2,
            X[:, 0] * X[:, 1]
        ])
        
        # Fit linear regression
        self.model = {
            'weights': np.linalg.lstsq(X_poly, y, rcond=None)[0],
            'mean': y.mean(),
            'std': y.std()
        }
    
    def predict(self, hours: int = 24) -> pd.DataFrame:
        """Predict traffic for future hours"""
        if self.model is None:
            raise ValueError("Model not fitted")
        
        future_dates = pd.date_range(start=datetime.now(), periods=hours, freq='h')
        
        predictions = []
        for i, dt in enumerate(future_dates):
            hour = dt.hour
            weekday = dt.weekday()
            
            # Create features
            features = np.array([
                hour,
                weekday,
                hour ** 2,
                weekday ** 2,
                hour * weekday
            ])
            
            # Predict
            pred = np.dot(features, self.model['weights'])
            predictions.append(pred)
        
        predictions = np.array(predictions)
        
        return pd.DataFrame({
            'timestamp': future_dates,
            'predicted_traffic': predictions,
            'lower_bound': predictions - 2 * self.model['std'],
            'upper_bound': predictions + 2 * self.model['std']
        })
    
    def detect_anomalies(self, df: pd.DataFrame, 
                         threshold: float = 2.0) -> pd.DataFrame:
        """Detect traffic anomalies"""
        if self.model is None:
            raise ValueError("Model not fitted")
        
        # Calculate Z-scores
        df = df.copy()
        df['zscore'] = (df['traffic'] - self.model['mean']) / self.model['std']
        
        # Detect anomalies
        df['anomaly'] = np.abs(df['zscore']) > threshold
        df['anomaly_score'] = np.abs(df['zscore'])
        
        return df


class ScalingRecommender:
    """Generates scaling recommendations based on traffic prediction"""
    
    def __init__(self):
        self.thresholds = {
            'cpu_high': 0.7,
            'cpu_critical': 0.9,
            'memory_high': 0.8,
            'memory_critical': 0.95,
            'traffic_high': 1500,
            'traffic_critical': 2000
        }
    
    def recommend(self, current_metrics: Dict, 
                  predicted_traffic: pd.DataFrame) -> List[Dict]:
        """Generate scaling recommendations"""
        recommendations = []
        
        # Check current CPU
        if current_metrics.get('cpu', 0) > self.thresholds['cpu_critical']:
            recommendations.append({
                'type': 'scale_up',
                'resource': 'cpu',
                'priority': 'critical',
                'action': 'Add more CPU cores immediately',
                'reason': f"CPU usage is {current_metrics['cpu']:.1%}"
            })
        elif current_metrics.get('cpu', 0) > self.thresholds['cpu_high']:
            recommendations.append({
                'type': 'scale_up',
                'resource': 'cpu',
                'priority': 'warning',
                'action': 'Consider adding more CPU cores',
                'reason': f"CPU usage is {current_metrics['cpu']:.1%}"
            })
        
        # Check current memory
        if current_metrics.get('memory', 0) > self.thresholds['memory_critical']:
            recommendations.append({
                'type': 'scale_up',
                'resource': 'memory',
                'priority': 'critical',
                'action': 'Add more memory immediately',
                'reason': f"Memory usage is {current_metrics['memory']:.1%}"
            })
        elif current_metrics.get('memory', 0) > self.thresholds['memory_high']:
            recommendations.append({
                'type': 'scale_up',
                'resource': 'memory',
                'priority': 'warning',
                'action': 'Consider adding more memory',
                'reason': f"Memory usage is {current_metrics['memory']:.1%}"
            })
        
        # Check predicted traffic
        if predicted_traffic is not None and len(predicted_traffic) > 0:
            max_predicted = predicted_traffic['predicted_traffic'].max()
            
            if max_predicted > self.thresholds['traffic_critical']:
                recommendations.append({
                    'type': 'scale_out',
                    'resource': 'instances',
                    'priority': 'critical',
                    'action': f"Scale to {int(max_predicted / 500) + 1} instances",
                    'reason': f"Predicted peak traffic: {max_predicted:.0f} rps"
                })
            elif max_predicted > self.thresholds['traffic_high']:
                recommendations.append({
                    'type': 'scale_out',
                    'resource': 'instances',
                    'priority': 'warning',
                    'action': f"Scale to {int(max_predicted / 500) + 1} instances",
                    'reason': f"Predicted peak traffic: {max_predicted:.0f} rps"
                })
        
        # Check for traffic anomalies
        if predicted_traffic is not None:
            if 'anomaly' in predicted_traffic.columns:
                anomalies = predicted_traffic[predicted_traffic['anomaly'] == True]
                if len(anomalies) > 0:
                    recommendations.append({
                        'type': 'investigate',
                        'resource': 'traffic',
                        'priority': 'warning',
                        'action': 'Investigate traffic anomalies',
                        'reason': f"Detected {len(anomalies)} traffic anomalies"
                    })
        
        return recommendations


class PerformanceOptimizer:
    """Generates performance optimization insights"""
    
    def __init__(self):
        self.baselines = {
            'latency_p95': 0.5,  # 500ms
            'error_rate': 0.01,  # 1%
            'availability': 0.999,  # 99.9%
            'cache_hit_rate': 0.95  # 95%
        }
    
    def analyze(self, metrics: Dict) -> List[Dict]:
        """Analyze performance and generate recommendations"""
        recommendations = []
        
        # Check latency
        latency = metrics.get('latency_p95', 0)
        if latency > self.baselines['latency_p95'] * 2:
            recommendations.append({
                'category': 'latency',
                'severity': 'critical',
                'metric': 'latency_p95',
                'current': latency,
                'baseline': self.baselines['latency_p95'],
                'recommendation': 'Optimize database queries, add caching',
                'impact': 'high'
            })
        elif latency > self.baselines['latency_p95'] * 1.5:
            recommendations.append({
                'category': 'latency',
                'severity': 'warning',
                'metric': 'latency_p95',
                'current': latency,
                'baseline': self.baselines['latency_p95'],
                'recommendation': 'Review slow queries, consider indexing',
                'impact': 'medium'
            })
        
        # Check error rate
        error_rate = metrics.get('error_rate', 0)
        if error_rate > self.baselines['error_rate'] * 2:
            recommendations.append({
                'category': 'reliability',
                'severity': 'critical',
                'metric': 'error_rate',
                'current': error_rate,
                'baseline': self.baselines['error_rate'],
                'recommendation': 'Investigate errors, add error handling',
                'impact': 'high'
            })
        
        # Check availability
        availability = metrics.get('availability', 1)
        if availability < self.baselines['availability']:
            recommendations.append({
                'category': 'availability',
                'severity': 'critical',
                'metric': 'availability',
                'current': availability,
                'baseline': self.baselines['availability'],
                'recommendation': 'Check service health, add redundancy',
                'impact': 'high'
            })
        
        # Check cache hit rate
        cache_hit_rate = metrics.get('cache_hit_rate', 1)
        if cache_hit_rate < self.baselines['cache_hit_rate']:
            recommendations.append({
                'category': 'cache',
                'severity': 'warning',
                'metric': 'cache_hit_rate',
                'current': cache_hit_rate,
                'baseline': self.baselines['cache_hit_rate'],
                'recommendation': 'Review cache strategy, increase TTL',
                'impact': 'medium'
            })
        
        return recommendations


def main():
    """Main function"""
    print("=" * 60)
    print("Exercise 3.2: Application Performance Intelligence")
    print("=" * 60)
    
    # Generate traffic data
    print("\n1. Generating traffic data...")
    simulator = TrafficSimulator()
    df = simulator.generate(periods=24 * 7)
    print(f"   Generated {len(df)} data points")
    
    # Train traffic predictor
    print("\n2. Training traffic predictor...")
    predictor = TrafficPredictor()
    predictor.fit(df)
    print("   Model trained")
    
    # Predict future traffic
    print("\n3. Predicting future traffic...")
    predictions = predictor.predict(hours=24)
    print(f"   Predicted {len(predictions)} hours")
    print(f"   Predicted peak: {predictions['predicted_traffic'].max():.0f} rps")
    
    # Detect anomalies
    print("\n4. Detecting traffic anomalies...")
    df_anomaly = predictor.detect_anomalies(df)
    anomalies = df_anomaly[df_anomaly['anomaly'] == True]
    print(f"   Detected {len(anomalies)} anomalies")
    
    # Generate scaling recommendations
    print("\n5. Generating scaling recommendations...")
    current_metrics = {
        'cpu': 0.75,
        'memory': 0.65,
        'latency_p95': 0.8,
        'error_rate': 0.02,
        'availability': 0.995,
        'cache_hit_rate': 0.92
    }
    
    recommender = ScalingRecommender()
    recommendations = recommender.recommend(current_metrics, predictions)
    
    print(f"   Generated {len(recommendations)} recommendations:")
    for rec in recommendations:
        print(f"     - [{rec['priority'].upper()}] {rec['action']}")
    
    # Analyze performance
    print("\n6. Analyzing performance...")
    optimizer = PerformanceOptimizer()
    optimizations = optimizer.analyze(current_metrics)
    
    print(f"   Generated {len(optimizations)} optimization insights:")
    for opt in optimizations:
        print(f"     - [{opt['severity'].upper()}] {opt['recommendation']}")
    
    # Generate report
    print("\n7. Generating report...")
    report = {
        'summary': {
            'total_data_points': len(df),
            'anomalies_detected': len(anomalies),
            'predictions_made': len(predictions),
            'scaling_recommendations': len(recommendations),
            'optimization_insights': len(optimizations)
        },
        'traffic_prediction': {
            'peak_predicted': float(predictions['predicted_traffic'].max()),
            'average_predicted': float(predictions['predicted_traffic'].mean()),
            'anomaly_count': len(anomalies)
        },
        'scaling_recommendations': recommendations,
        'optimization_insights': optimizations
    }
    
    with open('performance_intelligence_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print("   Report saved to performance_intelligence_report.json")
    
    # Save predictions
    predictions.to_csv('traffic_predictions.csv', index=False)
    print("   Predictions saved to traffic_predictions.csv")
    
    print("\n" + "=" * 60)
    print("Performance Intelligence Analysis Complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
