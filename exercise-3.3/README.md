# Exercise 3.3: Infrastructure Health Prediction

## Overview

Develop predictive infrastructure monitoring with disk space forecasting, network congestion prediction, security anomaly detection, cost optimization recommendations, and automated maintenance scheduling.

## Objectives

1. Analyze historical failure patterns for predictive maintenance
2. Implement disk space and resource exhaustion forecasting
3. Create network congestion and performance prediction models
4. Build security anomaly detection for infrastructure access
5. Implement cost optimization recommendations based on usage patterns
6. Generate automated infrastructure health reports

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│          Infrastructure Health Prediction System             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Disk      │  │   Network    │  │   Security   │       │
│  │  Prediction  │  │  Prediction  │  │  Detection   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Cost      │  │ Maintenance  │  │   Health     │       │
│  │ Optimization │  │  Scheduling  │  │   Scoring    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
            ┌───────┴───────┐   ┌───────┴───────┐
            │  Prometheus   │   │    Grafana    │
            │   (Metrics)   │   │  (Dashboard)  │
            └───────────────┘   └───────────────┘
```

## Directory Structure

```
exercise-3.3/
├── prometheus/
│   ├── prometheus.yml                  # Main Prometheus config
│   └── rules/
│       ├── health-prediction.yml       # Recording rules
│       └── alerts.yml                  # Alerting rules
├── grafana/
│   └── dashboards/
│       └── infrastructure-health.json  # Health prediction dashboard
├── ml-models/
│   └── health_prediction.py            # ML health prediction
├── simulation/
│   └── infrastructure_simulator.py     # Infrastructure scenario simulator
└── README.md                           # This file
```

## Quick Start

### 1. Start Prometheus

```bash
docker run -d \
  --name prometheus \
  -p 9090:9090 \
  -v $(pwd)/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v $(pwd)/prometheus/rules:/etc/prometheus/rules \
  prom/prometheus:latest
```

### 2. Start Grafana

```bash
docker run -d \
  --name grafana \
  -p 3000:3000 \
  -v $(pwd)/grafana/dashboards:/var/lib/grafana/dashboards \
  grafana/grafana:latest
```

### 3. Run ML Health Prediction

```bash
cd ml-models
pip install numpy pandas
python health_prediction.py
```

### 4. Run Infrastructure Simulation

```bash
cd simulation

# Disk exhaustion scenario
python infrastructure_simulator.py disk_exhaustion 300

# Memory leak scenario
python infrastructure_simulator.py memory_leak 300

# CPU spike scenario
python infrastructure_simulator.py cpu_spike 300

# Network congestion scenario
python infrastructure_simulator.py network_congestion 300

# Security breach scenario
python infrastructure_simulator.py security_breach 300
```

## Components

### 1. Disk Health Prediction

**Metrics:**
- `infra:disk_usage:current` - Current disk usage
- `infra:disk_usage:trend1h` - Disk usage trend (1 hour)
- `infra:disk_usage:trend6h` - Disk usage trend (6 hours)
- `infra:disk_exhaustion:predicted24h` - Exhaustion predicted in 24 hours
- `infra:disk_exhaustion:predicted7d` - Exhaustion predicted in 7 days
- `infra:disk_exhaustion:days_until` - Days until exhaustion
- `infra:disk_health:score` - Disk health score (0-100)

**Prediction Method:**
```promql
# Predict disk exhaustion in 24 hours
predict_linear(node_filesystem_avail_bytes[6h], 24 * 3600) < 0

# Calculate days until exhaustion
node_filesystem_avail_bytes / (abs deriv(node_filesystem_avail_bytes[6h]) * 86400)
```

### 2. Network Health Prediction

**Metrics:**
- `infra:network_utilization:current` - Current network utilization
- `infra:network_utilization:trend1h` - Network utilization trend
- `infra:network_saturation:predicted1h` - Saturation predicted in 1 hour
- `infra:network_errors:rate1m` - Network error rate
- `infra:network_health:score` - Network health score (0-100)

**Prediction Method:**
```promql
# Predict network saturation
predict_linear(
  rate(node_network_receive_bytes_total[1h]) + rate(node_network_transmit_bytes_total[1h]),
  3600
) > 1e9
```

### 3. CPU Health Prediction

**Metrics:**
- `infra:cpu_utilization:current` - Current CPU utilization
- `infra:cpu_utilization:trend1h` - CPU utilization trend
- `infra:cpu_saturation:predicted1h` - Saturation predicted in 1 hour
- `infra:cpu_load:average` - CPU load average
- `infra:cpu_health:score` - CPU health score (0-100)

**Prediction Method:**
```promql
# Predict CPU saturation
predict_linear(
  avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[1h])),
  3600
) > 0.9
```

### 4. Memory Health Prediction

**Metrics:**
- `infra:memory_utilization:current` - Current memory utilization
- `infra:memory_utilization:trend1h` - Memory utilization trend
- `infra:memory_exhaustion:predicted4h` - Exhaustion predicted in 4 hours
- `infra:memory_health:score` - Memory health score (0-100)

**Prediction Method:**
```promql
# Predict memory exhaustion
predict_linear(node_memory_MemAvailable_bytes[1h], 4 * 3600) < 0
```

### 5. Security Health Prediction

**Metrics:**
- `infra:security:failed_logins:rate1h` - Failed login rate
- `infra:security:open_ports:count` - Open ports count
- `infra:security_health:score` - Security health score (0-100)

**Detection Method:**
```promql
# Detect high failed login rate
infra:security:failed_logins:rate1h > 10
```

### 6. Cost Health Prediction

**Metrics:**
- `infra:cost:trend1d` - Daily cost trend
- `infra:cost:predicted30d` - 30-day cost prediction
- `infra:cost_health:score` - Cost health score (0-100)

**Prediction Method:**
```promql
# Predict 30-day cost
predict_linear(aws_billing_total_cost_amount[1d], 30 * 24 * 3600)
```

### 7. Overall Infrastructure Health

**Health Score Calculation:**
```
overall_health = cpu_health * 0.2 + memory_health * 0.2 + disk_health * 0.3 + network_health * 0.2 + security_health * 0.1
```

**Health Trend:**
```promql
# Calculate health trend
deriv(infra:health_score_overall:score[1h])

