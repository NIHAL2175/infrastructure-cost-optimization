# Changelog

All notable changes, architectural decisions, analytical models, policy assets, and validation milestones for the LendFlow Technologies Infrastructure Cost Optimisation & FinOps Framework are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased] - 2026-09-14

### Full Framework Enhancement: Gamified Simulator, Industrial Case Studies & Telemetry Integration
- **Added:** `docs/simulation-concept.md` detailing the complete strategic business and pedagogical architecture for **CLOUDBURN: The FinOps War Room Simulator** across Campaign Mode (6 progressive levels), Arena Mode (48-hour competitive sprint), and Sandbox Mode (custom scenario builder) with 10 achievement badges.
- **Added:** `docs/case-studies.md` conducting in-depth forensic investigations of 4 major real-world cloud cost case studies:
  1. *The $2.4M AWS Billing Shock* (ML auto-scaling disaster, PR typo, SCP guardrails, Infracost gate, runbook).
  2. *Razorpay's FinOps Transformation (India)* ($30M/yr spend, 35% cut, 4-phase transformation roadmap, unit economics).
  3. *Kubernetes Cost Explosion at a European Neobank* (EKS over-requested pod limits, VPA P95, Karpenter spot node pools, Kubecost).
  4. *Data Transfer Cost Disaster at a Singapore Fintech* (GCP cross-region egress, Singapore DB migration, Cloud CDN, gRPC, VPC Service Controls).
- **Added:** `docs/stakeholder-priority-matrix.md` establishing a formal standalone deliverable for all 6 stakeholder personas (Priya Menon, Arjun Deshmukh, Ravi Krishnan, Meera Iyer, Sanjay Patel, Anita Sharma), conflict governance ladders, and communication rhythms.
- **Built:** Playable interactive HTML5 web application in `dashboards/simulation-war-room.html` with live financial HUD ($180k down to $115.75k, unit cost $0.346 to $0.223), dynamic stakeholder sentiment tracking, sound effects, and unlockable badge gallery.
- **Integrated:** Detailed forensic telemetry tables (40 compute instances, 12 database/cache clusters, 17 storage inventory assets, and top 10 costliest data transfer paths) directly into `docs/cost-audit-report.md` fulfilling Appendix A deliverables 3, 4, 6, and 7.
- **Enhanced:** Local master portal `index.html` with direct simulation launch cards and comprehensive documentation navigation.
- **Updated:** Programmatic QA verification script `scripts/verify_cross_references.py` auditing all 26 deliverables from Appendix A with 100% pass rate.

### Stage 1: FinOps Foundations & Dataset Familiarisation (Day 1)
- **Added:** Git repository initialisation and standardized enterprise directory hierarchy (`docs/`, `analysis/`, `dashboards/`, `policies/`, `presentation/`, `daily-logs/`, `data/`).
- **Added:** High-fidelity simulated datasets in `data/` covering all 8 specified FinOps telemetry domains.
- **Added:** `analysis/billing-analysis.xlsx` detailing 12-month billing trends ($50,000 to $180,000) and Pareto distribution.
- **Added:** Stakeholder Priority Matrix and `daily-logs/day-01.md`.

### Stage 2: Compute & Database Analysis (Day 2)
- **Added:** Resource-level telemetry profiling of 41 EC2 compute instances and 12 database/caching clusters.
- **Identified:** 28 instances (68.3%) with sustained CPU <20%; immediate termination of 2 abandoned sandboxes ($1,042.56/mo waste).
- **Designed:** Automated non-production scheduling (9 AM - 7 PM weekdays) reducing non-prod compute hours by 69.4% ($8,200/mo savings).
- **Consolidated:** RDS reporting read-replica decommissioned in favor of S3/Athena lake ($1,411.20/mo savings); staging RDS converted to Single-AZ Graviton ($1,091.20/mo savings).
- **Built:** `analysis/savings-model.xlsx` featuring `Executive Summary`, `Compute Analysis`, and `Database Analysis` tabs.
- **Published:** `daily-logs/day-02.md`.

### Stage 3: Storage & Data Transfer Analysis (Day 3)
- **Added:** S3 lifecycle policy framework transitioning 145 TB of dormant KYC loan docs (>90d inactive) to Glacier Instant Retrieval ($1,850/mo savings) and audit logs to Glacier with WORM Object Lock ($1,250/mo savings).
- **Remediated:** 4 unattached orphan EBS volumes (7,500 GB) deleted ($750/mo savings); 32,000 GB of attached GP2 converted to GP3 ($650/mo savings); DLM 30d snapshot retention policy enforced ($1,000/mo savings).
- **Eliminated:** $7,560/mo in avoidable NAT Gateway data processing fees via AWS S3 Gateway VPC Endpoints.
- **Remediated:** Cross-AZ inter-service chatter via AZ-affinity topology-aware routing ($2,920/mo savings).
- **Appended:** `Storage Analysis` and `Data Transfer Analysis` tabs to `analysis/savings-model.xlsx`.
- **Published:** `daily-logs/day-03.md`.

