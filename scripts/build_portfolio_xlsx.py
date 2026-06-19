#!/usr/bin/env python3
"""Build a properly formatted portfolio.xlsx (bold headers, colours, $ formats,
green/red gains, totals). Current prices Jun 17-18 2026. Cost basis from the
EJ statement (flagged — confirm NOW)."""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

USDCAD = 1.41

# ticker, name, shares, cost_per_share, price_now, currency
HOLD = [
    ("CAD", [
        ("MDA",  "MDA Space",            1000, 45.08,  57.80),
        ("TD",   "TD Bank",               200, 49.19, 167.45),
        ("MFC",  "Manulife",              500, 16.50,  57.54),
        ("TRP",  "TC Energy",             250, 48.72,  96.25),
        ("ENB",  "Enbridge",              275, 50.74,  76.40),
        ("BNS",  "Bank of Nova Scotia",   180, 70.61, 123.03),
    ]),
    ("USD", [
        ("BWXT", "BWX Technologies",      125, 199.28, 203.07),
        ("NOW",  "ServiceNow (CONFIRM shares+price!)", 265, 94.86, 124.37),
        ("ASML", "ASML Holding",            5, 1381.65, 1929.68),
        ("RKLB", "Rocket Lab",            165, 103.00, 106.20),
        ("BEAM", "Beam Therapeutics",     100, 30.00,  32.50),
    ]),
]
CASH = 55140.0
FUNDS = 199189.0

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Portfolio"

NAVY = "1F3A5F"; LBLUE = "D6E4F0"; GREY = "EDEFF4"; GREEN = "0A7A4F"; RED = "C0392B"
wfont = Font(color="FFFFFF", bold=True)
hdr_fill = PatternFill("solid", fgColor=NAVY)
sec_fill = PatternFill("solid", fgColor=LBLUE)
tot_fill = PatternFill("solid", fgColor=NAVY)
thin = Side(style="thin", color="BBBBBB")
border = Border(bottom=thin)
money = '#,##0'
moneyc = '$#,##0'

# Title
ws.merge_cells("A1:H1")
c = ws["A1"]; c.value = "MY PORTFOLIO — full statement (CAD)"
c.font = Font(bold=True, size=16, color="FFFFFF"); c.fill = hdr_fill
c.alignment = Alignment(horizontal="left", vertical="center")
ws.row_dimensions[1].height = 28
ws.merge_cells("A2:H2")
ws["A2"] = "Prices Jun 19 2026 · USD converted at 1.41 · cost basis from your EJ statement (confirm)"
ws["A2"].font = Font(italic=True, size=9, color="666666")

headers = ["Holding","Ticker","Shares","Cost/sh","Price now","Value (native)","Value CAD","Gain/Loss CAD"]
r = 4
for i, h in enumerate(headers, 1):
    cell = ws.cell(r, i, h); cell.font = wfont; cell.fill = hdr_fill
    cell.alignment = Alignment(horizontal="right" if i > 2 else "left")

cad_total = 0.0; gain_total = 0.0
for cur, rows in HOLD:
    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    sc = ws.cell(r, 1, f"{'🇨🇦 CANADIAN' if cur=='CAD' else '🇺🇸 US'} HOLDINGS ({cur})")
    sc.font = Font(bold=True, color=NAVY); sc.fill = sec_fill
    for tk, nm, sh, cps, pn in rows:
        r += 1
        val_native = sh * pn
        fx = 1.0 if cur == "CAD" else USDCAD
        val_cad = val_native * fx
        gain_cad = (pn - cps) * sh * fx
        cad_total += val_cad; gain_total += gain_cad
        ws.cell(r, 1, nm)
        ws.cell(r, 2, tk)
        ws.cell(r, 3, sh)
        ws.cell(r, 4, cps).number_format = moneyc
        ws.cell(r, 5, pn).number_format = moneyc
        ws.cell(r, 6, val_native).number_format = moneyc
        ws.cell(r, 7, val_cad).number_format = moneyc
        g = ws.cell(r, 8, gain_cad); g.number_format = moneyc
        g.font = Font(color=GREEN if gain_cad >= 0 else RED, bold=True)
        for cc in range(1, 9): ws.cell(r, cc).border = border

# Cash + funds
for label, amt in [("Cash / HISA", CASH), ("Mutual funds (5 — selling)", FUNDS)]:
    r += 1
    ws.cell(r, 1, label)
    ws.cell(r, 7, amt).number_format = moneyc
    cad_total += amt
    for cc in range(1, 9): ws.cell(r, cc).border = border

# Total
r += 2
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
tc = ws.cell(r, 1, "TOTAL PORTFOLIO (CAD)"); tc.font = Font(bold=True, size=13, color="FFFFFF"); tc.fill = tot_fill
tv = ws.cell(r, 7, cad_total); tv.number_format = moneyc; tv.font = Font(bold=True, size=13, color="FFFFFF"); tv.fill = tot_fill
ws.cell(r, 8, "").fill = tot_fill
ws.row_dimensions[r].height = 24

r += 1
gc = ws.cell(r, 1, "Unrealized gain on stocks"); gc.font = Font(bold=True)
gv = ws.cell(r, 8, gain_total); gv.number_format = moneyc
gv.font = Font(bold=True, color=GREEN if gain_total >= 0 else RED)

# Notes
r += 2
notes = [
    "⚠️ ServiceNow UNRESOLVED: statement shows ~$124/sh but live feed shows ~$908/sh. NOT confirmed. Need your actual share count + EJ line value — this can swing the total $200K+.",
    "⚠️ Cost basis comes from your EJ statement. If a cost/sh is wrong, overwrite the Cost/sh cell with your real number and the gain updates.",
    "MDA at $57.80 per your read. RKLB ~breakeven. Prices Jun 19 2026.",
]
for n in notes:
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
    ws.cell(r, 1, n).font = Font(size=9, color="555555"); r += 1

widths = [24, 8, 9, 10, 11, 14, 13, 14]
for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "A5"

wb.save("/home/user/Claude-md/portfolio.xlsx")
print(f"saved. Total CAD = {cad_total:,.0f} | gain = {gain_total:,.0f}")
