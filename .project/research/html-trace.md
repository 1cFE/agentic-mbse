# Research: Alternative Source Strategy for Document Extraction

**Status:** Research / Proposal
**Author:** Reid Westwood
**Date:** 2026-02-09
**Related:** `extraction-design.md`, `evaluation-report.md`

---

## Motivation

The extraction pipeline evaluation (2026-02-06, commit 73a20d5) scored **2.68 / 5.00** across 7 PDF extractions. The five persistent failure modes — borderless tables rendered as plain text, section headers misidentified as bold text, equation garbling, page number and running header artifacts, and Unicode ligature failures — are all inherent to extracting structured content from a format (PDF) that was designed for visual rendering, not semantic representation.

Every one of these failure modes disappears when the source is HTML or XML instead of PDF:

| Failure Mode | PDF Severity | HTML/XML Severity | Why |
|---|---|---|---|
| Borderless tables | CRITICAL — 6/7 docs affected | **None** — tables are `<table>` elements | Semantic markup, not visual positioning |
| Headers as bold text | CRITICAL — 4/7 docs with empty indexes | **None** — headers are `<h1>`–`<h6>` or `<sec><title>` | Explicit hierarchy in markup |
| Equation garbling | MEDIUM — 3/7 docs | **None** — LaTeX `$...$` or MathML preserved | Math encoded symbolically, not as glyphs |
| Page artifacts | HIGH — all 7 docs | **None** — no page model in HTML | Continuous document, no headers/footers |
| Ligature failures | MEDIUM — 199 occurrences in doc 2235 | **None** — standard Unicode text | No font-specific glyph mapping |

Rather than investing further in post-processing heuristics for PDF extraction (header promotion, page number stripping, table strategy cascades), we should add an upstream **source discovery** step that finds HTML or XML versions of papers before falling back to PDF. This complements the existing extraction pipeline — PDF remains the last-resort backend — but shifts effort toward acquiring better inputs rather than fixing worse outputs.

---

## Available Structured Sources

### 1. arXiv HTML

arXiv launched HTML papers in December 2023 using the LaTeXML converter, and is gradually backfilling HTML for the full corpus of over 2 million papers. HTML versions appear on abstract pages below the existing PDF download link. Authors can preview their paper's HTML during the submission process.

**Availability and quality:**
- All new LaTeX submissions since December 2023 generate HTML
- Backfill of the existing corpus is ongoing
- Conversion success: approximately 74% fully clean (no errors), 97% at least partially viewable (based on ar5iv 2022 data, which uses the same LaTeXML converter)
- Three severity levels in conversion output: `no_problem`, `warning` (minor rendering issues), `error` (major issues but HTML still generated)
- Known limitations include unsupported LaTeX packages and certain rendering issues

**Access patterns:**
- **Abstract page:** `https://arxiv.org/abs/{id}` — HTML link appears below PDF
- **Direct HTML:** `https://arxiv.org/html/{id}` — full HTML version
- **ar5iv mirror:** `https://ar5iv.labs.arxiv.org/abs/{id}` — alternative rendering of the same LaTeXML output
- **API:** The arXiv API (`http://export.arxiv.org/api/query`) provides metadata and PDF links but does not have a dedicated endpoint for HTML retrieval. HTML availability must be checked by constructing the URL directly.

**Relevance to fusion corpus:** Many fusion research preprints appear on arXiv (especially in physics.plasm-ph). For any paper in the Zotero library with an arXiv ID, checking for HTML availability is a low-cost, high-reward operation.

> **Sources:**
> - arXiv accessible HTML announcement: https://info.arxiv.org/about/accessible_HTML.html
> - ar5iv project (LaTeXML-based HTML rendering): https://ar5iv.labs.arxiv.org
> - LaTeXML (open source converter): https://github.com/brucemiller/LaTeXML

### 2. PubMed Central (PMC) JATS XML

PubMed Central requires all deposited articles to be in JATS XML (Journal Article Tag Suite, NISO Z39.96 standard). The PMC Open Access Subset provides full-text XML with reuse licenses. As of late 2018, over 2.8 million full-text articles were available, and the collection continues to grow with daily updates.

