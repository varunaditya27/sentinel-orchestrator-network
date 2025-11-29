# Hydra Performance Report Template

## Overview
This template is used to document performance measurements for the Hydra speed layer in the Sentinel Orchestrator Network (SON). Fill in the measured values during demo runs and compare against targets.

## Test Environment
- **Date**: YYYY-MM-DD
- **Hardware**: [e.g., MacBook Pro M2, 16GB RAM]
- **Software**: Docker version X.X.X, Hydra version X.X.X
- **Network**: Localhost (mock mode)
- **Load**: Single-threaded sequential requests

## Performance Targets (Mock Mode)
- Open Head: <50ms
- Submit Order: <20ms
- Close Head: <100ms
- End-to-End (open + submit + close): <200ms
- Throughput: 200-500 orders/sec (stress test)

## Latency Measurements

### Open Head Operation
- **Target**: <50ms
- **Measured Average**: ___ ms
- **Measured P95**: ___ ms
- **Measured P99**: ___ ms
- **Sample Count**: ___

### Submit Order Operation
- **Target**: <20ms
- **Measured Average**: ___ ms
- **Measured P95**: ___ ms
- **Measured P99**: ___ ms
- **Sample Count**: ___

### Close Head Operation
- **Target**: <100ms
- **Measured Average**: ___ ms
- **Measured P95**: ___ ms
- **Measured P99**: ___ ms
- **Sample Count**: ___

### End-to-End Flow
- **Target**: <200ms
- **Measured Average**: ___ ms
- **Measured P95**: ___ ms
- **Measured P99**: ___ ms
- **Sample Count**: ___

## Throughput Measurements

### Sequential Orders (1 head, multiple orders)
- **Orders Processed**: ___
- **Total Time**: ___ seconds
- **Throughput**: ___ orders/sec

### Concurrent Heads (Multiple sessions)
- **Concurrent Heads**: ___
- **Orders per Head**: ___
- **Total Orders**: ___
- **Total Time**: ___ seconds
- **Throughput**: ___ orders/sec

### Stress Test (High load)
- **Target Load**: 500 orders/sec
- **Achieved Load**: ___ orders/sec
- **Error Rate**: ___%
- **Average Latency**: ___ ms
- **P99 Latency**: ___ ms

## Resource Utilization

### CPU Usage
- **Hydra Node**: ___%
- **Mock Control App**: ___%
- **Docker Host**: ___%

### Memory Usage
- **Hydra Node**: ___ MB
- **Mock Control App**: ___ MB
- **Total**: ___ MB

### Network I/O
- **Inbound**: ___ KB/s
- **Outbound**: ___ KB/s

## Sample Latency Logs

### Open Head Samples
```
Open Head #1: 12ms
Open Head #2: 8ms
Open Head #3: 15ms
...
Average: ___ms, P95: ___ms, P99: ___ms
```

### Submit Order Samples
```
Submit Order #1: 5ms
Submit Order #2: 7ms
Submit Order #3: 4ms
...
Average: ___ms, P95: ___ms, P99: ___ms
```

### End-to-End Samples
```
E2E Flow #1: 45ms
E2E Flow #2: 52ms
E2E Flow #3: 38ms
...
Average: ___ms, P95: ___ms, P99: ___ms
```

## Measurement Methodology

### Tools Used
- **Timing**: Python time.perf_counter() in mock app
- **Load Generation**: Sequential curl commands or simple Python script
- **Monitoring**: Docker stats, htop
- **Logging**: Application logs with timestamps

### Test Script Example
```bash
# Measure open head latency
for i in {1..100}; do
  START=$(date +%s%N)
  curl -s -X POST http://localhost:8084/hydra/open -H "Content-Type: application/json" -d '{"session_id":"test-'$i'","participants":["test"],"metadata":{}}' > /dev/null
  END=$(date +%s%N)
  echo $(( (END - START) / 1000000 ))ms
done
```

### Data Collection
- Run each test 100+ times for statistical significance
- Discard first 10 samples (warm-up)
- Calculate average, P95, P99 from remaining samples
- Log all raw measurements for analysis

## Conclusions

### Target Achievement
- [ ] All latency targets met (<50ms open, <20ms submit, <100ms close, <200ms e2e)
- [ ] Throughput target achieved (200-500 orders/sec)
- [ ] No errors under normal load
- [ ] Resource usage acceptable

### Bottlenecks Identified
- [List any performance issues found]

### Recommendations
- [Suggestions for optimization if targets not met]

## Demo Validation Checklist
- [ ] Judges can run docker-compose without other services
- [ ] Demo script executes successfully
- [ ] UI shows ORDER_FINALIZED with proof_ref
- [ ] End-to-end time <200ms measured
- [ ] No crashes or errors during demo

## Raw Data Attachment
[Attach CSV files or logs with raw measurement data]
