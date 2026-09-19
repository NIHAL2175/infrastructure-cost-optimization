import csv
import os
import math

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

ensure_dir('data')
ensure_dir('analysis')

# 1. monthly_cost_summary.csv
# 12 Months: Oct 2025 - Sep 2026
months = [
    ("2025-10", 50000, 52000, 210000),
    ("2025-11", 54000, 55000, 230000),
    ("2025-12", 61000, 58000, 255000),
    ("2026-01", 72000, 62000, 290000),
    ("2026-02", 85000, 66000, 325000),
    ("2026-03", 98000, 71000, 360000),
    ("2026-04", 112000, 76000, 395000),
    ("2026-05", 127000, 81000, 430000),
    ("2026-06", 141000, 85000, 460000),
    ("2026-07", 154000, 89000, 485000),
    ("2026-08", 168000, 92000, 505000),
    ("2026-09", 180000, 95000, 520000)
]

# Service percentage breakdown shift over time (Month 1 -> Month 12)
# In M12: EC2 ~34% ($61,200), RDS ~22% ($39,600), S3 ~11% ($19,800), DataTransfer ~12% ($21,600),
# ElastiCache ~7% ($12,600), NAT Gateway ~5% ($9,000), CloudWatch/Logging ~4% ($7,200), ELB ~3% ($5,400), Others ~2% ($3,600)

with open('data/monthly_cost_summary.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "billing_period", "budget_usd", "total_spend_usd", "budget_variance_usd",
        "loan_applications", "cost_per_application_usd",
        "ec2_instances_usd", "ec2_ebs_usd", "rds_postgres_usd", "s3_storage_usd",
        "data_transfer_usd", "elasticache_redis_usd", "nat_gateway_usd",
        "cloudwatch_logging_usd", "elb_alb_usd", "other_services_usd"
    ])
    
    for period, total, budget, loans in months:
        var = total - budget
        unit_cost = round(total / loans, 4)
        
        # Scaling service shares realistically from M1 to M12
        m_idx = months.index((period, total, budget, loans))
        factor = m_idx / 11.0 # 0.0 to 1.0
        
        ec2_inst = round(total * (0.28 + 0.04 * factor), 2)
        ec2_ebs = round(total * (0.05 + 0.015 * factor), 2)
        rds = round(total * (0.23 - 0.01 * factor), 2)
        s3 = round(total * (0.09 + 0.02 * factor), 2)
        dt = round(total * (0.08 + 0.04 * factor), 2)
        cache = round(total * (0.08 - 0.01 * factor), 2)
        nat = round(total * (0.04 + 0.015 * factor), 2)
        cw = round(total * (0.03 + 0.01 * factor), 2)
        elb = round(total * (0.04 - 0.01 * factor), 2)
        
        # Reconcile sum to exact total
        sub_sum = ec2_inst + ec2_ebs + rds + s3 + dt + cache + nat + cw + elb
        other = round(total - sub_sum, 2)
        
        writer.writerow([
            period, budget, total, var, loans, unit_cost,
            ec2_inst, ec2_ebs, rds, s3, dt, cache, nat, cw, elb, other
        ])

print("Generated monthly_cost_summary.csv")

# 2. daily_cost_detail.csv (Month 12: 30 days in September 2026, total = $180,000)
# Showing daily costs across 12 microservices, 3 environments (prod, staging, dev), 5 teams
services_info = [
    ("loan-application-service", "prod", "lending-core"),
    ("loan-application-service", "staging", "lending-core"),
    ("loan-application-service", "dev", "lending-core"),
    ("underwriting-engine", "prod", "risk-scoring"),
    ("underwriting-engine", "staging", "risk-scoring"),
    ("underwriting-engine", "dev", "risk-scoring"),
    ("credit-bureau-connector", "prod", "risk-scoring"),
    ("kyc-document-service", "prod", "lending-core"),
    ("kyc-document-service", "staging", "lending-core"),
    ("kyc-document-service", "dev", "lending-core"),
    ("payment-gateway-service", "prod", "payments"),
    ("disbursement-engine", "prod", "payments"),
    ("disbursement-engine", "staging", "payments"),
    ("collections-service", "prod", "lending-core"),
    ("ledger-accounting-service", "prod", "payments"),
    ("analytics-batch-pipeline", "prod", "data-eng"),
    ("feature-store-ml", "prod", "data-eng"),
    ("notification-service", "prod", "platform"),
    ("auth-identity-service", "prod", "platform"),
    ("api-gateway-mesh", "prod", "platform")
]

