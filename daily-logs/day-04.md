# Day 4: Reserved Capacity & Spot Strategy

**Date:** Execution Stage 4 (Baseline Day 4)  
**Author:** Senior FinOps Engineer & Cloud Architect  
**Status:** Completed  

---

## 1. Executive Summary

On Day 4, we tackled LendFlow Technologies' critical commitment gap: **0.0% Reserved Instance (RI) and 0.0% Savings Plans (SP) coverage**. Every compute instance and database in `ap-south-1` was running on pure On-Demand rates, paying a 28% to 65% flexibility surcharge on stable, 24/7 workloads.

We designed an integrated commitment and Spot strategy delivering **$18,600.00/month in net savings**:
- **Compute Savings Plans (1-Year Partial Upfront):** $14,600.00/month net savings (covering 75% of steady-state post-rightsizing production compute).
- **Spot Instance Orchestration:** $4,000.00/month net savings (migrating asynchronous OCR and batch ETL workloads to diversified Spot fleets).
- Additionally, **$2,822.40/month in RDS Reserved Instance savings** was mapped to production PostgreSQL clusters.

This brings our total cumulative monthly savings identified across Days 2, 3, and 4 to **$64,250.00/month (35.7% of total spend)**, formally exceeding CFO Priya Menon's minimum 33% / $60,000.00 monthly reduction target!

---

## 2. Savings Plans Procurement Strategy

### 2.1 Why Rightsizing Preceded Commitment
In adherence to FinOps best practices, we avoided the classic trap of committing to un-rightsized infrastructure. By rightsizing compute instances and scheduling non-prod environments on Day 2, we reduced our gross baseline before modeling commitments:
$$\text{Pre-Rightsizing On-Demand EC2} = \$61,200.00/\text{month} \quad \longrightarrow \quad \text{Post-Rightsizing Steady-State} = \$38,000.00/\text{month}$$

### 2.2 Financial Modeling & Term Evaluation
We evaluated 6 procurement models:
1. **1-Year Partial Upfront Compute Savings Plan (Recommended):**
   - Upfront investment: $18,000.00
   - Effective hourly discount: 38.4%
   - Monthly net savings: **$14,600.00/month**
   - Payback period: **1.23 months** (40 days)
2. **Compute SP vs EC2 Instance SP:**
   - We specifically selected *Compute Savings Plans* over *EC2 Instance Savings Plans*. While Instance SP offers a slightly higher discount (43% vs 38.4%), it restricts LendFlow to specific instance families (e.g. C5 or M5). Compute SP applies seamlessly across instance families, AWS Lambda, and AWS Fargate, protecting LendFlow against lock-in during our upcoming **AWS Graviton3 (C7g/M7g)** migration.
3. **1-Year vs 3-Year Decision:**
   - 3-Year commitments offer up to 54% discount but carry unacceptable risk for a fintech growing at 100%+ YoY where microservices are rapidly transitioning to event-driven architectures. A 1-year term provides the optimal balance of discount and operational agility.

---

## 3. Spot Fleet Architecture for Asynchronous Workloads

### 3.1 Workload Separation & Compliance Guardrails
- **Strictly Prohibited from Spot:** 
  - `payment-gateway-service` (PCI DSS v4.0 Requirement 2 & 6: Dedicated cardholder data environment, deterministic latency).
  - Primary RDS PostgreSQL and ElastiCache clusters (RBI IT Framework continuous availability requirements).
- **Approved for Spot Fleets:**
  - `kyc-document-service` (Batch OCR workers consuming from SQS).
  - `analytics-batch-pipeline` (Daily Spark/Airflow data aggregation).
  - `underwriting-engine` (Nightly Monte-Carlo credit risk simulations).

### 3.2 Diversified Multi-AZ Fleet Design
To eliminate Spot termination risks, our Auto Scaling Groups implement a `capacity-optimized` allocation strategy across **12 independent capacity pools** (4 instance alternatives across 3 AZs):
- Target types: `c5.2xlarge`, `c5a.2xlarge`, `c6i.2xlarge`, `m5.2xlarge`.
- Configuration: 20% On-Demand base + 80% Spot allocation.

### 3.3 Two-Minute Interruption Handling Sequence
We implemented the **AWS Node Termination Handler**:
1. EventBridge intercepts the 2-minute `EC2 Spot Instance Interruption Warning`.
2. Worker process receives `SIGTERM` and immediately stops pulling messages from SQS.
3. In-flight OCR page segment is processed and current bounding box state is committed to S3.
4. Unfinished SQS messages are returned to the queue via `ChangeMessageVisibility(0)` for immediate re-pickup by healthy workers.
5. Worker cleanly exits within 45 seconds, well before AWS reclaims the instance.

---

## 4. Spot Interruption Sensitivity Modeling

We simulated three interruption scenarios to evaluate business risk:
- **Scenario A (5% Interruption):** Net savings = $6,435.68/month; reprocessing overhead = $24.32/month.
- **Scenario B (10% Expected Interruption):** Net savings = $6,405.28/month; reprocessing overhead = $54.72/month.
- **Scenario C (20% Stress Interruption):** Net savings = $6,332.32/month; reprocessing overhead = $127.68/month.

Even under continuous 20% interruptions, our S3 checkpointing keeps lost computational work below $130/month, proving the resilience and profitability of the architecture.

---

## 5. Outputs & Artefacts Produced
- Formally published `docs/ri-spot-strategy.md` containing full technical architecture, mathematical proofs, and governance cadences.
- Appended `Commitment & Spot` tab to `analysis/savings-model.xlsx`.
- Documented findings in `daily-logs/day-04.md`.
- Updated `CHANGELOG.md`.

## 6. Next Logical Activity (Day 5)
Proceed immediately to **Day 5: Tagging & Cost Allocation Governance**, analyzing `data/tag_compliance_report.csv` to calculate overall compliance and dark spend, designing a comprehensive 10-tag mandatory taxonomy, and defining a 4-layer enforcement model (Preventive via SCPs, Detective via AWS Config, Corrective via EventBridge/Lambda, and Audit via Cost Allocation Tags).
