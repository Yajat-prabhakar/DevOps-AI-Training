#!/usr/bin/env python3
"""
ML Model Simulation for Anomaly Detection
Exercise 3.1: Enterprise Anomaly Detection System

This script simulates time series forecasting and anomaly detection
using Facebook Prophet and ARIMA models.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import sys
from typing import Dict, List, Tuple

class TimeSeriesSimulator:
    """Simulates time series data with anomalies"""
    
    def __init__(self, base_value: float = 50.0, trend: float = 0.1, 
                 seasonality: float = 10.0, noise: float = 5.0):
        self.base_value = base_value
        self.trend = trend
        self.seasonality = seasonality
        self.noise = noise
    
    def generate(self, periods: int = 24 * 7, freq: str = 'h') -> pd.DataFrame:
        """Generate time series data"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), 
                             periods=periods, freq=freq)
        
        # Base trend
        trend = np.linspace(self.base_value, 
                           self.base_value + self.trend * periods, periods)
        
        # Seasonality (24-hour cycle)
        seasonal = self.seasonality * np.sin(2 * np.pi * np.arange(periods) / 24)
        
        # Weekly seasonality
        weekly = 5 * np.sin(2 * np.pi * np.arange(periods) / (24 * 7))
        
        # Random noise
        noise = np.random.normal(0, self.noise, periods)
        
        # Combine
        values = trend + seasonal + weekly + noise
        
        return pd.DataFrame({
            'ds': dates,
            'y': values
        })
    
    def inject_anomalies(self, df: pd.DataFrame, 
                         n_anomalies: int = 5,
                         anomaly_type: str = 'spike') -> pd.DataFrame:
        """Inject anomalies into the data"""
        df = df.copy()
        anomaly_indices = np.random.choice(len(df), n_anomalies, replace=False)
        
        for idx in anomaly_indices:
            if anomaly_type == 'spike':
                df.loc[idx, 'y'] *= np.random.uniform(2, 4)
            elif anomaly_type == 'dip':
                df.loc[idx, 'y'] *= np.random.uniform(0.2, 0.5)
            elif anomaly_type == 'shift':
                df.loc[idx:, 'y'] += np.random.uniform(10, 30)
        
        return df, anomaly_indices


class ProphetForecaster:
    """Simulates Prophet-like forecasting"""
    
    def __init__(self):
        self.model = None
    
    def fit(self, df: pd.DataFrame) -> None:
        """Fit the model (simulated)"""
        self.model = {
            'trend': np.polyfit(range(len(df)), df['y'], 1),
            'seasonality': self._extract_seasonality(df),
            'mean': df['y'].mean(),
            'std': df['y'].std()
        }
    
    def _extract_seasonality(self, df: pd.DataFrame) -> float:
        """Extract seasonal component (simplified)"""
        if len(df) >= 24:
            return np.mean(df['y'].values[:24])
        return 0
    
    def predict(self, periods: int = 24) -> pd.DataFrame:
        """Generate predictions (simulated)"""
        if self.model is None:
            raise ValueError("Model not fitted")
        
        future_dates = pd.date_range(start=datetime.now(), 
                                    periods=periods, freq='h')
        
        # Trend prediction
        trend = np.polyval(self.model['trend'], 
                          range(len(self.model['trend'])))
        
        # Add seasonality
        seasonal = self.model['seasonality'] * np.sin(
            2 * np.pi * np.arange(periods) / 24
        )
        
        # Predictions with uncertainty
        predictions = self.model['mean'] + seasonal[:periods]
        
        return pd.DataFrame({
            'ds': future_dates,
            'yhat': predictions,
            'yhat_lower': predictions - 2 * self.model['std'],
            'yhat_upper': predictions + 2 * self.model['std']
        })
    
    def detect_anomalies(self, df: pd.DataFrame, 
                         threshold: float = 2.0) -> pd.DataFrame:
        """Detect anomalies using predicted bounds"""
        if self.model is None:
            raise ValueError("Model not fitted")
        
        predictions = self.predict(len(df))
        
        df = df.copy()
        df['yhat'] = predictions['yhat'].values[:len(df)]
        df['yhat_lower'] = predictions['yhat_lower'].values[:len(df)]
        df['yhat_upper'] = predictions['yhat_upper'].values[:len(df)]
        
        # Calculate Z-scores
        df['zscore'] = (df['y'] - self.model['mean']) / self.model['std']
        
        # Detect anomalies
        df['anomaly'] = (df['y'] < df['yhat_lower']) | (df['y'] > df['yhat_upper'])
        df['anomaly_score'] = np.abs(df['zscore'])
        
        return df


