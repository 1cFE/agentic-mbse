"""Tests for DocumentIdentifiers data model."""

import pytest

from src.doc_ingest.types import DocumentIdentifiers


class TestDocumentIdentifiers:
    """Tests for DocumentIdentifiers class."""

    def test_requires_at_least_one_identifier(self) -> None:
        """Given no identifiers, when constructed, then raises ValueError."""
        with pytest.raises(ValueError, match="At least one identifier required"):
            DocumentIdentifiers()

    def test_doi_has_highest_priority(self) -> None:
        """Given DOI and arXiv ID, when primary_identifier called, then returns DOI."""
        doc = DocumentIdentifiers(doi="10.1103/PhysRevLett.116.061102", arxiv_id="1602.03837")
        assert doc.primary_identifier() == ("doi", "10.1103/PhysRevLett.116.061102")

    def test_arxiv_id_second_priority(self) -> None:
        """Given only arXiv ID, when primary_identifier called, then returns arXiv."""
        doc = DocumentIdentifiers(arxiv_id="1602.03837")
        assert doc.primary_identifier() == ("arxiv", "1602.03837")

    def test_pmc_id_third_priority(self) -> None:
        """Given only PMC ID, when primary_identifier called, then returns PMC."""
        doc = DocumentIdentifiers(pmc_id="PMC4847581")
        assert doc.primary_identifier() == ("pmc", "PMC4847581")

    def test_local_path_lowest_priority(self) -> None:
        """Given only local path, when primary_identifier called, then returns local."""
        doc = DocumentIdentifiers(local_path="/path/to/paper.pdf")
        assert doc.primary_identifier() == ("local", "/path/to/paper.pdf")

    def test_priority_order_with_all_identifiers(self) -> None:
        """Given all identifiers, when primary_identifier called, then returns DOI."""
        doc = DocumentIdentifiers(
            doi="10.1103/PhysRevLett.116.061102",
            arxiv_id="1602.03837",
            pmc_id="PMC4847581",
            local_path="/path/to/paper.pdf",
        )
        assert doc.primary_identifier() == ("doi", "10.1103/PhysRevLett.116.061102")

    def test_display_key_uses_primary_identifier(self) -> None:
        """Given DOI, when display_key called, then returns 'doi:...' format."""
        doc = DocumentIdentifiers(doi="10.1103/PhysRevLett.116.061102")
        assert doc.display_key() == "doi:10.1103/PhysRevLett.116.061102"

    def test_display_key_with_arxiv_id(self) -> None:
        """Given only arXiv ID, when display_key called, then returns 'arxiv:...' format."""
        doc = DocumentIdentifiers(arxiv_id="1602.03837")
        assert doc.display_key() == "arxiv:1602.03837"

    def test_same_primary_identifier_generates_same_cache_key(self) -> None:
        """Given two docs with same DOI but different secondary IDs, then same display_key."""
        doc1 = DocumentIdentifiers(doi="10.1103/PhysRevLett.116.061102")
        doc2 = DocumentIdentifiers(doi="10.1103/PhysRevLett.116.061102", arxiv_id="1602.03837")
        assert doc1.display_key() == doc2.display_key()

    def test_zotero_key_does_not_affect_priority(self) -> None:
        """Given only Zotero key, when constructed, then raises ValueError."""
        # Zotero key alone is not sufficient
        with pytest.raises(ValueError, match="At least one identifier required"):
            DocumentIdentifiers(zotero_key="ABCD1234")

    def test_zotero_key_stored_but_not_used_in_priority(self) -> None:
        """Given Zotero key with DOI, when primary_identifier called, then returns DOI."""
        doc = DocumentIdentifiers(doi="10.1103/PhysRevLett.116.061102", zotero_key="ABCD1234")
        assert doc.primary_identifier() == ("doi", "10.1103/PhysRevLett.116.061102")
        assert doc.zotero_key == "ABCD1234"

    def test_arxiv_id_wins_over_pmc_id(self) -> None:
        """Given arXiv and PMC ID, when primary_identifier called, then returns arXiv."""
        doc = DocumentIdentifiers(arxiv_id="1602.03837", pmc_id="PMC4847581")
        assert doc.primary_identifier() == ("arxiv", "1602.03837")

    def test_pmc_id_wins_over_local_path(self) -> None:
        """Given PMC ID and local path, when primary_identifier called, then returns PMC."""
        doc = DocumentIdentifiers(pmc_id="PMC4847581", local_path="/path/to/paper.pdf")
        assert doc.primary_identifier() == ("pmc", "PMC4847581")
