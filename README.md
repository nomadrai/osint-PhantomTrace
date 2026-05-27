# PhantomTrace — OSINT Footprinting Tool

PhantomTrace aggregates public information for a name, username, email, image, or domain and generates a dark-themed HTML report.

**Ethical use disclaimer:** This tool is for lawful, authorized security research and personal data audits only. Do not use it to target individuals, invade privacy, or violate any terms of service or laws. You are responsible for how you use it.

## Features
- Username checker across 50+ platforms (async HTTP HEAD).
- Email breach lookup via HaveIBeenPwned API v3.
- EXIF metadata extraction for images (GPS, device, timestamps).
- WHOIS lookup for domains.
- Google dork generator (opens searches in browser).
- HTML report generation (Jinja2, dark theme).

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file from the sample:
```bash
cp .env.example .env
```

Fill in your HaveIBeenPwned API key and user agent in `.env`.

## Usage
```bash
python main.py --username johndoe --email johndoe@example.com --domain example.com --image samples/photo.jpg --dork "John Doe" --output output/report.html
```

Run multiple modules with `--all` (only those with inputs provided will execute):
```bash
python main.py --all --username johndoe --email johndoe@example.com --domain example.com
```

## Output
The HTML report is written to the `--output` path (default: `output/report.html`).
