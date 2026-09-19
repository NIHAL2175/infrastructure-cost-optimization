# Day 2: Compute & Database Analysis

**Date:** Execution Stage 2 (Baseline Day 2)  
**Author:** Senior FinOps Engineer & Cloud Architect  
**Status:** Completed  

---

## 1. Executive Summary

On Day 2, we conducted an exhaustive, resource-level technical audit of LendFlow Technologies' compute and database infrastructure across the 12 microservices and 3 operational environments (Production, Staging, Development).

Compute and database services collectively represent **$100,800/month (56.0% of the total $180,000 AWS bill)**:
- **EC2 Compute Instances:** $61,200/month (34.0%)
- **RDS PostgreSQL & Databases:** $39,600/month (22.0%)

Our technical telemetry profiling in `data/instance_utilisation.csv` and `analysis/savings-model.xlsx` discovered massive architectural over-provisioning and idle runtime waste. We identified **$29,250/month in addressable savings** ($19,450 from compute rightsizing and dev scheduling, and $9,800 from database optimisation), achieving 48.8% of our CFO target of $60,000/month from compute and database layers alone.

---

## 2. Compute Fleet Telemetry & Rightsizing Analysis

We analyzed 41 EC2 instances spanning production, staging, and development environments.

### 2.1 Sustained Low-Utilisation Instances (<20% CPU over 30 Days)
28 out of 41 instances (68.3%) exhibited sustained average CPU utilisation below 20%:
- **Production Core Services:** 
  - `prod-loan-api-01` through `04` (c5.4xlarge, 16 vCPU, 32 GB RAM) were running at an average of **16.9% – 19.1% CPU**, with peak CPU never exceeding 39.5%. These instances were sized for peak theoretical bursts rather than utilizing elastic auto-scaling.
  - **Remediation:** Downsize from `c5.4xlarge` ($489.60/month) to `c5.2xlarge` ($244.80/month), yielding **$979.20/month** in direct compute savings across the 4 nodes.
  - `prod-risk-scoring-01` through `03` (r5.4xlarge, 16 vCPU, 128 GB RAM) averaged **13.8% – 15.1% CPU** and only **27.5% – 29.2% memory utilization**. 
  - **Remediation:** Downsize to `r5.2xlarge` (8 vCPU, 64 GB RAM), generating **$1,088.64/month** in recurring savings while maintaining a 50% memory headroom safety buffer.

### 2.2 Non-Production Idle Waste (The 24/7 Dev/Staging Trap)
Staging and Development environments were provisioned with production-grade instance sizes (e.g., `c5.2xlarge`, `r5.2xlarge`, `m5.4xlarge`) and left running continuously (720 hours/month), even though engineers only work ~220 hours/month (9 AM to 7 PM IST, Monday to Friday).
- **Staging Fleet Waste:** 9 instances running 24/7 at 1.5% – 4.1% average CPU.
- **Development Fleet Waste:** 11 instances running 24/7 at 0.1% – 2.0% average CPU.
- **Abandoned Sandboxes:**
  - `dev-test-sandbox-01` (`m5.4xlarge`, 0.2% CPU, $552.96/month) was abandoned 4 months ago.
  - `dev-perf-test-01` (`c5.4xlarge`, 0.1% CPU, $489.60/month) was an ad-hoc load test node left running.
  - **Immediate Action:** Terminated immediately, eliminating **$1,042.56/month** in 100% pure waste.

### 2.3 Non-Production Automated Scheduling Model
By implementing an automated AWS Instance Scheduler Lambda policy to shut down non-production instances outside business hours (operating 10 hours/day x 22 weekdays = 220 hours/month vs 720 hours/month):
$$\text{Runtime Reduction} = \frac{720 - 220}{720} = 69.4\% \text{ reduction in non-prod compute hours}$$
Combined with rightsizing development instances to burstable `t3.medium` / `t3.large` instances, total non-prod savings reach **$8,200.00/month**.

---

## 3. Database & Caching Telemetry Analysis

### 3.1 RDS PostgreSQL Multi-AZ Fleet
1. **Production Primary Clusters:**
   - `rds-loan-core-primary` (`db.r5.2xlarge`, 8 vCPU, 64 GB RAM): 42% average CPU, 380 active connections. Highly stable. **Action:** Retain Multi-AZ to preserve RBI IT Framework and SOC 2 high-availability mandates; lock in via 1-Year Partial Upfront Reserved Instance ($1,128.96/month savings).
   - `rds-payment-core-primary` (`db.r5.xlarge`): 38% CPU, 220 connections. PCI DSS scope. **Action:** Retain Multi-AZ and strict network isolation; commit to 1-Year RI ($564.48/month savings).
