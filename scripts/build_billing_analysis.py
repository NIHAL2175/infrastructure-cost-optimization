import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import csv

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Color Palette: Professional FinOps Navy & Slate
NAVY_HEADER = "1B365D"
SLATE_ACCENT = "4A777A"
LIGHT_BLUE = "E8EEF5"
LIGHT_GRAY = "F4F6F8"
ALERT_RED = "FADBD8"
SUCCESS_GREEN = "D4EFDF"

header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
header_fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
title_font = Font(name="Calibri", size=14, bold=True, color="1B365D")
sub_font = Font(name="Calibri", size=10, italic=True, color="555555")
bold_font = Font(name="Calibri", size=11, bold=True)
regular_font = Font(name="Calibri", size=11)
currency_format = "$#,##0.00"
pct_format = "0.0%"
int_format = "#,##0"

thin_border = Border(
    left=Side(style='thin', color="CCCCCC"),
    right=Side(style='thin', color="CCCCCC"),
    top=Side(style='thin', color="CCCCCC"),
    bottom=Side(style='thin', color="CCCCCC")
)
total_border = Border(
    top=Side(style='thin', color="1B365D"),
    bottom=Side(style='double', color="1B365D")
)

# ----------------------------------------------------
# Sheet 1: 12-Month Spend Trend & MoM Growth
# ----------------------------------------------------
ws1 = wb.create_sheet(title="12-Month Spend Trend")
ws1.views.sheetView[0].showGridLines = True

ws1["A1"] = "LendFlow Technologies — 12-Month AWS Spend & Variance Analysis"
ws1["A1"].font = title_font
ws1["A2"] = "Baseline Analysis: October 2025 to September 2026 (Currency in USD)"
ws1["A2"].font = sub_font

headers_ws1 = [
    "Billing Period", "Budget (USD)", "Actual Spend (USD)", "Variance (USD)",
    "Variance %", "MoM Growth %", "Loan Applications", "Cost / Application (USD)"
]