class ARIMAForecaster:
    """Simulates ARIMA-like forecasting"""
    
    def __init__(self, order: Tuple[int, int, int] = (1, 1, 1)):
        self.order = order
        self.model = None
    
    def fit(self, df: pd.DataFrame) -> None:
        """Fit the model (simulated)"""
        # Simple ARIMA simulation
        values = df['y'].values
        
        # Calculate differencing
        diff = np.diff(values) if self.order[1] > 0 else values
        
        # Calculate moving average
        ma = np.convolve(diff, np.ones(self.order[2])/self.order[2], mode='valid')
        
        self.model = {
            'ar_coef': np.polyfit(range(len(values)-1), values[1:], 1),
            'ma_coef': ma.mean() if len(ma) > 0 else 0,
            'mean': values.mean(),
            'std': values.std(),
            'last_value': values[-1]
        }
    
    def predict(self, periods: int = 24) -> pd.DataFrame:
        """Generate predictions (simulated)"""
        if self.model is None:
            raise ValueError("Model not fitted")
        
        future_dates = pd.date_range(start=datetime.now(), 
                                    periods=periods, freq='h')
        
        # Simple prediction
        predictions = []
        last = self.model['last_value']
        
        for i in range(periods):
            # AR component
            ar = np.polyval(self.model['ar_coef'], last)
            # MA component
            ma = self.model['ma_coef']
            # Prediction
            pred = last + ar * 0.1 + ma * 0.1
            predictions.append(pred)
            last = pred
        
        predictions = np.array(predictions)
        
        return pd.DataFrame({
            'ds': future_dates,
            'yhat': predictions,
            'yhat_lower': predictions - 2 * self.model['std'],
            'yhat_upper': predictions + 2 * self.model['std']
        })
    
    def detect_anomalies(self, df: pd.DataFrame, 
                         threshold: float = 2.0) -> pd.DataFrame:
        """Detect anomalies using residuals"""
        if self.model is None:
            raise ValueError("Model not fitted")
        
        predictions = self.predict(len(df))
        
        df = df.copy()
        df['yhat'] = predictions['yhat'].values[:len(df)]
        df['yhat_lower'] = predictions['yhat_lower'].values[:len(df)]
        df['yhat_upper'] = predictions['yhat_upper'].values[:len(df)]
        
        # Calculate residuals
        df['residual'] = df['y'] - df['yhat']
        df['zscore'] = df['residual'] / self.model['std']
        
        # Detect anomalies
        df['anomaly'] = (df['y'] < df['yhat_lower']) | (df['y'] > df['yhat_upper'])
        df['anomaly_score'] = np.abs(df['zscore'])
        
        return df


class AnomalyDetector:
    """Combines multiple models for robust anomaly detection"""
    
    def __init__(self):
        self.prophet = ProphetForecaster()
        self.arima = ARIMAForecaster()
    
    def fit(self, df: pd.DataFrame) -> None:
        """Fit both models"""
        self.prophet.fit(df)
        self.arima.fit(df)
    
    def detect(self, df: pd.DataFrame, 
               method: str = 'ensemble') -> pd.DataFrame:
        """Detect anomalies using specified method"""
        if method == 'prophet':
            return self.prophet.detect_anomalies(df)
        elif method == 'arima':
            return self.arima.detect_anomalies(df)
        elif method == 'ensemble':
            prophet_result = self.prophet.detect_anomalies(df)
            arima_result = self.arima.detect_anomalies(df)
            
            # Ensemble: anomaly if either model detects
            df = df.copy()
            df['anomaly'] = prophet_result['anomaly'] | arima_result['anomaly']
            df['anomaly_score'] = (prophet_result['anomaly_score'] + 
                                  arima_result['anomaly_score']) / 2
            df['prophet_anomaly'] = prophet_result['anomaly']
            df['arima_anomaly'] = arima_result['anomaly']
            
            return df
    
    def forecast(self, periods: int = 24) -> Dict:
        """Generate ensemble forecast"""
        prophet_forecast = self.prophet.predict(periods)
        arima_forecast = self.arima.predict(periods)
        
        return {
            'prophet': prophet_forecast.to_dict('records'),
            'arima': arima_forecast.to_dict('records'),
            'ensemble': {
                'yhat': ((prophet_forecast['yhat'].values + 
                         arima_forecast['yhat'].values) / 2).tolist(),
                'yhat_lower': ((prophet_forecast['yhat_lower'].values + 
                               arima_forecast['yhat_lower'].values) / 2).tolist(),
                'yhat_upper': ((prophet_forecast['yhat_upper'].values + 
                               arima_forecast['yhat_upper'].values) / 2).tolist()
            }
        }


