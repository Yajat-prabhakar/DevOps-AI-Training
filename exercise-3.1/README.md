# Exercise 3.1: Enterprise Anomaly Detection System

## Overview

Build a comprehensive ML-powered monitoring solution with intelligent anomaly detection, predictive alerting, and health scoring for infrastructure and applications.

## Objectives

1. Deploy Grafana ML with Prometheus and Loki integration
2. Configure anomaly detection for CPU, memory, network, and disk metrics
3. Implement log anomaly detection for application and system logs
4. Create predictive models for capacity planning and scaling
5. Set up intelligent alerting with reduced false positives
6. Build executive dashboards with health scoring and trends

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Grafana ML Dashboard                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Anomaly    │  │  Predictive  │  │    Health    │       │
│  │  Detection   │  │  Forecasting │  │   Scoring    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────┴───────┐   ┌───────┴───────┐
            │  Prometheus   │   │     Loki      │
            │   (Metrics)   │   │    (Logs)     │
            └───────────────┘   └───────────────┘
                    │                   │
            ┌───────┴───────┐   ┌───────┴───────┐
            │  ML Models    │   │  Log Parser   │
            │  (Prophet/    │   │  (JSON/Regex) │
            │   ARIMA)      │   │               │
            └───────────────┘   └───────────────┘
```

## Directory Structure

```
exercise-3.1/
├── prometheus/
│   ├── prometheus.yml              # Main Prometheus config
│   ├── alertmanager.yml            # Alertmanager config
│   └── rules/
│       ├── anomaly-detection.yml   # Recording rules
│       └── alerts.yml              # Alerting rules
├── grafana/
│   ├── dashboards/
│   │   └── anomaly-detection.json  # Main dashboard
│   └── provisioning/
│       └── datasources.yml         # Datasource provisioning
├── loki/
│   └── loki-config.yml             # Loki configuration
├── ml-models/
│   └── anomaly_detection.py        # ML model simulation
├── simulation/
│   └── anomaly_simulator.py        # Anomaly injection simulator
└── README.md                       # This file
```

## Quick Start

### 1. Start Prometheus

```bash
# Start Prometheus with custom config
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v $(pwd)/prometheus/rules:/etc/prometheus/rules \
  prom/prometheus:latest \
  --config.file=/etc/prometheus/prometheus.yml
```

### 2. Start Alertmanager

```bash
# Start Alertmanager
docker run -d \
  --name alertmanager \
  -p 9093:9093 \
  -v $(pwd)/prometheus/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
  prom/alertmanager:latest
```

### 3. Start Loki

```bash
# Start Loki with custom config
docker run -d \
  --name loki \
  -p 3100:3100 \
  -v $(pwd)/loki/loki-config.yml:/etc/loki/local-config.yaml \
  grafana/loki:latest \
  -config.file=/etc/loki/local-config.yaml
```

### 4. Start Grafana

```bash
# Start Grafana with ML plugins
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v $(pwd)/grafana/provisioning:/etc/grafana/provisioning \
  -v $(pwd)/grafana/dashboards:/var/lib/grafana/dashboards \
  -e "GF_INSTALL_PLUGINS=grafana-ml-app" \
  grafana/grafana:latest
```

### 5. Run ML Model Simulation

```bash
# Install dependencies
pip install numpy pandas

# Run anomaly detection simulation
cd ml-models
python anomaly_detection.py
```

### 6. Run Anomaly Injection Simulator

```bash
# Run anomaly injection
cd simulation

# CPU spike scenario
python anomaly_simulator.py cpu_spike 300

# Memory leak scenario
python anomaly_simulator.py memory_leak 300

# Disk thrashing scenario
python anomaly_simulator.py disk_thrash 300

# Network flood scenario
python anomaly_simulator.py network_flood 300
```

## Components

### 1. Prometheus Configuration

**Recording Rules** (`rules/anomaly-detection.yml`):
- CPU anomaly detection with Z-score calculation
- Memory leak detection with trend analysis
- Disk I/O anomaly detection
- Network traffic anomaly detection
- Health score calculation

**Alerting Rules** (`rules/alerts.yml`):
- HighCpuAnomalyScore
- CriticalCpuSpike
- CpuUsagePrediction
- HighMemoryAnomalyScore
- MemoryLeakDetected
- MemoryExhaustionPrediction
- HighDiskIoAnomalyScore
- DiskSpaceExhaustionPrediction
- HighNetworkAnomalyScore
- NetworkSpikeDetected
- HighResponseTimeAnomalyScore
- LowOverallHealthScore

### 2. Grafana Dashboard

**Anomaly Detection Dashboard** (`dashboards/anomaly-detection.json`):
- Infrastructure Health Score (stat panel)
- Active Anomalies (stat panel)
- CPU/Memory Anomaly Scores (stat panels)
- CPU/Memory Usage with Anomaly Bounds (timeseries)
- Disk I/O with Anomaly Bounds (timeseries)
- Network Traffic with Anomaly Bounds (timeseries)
- CPU/Memory Anomaly Score Trends (timeseries)
- Application Response Time Anomaly (timeseries)
- Health Score Breakdown (bargauge)
- Firing Alerts (table)

### 3. ML Models

**Prophet Forecaster** (`ml-models/anomaly_detection.py`):
- Time series forecasting with trend and seasonality
- Uncertainty estimation with confidence intervals
- Anomaly detection using predicted bounds

**ARIMA Forecaster**:
- Autoregressive integrated moving average
- Residual-based anomaly detection

**Ensemble Detector**:
- Combines Prophet and ARIMA predictions
- Robust anomaly detection with multiple models

### 4. Anomaly Injection Simulator

**Simulator** (`simulation/anomaly_simulator.py`):
- Real-time metrics simulation
- Anomaly injection with various scenarios
- CPU spike, memory leak, disk thrashing, network flood
- Cascading failure simulation

## Anomaly Detection Methods

### Z-Score Method

```python
zscore = (value - mean) / std
anomaly = abs(zscore) > threshold  # threshold = 2 or 3
```

### Prophet Method

```python
# Fit model
model.fit(df)

