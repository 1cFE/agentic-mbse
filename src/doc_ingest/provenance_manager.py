"""Atomic persistence for provenance records.

Spec 009: ProvenanceManager provides crash-safe writes via temp file + atomic rename,
supports loading existing records by document hash, and handles UTF-8 encoding for
non-ASCII identifiers.
"""

import json
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from doc_ingest.types import ProvenanceRecord

if TYPE_CHECKING:
    from doc_ingest.types import DocumentIdentifiers


class ProvenanceManager:
    """Manage atomic persistence of provenance records.

    Writes provenance records to `output_dir/{document_hash}/provenance.json` using
    atomic temp file + rename pattern to prevent corruption on crashes. Loads existing
    provenance by document hash for resumability checks.

    All writes use UTF-8 encoding to preserve non-ASCII characters in identifiers.
    """

    def write(self, output_dir: Path, record: ProvenanceRecord) -> None:
        """Write provenance record atomically to output directory.

        Creates `output_dir/{hash}/provenance.json` using temp file + rename to ensure
        atomicity. If the process is killed mid-write, either the old file remains intact
        or the new file is complete (never partial JSON).

        Args:
            output_dir: Base output directory
            record: ProvenanceRecord to persist

        Raises:
            OSError: If directory creation or file write fails
        """
        # Get document hash for directory name
        document_hash = self._compute_hash(record.document_id)
        doc_dir = output_dir / document_hash
        doc_dir.mkdir(parents=True, exist_ok=True)

        provenance_path = doc_dir / "provenance.json"

        # Serialize to JSON with UTF-8 encoding
        json_bytes = json.dumps(
            self._to_dict(record),
            ensure_ascii=False,  # Preserve Unicode characters
            indent=2,
            sort_keys=True,  # Deterministic ordering
        ).encode("utf-8")

        # Write atomically via temp file in same directory (ensures same filesystem)
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=doc_dir,
            delete=False,
            prefix=".provenance_",
            suffix=".tmp",
        ) as tmp_file:
            tmp_file.write(json_bytes)
            tmp_file.flush()
            tmp_path = Path(tmp_file.name)

        # Atomic rename (POSIX guarantees atomicity on same filesystem)
        tmp_path.replace(provenance_path)

    def load(self, output_dir: Path, document_hash: str) -> ProvenanceRecord | None:
        """Load existing provenance record by document hash.

        Args:
            output_dir: Base output directory
            document_hash: Document hash (from DocumentIdentifiers.primary_identifier())

        Returns:
            ProvenanceRecord if file exists and is valid, None otherwise
        """
        provenance_path = output_dir / document_hash / "provenance.json"

        if not provenance_path.exists():
            return None

        try:
            with provenance_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return self._from_dict(data)
        except (json.JSONDecodeError, OSError, KeyError, TypeError):
            # Corrupted file or invalid structure → treat as missing
            return None

    def _compute_hash(self, document_id: "DocumentIdentifiers") -> str:
        """Compute hash from document identifiers for directory naming.

        Uses the primary identifier (doi > arxiv_id > pmc_id > local_path) to generate
        a deterministic hash for the output directory name.

        Args:
            document_id: DocumentIdentifiers instance

        Returns:
            Hash string for directory name
        """
        import hashlib

        id_type, id_value = document_id.primary_identifier()
        hash_input = f"{id_type}:{id_value}".encode()
        return hashlib.sha256(hash_input).hexdigest()[:16]

    def _to_dict(self, record: ProvenanceRecord) -> dict:
        """Convert ProvenanceRecord to JSON-serializable dict.

        Recursively converts all dataclass fields to dicts for JSON serialization.

        Args:
            record: ProvenanceRecord to serialize

        Returns:
            Dict with all fields serialized
        """
        from dataclasses import asdict

        return asdict(record)

    def _from_dict(self, data: dict) -> ProvenanceRecord:
        """Reconstruct ProvenanceRecord from dict loaded from JSON.

        Args:
            data: Dict loaded from JSON file

        Returns:
            ProvenanceRecord instance

        Raises:
            KeyError: If required fields are missing
            TypeError: If field types are incorrect
        """
        from doc_ingest.outcome_classifier import ExtractionAttempt
        from doc_ingest.types import DocumentIdentifiers, SourceCandidate

        # Reconstruct nested structures
        document_id = DocumentIdentifiers(**data["document_id"])

        discovered_sources = [SourceCandidate(**src) for src in data["discovered_sources"]]

        # ExtractionAttempt reconstruction (needs all fields from outcome_classifier)
        attempts = [ExtractionAttempt(**attempt) for attempt in data["attempts"]]

        return ProvenanceRecord(
            document_id=document_id,
            discovered_sources=discovered_sources,
            discovery_errors=data["discovery_errors"],
            discovery_cached=data["discovery_cached"],
            attempts=attempts,
            outcome=data["outcome"],
            final_converter=data.get("final_converter"),
            failure_category=data.get("failure_category"),
            created_at=data["created_at"],
            pipeline_version=data["pipeline_version"],
            total_elapsed_seconds=data["total_elapsed_seconds"],
        )
