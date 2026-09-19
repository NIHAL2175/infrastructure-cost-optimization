import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import csv

wb = openpyxl.Workbook()
wb.remove(wb.active) # Remove default sheet

# Professional FinOps Styling
NAVY = "1B365D"
DARK_TEAL = "005B60"
SLATE = "4A777A"
LIGHT_BLUE = "E8EEF5"
LIGHT_GRAY = "F8F9FA"
ACCENT_GREEN = "1E8449"
SOFT_GREEN = "D4EFDF"
ALERT_RED = "C0392B"
SOFT_RED = "FADBD8"
GOLD = "B7950B"

title_font = Font(name="Calibri", size=14, bold=True, color=NAVY)
sub_font = Font(name="Calibri", size=10, italic=True, color="555555")
header_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
header_fill_navy = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
header_fill_teal = PatternFill(start_color=DARK_TEAL, end_color=DARK_TEAL, fill_type="solid")
bold_font = Font(name="Calibri", size=10, bold=True)
regular_font = Font(name="Calibri", size=10)

currency_fmt = "$#,##0.00"
pct_fmt = "0.0%"
int_fmt = "#,##0"

thin_border = Border(
    left=Side(style='thin', color="E0E0E0"),
    right=Side(style='thin', color="E0E0E0"),
    top=Side(style='thin', color="E0E0E0"),
    bottom=Side(style='thin', color="E0E0E0")
)
total_border = Border(
    top=Side(style='thin', color=NAVY),
    bottom=Side(style='double', color=NAVY)
)

# -------------------------------------------------------------------------
# TAB 1: EXECUTIVE SUMMARY
# -------------------------------------------------------------------------
ws_sum = wb.create_sheet(title="Executive Summary")
ws_sum.views.sheetView[0].showGridLines = True

ws_sum["A1"] = "LendFlow Technologies — FinOps Financial Savings Model"
ws_sum["A1"].font = title_font
ws_sum["A2"] = "Master Financial Reconciliation & Baseline Run-Rate Target (Currency in USD)"
ws_sum["A2"].font = sub_font

# Headline Metrics Cards
ws_sum["A4"] = "Current Monthly Baseline Spend"
ws_sum["A5"] = 180000.00
ws_sum["A5"].number_format = currency_fmt
ws_sum["A5"].font = Font(name="Calibri", size=14, bold=True, color=ALERT_RED)

ws_sum["C4"] = "Target Cost Reduction"
ws_sum["C5"] = 0.3333
ws_sum["C5"].number_format = pct_fmt
ws_sum["C5"].font = Font(name="Calibri", size=14, bold=True, color=NAVY)

ws_sum["E4"] = "Projected Monthly Savings (Expected)"
ws_sum["E5"] = 64250.00
ws_sum["E5"].number_format = currency_fmt
ws_sum["E5"].font = Font(name="Calibri", size=14, bold=True, color=ACCENT_GREEN)

ws_sum["G4"] = "Target Monthly Run-Rate"
ws_sum["G5"] = 115750.00
ws_sum["G5"].number_format = currency_fmt
ws_sum["G5"].font = Font(name="Calibri", size=14, bold=True, color=NAVY)

for c_label, c_val in [("A", "B"), ("C", "D"), ("E", "F"), ("G", "H")]:
    ws_sum[f"{c_label}4"].font = bold_font
    ws_sum[f"{c_label}4"].fill = PatternFill(start_color=LIGHT_BLUE, end_color=LIGHT_BLUE, fill_type="solid")

# Savings by Category Table
sum_headers = [
    "Category #", "Optimisation Domain", "Current Spend (USD)",
    "Expected Monthly Savings (USD)", "Expected Annual Savings (USD)",
    "% Reduction", "Confidence Level", "Implementation Effort", "Key Stakeholder Lead"
]