# Predict health in 24 hours
predict_linear(infra:health_score_overall:score[6h], 24 * 3600)
```

### 8. Maintenance Scheduling

**Maintenance Rules:**
- Disk maintenance needed when `infra:maintenance:disk_needed == 1`
- Network maintenance needed when `infra:maintenance:network_needed == 1`
- Security maintenance needed when `infra:maintenance:security_needed == 1`

**Priority Calculation:**
```
priority = disk_maintenance * 0.4 + network_maintenance * 0.3 + security_maintenance * 0.3
```

### 9. Cost Optimization

**Cost Analysis:**
- Right-sizing CPU resources when utilization < 30%
- Right-sizing memory resources when utilization < 40%
- Deleting unused data when disk utilization < 50%

**Potential Savings Calculation:**
```
savings = hourly_cost * resource_count * 24 * 30
```

## Alerting Rules

### Disk Alerts
- `DiskSpaceCritical` - Disk usage > 90%
- `DiskSpaceWarning` - Disk usage > 80%
- `DiskExhaustionPredicted` - Exhaustion predicted in 24 hours
- `DiskExhaustionPredicted7d` - Exhaustion predicted in 7 days
- `LowDiskHealthScore` - Health score < 40

### Network Alerts
- `NetworkSaturationPredicted` - Saturation predicted in 1 hour
- `HighNetworkErrorRate` - Error rate > 0.01
- `LowNetworkHealthScore` - Health score < 40

### CPU Alerts
- `CpuSaturationPredicted` - Saturation predicted in 1 hour
- `LowCpuHealthScore` - Health score < 40

### Memory Alerts
- `MemoryExhaustionPredicted` - Exhaustion predicted in 4 hours
- `LowMemoryHealthScore` - Health score < 40

### Security Alerts
- `HighFailedLogins` - Failed login rate > 10/hour
- `LowSecurityHealthScore` - Health score < 40

### Infrastructure Health Alerts
- `LowInfrastructureHealth` - Overall health < 60
- `CriticalInfrastructureHealth` - Overall health < 40
- `HealthTrendDeclining` - Health trend < -5 points/hour

### Maintenance Alerts
- `DiskMaintenanceNeeded` - Disk maintenance required
- `NetworkMaintenanceNeeded` - Network maintenance required
- `SecurityMaintenanceNeeded` - Security maintenance required
- `HighMaintenancePriority` - High priority maintenance

### Cost Alerts
- `CostTrendIncreasing` - Daily cost trend increasing
- `CostPredictionHigh` - 30-day cost prediction > $10,000

## Simulation Scenarios

### Disk Exhaustion
- Disk space running low
- Expected alert: `DiskExhaustionPredicted`
- Action: Clean up disk space or add more storage

### Memory Leak
- Memory usage increasing due to leak
- Expected alert: `MemoryExhaustionPredicted`
- Action: Investigate memory usage, consider adding more memory

### CPU Spike
- CPU usage spike due to runaway process
- Expected alert: `CpuSaturationPredicted`
- Action: Investigate process list, check for DDoS

### Network Congestion
- Network traffic spike causing congestion
- Expected alert: `NetworkSaturationPredicted`
- Action: Investigate source, consider upgrading network

### Security Breach
- Security incident detected
- Expected alert: `HighFailedLogins`
- Action: Review security, check for unauthorized access

## ML Health Prediction

**Model Features:**
- Time series data for each component
- Linear regression for trend detection
- Polynomial features for non-linear patterns

**Predictions:**
- Future health scores for next 7 days
- Confidence intervals (95%)
- Maintenance scheduling based on predictions

**Maintenance Scheduling:**
- Critical maintenance when usage > threshold
- Warning maintenance when usage approaching threshold
- Days until threshold exceeded

## Cost Optimization

**Recommendations:**
- Right-sizing CPU resources
- Right-sizing memory resources
- Deleting unused data
- Optimizing storage tiers

**Savings Calculation:**
- Hourly cost per resource
- Monthly savings potential
- ROI analysis

## Troubleshooting

### Common Issues

1. **High disk usage**
   - Clean up logs and temporary files
   - Archive old data
   - Add more storage

2. **High memory usage**
   - Check for memory leaks
   - Optimize applications
   - Add more memory

3. **High CPU usage**
   - Check for runaway processes
   - Optimize code
   - Add more CPU cores

4. **Network congestion**
   - Check for DDoS attacks
   - Upgrade network capacity
   - Optimize traffic routing

## References

- [Prometheus Predictions](https://prometheus.io/docs/prometheus/latest/querying/functions/#predict_linear)
- [Infrastructure Monitoring Best Practices](https://prometheus.io/docs/practices/)
- [Cost Optimization Strategies](https://aws.amazon.com/aws-cost-management/)
