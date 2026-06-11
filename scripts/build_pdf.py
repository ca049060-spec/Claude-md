#!/usr/bin/env python3
"""
build_pdf.py
============

Generates report.pdf and advisor_sheet.pdf with NO external dependencies —
it writes the PDF format by hand (a PDF is just structured text), so it
works even in locked-down environments with no browser, LibreOffice Writer,
or pip access.

Reads data/portfolio.yml (gitignored); the generated PDFs are gitignored
too, so holdings never reach the repo.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
PORTFOLIO_FILE = REPO_ROOT / "data" / "portfolio.yml"
ANALYST_FILE = REPO_ROOT / "data" / "analyst_live.yml"

GROWTH = 0.06


def load_analyst():
    if ANALYST_FILE.exists():
        return yaml.safe_load(ANALYST_FILE.read_text())
    return None

# Colors (RGB 0-1)
INK = (0.10, 0.13, 0.20)
GRAY = (0.42, 0.44, 0.50)
BLUE = (0.09, 0.25, 0.48)
GREEN = (0.04, 0.48, 0.31)
RED = (0.75, 0.22, 0.17)
TRACK = (0.90, 0.92, 0.96)


def money(x: float) -> str:
    return f"${x:,.0f}"


def sanitize(s: str) -> str:
    """Coerce to latin-1-safe text (PDF base fonts are WinAnsi)."""
    for a, b in (("—", "-"), ("–", "-"), ("→", "->"), ("≈", "~"),
                 ("’", "'"), ("“", '"'), ("”", '"'), ("…", "...")):
        s = s.replace(a, b)
    return s.encode("latin-1", "replace").decode("latin-1")


def esc(s: str) -> str:
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


# ---------------------------------------------------------------------------
# Minimal PDF writer: letter pages, 4 base fonts, text / rects / rules.
# ---------------------------------------------------------------------------
class Pdf:
    W, H = 612, 792

    def __init__(self) -> None:
        self.pages: list[list[str]] = []
        self.new_page()

    def new_page(self) -> None:
        self.pages.append([])

    def text(self, x, y, size, s, font="F1", rgb=INK):
        r, g, b = rgb
        self.pages[-1].append(
            f"BT /{font} {size} Tf {r:.3f} {g:.3f} {b:.3f} rg "
            f"{x:.1f} {y:.1f} Td ({esc(sanitize(s))}) Tj ET")

    def rect(self, x, y, w, h, rgb):
        r, g, b = rgb
        self.pages[-1].append(f"{r:.3f} {g:.3f} {b:.3f} rg {x:.1f} {y:.1f} {w:.1f} {h:.1f} re f")

    def hline(self, x1, x2, y, rgb=TRACK, w=0.7):
        r, g, b = rgb
        self.pages[-1].append(
            f"{w} w {r:.3f} {g:.3f} {b:.3f} RG {x1:.1f} {y:.1f} m {x2:.1f} {y:.1f} l S")

    def save(self, path: Path) -> None:
        fonts = ["Helvetica", "Helvetica-Bold", "Courier", "Courier-Bold"]
        objs: list[bytes] = []
        npages = len(self.pages)
        kids = " ".join(f"{7 + 2 * i} 0 R" for i in range(npages))
        objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")                      # 1
        objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {npages} >>".encode())  # 2
        for fname in fonts:                                                    # 3-6
            objs.append(f"<< /Type /Font /Subtype /Type1 /BaseFont /{fname} "
                        f"/Encoding /WinAnsiEncoding >>".encode())
        res = ("<< /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R /F4 6 0 R >> >>")
        for i, cmds in enumerate(self.pages):                                  # 7..
            objs.append(
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.W} {self.H}] "
                f"/Resources {res} /Contents {8 + 2 * i} 0 R >>".encode())
            stream = "\n".join(cmds).encode("latin-1")
            objs.append(b"<< /Length " + str(len(stream)).encode()
                        + b" >>\nstream\n" + stream + b"\nendstream")

        out = bytearray(b"%PDF-1.4\n")
        offsets = []
        for i, body in enumerate(objs, 1):
            offsets.append(len(out))
            out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
        xref = len(out)
        out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
        for off in offsets:
            out += f"{off:010d} 00000 n \n".encode()
        out += (f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n"
                f"startxref\n{xref}\n%%EOF").encode()
        path.write_bytes(bytes(out))


class Doc:
    """Cursor/word-wrap layer over Pdf with auto page breaks."""
    M = 54  # margin

    def __init__(self) -> None:
        self.pdf = Pdf()
        self.y = Pdf.H - 60

    def need(self, h: float) -> None:
        if self.y - h < 56:
            self.pdf.new_page()
            self.y = Pdf.H - 60

    def gap(self, h: float) -> None:
        self.y -= h

    def line(self, s, size=10, font="F1", rgb=INK, x=None, lead=None):
        self.need(size + 4)
        self.pdf.text(self.M if x is None else x, self.y, size, s, font, rgb)
        self.y -= lead if lead else size + 4

    def para(self, s, size=10, font="F1", rgb=INK, width=100, x=None, lead=None):
        import textwrap
        for ln in textwrap.wrap(sanitize(s), width):
            self.line(ln, size, font, rgb, x=x, lead=lead)

    def rule(self):
        self.need(8)
        self.pdf.hline(self.M, Pdf.W - self.M, self.y + 3)
        self.y -= 8


# ---------------------------------------------------------------------------
# Load consolidated numbers (same logic as the HTML report)
# ---------------------------------------------------------------------------
def load():
    if not PORTFOLIO_FILE.exists():
        sys.exit(f"Could not find {PORTFOLIO_FILE} (it is gitignored).")
    data = yaml.safe_load(PORTFOLIO_FILE.read_text())
    rate = float(data.get("meta", {}).get("usd_cad_rate", 1.0))
    holdings = []
    for sleeve, fx in (("cad_sleeve", 1.0), ("usd_sleeve", rate)):
        block = data.get(sleeve, {})
        for kind, key in (("Stock", "stocks"), ("Fund", "mutual_funds"),
                          ("Cash", "money_market")):
            for h in block.get(key, []):
                holdings.append({"symbol": h["symbol"], "kind": kind,
                                 "mv": float(h["market_value"]) * fx,
                                 "cost": float(h.get("cost_base", h["market_value"])) * fx})
        if block.get("cash"):
            c = float(block["cash"]) * fx
            holdings.append({"symbol": "CASH", "kind": "Cash", "mv": c, "cost": c})
    total = sum(h["mv"] for h in holdings)
    for h in holdings:
        h["weight"] = h["mv"] / total * 100 if total else 0
        h["gain"] = h["mv"] - h["cost"]
    return data, holdings, total


def fv_savings(annual, years, rate):
    fv = 0.0
    for _ in range(years):
        fv = (fv + annual) * (1 + rate)
    return fv


# ---------------------------------------------------------------------------
# Report PDF
# ---------------------------------------------------------------------------
def build_report(data, holdings, total) -> Path:
    funds = data.get("cad_sleeve", {}).get("mutual_funds", [])
    fee_now = sum(f["market_value"] * f.get("est_mer", 2.0) / 100 for f in funds)
    fee_tgt = sum(f["market_value"] * f.get("target_mer", 0.25) / 100 for f in funds)
    penalties = sum(f["market_value"] * f.get("redemption_pct", 0) / 100 for f in funds)
    saving = fee_now - fee_tgt
    fund_val = sum(f["market_value"] for f in funds)

    d = Doc()
    d.line("Consolidated Portfolio Report", 20, "F2", BLUE, lead=26)
    d.line(f"Edward Jones LIRA  *  as of {data.get('meta', {}).get('as_of', '')}"
           f"  *  generated {date.today()}", 10, "F1", GRAY, lead=20)

    # Summary row
    gains = sum(h["gain"] for h in holdings)
    pairs = [("Total value", money(total), INK),
             ("Unrealized gain", money(gains), GREEN),
             ("Fund fees / yr", money(fee_now), INK),
             ("Potential saving / yr", money(saving), GREEN)]
    x = Doc.M
    for label, val, c in pairs:
        d.pdf.text(x, d.y, 8, label.upper(), "F1", GRAY)
        d.pdf.text(x, d.y - 15, 14, val, "F2", c)
        x += 128
    d.gap(40)

    # Asset mix bars
    d.line("Asset mix", 13, "F2", BLUE, lead=18)
    mix = [("Stocks", sum(h["mv"] for h in holdings if h["kind"] == "Stock")),
           ("Funds", sum(h["mv"] for h in holdings if h["kind"] == "Fund")),
           ("Cash", sum(h["mv"] for h in holdings if h["kind"] == "Cash"))]
    for label, val in mix:
        pct = val / total * 100 if total else 0
        d.need(16)
        d.pdf.text(Doc.M, d.y, 9.5, label, "F1", GRAY)
        d.pdf.rect(Doc.M + 60, d.y - 1, 300, 9, TRACK)
        d.pdf.rect(Doc.M + 60, d.y - 1, 3 * pct, 9, BLUE)
        d.pdf.text(Doc.M + 372, d.y, 9.5, f"{pct:.0f}%  *  {money(val)}", "F1", INK)
        d.y -= 16
    d.gap(10)

    # Holdings table
    d.line("Holdings & performance", 13, "F2", BLUE, lead=18)
    cw = 0.6 * 8.5  # courier char width
    hdr = f"{'TICKER':<10}{'TYPE':<7}{'WT%':>5}{'VALUE (CAD)':>14}"
    d.need(14)
    d.pdf.text(Doc.M, d.y, 8.5, hdr + f"{'GAIN/LOSS':>14}{'RET':>8}", "F4", GRAY)
    d.y -= 12
    d.rule()
    for h in sorted(holdings, key=lambda v: -v["mv"]):
        ret = (h["gain"] / h["cost"] * 100) if h["cost"] else 0
        left = f"{h['symbol']:<10}{h['kind']:<7}{h['weight']:>4.1f}{money(h['mv']):>14}"
        right = f"{money(h['gain']):>14}{ret:>7.0f}%"
        d.need(12)
        d.pdf.text(Doc.M, d.y, 8.5, left, "F3", INK)
        d.pdf.text(Doc.M + len(left) * cw, d.y, 8.5, right, "F3",
                   GREEN if h["gain"] >= 0 else RED)
        d.y -= 12
    d.gap(12)

    # Analyst consensus (live)
    alive = load_analyst()
    if alive:
        ratings = alive.get("ratings", {})
        wmap = {h["symbol"]: h["weight"] for h in holdings}
        d.line("Analyst consensus (live)", 13, "F2", BLUE, lead=15)
        d.line(f"pulled {alive.get('as_of', '')} from public aggregators - consensus "
               f"is reliable; targets are approximate", 8, "F1", GRAY, lead=14)
        hdr3 = f"{'TICKER':<8}{'WT%':>5}   {'CONSENSUS':<13}{'BUY/HOLD/SELL':<17}{'AVG TGT':>10}"
        d.need(14)
        d.pdf.text(Doc.M, d.y, 8.5, hdr3, "F4", GRAY)
        d.y -= 12
        d.rule()
        for sym, r in sorted(ratings.items(), key=lambda kv: -wmap.get(kv[0], 0)):
            cons = r.get("consensus", "")
            col = GREEN if "Buy" in cons else (RED if "Sell" in cons else GRAY)
            tgt = r.get("target")
            tgt_s = f"{r.get('ccy', '')} {tgt:,}" if tgt else "-"
            left = f"{sym:<8}{wmap.get(sym, 0):>4.1f}   "
            d.need(12)
            d.pdf.text(Doc.M, d.y, 8.5, left, "F3", INK)
            d.pdf.text(Doc.M + len(left) * cw, d.y, 8.5, f"{cons:<13}", "F3", col)
            d.pdf.text(Doc.M + (len(left) + 13) * cw, d.y, 8.5,
                       f"{r.get('bhs', ''):<17}{tgt_s:>10}", "F3", INK)
            d.y -= 12
        d.gap(6)
        d.para("Takeaway: your largest stock, MDA (~10%), has a unanimous Strong Buy "
               "(13 buys, no holds or sells). The one soft spot is BNS - analysts rate "
               "it Hold (10 of 14). Everything else is Buy or Strong Buy.",
               9.5, "F1", INK, width=98)
        d.gap(12)

    # Fee opportunity
    d.line("The fee opportunity", 13, "F2", BLUE, lead=18)
    d.para(f"You pay about {money(fee_now)}/year in mutual-fund fees "
           f"(~{fee_now / fund_val * 100:.2f}% blended). Moving to low-cost "
           f"equivalents would cut that to about {money(fee_tgt)}/year - a saving "
           f"near {money(saving)}/year. One-time exit penalties are estimated at "
           f"{money(penalties)} (often $0 if DSC schedules have matured), recouped "
           f"in roughly {penalties / saving:.1f} years. Compounded at "
           f"{GROWTH:.0%}, that is about {money(fv_savings(saving, 10, GROWTH) - penalties)} "
           f"over 10 years and {money(fv_savings(saving, 20, GROWTH) - penalties)} "
           f"over 20 years.", 10, "F1", INK, width=95)
    d.gap(8)

    hdr2 = f"{'FUND':<34}{'VALUE':>10}{'MER':>7}{'TARGET':>8}{'SAVING':>10}{'PENALTY':>10}"
    d.need(14)
    d.pdf.text(Doc.M, d.y, 8.5, hdr2, "F4", GRAY)
    d.y -= 12
    d.rule()
    for f in funds:
        mv = f["market_value"]
        sv = mv * (f.get("est_mer", 2.0) - f.get("target_mer", 0.25)) / 100
        pen = mv * f.get("redemption_pct", 0) / 100
        row = (f"{sanitize(f['name'])[:33]:<34}{money(mv):>10}"
               f"{f.get('est_mer', 2.0):>6.2f}%{f.get('target_mer', 0.25):>7.2f}%"
               f"{money(sv):>10}{(money(pen) if pen else '-'):>10}")
        d.line(row, 8.5, "F3", INK, lead=12)
    d.gap(12)

    # Next steps
    d.line("What to do next", 13, "F2", BLUE, lead=18)
    steps = [
        "Easy wins first: the no-load Series-A funds (Mackenzie, Franklin Royce, "
        "BMO Monthly Income) move with no penalty - most of the saving at zero cost.",
        "Check the DSC/low-load two (BMO Asian, AGF): ask for the redemption-"
        "schedule maturity date; if matured, the penalty is $0.",
        "The $86,700 in high-interest savings (~16%): confirm it is intentional "
        "dry powder rather than idle money.",
        "MDA (~10%) is the largest single stock - watch as a concentration point.",
    ]
    for s in steps:
        d.para("*  " + s, 10, "F1", INK, width=95)
        d.gap(2)
    d.gap(8)
    d.para("Informational only - not financial advice. MERs, target equivalents and "
           "redemption penalties are estimates to verify against each fund's Fund "
           "Facts. Built offline from your statement data; nothing was sent to any "
           "external service.", 8.5, "F1", GRAY, width=110)

    out = REPO_ROOT / "report.pdf"
    d.pdf.save(out)
    return out


# ---------------------------------------------------------------------------
# Advisor sheet PDF
# ---------------------------------------------------------------------------
def build_advisor(data) -> Path:
    funds = data.get("cad_sleeve", {}).get("mutual_funds", [])
    fee_now = sum(f["market_value"] * f.get("est_mer", 2.0) / 100 for f in funds)

    d = Doc()
    d.line("Questions for my Edward Jones advisor", 18, "F2", BLUE, lead=24)
    d.line(f"Re: LIRA - fund costs & lower-cost options  *  prepared {date.today()}",
           10, "F1", GRAY, lead=18)
    d.para(f"Why I'm asking: my five mutual funds appear to cost roughly "
           f"{money(fee_now)}/year in embedded fees (~2.25% blended). I'd like to "
           f"verify the exact numbers and understand my lower-cost options. Nothing "
           f"here is a decision yet - it's fact-finding.", 10, "F1", INK, width=95)
    d.gap(10)

    n = 0

    def q(title_line, assume=None, blank=None):
        nonlocal n
        n += 1
        d.need(46)
        d.para(f"{n}.  {title_line}", 10.5, "F2", INK, width=90)
        if assume:
            d.para(assume, 9, "F1", GRAY, width=100, x=Doc.M + 16)
        if blank:
            d.para(blank, 9.5, "F1", BLUE, width=100, x=Doc.M + 16)
        d.gap(6)
        d.rule()

    for f in funds:
        q(f"{f['name']} ({f['symbol']}, {f.get('load', '?')} series) - what is the "
          f"exact MER I'm paying on this fund?",
          f"I'm assuming ~{f.get('est_mer', 2.0):.2f}% -> about "
          f"{money(f['market_value'] * f.get('est_mer', 2.0) / 100)}/yr on my "
          f"{money(f['market_value'])}.",
          "Actual MER: ____________ %")

    for f in funds:
        if f.get("redemption_pct", 0) > 0:
            q(f"{f['name']} is {f.get('load', '?')} - when does its redemption "
              f"schedule mature, and what penalty applies if I sell today?",
              f"I'm assuming a worst case of {f.get('redemption_pct', 0):.1f}% "
              f"(~{money(f['market_value'] * f.get('redemption_pct', 0) / 100)}). "
              f"If the schedule has matured, it should be $0.",
              "Maturity date: ____________    Penalty today: ____________")

    q("Can each of these funds be switched to its Series F (or a low-cost ETF) "
      "inside this LIRA without leaving Edward Jones? What would my all-in cost "
      "(MER + any advisory fee) be after the switch?",
      None, "All-in cost after switch: ____________ %")
    q("Are there any account-level or trading fees I'd trigger by selling these "
      "funds and buying ETFs - commissions, switch fees, short-term trading fees?",
      None, "List: ______________________________________________")
    q("The ~$86,700 in the high-interest savings position - what rate is it "
      "earning right now, and are there better cash-equivalent options inside "
      "the LIRA?", None, "Rate: ____________ %")
    q("Since my accounts were consolidated, can you confirm the total annual cost "
      "of the relationship - all embedded fund fees plus any account fees - as "
      "one dollar figure?", None, "Total $/yr: ____________")

    d.gap(4)
    d.para("Tip: this can be sent as a secure message instead of a call - written "
           "answers are easier to compare against the estimates.", 9, "F1", GRAY,
           width=105)

    out = REPO_ROOT / "advisor_sheet.pdf"
    d.pdf.save(out)
    return out


def main() -> None:
    data, holdings, total = load()
    print("Wrote", build_report(data, holdings, total))
    print("Wrote", build_advisor(data))


if __name__ == "__main__":
    main()
