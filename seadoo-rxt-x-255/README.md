# Sea-Doo RXT-X 255 — Maintenance Walkthroughs

Project files for my **2008 Sea-Doo RXT-X 255** (Rotax 1503 4-TEC supercharged, 255 HP).

## Arman supercharger walkthrough

A friendly, phone-friendly walkthrough to send to Arman (the mechanic) covering the
**100-hour supercharger rebuild** the ski needs at ~100 hrs.

| File | What it is |
|------|------------|
| `arman-supercharger-walkthrough.html` | Source — a slide-per-screen "video style" deck (dark YouTube theme), built for mobile. |
| `Arman-Supercharger-Walkthrough.pdf` | **The deliverable.** Render of the HTML, sized like a phone screen — text this to Arman. |
| `build_pdf.py` | Rebuild the PDF from the HTML. |

### The job in a nutshell
- **Service:** Supercharger rebuild — due at **100 hours / 2 years**.
- **Why:** worn clutch washers slip and can send debris into the engine if neglected.
- **Kit:** OEM Sea-Doo S/C rebuild kit **P/N 420881102** (16-tooth, intercooled, steel washers).
- **Plan:** Shawn orders + ships the kit to Arman, drops the ski off, Arman rebuilds.
- **Time:** ~2–3 hrs bench + pull/reinstall; pros quote a 1-day turnaround.

### Rebuild the PDF
```bash
pip install weasyprint           # one-time
python3 build_pdf.py             # writes Arman-Supercharger-Walkthrough.pdf
```
> Note: emoji are intentionally avoided in the design — the icons are inline SVG so they
> render consistently in WeasyPrint (which doesn't rasterize color-emoji fonts).

*Reference material only — always defer to the Sea-Doo shop manual for torque specs.*