with open('data/daily_cost_detail.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "date", "day_of_week", "service_name", "environment", "team",
        "compute_cost_usd", "database_cost_usd", "storage_cost_usd",
        "network_cost_usd", "total_daily_cost_usd", "loan_applications_processed"
    ])
    
    # 30 days total ~180,000 => ~6000/day
    total_running = 0.0
    for day in range(1, 31):
        date_str = f"2026-09-{day:02d}"
        dow = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][(day + 1) % 7]
        is_weekend = dow in ["Sat", "Sun"]
        
        # Salary day spikes around 1st and 30th; mid-month spike around 15th
        day_weight = 1.0
        if day in [1, 2, 29, 30]:
            day_weight = 1.35
        elif day in [14, 15, 16]:
            day_weight = 1.15
        elif is_weekend:
            day_weight = 0.85
            
        base_daily = 6000.0 * (day_weight / 1.04) # normalized to total $180k
        daily_loans = int(17333 * day_weight)
        
        for s_name, env, team in services_info:
            # Distribution by env
            env_factor = 0.65 if env == "prod" else (0.20 if env == "staging" else 0.15)
            # Dev/staging runs 24/7 even on weekends! That is our waste pattern
            svc_share = (1.0 / len(services_info)) * env_factor * base_daily * 2.1
            
            c_cost = round(svc_share * 0.42, 2)
            d_cost = round(svc_share * 0.26, 2)
            s_cost = round(svc_share * 0.14, 2)
            n_cost = round(svc_share * 0.18, 2)
            tot_svc = round(c_cost + d_cost + s_cost + n_cost, 2)
            total_running += tot_svc
            
            writer.writerow([
                date_str, dow, s_name, env, team,
                c_cost, d_cost, s_cost, n_cost, tot_svc,
                daily_loans if env == "prod" and s_name == "loan-application-service" else 0
            ])

print("Generated daily_cost_detail.csv")