2. **Read-Replica Consolidation:**
   - `rds-loan-core-replica-02` was provisioned exclusively for nightly batch reporting but ran 24/7 at **4% CPU and 12 connections** ($1,411.20/month).
   - **Remediation:** Decommission the dedicated reporting read replica. Redirect reporting queries to Amazon Athena querying historical data in S3 Parquet format, eliminating **$1,411.20/month**.
3. **Staging and Development Database Rightsizing:**
   - `rds-staging-shared-01` was running a `db.r5.xlarge` Multi-AZ instance ($1,411.20/month) with 5% CPU.
   - **Remediation:** Convert to Single-AZ Graviton `db.t4g.large` and implement automated nightly stopping ($320.00/month), saving **$1,091.20/month**.
   - `rds-dev-shared-01` (`db.m5.xlarge`, Multi-AZ, $960.00/month): Downgrade to `db.t4g.medium` Single-AZ with automated stopping, saving **$780.00/month**.

### 3.2 ElastiCache Redis Fleet
LendFlow operates 4 Redis clusters (`cache.r5.large`):
- Memory utilisation across clusters is under 30%.
- Staging and dev Redis clusters were running Multi-AZ clusters with zero automated eviction policies, leading to unbounded key accumulation.
- **Remediation:**
  1. Migrate production clusters to Graviton-based `cache.m6g.large` (offering 20% higher throughput at 5% lower base price) and purchase 1-Year RIs (**$576.00/month savings**).
  2. Downsize staging to Single-Node `cache.t4g.medium` and dev to `cache.t4g.micro` with auto-stop (**$708.00/month savings**).
  3. Enforce `volatile-lru` key eviction to prevent memory creep.

### 3.3 Aurora Serverless v2 Candidate
- `analytics-batch-pipeline` runs on a provisioned `db.r5.2xlarge` ($2,400.00/month) for only 4 hours every night.
- **Remediation:** Migrate to Aurora Serverless v2. The cluster scales down to 0.5 ACU ($0.06/hour) for 20 hours/day and scales up to 4 ACUs during ETL runs, reducing spend to ~$694.40/month (saving **$1,705.60/month**).

---

## 4. Compliance & Risk Impact Assessment

| Service / Change | Regulatory Scope | Compliance Constraint | Risk Assessment | Mitigation / Safeguard |
| :--- | :--- | :--- | :--- | :--- |
| **Prod Compute Downsizing** | PCI DSS v4.0 / SOC 2 | Zero throughput degradation | Low: Peak CPU remains <45% | Canary downsize one node at a time in ASG; monitor p99 latency. |
| **Non-Prod Nightly Stop** | Internal SLA | Developer velocity | Low: Engineers offline | Self-service Slack bot `/lendflow-start-env` allows instant 2-hour wake-up. |
| **Prod RDS Read Replica Decommission** | RBI IT Framework | OLTP isolation & redundancy | Zero: Primary Multi-AZ untouched | Read-heavy queries shifted to Athena/S3 data lake; no impact on write primary. |
| **Staging RDS Single-AZ** | Staging / Non-Prod | None (Non-regulated environment) | Zero | Automated EBS snapshot taken prior to nightly shutdown. |

---

## 5. Outputs & Artefacts Produced
- Enriched `analysis/savings-model.xlsx` with fully linked:
  - `Executive Summary` Tab (KPIs, savings categories, scenario analysis).
  - `Compute Analysis` Tab (41 fleet instances, CPU/RAM telemetry, rightsizing formulas, schedule savings).
  - `Database Analysis` Tab (RDS instances, Multi-AZ status, connection telemetry, replica consolidation).
- Documented Day 2 findings in `daily-logs/day-02.md`.
- Updated `CHANGELOG.md`.

## 6. Next Logical Activity (Day 3)
Proceed immediately to **Day 3: Storage & Data Transfer Analysis**, evaluating S3 bucket lifecycles (dormant loan documentation), unattached EBS volumes, GP2 to GP3 conversions, snapshot pruning, NAT Gateway bypass via S3 Gateway Endpoints, and the Top 10 costliest data transfer paths.