JATS is the richest structured format available for scientific articles. Unlike HTML, JATS provides explicit semantic markup for section types (`<sec sec-type="intro">`), equations (MathML), structured citations, figure/table captions, and full bibliographic metadata. This makes it the highest-quality conversion source.

**Access patterns:**
- **OAI-PMH API:** `https://pmc.ncbi.nlm.nih.gov/api/oai/v1/mh/?verb=GetRecord&identifier=oai:pubmedcentral.nih.gov:{pmcid}&metadataPrefix=pmc` — retrieves full-text JATS XML for a single article
- **E-utilities (efetch):** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid}&retmode=xml` — retrieves full-text XML
- **BioC API:** `https://www.ncbi.nlm.nih.gov/research/bionlp/APIs/BioC-PMC/` — simplified text-mining-oriented format
- **Bulk FTP:** Available for the Open Access and Author Manuscript subsets
- **Rate limits:** Scripts making more than 100 requests should run outside peak hours; include `tool` and `email` parameters

**Conversion to markdown:**
Pandoc reads JATS as a first-class input format (`pandoc -f jats -t markdown`). This handles section hierarchy, math (MathML → LaTeX), tables, and citations with high fidelity. The conversion is deterministic and fast — no ML inference, no font heuristics, no timeout concerns.

**Relevance to fusion corpus:** Nuclear Fusion journal articles that are also deposited in PMC (common for publicly funded research) will have JATS XML available. The PMC ID can be discovered via OpenAlex or Unpaywall (see below).

> **Sources:**
> - PMC OAI-PMH API documentation: https://pmc.ncbi.nlm.nih.gov/tools/oai/
> - PMC developer tools: https://pmc.ncbi.nlm.nih.gov/tools/developers/
> - JATS standard: https://jats.nlm.nih.gov/archiving/
> - E-utilities documentation: https://www.ncbi.nlm.nih.gov/books/NBK25500/
> - PMC XML converters (public domain): https://github.com/ncbi/PMCXMLConverters

### 3. Publisher HTML (IOP Publishing / Nuclear Fusion)

Nuclear Fusion, the primary journal for the fusion research corpus, became fully open access in January 2023 and is published by IOP Publishing. IOP provides HTML view on IOPscience when full-text XML is available, which covers most recent articles. For bulk text/data mining access to the underlying XML, IOP requires an advance request via `contentsupport@ioppublishing.org` and provides data via SFTP.

Other relevant publishers (Taylor & Francis for Fusion Science and Technology, Springer for Journal of Fusion Energy) have varying levels of structured format availability. HTML is generally available for recent articles through publisher websites.

**Relevance to fusion corpus:** This is the single most relevant source for journal articles (as opposed to preprints or reports). Establishing a text mining agreement with IOP would provide high-quality XML for the majority of Nuclear Fusion articles.

> **Sources:**
> - IOP Publishing text and data mining policy: https://publishingsupport.iopscience.iop.org/questions/text-and-data-mining/
> - Nuclear Fusion open access announcement (January 2023): https://www.iaea.org/newscenter/news/nuclear-fusion-becomes-fully-open-access

### 4. Government and Institutional Reports

Some documents in the corpus (e.g., LA-UR-25-24580 from LANL) are government technical reports that may not have HTML/XML equivalents. These will continue to require PDF extraction. Similarly, older journal articles without digital structured versions will remain PDF-only.

---

## Source Discovery APIs

The practical question is: given a DOI, arXiv ID, or bibliographic record from Zotero, how do we programmatically find the best available structured source? Two free APIs make this feasible.

### OpenAlex

OpenAlex is an open-access bibliographic database that indexes over 240 million works, with approximately 50,000 added daily. It is a free replacement for proprietary databases like Scopus and Web of Science, with roughly 2× the coverage. All data is CC0 licensed.

**Key fields for source discovery:**