# 3. instance_utilisation.csv
# 65 EC2 instances across prod, staging, dev
instances = [
    # Production Core Services (Overprovisioned)
    ("i-0a1122334455aa01", "prod-loan-api-01", "loan-application-service", "prod", "lending-core", "c5.4xlarge", 16, 32, 18.2, 38.5, 34.0, 52.0, 720, 489.60, "c5.2xlarge", 244.80, "Sustained CPU <20% for 30 days. Downsize to c5.2xlarge."),
    ("i-0a1122334455aa02", "prod-loan-api-02", "loan-application-service", "prod", "lending-core", "c5.4xlarge", 16, 32, 17.5, 36.0, 32.5, 51.0, 720, 489.60, "c5.2xlarge", 244.80, "Sustained CPU <20% for 30 days. Downsize to c5.2xlarge."),
    ("i-0a1122334455aa03", "prod-loan-api-03", "loan-application-service", "prod", "lending-core", "c5.4xlarge", 16, 32, 16.9, 35.1, 33.1, 49.5, 720, 489.60, "c5.2xlarge", 244.80, "Sustained CPU <20% for 30 days. Downsize to c5.2xlarge."),
    ("i-0a1122334455aa04", "prod-loan-api-04", "loan-application-service", "prod", "lending-core", "c5.4xlarge", 16, 32, 19.1, 39.2, 35.2, 53.2, 720, 489.60, "c5.2xlarge", 244.80, "Sustained CPU <20% for 30 days. Downsize to c5.2xlarge."),
    ("i-0b2233445566bb01", "prod-risk-scoring-01", "underwriting-engine", "prod", "risk-scoring", "r5.4xlarge", 16, 128, 14.5, 28.0, 28.0, 42.0, 720, 725.76, "r5.2xlarge", 362.88, "Oversized memory & CPU. Avg memory 28%. Downsize to r5.2xlarge."),
    ("i-0b2233445566bb02", "prod-risk-scoring-02", "underwriting-engine", "prod", "risk-scoring", "r5.4xlarge", 16, 128, 13.8, 27.2, 27.5, 41.0, 720, 725.76, "r5.2xlarge", 362.88, "Oversized memory & CPU. Downsize to r5.2xlarge."),
    ("i-0b2233445566bb03", "prod-risk-scoring-03", "underwriting-engine", "prod", "risk-scoring", "r5.4xlarge", 16, 128, 15.1, 29.5, 29.2, 43.1, 720, 725.76, "r5.2xlarge", 362.88, "Oversized memory & CPU. Downsize to r5.2xlarge."),
    ("i-0c3344556677cc01", "prod-bureau-conn-01", "credit-bureau-connector", "prod", "risk-scoring", "m5.2xlarge", 8, 32, 11.2, 22.0, 22.4, 35.0, 720, 276.48, "m5.large", 207.36, "IO bound connector. CPU avg 11%. Downsize to m5.large."),
    ("i-0c3344556677cc02", "prod-bureau-conn-02", "credit-bureau-connector", "prod", "risk-scoring", "m5.2xlarge", 8, 32, 10.8, 21.5, 21.8, 34.0, 720, 276.48, "m5.large", 207.36, "IO bound connector. Downsize to m5.large."),
    ("i-0d4455667788dd01", "prod-kyc-ocr-01", "kyc-document-service", "prod", "lending-core", "c5.4xlarge", 16, 32, 12.0, 31.0, 25.0, 44.0, 720, 489.60, "c5.2xlarge (Spot Mix)", 342.72, "Batch OCR processing. Migrate to 70% Spot ASG with c5.2xlarge."),
    ("i-0d4455667788dd02", "prod-kyc-ocr-02", "kyc-document-service", "prod", "lending-core", "c5.4xlarge", 16, 32, 11.5, 30.2, 24.1, 42.5, 720, 489.60, "c5.2xlarge (Spot Mix)", 342.72, "Batch OCR processing. Migrate to 70% Spot ASG with c5.2xlarge."),
    ("i-0d4455667788dd03", "prod-kyc-ocr-03", "kyc-document-service", "prod", "lending-core", "c5.4xlarge", 16, 32, 12.8, 32.1, 26.0, 45.0, 720, 489.60, "c5.2xlarge (Spot Mix)", 342.72, "Batch OCR processing. Migrate to 70% Spot ASG with c5.2xlarge."),
    ("i-0e5566778899ee01", "prod-payment-gw-01", "payment-gateway-service", "prod", "payments", "c5.2xlarge", 8, 16, 38.0, 68.0, 45.0, 62.0, 720, 244.80, "Retain / CSP 1-Yr", 73.44, "PCI DSS scope. Well-utilised. Apply 1-Yr Savings Plan."),
    ("i-0e5566778899ee02", "prod-payment-gw-02", "payment-gateway-service", "prod", "payments", "c5.2xlarge", 8, 16, 36.5, 65.0, 44.0, 60.5, 720, 244.80, "Retain / CSP 1-Yr", 73.44, "PCI DSS scope. Well-utilised. Apply 1-Yr Savings Plan."),
    ("i-0f6677889900ff01", "prod-disburse-01", "disbursement-engine", "prod", "payments", "m5.2xlarge", 8, 32, 19.5, 41.0, 31.0, 48.0, 720, 276.48, "m5.xlarge", 138.24, "Downsize to m5.xlarge. Multi-AZ maintained."),
    ("i-0f6677889900ff02", "prod-disburse-02", "disbursement-engine", "prod", "payments", "m5.2xlarge", 8, 32, 18.2, 39.5, 30.2, 46.5, 720, 276.48, "m5.xlarge", 138.24, "Downsize to m5.xlarge. Multi-AZ maintained."),
    ("i-107788990011aa01", "prod-analytics-worker-01", "analytics-batch-pipeline", "prod", "data-eng", "r5.4xlarge", 16, 128, 8.5, 45.0, 18.0, 52.0, 720, 725.76, "r5.2xlarge (Spot)", 544.32, "Runs batch analytics 4h/day but kept 24/7. Convert to ASG Spot."),
    ("i-107788990011aa02", "prod-analytics-worker-02", "analytics-batch-pipeline", "prod", "data-eng", "r5.4xlarge", 16, 128, 7.8, 42.0, 17.5, 50.0, 720, 725.76, "r5.2xlarge (Spot)", 544.32, "Runs batch analytics 4h/day but kept 24/7. Convert to ASG Spot."),
    ("i-118899001122bb01", "prod-notification-01", "notification-service", "prod", "platform", "t3.xlarge", 4, 16, 15.0, 32.0, 25.0, 40.0, 720, 119.81, "t3.medium", 79.87, "Low CPU push service. Downsize to t3.medium."),
    ("i-118899001122bb02", "prod-notification-02", "notification-service", "prod", "platform", "t3.xlarge", 4, 16, 14.2, 30.5, 24.5, 39.0, 720, 119.81, "t3.medium", 79.87, "Low CPU push service. Downsize to t3.medium."),
    
    # Staging Environment (Idle & Oversized, Running 24/7)
    ("i-201122334455cc01", "stage-loan-api-01", "loan-application-service", "staging", "lending-core", "c5.2xlarge", 8, 16, 3.2, 12.0, 18.0, 25.0, 720, 244.80, "t3.xlarge + Schedule", 178.60, "Idle 24/7. Downsize to t3.xlarge and stop on nights/weekends."),
    ("i-201122334455cc02", "stage-loan-api-02", "loan-application-service", "staging", "lending-core", "c5.2xlarge", 8, 16, 2.8, 11.5, 17.5, 24.0, 720, 244.80, "t3.xlarge + Schedule", 178.60, "Idle 24/7. Downsize to t3.xlarge and stop on nights/weekends."),
    ("i-212233445566dd01", "stage-risk-scoring-01", "underwriting-engine", "staging", "risk-scoring", "r5.2xlarge", 8, 64, 4.1, 15.0, 12.0, 22.0, 720, 362.88, "t3.xlarge + Schedule", 282.98, "Oversized for staging. Downsize + schedule 9am-7pm weekdays."),
    ("i-223344556677ee01", "stage-bureau-conn-01", "credit-bureau-connector", "staging", "risk-scoring", "m5.xlarge", 4, 16, 2.1, 8.0, 14.0, 20.0, 720, 138.24, "t3.medium + Schedule", 111.60, "Downsize + schedule 9am-7pm weekdays."),
    ("i-234455667788ff01", "stage-kyc-ocr-01", "kyc-document-service", "staging", "lending-core", "c5.2xlarge", 8, 16, 2.5, 9.0, 15.0, 21.0, 720, 244.80, "t3.large + Schedule", 196.90, "Downsize + schedule 9am-7pm weekdays."),
    ("i-245566778899aa01", "stage-payment-gw-01", "payment-gateway-service", "staging", "payments", "c5.xlarge", 4, 8, 1.8, 7.0, 16.0, 22.0, 720, 122.40, "t3.medium + Schedule", 95.80, "Downsize + schedule 9am-7pm weekdays."),
    ("i-256677889900bb01", "stage-disburse-01", "disbursement-engine", "staging", "payments", "m5.xlarge", 4, 16, 2.0, 8.5, 15.5, 21.0, 720, 138.24, "t3.medium + Schedule", 111.60, "Downsize + schedule 9am-7pm weekdays."),
    ("i-267788990011cc01", "stage-analytics-01", "analytics-batch-pipeline", "staging", "data-eng", "r5.2xlarge", 8, 64, 3.5, 14.0, 14.0, 25.0, 720, 362.88, "t3.xlarge + Schedule", 282.98, "Downsize + schedule 9am-7pm weekdays."),
    ("i-278899001122dd01", "stage-notification-01", "notification-service", "staging", "platform", "t3.large", 2, 8, 1.5, 6.0, 12.0, 18.0, 720, 59.90, "t3.small + Schedule", 47.92, "Downsize + schedule 9am-7pm weekdays."),
    
    # Development Environment (Massive Idle Waste, Running 24/7)
    ("i-301122334455ee01", "dev-loan-api-01", "loan-application-service", "dev", "lending-core", "c5.2xlarge", 8, 16, 1.2, 8.0, 12.0, 18.0, 720, 244.80, "t3.medium + Schedule", 218.20, "Dev cluster running 24/7. Auto-stop after hours + downsize."),
    ("i-301122334455ee02", "dev-loan-api-02", "loan-application-service", "dev", "lending-core", "c5.2xlarge", 8, 16, 1.0, 7.5, 11.5, 17.0, 720, 244.80, "Terminate (redundant)", 244.80, "Redundant dev node. Single node sufficient for dev."),
    ("i-312233445566ff01", "dev-risk-scoring-01", "underwriting-engine", "dev", "risk-scoring", "r5.2xlarge", 8, 64, 2.0, 9.0, 10.0, 16.0, 720, 362.88, "t3.large + Schedule", 322.90, "Downsize to t3.large + Auto-stop 7pm-9am and weekends."),
    ("i-323344556677aa01", "dev-bureau-conn-01", "credit-bureau-connector", "dev", "risk-scoring", "m5.large", 2, 8, 1.1, 5.0, 10.0, 15.0, 720, 69.12, "t3.small + Schedule", 57.14, "Downsize + Auto-stop."),
    ("i-334455667788bb01", "dev-kyc-ocr-01", "kyc-document-service", "dev", "lending-core", "c5.2xlarge", 8, 16, 1.5, 7.0, 11.0, 17.0, 720, 244.80, "t3.medium + Schedule", 218.20, "Downsize + Auto-stop."),
    ("i-345566778899cc01", "dev-payment-gw-01", "payment-gateway-service", "dev", "payments", "c5.xlarge", 4, 8, 0.9, 4.5, 12.0, 16.0, 720, 122.40, "t3.small + Schedule", 108.42, "Mock payment service. t3.small sufficient."),
    ("i-356677889900dd01", "dev-disburse-01", "disbursement-engine", "dev", "payments", "m5.large", 2, 8, 1.0, 5.0, 11.0, 16.0, 720, 69.12, "t3.small + Schedule", 57.14, "Downsize + Auto-stop."),
    ("i-367788990011ee01", "dev-analytics-01", "analytics-batch-pipeline", "dev", "data-eng", "r5.2xlarge", 8, 64, 1.8, 8.0, 12.0, 18.0, 720, 362.88, "t3.large + Schedule", 322.90, "Downsize + Auto-stop."),
    ("i-378899001122ff01", "dev-feature-store-01", "feature-store-ml", "dev", "data-eng", "m5.2xlarge", 8, 32, 1.4, 6.0, 15.0, 20.0, 720, 276.48, "t3.large + Schedule", 236.50, "Downsize + Auto-stop."),
    ("i-389900112233aa01", "dev-test-sandbox-01", "sandbox-experimental", "dev", "lending-core", "m5.4xlarge", 16, 64, 0.2, 1.5, 5.0, 8.0, 720, 552.96, "Terminate (Abandoned)", 552.96, "Abandoned sandbox created 4 months ago. Terminate immediately."),
    ("i-390011223344bb01", "dev-perf-test-01", "perf-testing-load", "dev", "platform", "c5.4xlarge", 16, 32, 0.1, 0.8, 4.0, 6.0, 720, 489.60, "Terminate (Abandoned)", 489.60, "Ad-hoc load test instance left running. Terminate immediately.")
]