### Stage 4: Reserved Capacity & Spot Strategy (Day 4)
- **Audited:** 0.0% baseline RI/SP coverage across all 65 compute instances and 12 database clusters.
- **Designed:** 1-Year Partial Upfront Compute Savings Plan ($18,000 upfront, 1.23-month payback) yielding $14,600/mo savings on steady-state production compute, plus $2,822.40/mo on RDS Reserved Instances.
- **Architected:** Diversified Spot Fleets across 12 independent capacity pools (capacity-optimized allocation) with 20% on-demand base for asynchronous batch OCR and ETL pipelines ($4,000/mo savings).
- **Modeled:** Spot interruption sensitivity across 5%, 10%, and 20% scenarios; verified sub-page S3 checkpointing keeps reprocessing overhead <$130/mo.
- **Published:** `docs/ri-spot-strategy.md` and appended `Commitment & Spot` tab to `analysis/savings-model.xlsx`.
- **Published:** `daily-logs/day-04.md`.

### Stage 5: Tagging & Cost Allocation Governance (Day 5)
- **Audited:** 58.2% baseline tag compliance in `data/tag_compliance_report.csv`, identifying $75,420.00/month in unallocated dark spend.
- **Designed:** Enterprise 10-tag mandatory taxonomy (`business_unit`, `product`, `environment`, `cost_centre`, `team`, `service`, `created_by`, `ttl`, `compliance_scope`, `data_classification`).
- **Engineered:** 4-layer governance model (Preventive, Detective, Corrective, Audit & Showback) and proportional shared-cost allocation math.
- **Authored:** `policies/scp-mandatory-tags.json` and `policies/config-rules.yaml`.
- **Published:** `docs/tagging-taxonomy.md` and `daily-logs/day-05.md`.

### Stage 6: Cost Anomaly Detection (Day 6)
- **Audited:** 10 historical anomaly incidents in `data/cost_anomaly_events.csv` generating $31,512.80 in waste with average MTTD of 156.6 hours (6.5 days).
- **Designed:** Hybrid 3-tier detection framework (Sub-hour CloudWatch proxy alarms, Lambda Modified Z-Score with salary-day surge awareness, and AWS ML Cost Anomaly Detection).
- **Established:** 4-tier severity matrix (P1 Critical through P4 Low) with SLAs, automated PagerDuty/Slack routing, and 5-step operational Anomaly Investigation Runbook.
- **Published:** `docs/anomaly-detection.md` and `daily-logs/day-06.md`.

### Stage 7: Consolidated Cost Audit & Savings Model (Day 7)
- **Synthesised:** Master AWS Cost Audit Report (`docs/cost-audit-report.md`) detailing baseline spend ($180,000/mo), gross waste ($70,850/mo), net savings waterfall ($64,250/mo), and 90-day realization timeline.
- **Engineered:** Catalog of 16 prioritized optimisation recommendations (`docs/optimisation-recommendations.md`) complete with technical solutions, compliance assessments, and Impact vs Effort matrix.
- **Reconciled:** Probabilistic scenario modeling in `analysis/savings-model.xlsx` (Expected: $64,250/mo; Best-Case: $71,800/mo; Worst-Case: $56,400/mo).
- **Published:** `docs/cost-audit-report.md`, `docs/optimisation-recommendations.md`, and `daily-logs/day-07.md`.

### Stage 8: Auto-Scaling Architecture (Day 8)
- **Architected:** Asymmetric auto-scaling framework (60s scale-out cooldown, 300s-600s scale-in cooldown, 60s ELB connection draining) across 6 core microservices.
- **Deployed:** Predictive and scheduled scaling for borrower salary-day spikes (1st and 15th of the month) pre-warming capacity to eliminate transaction drop-offs.
- **Implemented:** Scheduled scaling for development and staging fleets (9 AM - 7 PM weekdays, stopped on weekends) capturing $8,200.00/month in idle compute waste.
- **Authored:** `policies/auto-scaling-loan-api.json`, `policies/auto-scaling-batch-ocr.json`, and `policies/auto-scaling-scheduled-dev.json`.
- **Published:** `docs/auto-scaling-policies.md` and `daily-logs/day-08.md`.