def main():
    """Main simulation function"""
    print("=" * 60)
    print("Exercise 3.1: ML Model Simulation for Anomaly Detection")
    print("=" * 60)
    
    # Create simulator
    simulator = TimeSeriesSimulator(
        base_value=50,
        trend=0.1,
        seasonality=10,
        noise=5
    )
    
    # Generate data
    print("\n1. Generating time series data...")
    df = simulator.generate(periods=24 * 7)  # 1 week of hourly data
    print(f"   Generated {len(df)} data points")
    
    # Inject anomalies
    print("\n2. Injecting anomalies...")
    df_anomaly, anomaly_indices = simulator.inject_anomalies(
        df, n_anomalies=10, anomaly_type='spike'
    )
    print(f"   Injected {len(anomaly_indices)} anomalies")
    print(f"   Anomaly indices: {anomaly_indices}")
    
    # Create detector
    print("\n3. Training ML models...")
    detector = AnomalyDetector()
    detector.fit(df_anomaly)
    print("   Prophet model fitted")
    print("   ARIMA model fitted")
    
    # Detect anomalies
    print("\n4. Detecting anomalies...")
    results = detector.detect(df_anomaly, method='ensemble')
    
    detected_anomalies = results[results['anomaly'] == True]
    print(f"   Detected {len(detected_anomalies)} anomalies")
    
    # Calculate metrics
    true_positives = len(set(anomaly_indices) & set(detected_anomalies.index))
    false_positives = len(detected_anomalies) - true_positives
    false_negatives = len(anomaly_indices) - true_positives
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\n   Metrics:")
    print(f"   - True Positives: {true_positives}")
    print(f"   - False Positives: {false_positives}")
    print(f"   - False Negatives: {false_negatives}")
    print(f"   - Precision: {precision:.2%}")
    print(f"   - Recall: {recall:.2%}")
    print(f"   - F1 Score: {f1_score:.2%}")
    
    # Generate forecast
    print("\n5. Generating forecast...")
    forecast = detector.forecast(periods=24)
    print(f"   Generated {len(forecast['ensemble']['yhat'])} prediction points")
    
    # Save results
    print("\n6. Saving results...")
    results_df = pd.DataFrame({
        'timestamp': results['ds'],
        'value': results['y'],
        'predicted': results['yhat'],
        'lower_bound': results['yhat_lower'],
        'upper_bound': results['yhat_upper'],
        'anomaly_score': results['anomaly_score'],
        'is_anomaly': results['anomaly']
    })
    results_df.to_csv('anomaly_detection_results.csv', index=False)
    print("   Results saved to anomaly_detection_results.csv")
    
    # Generate report
    report = {
        'summary': {
            'total_data_points': len(df),
            'anomalies_injected': len(anomaly_indices),
            'anomalies_detected': len(detected_anomalies),
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        },
        'forecast': {
            'periods': 24,
            'ensemble_mean': float(np.mean(forecast['ensemble']['yhat'])),
            'ensemble_std': float(np.std(forecast['ensemble']['yhat']))
        }
    }
    
    with open('anomaly_detection_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print("   Report saved to anomaly_detection_report.json")
    
    print("\n" + "=" * 60)
    print("Simulation complete!")
    print("=" * 60)
    
    return results, forecast, report


if __name__ == '__main__':
    results, forecast, report = main()