for col_idx, h in enumerate(headers_ws1, 1):
    cell = ws1.cell(row=4, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

# Read monthly data
with open('data/monthly_cost_summary.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for r_idx, row in enumerate(rows, 5):
    p = row["billing_period"]
    b = float(row["budget_usd"])
    a = float(row["total_spend_usd"])
    apps = int(row["loan_applications"])
    
    ws1.cell(row=r_idx, column=1, value=p).alignment = Alignment(horizontal="center")
    ws1.cell(row=r_idx, column=2, value=b).number_format = currency_format
    ws1.cell(row=r_idx, column=3, value=a).number_format = currency_format
    
    # Formula for Variance = Actual - Budget
    ws1.cell(row=r_idx, column=4, value=f"=C{r_idx}-B{r_idx}").number_format = currency_format
    
    # Formula for Variance % = (Actual - Budget) / Budget
    ws1.cell(row=r_idx, column=5, value=f"=D{r_idx}/B{r_idx}").number_format = pct_format
    
    # Formula for MoM Growth %
    if r_idx == 5:
        ws1.cell(row=r_idx, column=6, value="-").alignment = Alignment(horizontal="center")
    else:
        ws1.cell(row=r_idx, column=6, value=f"=(C{r_idx}-C{r_idx-1})/C{r_idx-1}").number_format = pct_format
        
    ws1.cell(row=r_idx, column=7, value=apps).number_format = int_format
    
    # Formula for Unit Cost = Actual / Applications
    ws1.cell(row=r_idx, column=8, value=f"=C{r_idx}/G{r_idx}").number_format = "$#,##0.000"
    
    for c in range(1, 9):
        ws1.cell(row=r_idx, column=c).border = thin_border
        if r_idx % 2 == 0:
            ws1.cell(row=r_idx, column=c).fill = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")

# Total Row
tot_row = len(rows) + 5
ws1.cell(row=tot_row, column=1, value="Total / Annual Run-Rate").font = bold_font
ws1.cell(row=tot_row, column=2, value=f"=SUM(B5:B{tot_row-1})").number_format = currency_format
ws1.cell(row=tot_row, column=3, value=f"=SUM(C5:C{tot_row-1})").number_format = currency_format
ws1.cell(row=tot_row, column=4, value=f"=C{tot_row}-B{tot_row}").number_format = currency_format
ws1.cell(row=tot_row, column=5, value=f"=D{tot_row}/B{tot_row}").number_format = pct_format
ws1.cell(row=tot_row, column=6, value=f"=(C{tot_row-1}-C5)/C5").number_format = pct_format # Full period growth
ws1.cell(row=tot_row, column=7, value=f"=SUM(G5:G{tot_row-1})").number_format = int_format
ws1.cell(row=tot_row, column=8, value=f"=C{tot_row}/G{tot_row}").number_format = "$#,##0.000"

for c in range(1, 9):
    ws1.cell(row=tot_row, column=c).font = bold_font
    ws1.cell(row=tot_row, column=c).border = total_border

# ----------------------------------------------------
# Sheet 2: Service Cost Breakdown (Month 12 Pareto)
# ----------------------------------------------------
ws2 = wb.create_sheet(title="M12 Service Spend Pareto")
ws2.views.sheetView[0].showGridLines = True

ws2["A1"] = "Month 12 (September 2026) Service Cost Breakdown & Pareto Distribution"
ws2["A1"].font = title_font
ws2["A2"] = "Total Current Monthly Baseline: $180,000.00 USD"
ws2["A2"].font = sub_font

headers_ws2 = ["AWS Service Category", "Monthly Spend (USD)", "% of Total Spend", "Cumulative %", "FinOps Focus Area"]
for col_idx, h in enumerate(headers_ws2, 1):
    cell = ws2.cell(row=4, column=col_idx, value=h)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = Alignment(horizontal="center", vertical="center")

services_m12 = [
    ("EC2 - Compute Instances", 61200.00, "Compute Rightsizing, Spot Migration & Savings Plans"),
    ("RDS - PostgreSQL (Multi-AZ)", 39600.00, "Replica Consolidation & Reserved DB Instances"),
    ("Data Transfer (Cross-AZ & Egress)", 21600.00, "VPC S3 Endpoints & AZ Affinity Routing"),
    ("S3 - Object Storage", 19800.00, "Intelligent-Tiering & Glacier Lifecycle Policies"),
    ("ElastiCache - Redis Cluster", 12600.00, "Memory Rightsizing & Node Reservations"),
    ("NAT Gateway (Hourly & Processing)", 9000.00, "Gateway Endpoints to eliminate data processing fees"),
    ("Amazon CloudWatch & Logging", 7200.00, "Log level filtering & VPC Interface Endpoints"),
    ("Elastic Load Balancing (ALB)", 5400.00, "ALB Consolidation & idle target group cleanup"),
    ("EBS - Block Storage", 9900.00, "GP2 to GP3 migration & unattached volume deletion"),
    ("Other Services & Support", 3700.00, "Cost anomaly detection & enterprise support audit")
]

# Sort descending
services_m12.sort(key=lambda x: x[1], reverse=True)

cum_pct = 0.0
for s_idx, (s_name, s_spend, focus) in enumerate(services_m12, 5):
    ws2.cell(row=s_idx, column=1, value=s_name).font = regular_font
    ws2.cell(row=s_idx, column=2, value=s_spend).number_format = currency_format
    ws2.cell(row=s_idx, column=3, value=f"=B{s_idx}/$B$15").number_format = pct_format
    
    if s_idx == 5:
        ws2.cell(row=s_idx, column=4, value=f"=C5").number_format = pct_format
    else:
        ws2.cell(row=s_idx, column=4, value=f"=D{s_idx-1}+C{s_idx}").number_format = pct_format
        
    ws2.cell(row=s_idx, column=5, value=focus).font = regular_font
    
    for c in range(1, 6):
        ws2.cell(row=s_idx, column=c).border = thin_border
        if s_idx % 2 == 0:
            ws2.cell(row=s_idx, column=c).fill = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")

# Total Row
tot_s_row = 15
ws2.cell(row=tot_s_row, column=1, value="Total AWS Spend").font = bold_font
ws2.cell(row=tot_s_row, column=2, value=f"=SUM(B5:B14)").number_format = currency_format
ws2.cell(row=tot_s_row, column=3, value=f"=SUM(C5:C14)").number_format = pct_format
ws2.cell(row=tot_s_row, column=4, value="100.0%").number_format = pct_format
ws2.cell(row=tot_s_row, column=5, value="Target Reduction >= $60,000 (33.3%)").font = bold_font

for c in range(1, 6):
    ws2.cell(row=tot_s_row, column=c).font = bold_font
    ws2.cell(row=tot_s_row, column=c).border = total_border

# Auto-fit columns
for ws in [ws1, ws2]:
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

wb.save('analysis/billing-analysis.xlsx')
print("Generated analysis/billing-analysis.xlsx with complete 12-month billing trend and Pareto analysis!")