for col_idx, h in enumerate(sum_headers, 1):
    cell = ws_sum.cell(row=8, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill_navy
    cell.alignment = Alignment(horizontal="center", vertical="center")

savings_categories = [
    ("CAT-01", "Compute Rightsizing & Non-Prod Scheduling", 61200.00, 19450.00, "High (90%)", "Low - Medium", "Ravi Krishnan (VP Eng)"),
    ("CAT-02", "Commitment Strategy (1-Yr Compute Savings Plans)", 38000.00, 14600.00, "Very High (95%)", "Low", "Priya Menon (CFO)"),
    ("CAT-03", "Database Optimisation (RDS Multi-AZ & ElastiCache)", 52200.00, 9800.00, "High (85%)", "Medium", "Arjun Deshmukh (CTO)"),
    ("CAT-04", "Data Transfer & NAT Gateway Bypass", 21600.00, 8800.00, "Very High (95%)", "Low (VPC Endpoints)", "Arjun Deshmukh (CTO)"),
    ("CAT-05", "Storage Lifecycle Policies & EBS GP3 Modernisation", 29700.00, 7600.00, "Very High (95%)", "Low", "Meera Iyer (Compliance)"),
    ("CAT-06", "Spot Instance Orchestration (Batch & OCR Workers)", 9500.00, 4000.00, "Medium (80%)", "Medium", "Sanjay Patel (Data Eng)")
]

for idx, (cid, dom, cur_sp, m_sav, conf, eff, lead) in enumerate(savings_categories, 9):
    ws_sum.cell(row=idx, column=1, value=cid).alignment = Alignment(horizontal="center")
    ws_sum.cell(row=idx, column=2, value=dom).font = regular_font
    ws_sum.cell(row=idx, column=3, value=cur_sp).number_format = currency_fmt
    ws_sum.cell(row=idx, column=4, value=m_sav).number_format = currency_fmt
    ws_sum.cell(row=idx, column=5, value=f"=D{idx}*12").number_format = currency_fmt
    ws_sum.cell(row=idx, column=6, value=f"=D{idx}/C{idx}").number_format = pct_fmt
    ws_sum.cell(row=idx, column=7, value=conf).alignment = Alignment(horizontal="center")
    ws_sum.cell(row=idx, column=8, value=eff).alignment = Alignment(horizontal="center")
    ws_sum.cell(row=idx, column=9, value=lead).font = regular_font
    
    for c in range(1, 10):
        ws_sum.cell(row=idx, column=c).border = thin_border
        if idx % 2 == 0:
            ws_sum.cell(row=idx, column=c).fill = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")

tot_sum_row = 15
ws_sum.cell(row=tot_sum_row, column=1, value="TOTALS").font = bold_font
ws_sum.cell(row=tot_sum_row, column=2, value="Consolidated FinOps Framework Target").font = bold_font
ws_sum.cell(row=tot_sum_row, column=3, value=180000.00).number_format = currency_fmt
ws_sum.cell(row=tot_sum_row, column=4, value=f"=SUM(D9:D14)").number_format = currency_fmt
ws_sum.cell(row=tot_sum_row, column=5, value=f"=D{tot_sum_row}*12").number_format = currency_fmt
ws_sum.cell(row=tot_sum_row, column=6, value=f"=D{tot_sum_row}/C{tot_sum_row}").number_format = pct_fmt
ws_sum.cell(row=tot_sum_row, column=7, value="Target Exceeded (+2.4% buffer)").font = bold_font
ws_sum.cell(row=tot_sum_row, column=8, value="90-Day Execution").font = bold_font
ws_sum.cell(row=tot_sum_row, column=9, value="Joint CoE Team").font = bold_font

for c in range(1, 10):
    ws_sum.cell(row=tot_sum_row, column=c).font = bold_font
    ws_sum.cell(row=tot_sum_row, column=c).border = total_border

# Scenario Sensitivity Table
ws_sum["A18"] = "Scenario & Sensitivity Analysis (90-Day Outlook)"
ws_sum["A18"].font = Font(name="Calibri", size=12, bold=True, color=NAVY)

scen_headers = ["Scenario", "Description / Risk Factors", "Monthly Savings (USD)", "Annual Savings (USD)", "% Spend Reduction", "New Monthly Spend (USD)"]
for col_idx, h in enumerate(scen_headers, 1):
    cell = ws_sum.cell(row=20, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill_teal
    cell.alignment = Alignment(horizontal="center", vertical="center")

scenarios = [
    ("Worst-Case Scenario", "Conservative rightsizing; 15% Spot interruption buffer; partial dev scheduling adherence", 56400.00),
    ("Expected Scenario (Base Case)", "Full rightsizing, 9am-7pm dev scheduling, 1-Yr CSP, S3 lifecycle, VPC endpoints", 64250.00),
    ("Best-Case Scenario", "Aggressive Graviton3 migration, 3-Yr CSP on core, 80% Spot in OCR batch processing", 71800.00)
]

for s_idx, (s_name, s_desc, m_sav) in enumerate(scenarios, 21):
    ws_sum.cell(row=s_idx, column=1, value=s_name).font = bold_font
    ws_sum.cell(row=s_idx, column=2, value=s_desc).font = regular_font
    ws_sum.cell(row=s_idx, column=3, value=m_sav).number_format = currency_fmt
    ws_sum.cell(row=s_idx, column=4, value=f"=C{s_idx}*12").number_format = currency_fmt
    ws_sum.cell(row=s_idx, column=5, value=f"=C{s_idx}/$C$15").number_format = pct_fmt
    ws_sum.cell(row=s_idx, column=6, value=f"=$C$15-C{s_idx}").number_format = currency_fmt
    
    for c in range(1, 7):
        ws_sum.cell(row=s_idx, column=c).border = thin_border
        if s_idx == 22:
            ws_sum.cell(row=s_idx, column=c).fill = PatternFill(start_color=SOFT_GREEN, end_color=SOFT_GREEN, fill_type="solid")

# -------------------------------------------------------------------------
# TAB 2: COMPUTE ANALYSIS
# -------------------------------------------------------------------------
ws_comp = wb.create_sheet(title="Compute Analysis")
ws_comp.views.sheetView[0].showGridLines = True

ws_comp["A1"] = "LendFlow Technologies — EC2 Compute Fleet Inventory & Rightsizing Telemetry"
ws_comp["A1"].font = title_font
ws_comp["A2"] = "Detailed Utilization Profiling & Downsizing Targets (Source: instance_utilisation.csv)"
ws_comp["A2"].font = sub_font

comp_headers = [
    "Instance ID", "Name / Service", "Environment", "Team", "Current Type",
    "vCPU", "RAM (GB)", "Avg CPU %", "Peak CPU %", "Avg RAM %", "Monthly Cost (USD)",
    "Recommended Target", "Target Monthly Cost (USD)", "Projected Monthly Savings (USD)",
    "Action Rationale"
]

for col_idx, h in enumerate(comp_headers, 1):
    cell = ws_comp.cell(row=4, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill_navy
    cell.alignment = Alignment(horizontal="center", vertical="center")

with open('data/instance_utilisation.csv', 'r', encoding='utf-8') as f:
    c_reader = csv.DictReader(f)
    c_rows = list(c_reader)

for r_idx, row in enumerate(c_rows, 5):
    iid = row["instance_id"]
    name = row["instance_name"]
    env = row["environment"]
    team = row["team"]
    itype = row["instance_type"]
    vcpu = int(row["vcpu"])
    ram = int(row["mem_gb"])
    avg_cpu = float(row["avg_cpu_pct"]) / 100.0
    peak_cpu = float(row["peak_cpu_pct"]) / 100.0
    avg_ram = float(row["avg_mem_pct"]) / 100.0
    m_cost = float(row["monthly_cost_usd"])
    rec = row["recommended_action"]
    sav = float(row["projected_monthly_savings_usd"])
    target_cost = m_cost - sav
    notes = row["technical_notes"]
    
    ws_comp.cell(row=r_idx, column=1, value=iid).alignment = Alignment(horizontal="center")
    ws_comp.cell(row=r_idx, column=2, value=name).font = regular_font
    ws_comp.cell(row=r_idx, column=3, value=env).alignment = Alignment(horizontal="center")
    ws_comp.cell(row=r_idx, column=4, value=team).font = regular_font
    ws_comp.cell(row=r_idx, column=5, value=itype).alignment = Alignment(horizontal="center")
    ws_comp.cell(row=r_idx, column=6, value=vcpu).alignment = Alignment(horizontal="center")
    ws_comp.cell(row=r_idx, column=7, value=ram).alignment = Alignment(horizontal="center")
    ws_comp.cell(row=r_idx, column=8, value=avg_cpu).number_format = pct_fmt
    ws_comp.cell(row=r_idx, column=9, value=peak_cpu).number_format = pct_fmt
    ws_comp.cell(row=r_idx, column=10, value=avg_ram).number_format = pct_fmt
    ws_comp.cell(row=r_idx, column=11, value=m_cost).number_format = currency_fmt
    ws_comp.cell(row=r_idx, column=12, value=rec).font = regular_font
    ws_comp.cell(row=r_idx, column=13, value=target_cost).number_format = currency_fmt
    ws_comp.cell(row=r_idx, column=14, value=f"=K{r_idx}-M{r_idx}").number_format = currency_fmt
    ws_comp.cell(row=r_idx, column=15, value=notes).font = regular_font
    
    # Highlight low CPU instances (<20%)
    if avg_cpu < 0.20:
        ws_comp.cell(row=r_idx, column=8).fill = PatternFill(start_color=SOFT_RED, end_color=SOFT_RED, fill_type="solid")
        
    for c in range(1, 16):
        ws_comp.cell(row=r_idx, column=c).border = thin_border
        if r_idx % 2 == 0 and avg_cpu >= 0.20:
            ws_comp.cell(row=r_idx, column=c).fill = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")

# Compute Totals Row
tot_c_row = len(c_rows) + 5
ws_comp.cell(row=tot_c_row, column=1, value="TOTALS").font = bold_font
ws_comp.cell(row=tot_c_row, column=2, value=f"{len(c_rows)} Evaluated Fleet Instances").font = bold_font
ws_comp.cell(row=tot_c_row, column=11, value=f"=SUM(K5:K{tot_c_row-1})").number_format = currency_fmt
ws_comp.cell(row=tot_c_row, column=13, value=f"=SUM(M5:M{tot_c_row-1})").number_format = currency_fmt
ws_comp.cell(row=tot_c_row, column=14, value=f"=SUM(N5:N{tot_c_row-1})").number_format = currency_fmt
ws_comp.cell(row=tot_c_row, column=15, value="Achieves $19,450/mo Rightsizing + Dev Schedule target").font = bold_font

for c in range(1, 16):
    ws_comp.cell(row=tot_c_row, column=c).font = bold_font
    ws_comp.cell(row=tot_c_row, column=c).border = total_border

# -------------------------------------------------------------------------
# TAB 3: DATABASE ANALYSIS
# -------------------------------------------------------------------------
ws_db = wb.create_sheet(title="Database Analysis")
ws_db.views.sheetView[0].showGridLines = True

ws_db["A1"] = "LendFlow Technologies — RDS PostgreSQL & ElastiCache Optimisation"
ws_db["A1"].font = title_font
ws_db["A2"] = "Database Sizing, Multi-AZ Evaluation, Replica Consolidation & Caching Efficiency"
ws_db["A2"].font = sub_font

db_headers = [
    "Cluster / DB ID", "Service Name", "Environment", "Engine & Topology",
    "Current Instance Type", "vCPU", "RAM (GB)", "Avg CPU %", "Avg Connections",
    "Current Spend (USD)", "Optimisation Recommendation", "Target Topology / Type",
    "Projected Monthly Savings (USD)", "Compliance Verification (RBI / PCI DSS)"
]

for col_idx, h in enumerate(db_headers, 1):
    cell = ws_db.cell(row=4, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill_navy
    cell.alignment = Alignment(horizontal="center", vertical="center")

db_data = [
    ("rds-loan-core-primary", "loan-application-service", "prod", "PostgreSQL Multi-AZ", "db.r5.2xlarge", 8, 64, 0.42, 380, 2822.40, "Retain Multi-AZ for RBI compliance; apply 1-Yr Partial Upfront RI", "db.r5.2xlarge (Reserved)", 1128.96, "RBI Multi-AZ synchronous replication preserved"),
    ("rds-loan-core-replica-01", "loan-application-service", "prod", "PostgreSQL Read Replica", "db.r5.2xlarge", 8, 64, 0.18, 45, 1411.20, "Consolidate read replica to db.r5.xlarge (QPS easily handled by xlarge)", "db.r5.xlarge", 705.60, "Audit logging and read isolation maintained"),
    ("rds-loan-core-replica-02", "reporting-analytics", "prod", "PostgreSQL Read Replica", "db.r5.2xlarge", 8, 64, 0.04, 12, 1411.20, "Decommission dedicated replica; shift scheduled reports to Athena/S3 lake", "Decommission / S3 Lake", 1411.20, "Zero production OLTP performance impact"),
    ("rds-payment-core-primary", "payment-gateway-service", "prod", "PostgreSQL Multi-AZ", "db.r5.xlarge", 4, 32, 0.38, 220, 1411.20, "PCI DSS scope. Retain Multi-AZ; apply 1-Yr Partial Upfront RI", "db.r5.xlarge (Reserved)", 564.48, "PCI DSS network isolation & Multi-AZ preserved"),
    ("rds-underwrite-db", "underwriting-engine", "prod", "PostgreSQL Multi-AZ", "db.r5.2xlarge", 8, 64, 0.28, 190, 2822.40, "Apply 1-Yr Partial Upfront RI", "db.r5.2xlarge (Reserved)", 1128.96, "SOC 2 Type II audit logging preserved"),
    ("rds-staging-shared-01", "staging-environment", "staging", "PostgreSQL Multi-AZ", "db.r5.xlarge", 4, 32, 0.05, 15, 1411.20, "Downgrade Multi-AZ to Single-AZ db.t4g.large (Graviton); schedule off-hours", "db.t4g.large (Single-AZ)", 1091.20, "Staging only; no compliance SLA required"),
    ("rds-dev-shared-01", "dev-environment", "dev", "PostgreSQL Multi-AZ", "db.m5.xlarge", 4, 16, 0.02, 6, 960.00, "Downgrade to db.t4g.medium Single-AZ; auto-stop 7pm-9am and weekends", "db.t4g.medium (Single-AZ)", 780.00, "Dev only; automated snapshot before nightly stop"),
    ("cache-redis-prod-cluster", "loan-application-service", "prod", "Redis Multi-AZ (3 Nodes)", "cache.r5.large", 2, 13, 0.25, 450, 864.00, "Migrate to Graviton cache.m6g.large (5% cheaper + 20% faster) + 1-Yr RI", "cache.m6g.large (Reserved)", 345.60, "Zero cache downtime via rolling replacement"),
    ("cache-redis-session-prod", "auth-identity-service", "prod", "Redis Multi-AZ (2 Nodes)", "cache.r5.large", 2, 13, 0.22, 320, 576.00, "Migrate to Graviton cache.m6g.large + 1-Yr RI", "cache.m6g.large (Reserved)", 230.40, "Session resilience preserved"),
    ("cache-redis-staging", "staging-environment", "staging", "Redis Multi-AZ (2 Nodes)", "cache.r5.large", 2, 13, 0.03, 20, 576.00, "Convert to Single-Node cache.t4g.medium; schedule off-hours", "cache.t4g.medium", 456.00, "Staging test caching"),
    ("cache-redis-dev-idle", "dev-environment", "dev", "Redis Single Node", "cache.r5.large", 2, 13, 0.01, 4, 288.00, "Convert to cache.t4g.micro; auto-stop nights & weekends", "cache.t4g.micro", 252.00, "Development mock caching"),
    ("aurora-analytics-candidate", "analytics-batch-pipeline", "prod", "Provisioned Aurora PG", "db.r5.2xlarge", 8, 64, 0.12, 30, 2400.00, "Migrate variable batch querying to Aurora Serverless v2 (0.5 to 4 ACUs)", "Aurora Serverless v2", 1705.60, "Scales down to 0.5 ACU ($0.06/hr) outside 4h run")
]

for r_idx, (db_id, svc, env, top, itype, vcpu, ram, cpu, conn, cur_sp, rec, tgt, sav, comp) in enumerate(db_data, 5):
    ws_db.cell(row=r_idx, column=1, value=db_id).font = regular_font
    ws_db.cell(row=r_idx, column=2, value=svc).font = regular_font
    ws_db.cell(row=r_idx, column=3, value=env).alignment = Alignment(horizontal="center")
    ws_db.cell(row=r_idx, column=4, value=top).font = regular_font
    ws_db.cell(row=r_idx, column=5, value=itype).alignment = Alignment(horizontal="center")
    ws_db.cell(row=r_idx, column=6, value=vcpu).alignment = Alignment(horizontal="center")
    ws_db.cell(row=r_idx, column=7, value=ram).alignment = Alignment(horizontal="center")
    ws_db.cell(row=r_idx, column=8, value=cpu).number_format = pct_fmt
    ws_db.cell(row=r_idx, column=9, value=conn).number_format = int_fmt
    ws_db.cell(row=r_idx, column=10, value=cur_sp).number_format = currency_fmt
    ws_db.cell(row=r_idx, column=11, value=rec).font = regular_font
    ws_db.cell(row=r_idx, column=12, value=tgt).font = regular_font
    ws_db.cell(row=r_idx, column=13, value=sav).number_format = currency_fmt
    ws_db.cell(row=r_idx, column=14, value=comp).font = regular_font
    
    for c in range(1, 15):
        ws_db.cell(row=r_idx, column=c).border = thin_border
        if r_idx % 2 == 0:
            ws_db.cell(row=r_idx, column=c).fill = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")

tot_db_row = len(db_data) + 5
ws_db.cell(row=tot_db_row, column=1, value="TOTALS").font = bold_font
ws_db.cell(row=tot_db_row, column=2, value="Evaluated Database & Cache Estate").font = bold_font
ws_db.cell(row=tot_db_row, column=10, value=f"=SUM(J5:J{tot_db_row-1})").number_format = currency_fmt
ws_db.cell(row=tot_db_row, column=13, value=f"=SUM(M5:M{tot_db_row-1})").number_format = currency_fmt
ws_db.cell(row=tot_db_row, column=14, value="Achieves $9,800/mo Database Optimisation target").font = bold_font

for c in range(1, 15):
    ws_db.cell(row=tot_db_row, column=c).font = bold_font
    ws_db.cell(row=tot_db_row, column=c).border = total_border

# Auto-fit column widths across all three sheets
for ws in [ws_sum, ws_comp, ws_db]:
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(min(max_len + 3, 45), 11)

wb.save('analysis/savings-model.xlsx')
print("Generated analysis/savings-model.xlsx with Executive Summary, Compute, and Database tabs!")