### Stage 9: FinOps Governance Model (Day 9)
- **Established:** FinOps Center of Excellence (CoE) operating bridge uniting Finance, Engineering, Compliance, and Product.
- **Designed:** Comprehensive RACI matrix mapping all 6 executive personas across 10 operational cloud domains.
- **Structured:** 4-tier recurring FinOps operating cadences (Daily automated, Weekly tactical, Monthly operational, Quarterly strategic).
- **Enforced:** 4-level cascading budget hierarchy (Org $\rightarrow$ BU $\rightarrow$ Team $\rightarrow$ Project) with automated 80%, 90%, 100%, and 120% escalation gates.
- **Published:** `docs/governance-model.md` and `daily-logs/day-09.md`.

### Stage 10: Cost Dashboard Design (Day 10)
- **Authored:** Publication-quality interactive HTML5/CSS3 executive strategic dashboard (`dashboards/executive-dashboard.html`) featuring 12-month trends, 90-day forecast, unit cost, and top service drivers.
- **Authored:** Tactical engineering manager dashboard (`dashboards/engineering-dashboard.html`) featuring fleet CPU/RAM telemetry, rightsizing action backlog, and squad showback scorecards.
- **Authored:** Squad & microservice dashboard (`dashboards/team-dashboard.html`) showcasing real-time instance health, deployment cost deltas, and live scaling event feeds.
- **Published:** `dashboards/` suite and `daily-logs/day-10.md`.

### Stage 11: Review Process & FinOps Maturity (Day 11)
- **Standardized:** 10-section Monthly Cloud Financial Report package featuring mandatory deep-dives into >10% variances, loan volume correlation, and regulatory sign-offs.
- **Structured:** Quarterly Strategic Executive Review package covering 12-month trends, unit economics, and multi-year capital commitment renewals.
- **Defined:** FinOps Maturity Model (Crawl $\rightarrow$ Walk $\rightarrow$ Run across Visibility, Optimisation, Commitments, Governance, Culture).
- **Established:** Quantitative Enterprise FinOps OKRs (Cost reduction: $180k to $115.75k, $/loan: $0.346 to $0.223, Tagging >96%, Anomaly MTTD <2 hours, CSP utilisation >95%).
- **Published:** `docs/review-process.md` and `daily-logs/day-11.md`.

### Stage 12: Policy-as-Code & Automation (Day 12)
- **Authored:** Syntactically valid AWS Service Control Policies: `policies/scp-gpu-restriction.json`, `policies/scp-region-restriction.json`, and `policies/scp-instance-cap.json`.
- **Engineered:** AWS Config Conformance Pack (`policies/config-rules.yaml`) for continuous compliance auditing.
- **Developed:** Reusable Terraform Cost Governance Module in `policies/terraform-cost-module/` with HCL regex validation, automated 10-tag mapping, and Infracost CI/CD pre-commit gates ($500/mo overrun blocker).
- **Published:** `policies/` suite and `daily-logs/day-12.md`.

### Stage 13: CFO Review Panel Presentation (Day 13)
- **Delivered:** Professional 20-slide CFO review panel presentation transcript with comprehensive speaker notes in `presentation/cfo-presentation.md`.
- **Developed:** Modern, interactive HTML5 presentation deck in `presentation/cfo-presentation.html` with keyboard navigation and KPI summary cards.
- **Reconciled:** 100% numerical consistency across baseline ($180,000/mo), net savings ($64,250/mo), target run-rate ($115,750/mo), and 90-day implementation roadmap.
- **Published:** `presentation/` assets and `daily-logs/day-13.md`.

### Stage 14: Full Cross-Reference & Quality Assurance (Day 14)
- **Executed:** Automated programmatic QA audit across all 30 repository deliverables via `scripts/verify_cross_references.py`.
- **Validated:** 100% JSON/YAML/HCL syntax validity across all policy assets in `policies/`.
- **Enforced:** Strict terminology consistency for British English ("optimisation") and numerical reconciliation ($180,000 baseline, $64,250 net savings, $115,750 run-rate target).
- **Constructed:** Cross-Reference Validation Matrix in `daily-logs/day-14.md`.

### Stage 15: Final Review, Security Audit & Production Release (Day 15)
- **Verified:** All 15 daily logs (`day-01.md` through `day-15.md`) populated with substantive analysis, decisions, and architectural outputs.
- **Audited:** Zero secrets, zero plain-text tokens, zero private keys, and zero `.env` files detected across the repository.
- **Validated:** Git repository cleanliness, semantic commit history, and verified master financial spreadsheet formulas.
- **Concluded:** Formal release of the LendFlow Technologies Infrastructure Cost Optimisation & FinOps Framework achieving $64,250.00/month net savings (35.7% reduction).
- **Published:** `daily-logs/day-15.md`.
