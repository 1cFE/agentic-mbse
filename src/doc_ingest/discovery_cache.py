"""Discovery cache for source candidates.

Provides TTL-based caching of discovered source candidates to avoid redundant
API calls during document discovery. Implements file system storage with
per-identifier cache files and configurable time-to-live.

Spec 013: DiscoveryCache supports efficient source discovery with freshness
checks and targeted invalidation.
"""

import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path

from doc_ingest.types import SourceCandidate


class DiscoveryCache:
    """Cache for discovered source candidates with TTL-based freshness checks.

    Stores discovered sources on the local file system keyed by document
    identifier, with configurable time-to-live for staleness detection.
    Supports per-identifier invalidation and bulk cache clearing.

    The cache directory structure is flat: each identifier gets one JSON file
    named by the SHA-256 hash of the identifier key (to handle special characters).

    Cache file format:
        {
            "timestamp": 1234567890.0,  # Unix timestamp
            "identifier_key": "doi:10.1234/foo",
            "sources": [...]  # List of SourceCandidate dicts
        }

    Attributes:
        cache_dir: Directory path for cache storage
        ttl_days: Time-to-live in days for cache freshness
    """

    def __init__(self, cache_dir: Path, ttl_days: int):
        """Initialize cache with directory and TTL.

        Args:
            cache_dir: Path to cache directory (will be created if missing)
            ttl_days: Cache entry TTL in days (entries older than this are stale)

        Examples:
            >>> cache = DiscoveryCache(Path.home() / ".cache" / "doc-ingest", ttl_days=30)
            >>> cache.put("doi:10.1234/foo", sources)
            >>> cached = cache.get("doi:10.1234/foo")
        """
        self.cache_dir = cache_dir
        self.ttl_days = ttl_days
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_file_path(self, identifier_key: str) -> Path:
        """Return cache file path for identifier.

        Uses SHA-256 hash of identifier key to handle special characters
        and ensure consistent file naming.

        Args:
            identifier_key: Document identifier key (e.g., "doi:10.1234/foo")

        Returns:
            Path to cache file for this identifier
        """
        # Hash the identifier to create safe filename
        key_hash = hashlib.sha256(identifier_key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, identifier_key: str) -> list[SourceCandidate] | None:
        """Return cached sources if fresh, None if missing or stale.

        Args:
            identifier_key: Document identifier key to look up

        Returns:
            List of cached SourceCandidate objects if fresh, None if missing or stale

        Examples:
            >>> cache.get("doi:10.1234/foo")  # Returns cached sources or None
        """
        cache_file = self._cache_file_path(identifier_key)

        if not cache_file.exists():
            return None

        try:
            with cache_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Check freshness
            timestamp = data["timestamp"]
            age_seconds = time.time() - timestamp
            age_days = age_seconds / (24 * 3600)

            if age_days > self.ttl_days:
                # Stale entry
                return None

            # Reconstruct SourceCandidate objects from dicts
            sources = [SourceCandidate(**source) for source in data["sources"]]
            return sources

        except (json.JSONDecodeError, KeyError, TypeError):
            # Corrupted cache file - treat as missing
            return None

    def put(self, identifier_key: str, sources: list[SourceCandidate]) -> None:
        """Cache discovered sources with current timestamp.

        Args:
            identifier_key: Document identifier key
            sources: List of discovered SourceCandidate objects to cache

        Examples:
            >>> cache.put("doi:10.1234/foo", [source1, source2])
        """
        cache_file = self._cache_file_path(identifier_key)

        # Serialize sources to dicts
        sources_data = [asdict(source) for source in sources]

        data = {
            "timestamp": time.time(),
            "identifier_key": identifier_key,
            "sources": sources_data,
        }

        # Atomic write using temp file
        temp_file = cache_file.with_suffix(".tmp")
        try:
            with temp_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_file.replace(cache_file)
        except Exception:
            # Clean up temp file on failure
            if temp_file.exists():
                temp_file.unlink()
            raise

    def invalidate(self, identifier_key: str) -> bool:
        """Remove specific entry. Returns True if existed.

        Args:
            identifier_key: Document identifier key to invalidate

        Returns:
            True if the cache entry existed and was removed, False otherwise

        Examples:
            >>> cache.invalidate("doi:10.1234/foo")  # Returns True if existed
        """
        cache_file = self._cache_file_path(identifier_key)

        if cache_file.exists():
            cache_file.unlink()
            return True
        return False

    def clear(self, max_age_days: int | None = None) -> int:
        """Remove all entries (or only old ones). Returns count removed.

        Args:
            max_age_days: If provided, only remove entries older than this many days.
                         If None, remove all entries.

        Returns:
            Number of cache entries removed

        Examples:
            >>> cache.clear()  # Remove all entries
            42
            >>> cache.clear(max_age_days=30)  # Remove only entries older than 30 days
            10
        """
        if not self.cache_dir.exists():
            return 0

        removed_count = 0
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.json"):
            should_remove = False

            if max_age_days is None:
                # Remove all entries
                should_remove = True
            else:
                # Check age and remove if too old
                try:
                    with cache_file.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                    timestamp = data["timestamp"]
                    age_seconds = current_time - timestamp
                    age_days = age_seconds / (24 * 3600)

                    if age_days > max_age_days:
                        should_remove = True
                except (json.JSONDecodeError, KeyError, OSError):
                    # Corrupted or unreadable - remove it
                    should_remove = True

            if should_remove:
                cache_file.unlink()
                removed_count += 1

        return removed_count