# Predict
forecast = model.predict(periods)

# Detect anomalies
anomaly = value < forecast['yhat_lower'] or value > forecast['yhat_upper']
```

### Ensemble Method

```python
# Combine predictions from multiple models
prophet_anomaly = prophet.detect(df)
arima_anomaly = arima.detect(df)

# Ensemble: anomaly if either model detects
anomaly = prophet_anomaly['anomaly'] or arima_anomaly['anomaly']
```

## Metrics Collected

### CPU Metrics
- `cpu_usage_percent` - Current CPU usage
- `cpu_usage_rate` - CPU usage rate (5-minute average)
- `cpu_anomaly_score` - Z-score for CPU anomalies
- `cpu_spike_detected` - Binary spike detection

### Memory Metrics
- `memory_usage_percent` - Current memory usage
- `memory_usage_rate` - Memory usage rate (5-minute average)
- `memory_anomaly_score` - Z-score for memory anomalies
- `memory_leak_detected` - Binary leak detection

### Disk Metrics
- `disk_usage_percent` - Current disk usage
- `disk_io_rate` - Disk I/O rate (5-minute average)
- `disk_anomaly_score` - Z-score for disk anomalies
- `disk_exhaustion_predicted` - Binary prediction

### Network Metrics
- `network_rx_rate` - Network receive rate
- `network_tx_rate` - Network transmit rate
- `network_anomaly_score` - Z-score for network anomalies
- `network_spike_detected` - Binary spike detection

### Application Metrics
- `http_requests_rate` - HTTP request rate
- `http_errors_rate` - HTTP error rate
- `response_time_p95` - 95th percentile response time
- `response_time_anomaly_score` - Z-score for response time

## Health Scoring

### Component Health Scores (0-100)

**CPU Health Score:**
```
score = clamp(100 - (cpu_usage * 100), 0, 100)
```

**Memory Health Score:**
```
score = clamp(100 - (memory_usage * 100), 0, 100)
```

**Disk Health Score:**
```
score = clamp(100 - (disk_usage * 100), 0, 100)
```

**Overall Health Score (Weighted):**
```
score = cpu * 0.3 + memory * 0.3 + disk * 0.4
```

### Health Score Thresholds

- **Excellent:** 80-100
- **Good:** 60-79
- **Warning:** 40-59
- **Critical:** 0-39

## Intelligent Alerting

### Alert Categories

**Anomaly Alerts:**
- Triggered by Z-score > threshold
- Reduced false positives with statistical methods
- Context-aware notification routing

**Prediction Alerts:**
- Triggered by trend extrapolation
- Early warning for capacity issues
- Proactive issue resolution

**Health Alerts:**
- Triggered by health score thresholds
- Composite scoring across multiple metrics
- Executive-level reporting

### Alert Suppression

- **Group by:** alertname, instance
- **Group wait:** 30 seconds
- **Group interval:** 5 minutes
- **Repeat interval:** 1-4 hours

### Inhibition Rules

- Critical alerts suppress warning alerts
- Same alertname and instance required

## Integration Points

### Prometheus Integration

- Metrics collection from multiple sources
- Recording rules for anomaly detection
- Alerting rules for threshold-based alerts
- Remote write for long-term storage

### Grafana Integration

- Real-time dashboards with ML panels
- Anomaly visualization with bounds
- Health score dashboards
- Alert management UI

### Loki Integration

- Log aggregation from multiple sources
- Log anomaly detection with patterns
- Correlation with metrics
- Structured logging support

## Advanced Features

### Capacity Planning

```python
# Predict resource exhaustion
predict_linear(disk_avail_bytes[6h], 24 * 3600) < 0
```

### Trend Analysis

```python
# Detect sustained increases
memory_usage_rate - memory_usage_rate offset 1h > 0.1
```

### Correlation Analysis

```python
# Correlate metrics for root cause analysis
cpu_spike and memory_spike and disk_spike
```

## Troubleshooting

### Common Issues

1. **No data in Grafana**
   - Check Prometheus is running
   - Verify datasources in Grafana
   - Check network connectivity

2. **Alerts not firing**
   - Verify alert rules are loaded
   - Check Alertmanager configuration
   - Ensure metrics are being collected

3. **Anomalies not detected**
   - Check Z-score thresholds
   - Verify data quality
   - Adjust sensitivity parameters

4. **High false positive rate**
   - Increase Z-score threshold
   - Add more training data
   - Use ensemble methods

## References

- [Grafana ML Documentation](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/annotate-visualizations/)
- [Prometheus Recording Rules](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
- [Anomaly Detection Methods](https://en.wikipedia.org/wiki/Anomaly_detection)
- [Z-Score Method](https://en.wikipedia.org/wiki/Standard_score)
