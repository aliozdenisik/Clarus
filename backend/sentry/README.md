# Sentry Configuration

This directory contains configuration files for Sentry alerts and dashboards.

## Task 13: Alert Rules Setup

Navigate to **Sentry Dashboard → Alerts → Create Alert Rule** and create the following 4 alerts:

### 1. High Error Rate Alert

| Setting | Value |
|---------|-------|
| **Name** | High Error Rate |
| **Type** | Issue Alert |
| **Condition** | Number of events > 50 in 1 hour |
| **Filter** | Level: error, fatal |
| **Environment** | production |
| **Project** | python |
| **Description** | Error rate exceeds 50 events per hour. See: RUNBOOKS.md#error-rate-high |

**Steps:**
1. Go to Alerts → Create Alert Rule → Issue Alert
2. Set "When" to: "A new issue is created" OR "The issue is seen more than 50 times in 1 hour"
3. Set "Filter" to: `level:error OR level:fatal`
4. Set "Then" to: "Send a notification to Sentry"
5. Add description with runbook link

### 2. High Latency Alert (p95 > 60s)

| Setting | Value |
|---------|-------|
| **Name** | High Latency (p95 > 60s) |
| **Type** | Metric Alert |
| **Metric** | transaction.duration |
| **Aggregation** | p95 |
| **Threshold** | > 60000ms (60 seconds) |
| **Time Window** | 5 minutes |
| **Filter** | `transaction:app.api.stream.* OR transaction:rag.*` |
| **Environment** | production |
| **Description** | Transaction p95 latency exceeds 60 seconds. See: RUNBOOKS.md#latency-high |

**Steps:**
1. Go to Alerts → Create Alert Rule → Metric Alert
2. Select metric: "transaction.duration"
3. Set aggregation: "p95"
4. Set threshold: "> 60000 ms"
5. Set time window: "5 minutes"
6. Add filter: `transaction:app.api.stream.* OR transaction:rag.*`

### 3. Circuit Breaker OPEN Alert

| Setting | Value |
|---------|-------|
| **Name** | Circuit Breaker OPEN |
| **Type** | Issue Alert |
| **Condition** | First seen |
| **Filter** | `message:"Circuit breaker OPEN"` |
| **Environment** | production |
| **Project** | python |
| **Description** | Circuit breaker has opened due to failures. See: RUNBOOKS.md#circuit-breaker-open |

**Steps:**
1. Go to Alerts → Create Alert Rule → Issue Alert
2. Set "When" to: "A new issue is created"
3. Set "Filter" to: `message:*Circuit breaker OPEN*`
4. Set action: "Send notification immediately"

### 4. LLM Error Rate Critical

| Setting | Value |
|---------|-------|
| **Name** | LLM Error Rate Critical |
| **Type** | Metric Alert |
| **Metric** | span failure rate |
| **Threshold** | > 20% |
| **Time Window** | 15 minutes |
| **Filter** | `span.op:llm.* OR span.op:http.client` with `*openrouter*` |
| **Severity** | Critical |
| **Description** | LLM call failure rate exceeds 20%. See: RUNBOOKS.md#llm-error-rate |

**Steps:**
1. Go to Alerts → Create Alert Rule → Metric Alert
2. Select metric: "failure_rate()" or custom span metrics
3. Set threshold: "> 20%"
4. Filter by span operation containing "llm" or "openrouter"
5. Set severity to Critical

---

## Task 14: RAG Pipeline Dashboard Setup

Navigate to **Sentry Dashboard → Dashboards → Create Dashboard**

### Dashboard Name
**RAG Pipeline Performance**

### Widgets to Create

#### 1. Query Count (24h) - Big Number
- **Query**: `count()`
- **Filter**: `transaction:app.api.stream.* OR transaction:rag.*`
- **Display**: Big Number

#### 2. Average Latency - Table
- **Fields**: transaction, p50(duration), p95(duration), p99(duration)
- **Filter**: `transaction:app.api.stream.* OR transaction:rag.*`
- **Order by**: p95 descending

#### 3. Error Rate - Line Chart
- **Query**: `failure_rate()`
- **Filter**: `transaction:app.api.stream.* OR transaction:rag.*`
- **Display**: Line chart over time

#### 4. Per-Agent Breakdown - Table
- **Fields**: span.op, count(), avg(duration), p95(duration)
- **Filter**: `span.op:rag.agent.*`
- **Display**: Table

#### 5. Cache Hit Rate - Big Number
- **Query**: Count where `span.data.cache_hit = true` / total count
- **Filter**: `span.op:embedding.* OR span.op:llm.*`

#### 6. LLM Cost (Daily) - Line Chart
- **Query**: `sum(measurements.llm.cost.estimated)`
- **Filter**: `has:measurements.llm.cost.estimated`
- **Display**: Line chart by day

#### 7. LLM Token Usage - Area Chart
- **Queries**:
  - `sum(measurements.llm.tokens.input)`
  - `sum(measurements.llm.tokens.output)`
- **Display**: Stacked area chart

#### 8. Top Slow Transactions - Table
- **Fields**: transaction, count(), p95(duration)
- **Filter**: `transaction:app.api.* OR transaction:rag.*`
- **Order by**: p95 descending
- **Limit**: 10

### After Creating Dashboard
1. Click "Export" or copy dashboard ID
2. Save configuration to `dashboards/rag-pipeline.json`

---

## Quick Links

- **Sentry Dashboard**: https://claruss.sentry.io
- **Alerts**: https://claruss.sentry.io/alerts/rules/
- **Dashboards**: https://claruss.sentry.io/dashboards/
- **Runbooks**: [RUNBOOKS.md](../RUNBOOKS.md)

## Files

- `alerts/alert-rules.json` - Alert rule configurations (reference)
- `dashboards/rag-pipeline.json` - Dashboard widget configurations (reference)
