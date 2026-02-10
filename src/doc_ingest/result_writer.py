"""Write extraction outputs to the file system.

Spec 012: ResultWriter provides atomic writes for markdown content, legacy summary.json,
and delegates provenance persistence to ProvenanceManager. Only successful extractions
produce output.md and summary.json; failed extractions only write provenance.json.
"""

import json
from pathlib import Path

from doc_ingest.provenance_manager import ProvenanceManager
from doc_ingest.types import ExtractionResult


class ResultWriter:
    """Write extraction results to the file system.

    Handles writing markdown outputs, legacy summary.json for backward compatibility,
    and delegates provenance writing to ProvenanceManager. Uses deterministic directory
    naming based on document hash.

    Only successful extractions (markdown is not None) produce output.md and summary.json.
    Failed extractions only write provenance.json via the provenance manager.
    """

    def __init__(self, provenance_manager: ProvenanceManager) -> None:
        """Initialize ResultWriter with provenance manager dependency.

        Args:
            provenance_manager: ProvenanceManager instance for delegating provenance writes
        """
        self.provenance_manager = provenance_manager

    def write(self, output_dir: Path, result: ExtractionResult) -> None:
        """Write extraction outputs to output directory.

        Creates `output_dir/{document_hash}/` directory and writes:
        - output.md: Extracted markdown (success only)
        - summary.json: Legacy metadata (success only)
        - provenance.json: Complete provenance (delegated to ProvenanceManager)

        Directory naming uses document hash from primary identifier for deterministic
        and collision-free naming.

        Args:
            output_dir: Base output directory path
            result: ExtractionResult with markdown and provenance

        Raises:
            OSError: If directory creation or file writes fail
        """
        # Delegate provenance writing first (always written)
        self.provenance_manager.write(output_dir, result.provenance)

        # Skip markdown and summary writes for failed extractions
        if result.markdown is None:
            return

        # Compute document hash for directory name
        document_hash = self.provenance_manager._compute_hash(result.provenance.document_id)
        doc_dir = output_dir / document_hash

        # Directory should already exist from provenance write, but be defensive
        doc_dir.mkdir(parents=True, exist_ok=True)

        # Write output.md
        output_md_path = doc_dir / "output.md"
        output_md_path.write_text(result.markdown, encoding="utf-8")

        # Write summary.json (legacy format for backward compatibility)
        summary_data = self._build_summary(result)
        summary_path = doc_dir / "summary.json"
        summary_json = json.dumps(summary_data, ensure_ascii=False, indent=2, sort_keys=True)
        summary_path.write_text(summary_json, encoding="utf-8")

    def _build_summary(self, result: ExtractionResult) -> dict:
        """Build legacy summary.json structure from extraction result.

        Constructs a backward-compatible summary dictionary with key metadata fields
        for consumption by legacy tools or downstream processors.

        Args:
            result: ExtractionResult with provenance and markdown

        Returns:
            Dict with summary fields: document_hash, source_info, processed_at,
            backend_used, outcome, statistics, warnings (if present)
        """
        prov = result.provenance
        document_hash = self.provenance_manager._compute_hash(prov.document_id)

        # Build source info from document identifiers
        source_info = {}
        if prov.document_id.doi:
            source_info["doi"] = prov.document_id.doi
        if prov.document_id.arxiv_id:
            source_info["arxiv_id"] = prov.document_id.arxiv_id
        if prov.document_id.pmc_id:
            source_info["pmc_id"] = prov.document_id.pmc_id
        if prov.document_id.local_path:
            source_info["local_path"] = prov.document_id.local_path
        if prov.document_id.zotero_key:
            source_info["zotero_key"] = prov.document_id.zotero_key

        # Base summary structure
        summary = {
            "document_hash": document_hash,
            "source_info": source_info,
            "processed_at": prov.created_at,
            "backend_used": prov.final_converter,
            "outcome": prov.outcome,
            "statistics": {
                "total_elapsed_seconds": prov.total_elapsed_seconds,
                "num_attempts": len(prov.attempts),
                "num_sources_discovered": len(prov.discovered_sources),
            },
        }

        return summary