Each Work object includes:
- `doi` — canonical DOI
- `ids` — contains `openalex`, `doi`, `pmid`, `pmcid` (when available)
- `open_access` — contains `is_oa` (boolean), `oa_status` (gold/green/bronze/closed), `oa_url` (URL to best OA version)
- `best_oa_location` — the single best open access location
- `locations` — all known locations (publisher, repositories, preprint servers) with `url`, `pdf_url`, `version`, `license`, `is_oa`
- `primary_location.source` — journal/repository metadata

**API access:**

```
# Lookup by DOI
GET https://api.openalex.org/works/https://doi.org/10.1088/1741-4326/ac1654

# Batch lookup (up to 50 DOIs per request)
GET https://api.openalex.org/works?filter=doi:DOI1|DOI2|DOI3&per-page=50

# Filter for open access fusion papers
GET https://api.openalex.org/works?filter=primary_location.source.id:S25169967,is_oa:true
```

As of February 2025, OpenAlex requires an API key for more than 100 requests/day (free keys provide 100,000 credits/day). Include `mailto` parameter for polite access.

**Python example:**

```python
import requests

def discover_sources(doi: str, email: str) -> dict:
    """Query OpenAlex for structured source locations."""
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    params = {"mailto": email}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    work = resp.json()

    result = {
        "doi": doi,
        "pmcid": work.get("ids", {}).get("pmcid"),
        "arxiv_id": None,
        "oa_url": work.get("open_access", {}).get("oa_url"),
        "locations": [],
    }

    # Extract arXiv ID from locations
    for loc in work.get("locations", []):
        source = loc.get("source", {}) or {}
        if source.get("display_name") == "arXiv":
            landing = loc.get("landing_page_url", "")
            if "arxiv.org/abs/" in landing:
                result["arxiv_id"] = landing.split("arxiv.org/abs/")[-1]

        result["locations"].append({
            "url": loc.get("landing_page_url"),
            "pdf_url": loc.get("pdf_url"),
            "version": loc.get("version"),
            "is_oa": loc.get("is_oa"),
            "source_name": source.get("display_name"),
            "host_type": source.get("host_organization_name"),
        })

    return result
```

> **Sources:**
> - OpenAlex documentation: https://docs.openalex.org
> - OpenAlex API guide for LLMs: https://docs.openalex.org/api-guide-for-llms
> - OpenAlex Work object: https://docs.openalex.org/api-entities/works/work-object
> - OpenAlex Python tutorial: https://ua-libraries-research-data-services.github.io/UALIB_ScholarlyAPI_Cookbook/src/python/openalex.html

### Unpaywall

Unpaywall is a free index of open access papers, integrated into Web of Science, Scopus, and many library systems. It provides `oa_locations` with URLs to free versions of papers hosted by publishers, repositories, and preprint servers.

**API access:**

```
GET https://api.unpaywall.org/v2/{doi}?email=YOUR_EMAIL
```

**Response structure (key fields):**

```json
{
  "doi": "10.1088/1741-4326/ac1654",
  "is_oa": true,
  "oa_status": "gold",
  "best_oa_location": {
    "url": "https://iopscience.iop.org/article/...",
    "url_for_pdf": "https://iopscience.iop.org/article/.../pdf",
    "version": "publishedVersion",
    "license": "cc-by",
    "host_type": "publisher"
  },
  "oa_locations": [
    { "url": "...", "version": "publishedVersion", "host_type": "publisher" },
    { "url": "https://arxiv.org/abs/...", "version": "submittedVersion", "host_type": "repository" }
  ]
}
```

Unpaywall was recently rewritten (May 2025) with 10× faster API responses (average 50ms, down from 500ms). Community curation is now available at `unpaywall.org/fix` for reporting data quality issues. Two fields were deprecated in the rewrite: `oa_locations.evidence` and `oa_locations.updated`.

The rate limit is 100,000 requests per day. No API key is required — just provide a valid email address.

> **Sources:**
> - Unpaywall API: https://unpaywall.org/products/api
> - Unpaywall data format: https://unpaywall.org/data-format
> - Unpaywall May 2025 rewrite announcement: https://blog.openalex.org/major-update-to-unpaywall-database/
> - Community curation: https://unpaywall.org/fix

### Combining the APIs

