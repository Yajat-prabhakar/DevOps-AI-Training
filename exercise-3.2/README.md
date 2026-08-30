# Exercise 3.2: Application Performance Intelligence

## Overview

Implement AI-driven application monitoring with performance regression detection, user behavior analysis, traffic prediction, and automated scaling recommendations.

## Objectives

1. Monitor application response times and error rates
2. Detect performance regressions in deployment pipelines
3. Implement user behavior anomaly detection
4. Create predictive models for traffic and load patterns
5. Build automated scaling recommendations
6. Generate performance optimization insights and recommendations

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│            Application Performance Intelligence              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Latency    │  │    Error     │  │   Traffic    │       │
│  │  Analysis    │  │   Analysis   │  │  Prediction  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Scaling    │  │  Regression  │  │   Health     │       │
│  │ Recommendations│  │  Detection   │  │   Scoring    │       │
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
exercise-3.2/
├── prometheus/
│   ├── prometheus.yml                  # Main Prometheus config
│   └── rules/
│       ├── performance-rules.yml       # Recording rules
│       └── alerts.yml                  # Alerting rules
├── grafana/
│   └── dashboards/
│       └── performance-intelligence.json  # Performance dashboard
├── ml-models/
│   └── traffic_prediction.py           # ML traffic prediction
├── simulation/
│   └── performance_simulator.py        # Performance scenario simulator
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

### 3. Run ML Traffic Prediction

```bash
cd ml-models
pip install numpy pandas
python traffic_prediction.py
```

### 4. Run Performance Simulation

```bash
cd simulation

# Latency spike scenario
python performance_simulator.py latency_spike 300

# Error spike scenario
python performance_simulator.py error_spike 300

# Throughput drop scenario
python performance_simulator.py throughput_drop 300

# Cascading failure scenario
python performance_simulator.py cascading_failure 300

# Load test
python performance_simulator.py load 60 100
```

## Components

### 1. Performance Metrics

**HTTP Metrics:**
- `http:request_rate:rate1m` - Request rate per service
- `http:error_rate:rate1m` - Error rate per service
- `http:latency_p50:histogram` - 50th percentile latency
- `http:latency_p95:histogram` - 95th percentile latency
- `http:latency_p99:histogram` - 99th percentile latency
- `http:throughput:rps` - Throughput (requests/second)
- `http:availability:ratio` - Availability ratio

**Database Metrics:**
- `db:query_rate:rate1m` - Query rate
- `db:cache_hit_ratio:ratio` - Cache hit ratio
- `db:connections:count` - Connection count
- `db:rollback_rate:rate1m` - Rollback rate
- `db:deadlocks:rate1m` - Deadlock rate

**Cache Metrics:**
- `redis:hit_rate:ratio` - Redis hit rate
- `redis:memory_usage:bytes` - Redis memory usage
- `redis:ops_rate:rate1m` - Operations per second

**Queue Metrics:**
- `queue:depth:count` - Queue depth
- `queue:consume_rate:rate1m` - Consume rate
- `queue:latency:rate1m` - Message latency

### 2. Performance Regression Detection

**Latency Regression:**
```promql
http:latency_p95:histogram > http:latency_mean:rate1m + 2 * http:latency_stddev:rate1m
```

**Error Rate Regression:**
```promql
http:error_rate:rate1m > 0.05
```

**Throughput Regression:**
```promql
http:throughput:rps < avg_over_time(http:throughput:rps[1h]) * 0.7
```

### 3. Scaling Recommendations

**CPU Scaling:**
```promql
node:cpu_usage_rate:avg5m > 0.7
```

**Memory Scaling:**
```promql
node:memory_usage_rate:avg5m > 0.8
```

**Database Connection Scaling:**
```promql
db:connections:count > 80
```

**Cache Scaling:**
```promql
redis:hit_rate:ratio < 0.9
```

**Queue Scaling:**
```promql
queue:depth:count > 1000
```

### 4. Health Scoring

**HTTP Health Score (0-100):**
```
score = http:availability:ratio * 100
```

**Database Health Score (0-100):**
```
score = db:cache_hit_ratio:ratio * 100
```

