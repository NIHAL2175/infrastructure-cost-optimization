# Day 6: Cost Anomaly Detection

**Date:** Execution Stage 6 (Baseline Day 6)  
**Author:** Senior FinOps Engineer & Cloud Architect  
**Status:** Completed  

---

## 1. Executive Summary

On Day 6, we audited historical cost spikes and designed a comprehensive, multi-tiered **Cost Anomaly Detection Framework & Operational Runbook**.

Our review of `data/cost_anomaly_events.csv` revealed 10 major cost anomaly incidents over the past 6 months that generated **$31,512.80 in pure waste** (~$5,250.00/month ongoing leak). More critically, the average Mean Time to Detection (MTTD) was **156.6 hours (6.5 days)**, with some incidents (such as an abandoned GPU instance or broken snapshot cleanup scripts) remaining completely undetected for 14 to 30 days until the end-of-month invoice arrived.

We developed an integrated 3-tier detection framework combining real-time CloudWatch infrastructure metric alarms, calendar-aware statistical Modified Z-Scores (accounting for 1st and 15th salary credit day surges), and AWS Cost Anomaly Detection ML models. We established a 4-tier severity matrix, automated escalation workflows, and published an operational **Anomaly Investigation Runbook** targeting an MTTD under 2 hours for critical incidents.

---

## 2. Historical Incident Analysis & Root Causes

We categorized the 10 historical anomaly incidents into four primary architectural patterns:

```text
Historical Anomaly Root Cause Distribution:
1. Release & Configuration Regressions (40%):
   - ANOM-003: KYC release v2.4 dropped S3 Gateway Endpoint ($4,600 waste, 72h TTD)
   - ANOM-006: Payment service accidentally left at DEBUG log level ($3,900 waste, 60h TTD)
   - ANOM-008: Disbursement engine cross-region duplicate sync ($1,340 waste, 24h TTD)
   - ANOM-010: Staging Redis session store memory creep ($1,002 waste, 48h TTD)
2. Abandoned Non-Production Infrastructure (30%):
   - ANOM-002: Abandoned p3.8xlarge GPU instance in dev sandbox ($6,144 waste, 336h TTD)
   - ANOM-004: Load test cluster left running over 4-day holiday weekend ($3,716.80 waste, 96h TTD)
   - ANOM-009: Orphaned unattached EBS volumes from load pipeline ($1,800 waste, 120h TTD)
3. Infinite Loops & Queue Failures (20%):
   - ANOM-001: Runaway Spark/EMR job looping over unindexed S3 partition ($3,730 waste, 48h TTD)
   - ANOM-005: Cross-AZ Kafka consumer fetch loop ($2,530 waste, 36h TTD)
4. Unmonitored Custom Scripts (10%):
   - ANOM-007: Custom backup Lambda failing silently before deletion ($2,750 waste, 720h TTD)
```

### Key Analytical Takeaways:
- **Human Inattention over Weekends:** Friday deployments and pre-weekend stress tests were the primary culprits behind catastrophic multi-day anomalies.
- **Invoice-Driven Detection:** Over 50% of financial losses were discovered only when CFO Priya Menon noticed massive invoice discrepancies at month-end.

---

## 3. Multi-Layer Anomaly Detection Architecture

To achieve rapid, high-confidence detection without creating false-positive alarm fatigue, we engineered a hybrid 3-tier detection architecture:

1. **Tier 1: Sub-Hour Telemetry Proxies (CloudWatch Metric Alarms):**
   - High-volume spend drivers are monitored at the infrastructure proxy layer:
     - NAT Gateway `BytesProcessed` > 50 GB/hour alarm.
     - CloudWatch Logs `IncomingBytes` > 10 GB/hour alarm.
     - EC2 `RunningInstances` count changes outside scheduled CI/CD windows.
   - MTTD: **< 30 minutes**.
2. **Tier 2: Statistical Adaptive Anomaly Detection (Lambda + EventBridge):**
   - Implements a **Modified Z-Score** calculated against 14-day rolling medians:
     $$M_i = \frac{0.6745 \cdot (x_i - \tilde{x})}{\text{MAD}}$$
   - Includes calendar-aware weighting to suppress alerts during predictable salary-day volume spikes (days 1-2 and 29-30, and mid-month days 14-16).
   - MTTD: **< 4 hours**.
3. **Tier 3: AWS Cost Anomaly Detection (Machine Learning):**
   - Configured AWS Cost Anomaly Monitors across all linked accounts with a threshold of **$100.00 and 20% expected variance**.
   - MTTD: **< 24 hours** (aligned with AWS CUR ingestion).

---

## 4. Severity Matrix & Investigation Runbook

Cost anomalies are mapped to 4 operational tiers:
* **P1 Critical (> $1,000/day impact):** Automated PagerDuty escalation to CFO Priya Menon, CTO Arjun Deshmukh, and FinOps Lead. SLA: Contain within 2 hours.
* **P2 High ($300 – $1,000/day impact):** Slack `#finops-alerts` notification + urgent JIRA ticket to squad tech lead. SLA: Contain within 6 hours.
* **P3 Moderate ($100 – $300/day impact):** Slack `#finops-daily-digest`. SLA: Resolve within 24 hours.
* **P4 Low (< $100/day drift):** Aggregated in weekly showback reports.

The documented **5-Step Runbook** covers:
1. Triage & Business Calendar Verification
2. Immediate Containment (Stop/Terminate/Drop Log Level)
3. Root Cause Isolation via CloudTrail
4. Permanent Remediation (Code/Policy)
5. Post-Incident Review (PIR) & 5-Whys RCA

---

## 5. Outputs & Artefacts Produced
- Formally published `docs/anomaly-detection.md` detailing incident history, algorithm evaluations, severity matrix, and the full 5-step operational runbook.
- Documented findings in `daily-logs/day-06.md`.
- Updated `CHANGELOG.md`.

## 6. Next Logical Activity (Day 7)
Proceed immediately to **Day 7: Consolidated Cost Audit & Savings Model**, synthesising all findings from Days 1-6 into a professional consulting-quality **Master Cost Audit Report** (`docs/cost-audit-report.md`), finalizing `analysis/savings-model.xlsx` with scenario models, and constructing the comprehensive catalog of **15+ Prioritized Optimisation Recommendations** with full compliance impact assessments and the Impact vs. Effort matrix.