OpenAlex internally uses Unpaywall data for its open access fields, so the two APIs provide overlapping but not identical information. OpenAlex is better for batch operations (50 DOIs per request) and provides richer metadata (PMC IDs, arXiv IDs, institutional affiliations). Unpaywall is better for targeted single-DOI lookups with detailed OA location data.

For the extraction pipeline, **OpenAlex is the recommended primary API** because:
1. A single batch call can process 50 DOIs simultaneously
2. It returns PMC IDs and arXiv IDs directly, which are needed for JATS XML and arXiv HTML lookups
3. It provides the same OA location data that Unpaywall does (since it sources from Unpaywall)
4. The cursor-based pagination makes it efficient for processing an entire Zotero library

Unpaywall serves as a useful **fallback** for DOIs that OpenAlex doesn't cover or when more detailed location metadata is needed.

---

## HTML/XML to Markdown Conversion

### Converter Options

| Library | Best For | Dependencies | Notes |
|---|---|---|---|
| **Pandoc** (via `pypandoc`) | JATS XML, complex HTML | System binary | Only option that reads JATS natively; handles LaTeX math, citations, tables |
| **markdownify** | Publisher HTML with custom needs | BeautifulSoup | Highly customizable via subclassing; good for domain-specific tag handling |
| **html2text** | Simple HTML, zero-dep environments | None | Battle-tested (originally by Aaron Swartz); extensive configuration options |
| **html-to-markdown** | Modern HTML5 content | BeautifulSoup | Rewritten fork of markdownify with type safety; Python 3.9+; active maintenance |
| **trafilatura** | Web pages with boilerplate | Various | Intelligent content extraction; removes navigation/ads; best for scraping |

### Recommended Conversion Paths

**JATS XML → Pandoc → Markdown** (highest quality)

```bash
pandoc -f jats -t markdown --wrap=none -o output.md input.xml
```

Pandoc's JATS reader handles `<sec>` → headers, `<table-wrap>` → pipe tables, MathML → LaTeX math, `<ref-list>` → reference section. This is deterministic, fast, and produces markdown that is structurally faithful to the original document.

**arXiv HTML → markdownify → Markdown** (good quality)

```python
from markdownify import markdownify as md
import requests

html = requests.get(f"https://arxiv.org/html/{arxiv_id}").text
markdown = md(html, heading_style="ATX", strip=["script", "style", "nav"])
```

arXiv HTML preserves LaTeX math in `<math>` tags with LaTeX annotations, which markdownify can be configured to extract. Tables are semantic `<table>` elements that convert cleanly to pipe tables.

**Publisher HTML → html2text → Markdown** (good quality, simple)

```python
from html2text import HTML2Text

h = HTML2Text()
h.body_width = 0          # No line wrapping
h.ignore_images = False    # Keep image references
h.unicode_snob = True      # Use Unicode characters
markdown = h.handle(html)
```

html2text is the best option when you want something that works immediately without configuration. It handles most publisher HTML layouts correctly.

> **Sources:**
> - Pandoc: https://pandoc.org
> - markdownify: https://github.com/matthewwithanm/python-markdownify
> - html2text: https://github.com/Alir3z4/html2text
> - html-to-markdown: https://github.com/Goldziher/html-to-markdown
> - trafilatura: https://trafilatura.readthedocs.io

---

## Proposed Design

### Architecture: Source Discovery Layer

The source discovery layer sits upstream of the existing backend selection logic in `extraction-design.md`. It adds a new step between "receive input" and "select backend":

```
Input (DOI / arXiv ID / file path)
        │
        ▼
┌──────────────────────┐
│  Source Discovery     │  NEW: Query OpenAlex/Unpaywall for structured sources
│  (source_discovery.py)│
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Source Selection     │  Choose best available format
│  (source_selector.py) │
└──────────┬───────────┘
           │
     ┌─────┼─────┬──────────┐
     ▼     ▼     ▼          ▼
  JATS   arXiv  Publisher   PDF
  XML    HTML   HTML        (existing)
     │     │     │          │
     ▼     ▼     ▼          ▼
  pandoc  markdownify  html2text  pymupdf/docling
     │     │     │          │
     └─────┴─────┴──────────┘
                 │
                 ▼
         full_document.md + images/ + INDEX.md
```

