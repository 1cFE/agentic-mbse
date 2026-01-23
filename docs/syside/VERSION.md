# Syside Documentation

**Current Version:** v0.8.4
**Last Updated:** 2026-01-16

## Directory Structure

| Path | Description | Version |
|------|-------------|---------|
| `python/v0.8.4/` | Python API docs (main reference) | v0.8.4 |
| `automator/` | Automator guide (expressions, execution) | v0.8.4 |
| `examples/` | Usage examples | v0.8.4 |
| `api/` | Compatibility symlinks for agents | v0.8.4 |
| `v0.8.1/` | Archived previous version | v0.8.1 |

## Compatibility Symlinks

For backwards compatibility with agents expecting the old structure:

- `api/README.md` -> `python/v0.8.4/README.md`
- `api/generated/` -> `python/v0.8.4/syside/`

## Updating Documentation

To update to a new syside version:

1. Update the scraper seeds in `~/m-scout/tools/syside_docs/scrape_docs.py`
2. Set `OUTDIR` to target this directory
3. Run the scraper:
   ```bash
   source ~/m-scout/pdf_env/bin/activate
   python ~/m-scout/tools/syside_docs/scrape_docs.py
   deactivate
   ```
4. Update symlinks in `api/` to point to new version
5. Update this VERSION.md file

## Source

Documentation scraped from: https://docs.sensmetry.com/python/latest/
