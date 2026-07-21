# PhantomTrace — OSINT Footprinting Tool

PhantomTrace aggregates public information for a name, username, email, image, or domain and generates a HTML report.

**Ethical use disclaimer:** This tool is for lawful, authorized security research and personal data audits only. Do not use it to target individuals, invade privacy, or violate any terms of service or laws. You are responsible for how you use it.

![PhantomTrace report preview](assets/phantomtrace-report.png)

## Features
- **Username checker** across 38 platforms (async `aiohttp` requests using per-platform detection — HTTP status code or response-body inspection — to reduce false positives).
- **Email breach lookup** via the HaveIBeenPwned API v3 (requires an API key).
- **EXIF metadata extraction** for images, including GPS coordinates, camera/device info, and timestamps.
- **WHOIS lookup** for domains (registrar, creation/expiration/updated dates, name servers, status, contact emails).
- **Google dork generator** that builds targeted search queries and can open them in your browser.
- **HTML report generation** (Jinja2, dark theme) with a summary of modules run, platforms checked, profiles found, breaches, and dorks generated.

Each run assembles the results of the modules you invoke into a single self-contained HTML report.

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file from the sample:
```bash
cp .env.example .env
```

Fill in your HaveIBeenPwned API key and user agent in `.env`.

## Usage
```bash
python main.py --username johndoe --email johndoe@example.com --domain example.com --image samples/photo.jpg --dork "John Doe"
```

Run multiple modules with `--all` (only those with inputs provided will execute):
```bash
python main.py --all --username johndoe --email johndoe@example.com --domain example.com
```

### CLI options
| Flag | Description |
| --- | --- |
| `--username` | Username to check across platforms |
| `--email` | Email address for breach lookup |
| `--image` | Image path for EXIF extraction |
| `--domain` | Domain for WHOIS lookup |
| `--dork` | Target name/domain for Google dorks |
| `--all` | Run all modules for which inputs are provided |
| `--open-dorks` | Open the generated dork URLs in your default browser |
| `--output` | Explicit output path for the HTML report |

## Folder Structure & Output

### Folders
- **`samples/`**: Put local target files (e.g. photos/images for EXIF extraction) here for scanning. The contents of this folder are ignored by Git (`.gitignore`) to keep your target files private.
- **`output/`**: The generated HTML reports are written here. Like `samples/`, its contents are ignored by Git.

### Report Name Format
Unless an output path is explicitly provided via the `--output` parameter, the report is automatically saved in `output/` with a dynamic filename based on the scan inputs:
- **If Username is checked**: `report [username: <username>].html`
- **If Email is checked (and no username)**: `report [email: <email>].html`
- **If Domain is checked (and no username/email)**: `report [domain: <domain>].html`
- **If Dork target is checked (and no username/email/domain)**: `report [name: <dork_query>].html`
- **Fallback**: `report.html`