### Tiered Source Selection

Given a paper identifier, the pipeline should try sources in this priority order:

| Priority | Source | Quality | How to Check | Converter |
|---|---|---|---|---|
| 1 | JATS XML (PMC) | ★★★★★ | PMC ID from OpenAlex `ids.pmcid` | Pandoc `-f jats` |
| 2 | arXiv HTML | ★★★★ | arXiv ID from OpenAlex locations | markdownify |
| 3 | Publisher HTML | ★★★★ | OA URL from OpenAlex `best_oa_location` | html2text or markdownify |
| 4 | PDF (existing pipeline) | ★★½ | Always available (local file) | pymupdf4llm / Docling |

The selection logic should be conservative: only use an HTML/XML source if it can be validated (non-empty response, correct content type, reasonable length). If a structured source fails to download or convert, fall through to the next tier silently.

### Component: `source_discovery.py`

```python
"""Discover structured sources for a paper given its identifiers."""

from dataclasses import dataclass
from pathlib import Path

@dataclass
class SourceCandidate:
    """A potential structured source for a paper."""
    format: str          # "jats_xml", "arxiv_html", "publisher_html", "pdf"
    url: str             # URL to fetch
    version: str | None  # "publishedVersion", "submittedVersion", etc.
    quality_tier: int    # 1 (best) through 4 (fallback)
    license: str | None  # "cc-by", etc.

def discover_sources(
    doi: str | None = None,
    arxiv_id: str | None = None,
    pmcid: str | None = None,
    email: str = "",
) -> list[SourceCandidate]:
    """Query external APIs to find structured sources for a paper.

    Returns candidates sorted by quality tier (best first).
    Requires at least one identifier (DOI, arXiv ID, or PMC ID).
    """
    candidates = []

    # Step 1: If we have a PMC ID, we know JATS XML is available
    if pmcid:
        candidates.append(SourceCandidate(
            format="jats_xml",
            url=f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmcid}&retmode=xml",
            version="publishedVersion",
            quality_tier=1,
            license=None,
        ))

    # Step 2: If we have an arXiv ID, check for HTML
    if arxiv_id:
        candidates.append(SourceCandidate(
            format="arxiv_html",
            url=f"https://arxiv.org/html/{arxiv_id}",
            version="submittedVersion",
            quality_tier=2,
            license="arxiv",
        ))

    # Step 3: If we have a DOI but no PMC ID or arXiv ID,
    #         query OpenAlex to discover them
    if doi and not (pmcid or arxiv_id):
        openalex_results = _query_openalex(doi, email)
        # ... populate candidates from results

    return sorted(candidates, key=lambda c: c.quality_tier)


def _query_openalex(doi: str, email: str) -> dict:
    """Query OpenAlex for a single DOI. Returns work object."""
    ...

def batch_discover(
    identifiers: list[dict],
    email: str,
) -> dict[str, list[SourceCandidate]]:
    """Batch discover sources for multiple papers.

    Uses OpenAlex batch API (50 DOIs per request) for efficiency.
    identifiers: list of {"doi": ..., "arxiv_id": ..., "pmcid": ...}
    Returns: {doi: [SourceCandidate, ...], ...}
    """
    ...
```

### Component: `source_fetcher.py`

```python
"""Fetch and validate structured sources."""

from pathlib import Path

def fetch_source(candidate: SourceCandidate, output_dir: Path) -> Path | None:
    """Download a structured source and validate it.

    Returns path to downloaded file, or None if fetch/validation failed.
    Validation checks: non-empty, correct content type, reasonable size.
    """
    ...

def convert_to_markdown(
    source_path: Path,
    format: str,
    output_dir: Path,
) -> Path | None:
    """Convert a structured source to full_document.md.

    Dispatches to appropriate converter based on format.
    Returns path to markdown file, or None on failure.
    """
    if format == "jats_xml":
        return _convert_jats(source_path, output_dir)
    elif format == "arxiv_html":
        return _convert_html(source_path, output_dir, converter="markdownify")
    elif format == "publisher_html":
        return _convert_html(source_path, output_dir, converter="html2text")
    return None
```