with open('data/instance_utilisation.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "instance_id", "instance_name", "service_name", "environment", "team",
        "instance_type", "vcpu", "mem_gb", "avg_cpu_pct", "peak_cpu_pct",
        "avg_mem_pct", "peak_mem_pct", "hours_running_monthly", "monthly_cost_usd",
        "recommended_action", "projected_monthly_savings_usd", "technical_notes"
    ])
    for row in instances:
        writer.writerow(row)

print("Generated instance_utilisation.csv")

# 4. storage_inventory.csv
# S3 buckets, EBS volumes, EFS
storage = [
    # S3 Buckets
    ("s3-lendflow-loan-docs-prod", "s3-bucket", "kyc-document-service", "prod", 145000, "S3 Standard", 0, 180, 3335.00, "attached", 0, 0, "active", "Apply Lifecycle: >30d to Standard-IA, >90d to Glacier Instant", 1850.00),
    ("s3-lendflow-audit-logs-prod", "s3-bucket", "platform-compliance", "prod", 85000, "S3 Standard", 0, 365, 1955.00, "attached", 0, 0, "active", "Apply Lifecycle: >90d to Glacier Flexible (SOC 2 / RBI compliant)", 1250.00),
    ("s3-lendflow-raw-analytics-prod", "s3-bucket", "analytics-batch-pipeline", "prod", 110000, "S3 Standard", 0, 120, 2530.00, "attached", 0, 0, "active", "Enable S3 Intelligent-Tiering for variable analytics data", 1100.00),
    ("s3-lendflow-dev-temp-dumps", "s3-bucket", "sandbox-experimental", "dev", 35000, "S3 Standard", 0, 150, 805.00, "attached", 0, 0, "stale", "Purge temp test dumps >14 days. Apply 14d TTL lifecycle.", 680.00),
    
    # EBS Volumes - Unattached (Orphaned Waste)
    ("vol-0a111111111111111", "ebs-volume", "loan-application-service", "prod", 1000, "gp2", 3000, 120, 100.00, "unattached", 12, 1200, "orphaned", "Delete orphaned volume and purge old snapshots", 100.00),
    ("vol-0a222222222222222", "ebs-volume", "underwriting-engine", "prod", 2000, "gp2", 6000, 180, 200.00, "unattached", 18, 2800, "orphaned", "Delete orphaned volume and purge old snapshots", 200.00),
    ("vol-0a333333333333333", "ebs-volume", "kyc-document-service", "staging", 1500, "gp2", 4500, 90, 150.00, "unattached", 8, 1200, "orphaned", "Delete orphaned volume", 150.00),
    ("vol-0a444444444444444", "ebs-volume", "perf-testing-load", "dev", 3000, "gp2", 9000, 140, 300.00, "unattached", 15, 3500, "orphaned", "Delete orphaned volume from perf testing", 300.00),
    
    # EBS Volumes - Attached (GP2 to GP3 Migration & Oversized)
    ("vol-0b111111111111111", "ebs-volume", "loan-application-service", "prod", 4000, "gp2", 12000, 1, 400.00, "attached", 45, 8000, "active", "Migrate GP2 to GP3 (20% savings + higher baseline IOPS)", 80.00),
    ("vol-0b222222222222222", "ebs-volume", "underwriting-engine", "prod", 6000, "gp2", 18000, 1, 600.00, "attached", 60, 12000, "active", "Migrate GP2 to GP3", 120.00),
    ("vol-0b333333333333333", "ebs-volume", "payment-gateway-service", "prod", 2000, "gp2", 6000, 1, 200.00, "attached", 30, 4000, "active", "Migrate GP2 to GP3 (PCI DSS compliant)", 40.00),
    ("vol-0b444444444444444", "ebs-volume", "disbursement-engine", "prod", 3000, "gp2", 9000, 1, 300.00, "attached", 40, 6000, "active", "Migrate GP2 to GP3", 60.00),
    ("vol-0b555555555555555", "ebs-volume", "analytics-batch-pipeline", "prod", 8000, "gp2", 24000, 1, 800.00, "attached", 90, 18000, "active", "Migrate GP2 to GP3 + purge snapshots >30d", 160.00),
    ("vol-0b666666666666666", "ebs-volume", "feature-store-ml", "prod", 5000, "gp2", 15000, 1, 500.00, "attached", 50, 10000, "active", "Migrate GP2 to GP3", 100.00),
    ("vol-0b777777777777777", "ebs-volume", "stage-loan-api", "staging", 2000, "gp2", 6000, 1, 200.00, "attached", 25, 3000, "active", "Migrate GP2 to GP3 & reduce size to 500GB", 130.00),
    ("vol-0b888888888888888", "ebs-volume", "dev-loan-api", "dev", 2000, "gp2", 6000, 1, 200.00, "attached", 20, 2500, "active", "Migrate GP2 to GP3 & reduce size to 300GB", 150.00),
    
    # EBS Snapshot Waste (>30 days non-compliant accumulation)
    ("snap-fleet-policy-waste", "ebs-snapshots", "all-services", "all", 65000, "EBS Snapshot", 0, 210, 3250.00, "attached", 420, 65000, "accumulated", "Enforce DLM lifecycle: max 30d retention (saves 50% snapshot spend)", 1000.00)
]

