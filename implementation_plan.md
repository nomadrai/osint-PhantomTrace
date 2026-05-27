# PhantomTrace OSINT Tool — Audit & Improvement Plan

## Audit Findings

### ✅ What's Working
- **Project structure** is clean and well-organized
- **Imports** across all modules are correct — no broken imports
- **Pipeline flow** `main.py → modules → report/generator.py → output/report.html` is intact and functional
- **config.py** is clean, uses `dataclass` + `dotenv` properly
- **username_checker.py** — async logic, fallback from HEAD to GET on 403/405, timeout handling all look solid
- **email_breach.py** — proper API key validation, error handling, and HTTP status handling
- **whois_lookup.py** — clean wrapper around `python-whois`, `_format_value` handles lists
- **exif_extractor.py** — GPS DMS→DD conversion, altitude extraction, EXIF tag resolution all work
- **dork_generator.py** — proper URL encoding, sensible dork templates
- **report/generator.py** — Jinja2 templating with `FileSystemLoader`, output dir creation, UTC timestamps

### 🐛 Bugs & Issues Found

#### 1. `modules/whois_lookup.py` — No error handling
- `whois.whois()` can throw exceptions (network errors, invalid domains, WHOIS server unavailable)
- No `try/except` — will crash `main.py` and prevent report generation

#### 2. `modules/exif_extractor.py` — No error handling for file not found / invalid image
- `Image.open()` will raise `FileNotFoundError` or `PIL.UnidentifiedImageError`
- No `try/except` — will crash the pipeline
- **GPS `_convert_to_degrees`** assumes old-style rational tuples `(numerator, denominator)` but modern Pillow (10.x+) returns `IFDRational` objects that are already float-like. The `value[0][0] / value[0][1]` indexing will fail with `TypeError` on modern Pillow.

#### 3. `modules/dork_generator.py` — `open_dorks` calls `webbrowser.open()` for every dork
- Opens 14 browser tabs simultaneously — likely unintentional for report-only mode
- `main.py` always calls `open_dorks(dorks)` which triggers browser tabs, even in headless/report-only workflows
- Should only generate URLs, with browser opening as opt-in

#### 4. `report/generator.py` — Missing `target_name` in template context
- The template needs a target name for the header, but `generate_report` only passes `**results` and `generated_at`
- No way to display target identity in the report header

#### 5. `report/generator.py` — `os.path.dirname()` on relative path
- When `output_path` is `"output/report.html"`, `os.path.dirname()` returns `"output"`, which works
- But if just `"report.html"` (no dir), `os.path.dirname()` returns `""` and `os.makedirs("", exist_ok=True)` raises `FileNotFoundError`

#### 6. `report/template.html` — Design issues
- No summary bar with stats
- No "FOR EDUCATIONAL USE ONLY" badge
- No target name in header
- No color-coded status for "unknown/timeout" (only found/notfound)
- No monospace font for data values
- Basic visual design — lacks polish, glassmorphism, micro-animations
- No `<base>` tag or proper relative paths for Live Server compatibility (though the current template has no external resources, so this is minor)

#### 7. `main.py` — No target name tracking
- None of the CLI args are tracked as a "target name" for the report header
- The `--all` flag is parsed but never changes execution — all modules still require their individual flags

---

## Proposed Changes

### Module Fixes

#### [MODIFY] [whois_lookup.py](file:///home/nomad_aadi/Documents/Projects/osint-footprint/modules/whois_lookup.py)
- Wrap `whois.whois()` in `try/except` to catch network/parsing errors
- Return error dict on failure instead of crashing

#### [MODIFY] [exif_extractor.py](file:///home/nomad_aadi/Documents/Projects/osint-footprint/modules/exif_extractor.py)
- Add `try/except` around `Image.open()` for missing/invalid files
- Fix `_convert_to_degrees` to handle modern Pillow `IFDRational` objects (which are directly float-castable, not tuples)
- Return error dict on failure