### Integration with Existing Pipeline

The source discovery layer integrates with the `cmd_extract` orchestration flow from `extraction-design.md`. The modified flow becomes:

1. Validate input path exists
2. Discover documents (PDF/DOCX)
3. **For each document, extract identifiers** (DOI from filename, Zotero metadata, or PDF metadata)
4. **Query source discovery** to find structured alternatives
5. **Attempt structured source extraction** (JATS → Pandoc, HTML → markdownify)
6. **On failure, fall back to existing backend selection** (Docling → pymupdf for PDF)
7. Write `summary.json` metadata (now includes `source_format` and `source_url`)
8. If `--index`: run index generation
9. If `--fix-tables`: run table repair pass (less likely needed with structured sources)

### Zotero Integration

Zotero stores DOIs and arXiv IDs in standardized fields that can be exported programmatically. The `pyzotero` library provides API access to a Zotero library. The workflow for processing the entire corpus:

1. Export identifiers from Zotero (DOI, arXiv ID, PMC ID for each item)
2. Batch query OpenAlex (50 DOIs per request) to discover structured sources
3. For items with structured sources available, download and convert
4. For remaining items, extract from the PDF attachment in Zotero
5. Optionally store discovered source URLs back into Zotero (as linked attachments or notes)

The `zotero-zotadata` plugin can assist with metadata enrichment, including DOI discovery and file retrieval from Unpaywall and arXiv.

### CLI Changes

Add a `--discover-sources` flag to the extract command:

```
agentic-mbse extract <path> [options]

New options:
  --discover-sources     Query OpenAlex/Unpaywall for HTML/XML sources before PDF extraction
  --email EMAIL          Email for API access (required with --discover-sources)
  --prefer-source TYPE   Force preference: jats, arxiv, html, pdf (default: auto)
  --zotero-library ID    Process all items in a Zotero library
```

### Dependencies

```toml
[project.optional-dependencies]
extract = ["pymupdf4llm>=0.0.17"]
extract-full = ["docling>=2.0", "pymupdf4llm>=0.0.17"]
extract-sources = [
    "pymupdf4llm>=0.0.17",
    "requests>=2.28",         # API calls
    "markdownify>=0.12",      # HTML → Markdown
    "html2text>=2024.2",      # HTML → Markdown (alternative)
]
```

Pandoc remains a system dependency (already used in the DOCX backend). No additional system packages required.

---

## Expected Impact

### Coverage Estimate

Based on Unpaywall coverage rates and the composition of a typical nuclear fusion research corpus:

| Paper Type | Estimated % of Corpus | Structured Source Likely? | Expected Source |
|---|---|---|---|
| Nuclear Fusion journal (IOP) | ~30% | Yes (post-2023, OA) | Publisher HTML or JATS |
| arXiv preprints | ~20% | Yes (post-2023 HTML) | arXiv HTML |
| Other OA journals (PMC) | ~15% | Yes | JATS XML |
| Government reports (LANL, etc.) | ~15% | No | PDF only |
| Older journal articles | ~10% | Unlikely | PDF only |
| Conference proceedings | ~10% | Varies | Mixed |

**Conservative estimate:** 40–60% of the corpus could have structured sources, reducing PDF extraction to the minority case rather than the universal one.

### Quality Improvement

For papers where structured sources are found:
- **Table extraction** would go from 2.00/5 to approximately 4.5/5 (semantic tables)
- **Index quality** would go from 2.43/5 to approximately 4.5/5 (semantic headers)
- **Markdown structure** would go from 2.64/5 to approximately 4.5/5 (no artifacts)
- **Overall score** would go from 2.68/5 to approximately 4.5/5

For the corpus-wide average (assuming 50% structured source coverage):
- **Projected overall score:** ~3.6/5 (up from 2.68/5)

This is a larger improvement than all of the PDF post-processing recommendations in the evaluation report combined, and with less implementation complexity.

---

## Implementation Order

