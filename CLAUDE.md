# Seals Go Pro — website project notes

Marketing website for **Seals Go Pro**, a driveway sealing business.

## Business facts (keep accurate)
- **Owner / operator (field, customer-facing):** Marcus Piasentin
- **Owner (strategy/systems):** Shawn Piasentin
- **Contact:** (416) 474-8131 (call *or* text Marcus) · marcus@sealsgopro.com
- **Service area:** Highway 401 corridor, Markham → Trenton, Ontario (Markham, Pickering, Ajax, Whitby, Oshawa, Bowmanville, Port Hope, Cobourg, Brighton, Trenton). CAD pricing.
- **Core service:** hand-applied (squeegee) asphalt driveway sealing + crack repair
- **Secondary (mention only):** interlock/paver repair, handyman services
- **Coming soon (teaser only, not bookable):** parking-lot line painting for commercial properties. Concrete work planned later — do NOT mention yet.

### Accuracy guardrails — do NOT publish these
- ❌ Don't claim "insured" / "fully insured" — insurance is not in place yet.
- ❌ Don't use the word "franchise" (legally regulated in Canada) — say "run your own operation."
- ❌ Don't publish prices — pricing isn't finalized.

## The site
- **One file:** `site/index.html` — self-contained (CSS inline, images embedded as base64 data URIs) so it deploys as a single file upload.
- **Brand colors:** navy `#16243f`/`#101d33`, gold `#e8a82a`/`#f4c659`, sky accent `#37a6e6`.
- **Logo:** inline SVG `#shield`. **Mascot:** shield-guardian "Sealy", inline SVG `#mascot` (floats in hero).
- **Photo sources:** `site/images/` (`before.jpg`, `after.jpg`, `crack.jpg`). To add/replace photos: resize with Pillow (~1200px wide, JPEG q80), then embed as a data URI so the page stays a single file.

## Preview / verify changes (rendering works in this env)
The Playwright CDN is blocked, but a Chromium build is pre-installed. Render with:
```python
from playwright.sync_api import sync_playwright; import pathlib
url="file://"+str(pathlib.Path("site/index.html").resolve())
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args=["--no-sandbox"])
    pg=b.new_page(viewport={"width":1280,"height":860}); pg.goto(url); pg.wait_for_timeout(800)
    pg.screenshot(path="site/_preview_full.png", full_page=True); b.close()
```
Preview PNGs (`site/_preview_*.png`) are gitignored.

## Hosting / deploy
- **Host:** Netlify project `resilient-starlight-d2af5f` (shown as "sealsgopro.com").
- **Domain:** sealsgopro.com, DNS managed at **Wix**. Records: `A @ → 75.2.60.5`, `CNAME www → resilient-starlight-d2af5f.netlify.app`. **Email MX/TXT left untouched** — never modify those.
- **Current deploy = manual:** Netlify → Deploys → "browse files to upload" → pick `site/index.html`.
- **Not yet set up:** GitHub→Netlify auto-deploy (would publish changes automatically; needs Shawn to authorize in Netlify). Account actions (Netlify/Wix/Google) must be done by the owner — Claude can't log into them.

## Dev branch
Work happens on `claude/test-coverage-analysis-UNXxX` (legacy branch name; content is the website). PR #2.
