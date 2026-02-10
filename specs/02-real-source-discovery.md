# Spec 02: Real Source Discovery (OpenAlex + arXiv)

## Priority: THIRD — After extraction quality is proven

## Problem

`source_discoverer.py` is a stub that returns mock sources for DOIs and arXiv IDs. The whole point of the routing architecture is to discover structured alternatives (JATS XML, arXiv HTML) that are higher quality than PDF. But we've never tested this on a real DOI.

## Why This Is Third

Source discovery is useless if the converters produce bad output. Fix extraction quality first (Specs 00-01), then wire in real discovery so the quality-ordered routing actually matters.

## Approach

### OpenAlex API (DOI → structured sources)

OpenAlex provides free metadata for academic papers, including links to:
- Publisher landing pages (may have HTML full text)
- Open access PDF URLs
- PMC links (which have JATS XML)

```python
class OpenAlexClient:
    def query(self, doi: str) -> list[SourceCandidate]:
        """Query OpenAlex for a DOI, return discovered sources."""
        # GET https://api.openalex.org/works/doi:{doi}
        # Parse: open_access.oa_url, primary_location.landing_page_url,
        #        host_venue.url, best_oa_location
        # Return SourceCandidates sorted by quality tier
```

### arXiv API (arXiv ID → HTML + PDF)

arXiv provides:
- HTML5 rendering: `https://arxiv.org/html/{arxiv_id}` (high quality, MathML preserved)
- PDF: `https://arxiv.org/pdf/{arxiv_id}.pdf`

```python
class ArXivClient:
    def query(self, arxiv_id: str) -> list[SourceCandidate]:
        """Resolve arXiv ID to HTML and PDF sources."""
        # Check if HTML version exists (HEAD request to /html/{id})
        # Return [html_source (tier 2), pdf_source (tier 4)]
```

### PMC API (PMC ID → JATS XML)

PMC provides JATS XML for open-access papers:
- `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc_id}&rettype=xml`

## What We Don't Know

- **Does OpenAlex return useful links for our test DOIs?** Need to manually query `https://api.openalex.org/works/doi:10.1098/rsta.2020.0053` and inspect.
- **Does the arXiv HTML converter actually work on real arXiv HTML?** It was tested with synthetic HTML only.
- **Does the JATS converter work on real PMC XML?** Same — tested with synthetic XML only.
- **What's the OpenAlex rate limit?** Free tier is 100K requests/day (generous), but need to verify.
- **How many of our test papers have structured alternatives?** Unknown until we query.

## Test Strategy

Before writing any code:
1. **Manual API queries**: For each test paper DOI, query OpenAlex and record what sources are available
2. **Manual converter test**: Download one real arXiv HTML page, run through ArXivHTMLConverter, inspect output
3. **Manual converter test**: Download one real JATS XML file, run through JATSPandocConverter, inspect output

If the converters produce garbage on real input, fix them before wiring in discovery.

## Acceptance Criteria

- [ ] `SourceDiscoverer.discover(DocumentIdentifiers(doi="10.1098/rsta.2020.0053"))` returns real sources from OpenAlex
- [ ] At least one structured source (HTML or JATS) is discovered for a paper that has one
- [ ] The quality-tier ordering actually routes to the structured source first
- [ ] Extraction from the structured source produces quality >= PDF extraction (measured by test harness)
- [ ] Discovery cache prevents re-querying the same DOI
- [ ] API errors are handled gracefully (recorded in provenance, falls back to PDF)

## Implementation Notes

- Keep the stub discoverer as fallback — if API calls fail, local file discovery still works
- Rate limit: Add 100ms delay between API calls (be a good citizen)
- The existing `DiscoveryCache` is ready to use — just plug real API clients into it
