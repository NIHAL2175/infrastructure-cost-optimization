# Day 5: Tagging & Cost Allocation Governance

**Date:** Execution Stage 5 (Baseline Day 5)  
**Author:** Senior FinOps Engineer & Cloud Architect  
**Status:** Completed  

---

## 1. Executive Summary

On Day 5, we addressed the foundational root cause of LendFlow Technologies' cost sprawl: **the absence of rigorous tagging and financial attribution**. Prior to this stage, Finance could not account for **$75,420.00/month (41.9% of the total $180,000 AWS bill)**, which was categorised as unallocated or "dark spend".

We analysed `data/tag_compliance_report.csv`, designed a comprehensive **10-Tag Mandatory Taxonomy**, established a mathematical **Shared Cost Allocation Methodology**, and implemented a **4-Layer Automated Governance Engine** combining preventive Service Control Policies (SCPs), detective AWS Config rules, and corrective event-driven remediation.

With this framework, LendFlow eliminates dark spend, lifts resource tag compliance from **58.2% to >98%**, and empowers CFO Priya Menon and engineering managers with automated weekly showback reporting.

---

## 2. Baseline Tagging Audit & Dark Spend Discovery

Analysis of our resource inventory across 150+ AWS assets revealed severe compliance decay:

```text
Tagging Compliance Breakdown:
- Overall Compliance Rate: 58.2%
- Total Unallocated / Dark Spend: $75,420.00 / month
- Production Assets:  78.4% Compliant (Legacy partial tagging)
- Staging Assets:     44.1% Compliant (Missing team & cost centre tags)
- Dev / Sandboxes:    26.5% Compliant (Widespread untagged sprawl)
```

### Key Statistical Vulnerabilities:
1. **Missing Cost Centre Attribution:** 47% of EC2 and EBS assets lacked `cost_centre` tags, preventing accurate General Ledger (GL) posting in NetSuite.
2. **Missing Owner / Creator Identity:** 65% of development resources lacked `created_by` and `ttl` tags, which directly caused the abandoned GPU instances and orphaned EBS volumes discovered on Day 2 and Day 3.
3. **Shared Infrastructure Blurry Spend:** $14,500.00/month in central networking (NAT Gateways, Transit Gateways) was unallocated, sitting as an overhead penalty on the Platform Engineering budget.

---

## 3. Mandatory 10-Tag Taxonomy Specification

We standardized 10 mandatory tags across all AWS resources:
1. `business_unit`: `retail-lending`, `msme-credit`, `risk-analytics`, `payments-core`, `platform-engineering`
2. `product`: `personal-loan`, `merchant-credit`, `credit-line`, `scoring-api`, `shared-platform`
3. `environment`: `prod`, `staging`, `dev`, `sandbox`, `dr`
4. `cost_centre`: Standardized NetSuite accounting codes (`CC-101` through `CC-105`)
5. `team`: Engineering squad ownership (`lending-core`, `risk-scoring`, `payments`, `data-eng`, `platform`, `secops`)
6. `service`: Microservice identifier matching internal service catalog
7. `created_by`: SSO email identity or CI/CD service principal
8. `ttl`: Time-To-Live ISO date (`YYYY-MM-DD`) for automated reaping of non-prod assets
9. `compliance_scope`: Regulatory classification (`pci-dss-cde`, `soc2-audit`, `rbi-core`, `gdpr-eu`, `non-regulated`)
10. `data_classification`: Sensitivity tier (`restricted-pii`, `confidential-financial`, `internal`, `public`)

---

## 4. The 4-Layer Governance Architecture

To guarantee sustainability, we engineered four concentric governance layers:

1. **Layer 1: Preventive (Block at Creation):**
   - Implemented `policies/scp-mandatory-tags.json` at the AWS Organizations root. The SCP enforces explicit `Deny` rules on `ec2:RunInstances`, `rds:CreateDBInstance`, and `s3:CreateBucket` if mandatory tags are missing from API request parameters.
   - Guardrails integrated into Terraform CI/CD pipelines via Infracost and TFLint.
2. **Layer 2: Detective (Continuous Audit):**
   - Deployed `policies/config-rules.yaml` establishing AWS Config managed rules (`REQUIRED_TAGS`, `EC2_LOW_CPU_UTILIZATION_CHECK`, `S3_LIFECYCLE_POLICY_CHECK`, `EC2_VOLUME_IN_USE_CHECK`).
3. **Layer 3: Corrective (Event-Driven Remediation):**
   - Automated Lambda workflow: Non-compliant development resources receive a 24-hour warning via Slack. If un-remediated at 48 hours, the instance is automatically stopped.
   - Production safety gate: Production resources are never auto-terminated; a P2 JIRA ticket is dispatched to the squad lead.
4. **Layer 4: Audit & Showback:**
   - Activated AWS User-Defined Cost Allocation Tags in Billing Preferences.
   - Weekly automated showback reports delivered to engineering leads every Monday morning.

---

## 5. Outputs & Artefacts Produced
- Formally published `docs/tagging-taxonomy.md` detailing taxonomy schemas, allowed values, validation regex, and shared cost math.
- Authored production-ready policy assets:
  - `policies/scp-mandatory-tags.json` (Syntactically valid AWS Organizations SCP).
  - `policies/config-rules.yaml` (AWS Config conformance pack template).
- Documented Day 5 analysis and architecture in `daily-logs/day-05.md`.
- Updated `CHANGELOG.md`.

## 6. Next Logical Activity (Day 6)
Proceed immediately to **Day 6: Cost Anomaly Detection**, analyzing the 10 historical anomaly incidents in `data/cost_anomaly_events.csv`, comparing static vs statistical vs ML detection algorithms (Z-Score, Isolation Forest, Prophet), establishing severity thresholds, notification channels, SLAs, escalation matrices, and publishing `docs/anomaly-detection.md` with an operational Anomaly Investigation Runbook.