| Priority | Item | Effort | Impact |
|---|---|---|---|
| 1 | `source_discovery.py` — OpenAlex batch API integration | Small | Enables all downstream work |
| 2 | JATS XML → Pandoc → Markdown conversion path | Small | Highest quality for PMC papers |
| 3 | arXiv HTML → markdownify → Markdown conversion path | Small | Covers arXiv preprints |
| 4 | Integration with `cmd_extract` orchestration | Medium | Makes it usable end-to-end |
| 5 | Zotero identifier export utility | Small | Batch processing of corpus |
| 6 | Publisher HTML → html2text → Markdown path | Small | Covers IOP and other publishers |
| 7 | `summary.json` schema update for source metadata | Trivial | Tracking/auditability |
| 8 | IOP text mining agreement request | N/A (email) | Unlocks Nuclear Fusion XML |

Items 1–3 can be implemented independently and tested before integrating into the full pipeline. The JATS and arXiv paths are the highest-value targets.

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| OpenAlex API rate limits or downtime | Low | Medium | Cache results locally; Unpaywall as fallback; batch processing reduces calls |
| arXiv HTML conversion quality issues | Medium | Low | Validate output before accepting; fall back to PDF |
| PMC XML not available for fusion-specific journals | Medium | Medium | Nuclear Fusion is OA but may not be in PMC; IOP agreement fills the gap |
| HTML sources missing images/figures | Low | Medium | Check image count in converted output; fall back to PDF if significantly fewer |
| API schema changes | Low | Low | Pin to known response structures; add versioning |
| Publisher access restrictions | Medium | Medium | IOP text mining agreement; respect `robots.txt` and ToS |

---

## Relationship to Existing Recommendations

The evaluation report recommended 10 implementation items for improving PDF extraction quality. This source discovery strategy does not replace those items — it **reduces the number of documents that need them**. The recommended priority becomes:

1. **Source discovery** (this proposal) — eliminates PDF failure modes for 40–60% of corpus
2. **Header promotion post-processing** — still needed for remaining PDF-only documents
3. **Absolute image path rewrite** — still needed for pymupdf backend
4. **Page artifact stripping** — still needed for PDF-only documents
5. **`--fix-tables` implementation** — still needed for PDF-only documents, but fewer tables to fix

Items that become lower priority with structured sources:
- `table_strategy` cascade — structured sources have proper tables
- `hdr_info=TocHeaders` — structured sources have proper headers
- Ligature replacement — structured sources use Unicode text
- Docling failure investigation — less critical when structured sources cover many papers

---

## References

1. arXiv HTML Papers — https://info.arxiv.org/about/accessible_HTML.html
2. ar5iv (LaTeXML HTML mirror) — https://ar5iv.labs.arxiv.org
3. LaTeXML — https://github.com/brucemiller/LaTeXML
4. PMC Developer Tools — https://pmc.ncbi.nlm.nih.gov/tools/developers/
5. PMC OAI-PMH API — https://pmc.ncbi.nlm.nih.gov/tools/oai/
6. JATS Standard (NISO Z39.96) — https://jats.nlm.nih.gov/archiving/
7. NCBI E-utilities — https://www.ncbi.nlm.nih.gov/books/NBK25500/
8. PMC XML Converters (public domain) — https://github.com/ncbi/PMCXMLConverters
9. OpenAlex Documentation — https://docs.openalex.org
10. OpenAlex Work Object — https://docs.openalex.org/api-entities/works/work-object
11. OpenAlex API Guide — https://docs.openalex.org/api-guide-for-llms
12. Unpaywall API — https://unpaywall.org/products/api
13. Unpaywall Data Format — https://unpaywall.org/data-format
14. Unpaywall May 2025 Rewrite — https://blog.openalex.org/major-update-to-unpaywall-database/
15. Pandoc — https://pandoc.org
16. markdownify — https://github.com/matthewwithanm/python-markdownify
17. html2text — https://github.com/Alir3z4/html2text
18. html-to-markdown — https://github.com/Goldziher/html-to-markdown
19. trafilatura — https://trafilatura.readthedocs.io
20. IOP Publishing Text & Data Mining — https://publishingsupport.iopscience.iop.org/questions/text-and-data-mining/