with open('data/storage_inventory.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "resource_id", "resource_type", "service_name", "environment",
        "size_gb", "storage_tier_type", "iops", "last_access_days",
        "monthly_cost_usd", "attachment_status", "snapshot_count",
        "snapshot_size_gb", "lifecycle_status", "recommendation",
        "projected_monthly_savings_usd"
    ])
    for row in storage:
        writer.writerow(row)

print("Generated storage_inventory.csv")

# 5. data_transfer_log.csv
# Top 10 costliest transfer paths
dt_paths = [
    ("DT-PATH-01", "kyc-document-service (ap-south-1a)", "s3-lendflow-loan-docs-prod (via Public NAT)", "NAT Gateway Data Processing", 105000, 0.045, 4725.00, "EC2 downloading S3 docs via Public NAT Gateway instead of S3 Gateway Endpoint", "Deploy AWS S3 Gateway Endpoint (Free route via VPC route table)", "Preserves data localisation and RBI multi-AZ compliance", 4725.00),
    ("DT-PATH-02", "loan-application-service (ap-south-1a)", "rds-postgres-primary (ap-south-1b)", "Cross-AZ Inter-Service Transfer", 185000, 0.020, 3700.00, "API in AZ-1a constantly querying Primary DB located in AZ-1b without AZ-affinity", "Align primary application workloads with DB AZ; use read-replicas in AZ-1a", "Maintains multi-AZ standby for RBI/SOC2 high availability", 1850.00),
    ("DT-PATH-03", "underwriting-engine (ap-south-1b)", "credit-bureau-connector (ap-south-1c)", "Cross-AZ Inter-Service Transfer", 75000, 0.020, 1500.00, "Microservices communicating across AZs through external ALB rather than internal DNS/Service Connect", "Implement AWS Cloud Map / ECS Service Connect with local AZ priority routing", "Internal TLS 1.3 encryption maintained for PCI DSS", 750.00),
    ("DT-PATH-04", "analytics-batch-pipeline (ap-south-1a)", "s3-lendflow-raw-analytics-prod (via Public NAT)", "NAT Gateway Data Processing", 45000, 0.045, 2025.00, "Nightly batch ETL downloading large parquet dumps through NAT Gateway", "Route all S3 analytics traffic through S3 VPC Gateway Endpoint", "Zero data egress charge via Gateway Endpoint", 2025.00),
    ("DT-PATH-05", "api-gateway-mesh (ap-south-1)", "external-client-egress (Internet)", "Internet Egress Transfer", 80000, 0.090, 7200.00, "Direct API responses, uncompressed JSON payloads, redundant polling headers", "Enable GZIP/Brotli compression at ALB/CloudFront; implement HTTP 304 caching", "Safe, no compliance breach; improves client latency", 1440.00),
    ("DT-PATH-06", "audit-logging-agent (ap-south-1)", "cloudwatch-logs / datadog (Internet)", "Public NAT / Internet Egress", 35000, 0.045, 1575.00, "Verbose debug logs shipped to external SaaS over NAT Gateway", "Deploy CloudWatch Logs Interface VPC Endpoint; filter redundant debug logs", "SOC 2 Type II audit trail fully retained at lower volume", 700.00),
    ("DT-PATH-07", "payment-gateway-service (ap-south-1a)", "payment-processor-partner (Internet)", "Internet Egress Transfer", 22000, 0.090, 1980.00, "PCI payment token authorization payloads to payment aggregator", "Optimise payload schema, negotiate AWS Direct Connect / Partner Interconnect", "Strict PCI DSS network isolation verified", 198.00),
    ("DT-PATH-08", "disbursement-engine (ap-south-1b)", "core-banking-api (eu-west-1 Partner)", "Cross-Region Transfer", 12000, 0.020, 240.00, "Banking settlement synchronization with European partner bank", "Batch settlement summaries hourly instead of real-time per-transaction RPC", "GDPR compliance verified; EU data remains strictly within EU boundaries", 72.00),
    ("DT-PATH-09", "staging-environment (ap-south-1)", "s3-lendflow-dev-temp-dumps (via NAT)", "NAT Gateway Data Processing", 18000, 0.045, 810.00, "Staging regression tests downloading test datasets through NAT Gateway", "Enable S3 VPC Endpoint on Staging VPC route tables", "Staging testing unaffected", 810.00),
    ("DT-PATH-10", "monitoring-prometheus (ap-south-1a)", "all-nodes (ap-south-1b, ap-south-1c)", "Cross-AZ Inter-Service Transfer", 32000, 0.020, 640.00, "Centralised Prometheus scraper pulling metrics across AZ boundaries every 15s", "Deploy local Prometheus agent per AZ with remote write aggregation", "Improves monitoring reliability during AZ degradation", 320.00)
]