**Cache Health Score (0-100):**
```
score = redis:hit_rate:ratio * 100
```

**Overall Performance Health Score:**
```
score = http_health * 0.4 + db_health * 0.3 + cache_health * 0.3
```

### 5. ML Traffic Prediction

**Features:**
- Hour of day (0-23)
- Day of week (0-6)
- Polynomial features for non-linear patterns

**Predictions:**
- Traffic forecast for next 24 hours
- Confidence intervals (95%)
- Anomaly detection based on predicted bounds

**Scaling Recommendations:**
- Scale out based on predicted peak traffic
- Scale up based on current resource usage
- Investigate traffic anomalies

### 6. Performance Optimization Insights

**Latency Optimization:**
- Optimize database queries
- Add caching
- Review slow queries
- Consider indexing

**Error Rate Optimization:**
- Investigate errors
- Add error handling
- Improve logging

**Cache Optimization:**
- Review cache strategy
- Increase TTL
- Optimize key expiration

**Availability Optimization:**
- Check service health
- Add redundancy
- Implement circuit breakers

## Alerting Rules

### Latency Alerts
- `HighLatencyP95` - p95 latency > 2s
- `CriticalLatency` - p95 latency > 5s
- `LatencyAnomaly` - Latency anomaly score > 2.5

### Error Rate Alerts
- `HighErrorRate` - Error rate > 5%
- `CriticalErrorRate` - Error rate > 10%
- `ErrorRateRegression` - Error rate regression detected

### Throughput Alerts
- `LowThroughput` - Throughput < 10 rps
- `ThroughputRegression` - Throughput regression detected

### Availability Alerts
- `LowAvailability` - Availability < 99%
- `CriticalAvailability` - Availability < 95%

### Database Alerts
- `HighDatabaseConnections` - Connections > 80
- `LowCacheHitRatio` - Cache hit ratio < 90%
- `HighRollbackRate` - Rollback rate > 1%
- `DatabaseDeadlocks` - Deadlocks detected

### Cache Alerts
- `LowRedisHitRate` - Redis hit rate < 90%
- `HighRedisMemory` - Redis memory > 1GB

### Queue Alerts
- `HighQueueDepth` - Queue depth > 1000
- `QueueConsumerBacklog` - Queue depth > 5000

### User Behavior Alerts
- `HighErrorPagesPerUser` - Error pages per user > 0.1
- `LowConversionRate` - Conversion rate < 1%

### Deployment Alerts
- `LowDeploymentSuccessRate` - Success rate < 90%
- `HighRollbackRate` - Rollback rate > 10%

### Performance Health Alerts
- `LowPerformanceHealth` - Health score < 70
- `CriticalPerformanceHealth` - Health score < 50

## Simulation Scenarios

### Latency Spike
- Sudden increase in response latency
- Expected alert: `HighLatencyP95`
- Action: Check database queries, optimize slow endpoints

### Error Spike
- Increase in HTTP error rates
- Expected alert: `HighErrorRate`
- Action: Check application logs, investigate errors

### Throughput Drop
- Decrease in request throughput
- Expected alert: `LowThroughput`
- Action: Check load balancer, verify service health

### Cascading Failure
- Multiple performance issues occurring together
- Expected alert: `CriticalPerformanceHealth`
- Action: Immediate investigation required

## Load Testing

### Load Test Results
- Total requests
- Average latency
- p95 latency
- p99 latency
- Error rate

### Endpoint Breakdown
- Latency by endpoint
- Error rate by endpoint
- Throughput by endpoint

## Troubleshooting

### Common Issues

1. **High latency**
   - Check database queries
   - Optimize slow endpoints
   - Add caching

2. **High error rate**
   - Check application logs
   - Investigate errors
   - Add error handling

3. **Low throughput**
   - Check load balancer
   - Verify service health
   - Scale instances

4. **Low availability**
   - Check service health
   - Add redundancy
   - Implement circuit breakers

## References

- [Prometheus Histograms](https://prometheus.io/docs/practices/histograms/)
- [Grafana Performance Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [Performance Best Practices](https://prometheus.io/docs/practices/)
