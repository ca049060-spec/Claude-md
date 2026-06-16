#!/usr/bin/env python3
"""
refresh.py — one command rebuilds the whole system.

Runs every generator in order and reports what was produced. This is the
"morning button": after any data change (new statement, updated calls,
fresh prices), run `python3 scripts/refresh.py` and every artifact —
dashboard, studio, brief, report PDF, advisor sheet — is regenerated from
the current data files, plus the engines re-run and the tests re-checked.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

# (label, script, produces) — order matters: engines before the views
# that consume their output.
STEPS = [
    ("Model self-tests",        "test_engine.py",        None),
    ("Edge scorecard",          "scorecard.py",          None),
    ("VACS engine",             "vacs.py",               None),
    ("Weighted consensus (v2)", "weighted_consensus.py", "data/weighted_consensus.yml"),
    ("Analyst track scores",    "analyst_scoring.py",    None),
    ("Portfolio review",        "portfolio_review.py",   None),
    ("Fee + performance",       "fee_and_performance.py", None),
    ("Fee-switch plan",         "fee_switch_plan.py",    None),
    ("Fund alpha vs benchmark", "fund_alpha.py",         None),
    ("Dashboard",               "build_dashboard.py",    "dashboard.html"),
    ("Cash studio",             "build_studio.py",       "studio.html"),
    ("Research brief",          "build_brief.py",        "brief.html"),
    ("Plan (one page)",          "build_plan.py",         "plan.html"),
    ("Master allocation",        "build_master.py",       "master.html"),
    ("Report + advisor PDFs",   "build_pdf.py",          "report.pdf / advisor_sheet.pdf"),
]


def main() -> None:
    print(f"\n{'='*60}\n  Refreshing the whole system\n{'='*60}\n")
    ok = 0
    failed = []
    for label, script, produces in STEPS:
        path = SCRIPTS / script
        if not path.exists():
            print(f"  ⚠  {label:<26} (missing {script}, skipped)")
            continue
        res = subprocess.run([sys.executable, str(path)],
                             capture_output=True, text=True)
        if res.returncode == 0:
            tail = produces or "ok"
            print(f"  ✓  {label:<26} → {tail}")
            ok += 1
        else:
            print(f"  ✗  {label:<26} FAILED")
            err = (res.stderr or res.stdout).strip().splitlines()
            if err:
                print(f"       {err[-1]}")
            failed.append(label)

    print(f"\n{'='*60}")
    print(f"  {ok}/{len(STEPS)} steps ok"
          + (f" · FAILED: {', '.join(failed)}" if failed else " · all green"))
    print(f"  Open: dashboard.html (review) · studio.html (explore) · brief.html (why)")
    print(f"{'='*60}\n")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