with open('data/data_transfer_log.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "path_id", "source_service", "destination_service", "transfer_type",
        "monthly_bytes_gb", "cost_per_gb_usd", "monthly_cost_usd",
        "architectural_reason", "optimisation_recommendation",
        "compliance_impact", "projected_monthly_savings_usd"
    ])
    for row in dt_paths:
        writer.writerow(row)

print("Generated data_transfer_log.csv")

# 6. reserved_instance_coverage.csv
# 0% current coverage across all 65 instances
ri_coverage = [
    ("c5.4xlarge", "Compute Optimized", 10, 7200, 4896.00, 0.0, 0.0, 3182.40, 2937.60, 2448.00, "Right-size first to c5.2xlarge, then cover remaining prod baseline with 1-Yr Partial Upfront CSP", 1958.40),
    ("c5.2xlarge", "Compute Optimized", 14, 10080, 3427.20, 0.0, 0.0, 2227.68, 2056.32, 1713.60, "Cover 8 prod baseline instances with 1-Yr Compute Savings Plan", 1370.88),
    ("r5.4xlarge", "Memory Optimized", 6, 4320, 4354.56, 0.0, 0.0, 2830.46, 2612.74, 2177.28, "Right-size to r5.2xlarge, cover prod DB & Scoring with 1-Yr CSP", 1741.82),
    ("r5.2xlarge", "Memory Optimized", 8, 5760, 2903.04, 0.0, 0.0, 1886.98, 1741.82, 1451.52, "Cover prod instances with 1-Yr Partial Upfront CSP", 1161.22),
    ("m5.2xlarge", "General Purpose", 6, 4320, 1658.88, 0.0, 0.0, 1078.27, 995.33, 829.44, "Right-size to m5.xlarge, commit baseline to 1-Yr CSP", 663.55),
    ("m5.xlarge", "General Purpose", 8, 5760, 1105.92, 0.0, 0.0, 718.85, 663.55, 552.96, "Cover prod disbursement baseline with 1-Yr CSP", 442.37),
    ("db.r5.2xlarge", "RDS PostgreSQL Multi-AZ", 2, 1440, 2822.40, 0.0, 0.0, 1834.56, 1693.44, 1411.20, "1-Yr Partial Upfront RDS Reserved Instance for Primary Prod DB", 1128.96),
    ("db.r5.xlarge", "RDS PostgreSQL Multi-AZ", 2, 1440, 1411.20, 0.0, 0.0, 917.28, 846.72, 705.60, "1-Yr Partial Upfront RDS Reserved Instance for Payment Core DB", 564.48),
    ("cache.r5.large", "ElastiCache Redis Cluster", 4, 2880, 1152.00, 0.0, 0.0, 748.80, 691.20, 576.00, "1-Yr Partial Upfront ElastiCache Reserved Node", 460.80)
]

