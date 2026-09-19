# Day 8: Auto-Scaling Architecture

**Date:** Execution Stage 8 (Baseline Day 8)  
**Author:** Senior FinOps Engineer & Cloud Architect  
**Status:** Completed  

---

## 1. Executive Summary

On Day 8, we transitioned LendFlow Technologies from static, over-provisioned infrastructure to an elastic, intelligent **Auto-Scaling Architecture**.

Prior to this implementation, production services were statically scaled to handle theoretical 99th-percentile peak bursts 24/7, resulting in an average fleet CPU utilization below 20%. Furthermore, non-production environments ran continuously over nights and weekends, burning $8,200.00/month in idle compute.

We engineered:
1. **Asymmetric Auto-Scaling Mechanics:** Aggressive scale-out (60s cooldown, +50% capacity step) combined with conservative scale-in (300s-600s cooldown, 1 node step-down with 60s deregistration delay) across 6 core microservices.
2. **Predictive Scaling Engine:** Calendar-aware scheduled pre-warming for borrower salary-day surges (1st and 15th of the month).
3. **Automated Non-Production Scheduling:** Automated scale-down of Development and Staging fleets outside business hours (9:00 AM to 7:00 PM IST weekdays), capturing **$8,200.00/month in net savings**.
4. **Policy-as-Code Configuration Files:** Production-ready JSON policies committed to `policies/`.

---

## 2. Asymmetric Scaling Policy Implementation

Fintech platforms cannot tolerate dropped transactions or latency spikes during credit authorization. Asymmetric scaling addresses this by decoupling scale-out velocity from scale-in damping:

```text
Asymmetric Scaling Operational Parameters:
- Scale-Out Trigger: Metric > Threshold for 1 minute (60s)
- Scale-Out Action: Immediate +50% capacity addition (minimum 2 nodes)
- Scale-Out Cooldown: 60 seconds
- Scale-In Trigger: Metric < Threshold for 15 consecutive minutes (900s)
- Scale-In Action: Gradual removal of 1 instance per step
- Scale-In Cooldown: 300 to 600 seconds
- Deregistration Delay: 60 seconds (allows in-flight HTTP requests and DB commits to drain cleanly)
```

### Microservice Policy Summary:
1. **Loan Application API:** Target tracking at 1,200 req/min & 60% CPU; min 4, max 20 `c5.2xlarge`; 100% Compute Savings Plan coverage.
2. **Credit Scoring Engine:** Target tracking at 60% CPU; min 3, max 12 `r5.2xlarge`; 100% CSP.
3. **KYC Document Processing:** Custom SQS backlog tracking (50 msgs/instance); min 2, max 16 `c5.2xlarge`; **80% Spot Fleet** with AWS Node Termination Handler and S3 checkpointing.
4. **Payment Gateway Service:** Target tracking at 800 req/min & 50% CPU; min 4, max 12 `c5.2xlarge`; **0% Spot (Strict PCI DSS CDE constraint)**.
5. **Reporting & Analytics ETL:** SQS-driven batch scaling; min 0, max 8 `r5.2xlarge`; **100% Spot Fleet**; auto-scales to 0 when queue drains.
6. **Notification Service:** Target tracking at 65% CPU; min 2, max 6 `t3.medium`; 50% Spot mix.

---

## 3. Predictive Scaling & Calendar Surges

LendFlow's business data demonstrates extreme cyclical surges around borrower salary cycles:
- **1st & 2nd of Month:** Repayment processing and loan limit inquiries spike by **+135%**.
- **14th – 16th of Month:** Mid-month credit disbursements spike by **+115%**.

Instead of waiting for reactive metrics to breach thresholds (which causes a 3-5 minute warmup latency lag), we deployed **Scheduled Scaling Actions**:
- At **05:30 AM IST** on the 1st and 15th, ASGs automatically pre-warm, doubling minimum capacity from 4 to 8 nodes before morning web traffic arrives.
- At **20:00 PM IST** on the 2nd and 16th, minimum capacity safely returns to normal baseline.

---

## 4. Non-Production Business-Hours Automation

We implemented scheduled scaling across `asg-lendflow-dev-shared-fleet` and `asg-lendflow-staging-shared-fleet`:
- **Morning Wake-Up:** 09:00 AM IST (Monday to Friday) $\rightarrow$ Desired = 1, Min = 1.
- **Evening Shutdown:** 07:00 PM IST (Monday to Friday) $\rightarrow$ Desired = 0, Min = 0.
- **Weekends:** Remainder at 0 capacity.
- **Monthly Savings:** **$8,200.00 / month ($98,400.00 / year)** via 69.4% runtime reduction.
- **Developer Experience:** Integrated `/lendflow-wake-env` Slack command for instant 2-hour temporary overrides during off-hours debugging.

---

## 5. Outputs & Artefacts Produced
- Formally published `docs/auto-scaling-policies.md` with deep mathematical justifications and policy schemas.
- Authored production-ready JSON configurations:
  - `policies/auto-scaling-loan-api.json` (Production Loan Application API)
  - `policies/auto-scaling-batch-ocr.json` (KYC OCR 80% Spot Fleet)
  - `policies/auto-scaling-scheduled-dev.json` (Dev/Staging business-hours scheduled scaling)
- Documented findings in `daily-logs/day-08.md`.
- Updated `CHANGELOG.md`.

## 6. Next Logical Activity (Day 9)
Proceed immediately to **Day 9: FinOps Governance Model**, establishing the organizational FinOps Operating Model, defining the full RACI matrix across all 6 stakeholders (Priya Menon, Arjun Deshmukh, Ravi Krishnan, Meera Iyer, Sanjay Patel, Anita Sharma), designing the 4-tier FinOps meeting cadences (Daily automated, Weekly tactical, Monthly operational, Quarterly strategic), and building the multi-tier budget hierarchy (Org $\rightarrow$ BU $\rightarrow$ Team $\rightarrow$ Project) with 80%, 90%, 100%, and 120% escalation thresholds.