#### [MODIFY] [dork_generator.py](file:///home/nomad_aadi/Documents/Projects/osint-footprint/modules/dork_generator.py)
- Split `open_dorks` into URL generation only (no browser opening)
- Add separate `open_in_browser` parameter or function, controlled by caller
- `main.py` will only open browser tabs if explicitly requested

---

### Pipeline & Main Fixes

#### [MODIFY] [main.py](file:///home/nomad_aadi/Documents/Projects/osint-footprint/main.py)
- Build a `target_name` from the first available input arg (username, email, domain, or dork target)
- Pass `target_name` to `generate_report()`
- Make dork browser opening opt-in (add `--open-dorks` flag, default off)
- Fix `os.path.dirname` edge case for output path

#### [MODIFY] [generator.py](file:///home/nomad_aadi/Documents/Projects/osint-footprint/report/generator.py)
- Accept and pass `target_name` to template context
- Compute summary stats (platforms checked, found count, breach count, dork count, modules run) and pass to template
- Fix `os.path.dirname` edge case

---

### HTML Report Redesign

#### [MODIFY] [template.html](file:///home/nomad_aadi/Documents/Projects/osint-footprint/report/template.html)
Complete redesign with:

**Header:**
- PhantomTrace branded header with target name prominently displayed
- Timestamp with clean formatting
- `"OSINT REPORT — FOR EDUCATIONAL USE ONLY"` badge (amber/yellow pill)

**Summary Bar:**
- Row of stat cards showing: Modules Run, Platforms Checked, Profiles Found, Breaches Found, Dorks Generated
- Color-coded numbers (green for positive findings, neutral gray for info)

**Module Cards:**
- Each module gets its own card with icon indicator and section title
- Username Check: table with platform, profile link, and 3-state badge (green=Found, red=Not Found, yellow=Timeout/Unknown)
- Email Breach: table with breach name, domain, date; or success/error status
- EXIF Metadata: key-value grid with monospace data font
- WHOIS Lookup: key-value grid with monospace data font  
- Google Dorks: table with query and clickable search link

**Design System (pure inline CSS):**
- Dark theme: `#0a0c10` base, `#12151c` card backgrounds, subtle border glows
- Monospace font (`'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace`) for all data values
- Sans-serif (`'Inter', 'Segoe UI', system-ui`) for headings/labels
- Color-coded badges: `#22c55e` green (found), `#ef4444` red (not found), `#eab308` yellow (unknown/timeout)
- Card glassmorphism with subtle `backdrop-filter` and border glow
- Smooth hover transitions on table rows
- Mobile-responsive with CSS grid that collapses on small screens
- No external CDN dependencies — all styles inline

**Live Server Compatibility:**
- Self-contained HTML with no external dependencies
- Proper `<!DOCTYPE html>`, `charset`, `viewport` meta tags
- No `<base>` tag needed since there are no relative resource paths

---

## Verification Plan

### Automated Tests
```bash
# Verify Python syntax and imports
python -c "from modules.username_checker import check_username"
python -c "from modules.whois_lookup import lookup_domain"
python -c "from modules.exif_extractor import extract_exif"
python -c "from modules.email_breach import check_breaches"
python -c "from modules.dork_generator import generate_dorks"
python -c "from report.generator import generate_report"

# Test report generation with mock data
python -c "
from report.generator import generate_report
results = {
    'username_results': [{'platform': 'GitHub', 'url': 'https://github.com/test', 'status': 200, 'found': True}],
    'email_results': {'status': None, 'breaches': [], 'error': 'No API key'},
    'exif_results': None,
    'whois_results': None,
    'dork_results': [{'query': 'test', 'url': 'https://google.com/search?q=test'}],
}
generate_report(results, 'output/report.html', target_name='TestUser')
print('Report generated successfully')
"
```

### Manual Verification
- Open `output/report.html` in browser / Live Server on port 5500
- Verify all sections render correctly
- Check mobile responsiveness
- Verify badge colors for found/not-found/unknown states