with open('data/reserved_instance_coverage.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "instance_family", "workload_category", "active_instance_count",
        "monthly_hours", "current_on_demand_spend_usd", "current_ri_coverage_pct",
        "current_sp_coverage_pct", "rate_1yr_no_upfront_usd",
        "rate_1yr_partial_upfront_usd", "rate_3yr_partial_upfront_usd",
        "recommended_commitment_strategy", "projected_monthly_savings_usd"
    ])
    for row in ri_coverage:
        writer.writerow(row)

print("Generated reserved_instance_coverage.csv")

# 7. tag_compliance_report.csv
# Audit showing ~58% compliance, identifying untagged dark spend
tags_data = [
    ("ec2-prod-loan-api-01", "ec2-instance", "prod", "lending-core", "Retail Lending", "CC-101", "LoanApp", "PCI-Scope", "None", "Confidential", "terraform", "COMPLIANT", 0, 489.60, "Fully Allocated"),
    ("ec2-prod-risk-scoring-01", "ec2-instance", "prod", "risk-scoring", "Risk & Underwriting", "CC-102", "RiskEngine", "SOC2-Scope", "None", "Restricted", "terraform", "COMPLIANT", 0, 725.76, "Fully Allocated"),
    ("ec2-stage-loan-api-01", "ec2-instance", "staging", "lending-core", "Retail Lending", "CC-101", "LoanApp", "None", "30d", "Internal", "manual-console", "NON_COMPLIANT", 3, 244.80, "Partially Allocated"),
    ("ec2-dev-loan-api-02", "ec2-instance", "dev", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", "None", "None", "UNKNOWN", "arjun.d", "NON_COMPLIANT", 7, 244.80, "Dark Spend (Untagged)"),
    ("ec2-dev-perf-test-01", "ec2-instance", "dev", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", "None", "None", "UNKNOWN", "ad-hoc-test", "NON_COMPLIANT", 8, 489.60, "Dark Spend (Untagged)"),
    ("ec2-dev-test-sandbox-01", "ec2-instance", "dev", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", "None", "None", "UNKNOWN", "sanjay.p", "NON_COMPLIANT", 8, 552.96, "Dark Spend (Untagged)"),
    ("vol-0a111111111111111", "ebs-volume", "prod", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", "None", "None", "UNKNOWN", "legacy", "NON_COMPLIANT", 8, 100.00, "Dark Spend (Orphaned)"),
    ("vol-0a444444444444444", "ebs-volume", "dev", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", "None", "None", "UNKNOWN", "perf-script", "NON_COMPLIANT", 8, 300.00, "Dark Spend (Orphaned)"),
    ("s3-lendflow-dev-temp-dumps", "s3-bucket", "dev", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", "None", "None", "UNKNOWN", "developer", "NON_COMPLIANT", 7, 805.00, "Dark Spend (Untagged)"),
    ("rds-postgres-staging-01", "rds-instance", "staging", "platform", "Platform Core", "CC-104", "DB-Shared", "None", "None", "Internal", "terraform", "NON_COMPLIANT", 2, 1411.20, "Partially Allocated"),
    ("elasticache-redis-dev-01", "elasticache-cluster", "dev", "UNKNOWN", "UNKNOWN", "UNKNOWN", "UNKNOWN", "None", "None", "UNKNOWN", "console", "NON_COMPLIANT", 7, 576.00, "Dark Spend (Untagged)"),
    ("nat-gw-ap-south-1a", "nat-gateway", "prod", "platform", "Platform Core", "CC-104", "Networking", "None", "None", "Internal", "terraform", "NON_COMPLIANT", 3, 2450.00, "Unallocated Shared Cost"),
    ("nat-gw-ap-south-1b", "nat-gateway", "prod", "platform", "Platform Core", "CC-104", "Networking", "None", "None", "Internal", "terraform", "NON_COMPLIANT", 3, 2450.00, "Unallocated Shared Cost"),
    ("nat-gw-ap-south-1c", "nat-gateway", "prod", "platform", "Platform Core", "CC-104", "Networking", "None", "None", "Internal", "terraform", "NON_COMPLIANT", 3, 2450.00, "Unallocated Shared Cost")
]

with open('data/tag_compliance_report.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "resource_id", "resource_type", "environment", "team", "business_unit",
        "tag_cost_centre", "tag_product", "tag_compliance_scope", "tag_ttl",
        "tag_data_classification", "tag_created_by", "compliance_status",
        "missing_mandatory_tags", "monthly_spend_usd", "allocation_category"
    ])
    for row in tags_data:
        writer.writerow(row)

print("Generated tag_compliance_report.csv")

# 8. cost_anomaly_events.csv
# 10 historical anomaly events
anomalies = [
    ("ANOM-2026-001", "2026-04-12", "analytics-batch-pipeline", "prod", "Runaway Spark / EMR Job", "Developer test script looping over unindexed S3 partition in infinite retry", "AWS Cost Anomaly Detection (Email)", 48, 120.00, 3850.00, 3730.00, "Job terminated manually; S3 partition index fixed; retry limit enforced", "RESOLVED"),
    ("ANOM-2026-002", "2026-05-03", "sandbox-experimental", "dev", "Abandoned GPU Instance", "Data scientist launched p3.8xlarge for exploratory credit scoring model and forgot to stop", "End of month invoice review", 336, 0.00, 6144.00, 6144.00, "Instance terminated; auto-stop policy created; GPU launches restricted via IAM", "RESOLVED"),
    ("ANOM-2026-003", "2026-06-18", "kyc-document-service", "prod", "NAT Gateway Egress Surge", "Microservice release v2.4 changed S3 client SDK configuration, dropping VPC Gateway Endpoint route", "Datadog network monitor", 72, 800.00, 5400.00, 4600.00, "Hotfix deployed restoring VPC endpoint; integration tests added for routing tables", "RESOLVED"),
    ("ANOM-2026-004", "2026-07-02", "perf-testing-load", "dev", "Load Test Cluster Left Active", "Pre-launch stress test cluster (20x c5.4xlarge) left running over 4-day long holiday weekend", "Priya Menon (CFO) budget threshold alert", 96, 200.00, 3916.80, 3716.80, "Instances terminated; TTL tags mandated on all perf test infrastructure", "RESOLVED"),
    ("ANOM-2026-005", "2026-07-24", "underwriting-engine", "prod", "Cross-AZ Traffic Loop", "Kafka partition rebalancing caused consumer group to fetch across AZ-1a and AZ-1c continuously", "CloudWatch network metric alarm", 36, 450.00, 2980.00, 2530.00, "Kafka rack-awareness enabled so consumers fetch from leader in same AZ", "RESOLVED"),
    ("ANOM-2026-006", "2026-08-08", "cloudwatch-logging", "prod", "Debug Logging Flood", "Payment service accidentally set to DEBUG log level before marketing campaign push", "CloudWatch billing metric alarm", 60, 300.00, 4200.00, 3900.00, "Log level restored to INFO; CloudWatch log ingestion anomaly alarm configured", "RESOLVED"),
    ("ANOM-2026-007", "2026-08-22", "ebs-snapshots", "prod", "Snapshot Retention Bug", "Custom backup Lambda script threw exception before calling delete_snapshot on older items", "Monthly FinOps storage audit", 720, 1100.00, 3850.00, 2750.00, "Replaced custom Lambda with native AWS Data Lifecycle Manager (DLM) policies", "RESOLVED"),
    ("ANOM-2026-008", "2026-09-02", "disbursement-engine", "prod", "Cross-Region Duplicate Sync", "Disbursement reconciler synced entire transaction history instead of delta across region", "FinOps daily cost check", 24, 80.00, 1420.00, 1340.00, "Delta-only sync logic verified and deployed with idempotency keys", "RESOLVED"),
    ("ANOM-2026-009", "2026-09-15", "loan-application-service", "dev", "Orphaned Unattached EBS Fleet", "DevOps test pipeline created test volumes during load run without delete_on_termination flag", "Weekly tag & resource compliance report", 120, 50.00, 1850.00, 1800.00, "Cleaned unattached volumes; enforced Terraform security guardrails", "RESOLVED"),
    ("ANOM-2026-010", "2026-09-25", "elasticache-redis", "staging", "Unbounded Redis Key Accumulation", "Session store TTL bug in staging caused memory exhaustion and auto-scaling to larger node", "CloudWatch ElastiCache memory alert", 48, 150.00, 1152.00, 1002.00, "Fixed Redis eviction policy to volatile-lru; rightsized cluster back to cache.t3.medium", "RESOLVED")
]

with open('data/cost_anomaly_events.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "event_id", "detection_date", "affected_service", "environment",
        "anomaly_type", "root_cause", "detection_mechanism",
        "time_to_detection_hours", "expected_cost_usd", "actual_cost_usd",
        "financial_impact_usd", "remediation_action", "resolution_status"
    ])
    for row in anomalies:
        writer.writerow(row)

print("Generated cost_anomaly_events.csv")
print("All 8 simulated datasets successfully generated in data/ folder!")
