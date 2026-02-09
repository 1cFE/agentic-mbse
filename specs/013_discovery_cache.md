
## Purpose
Cache discovered source candidates per document identifier to avoid redundant API calls, with TTL-based freshness checks and per-identifier invalidation.

## Requirements
- Store discovered sources keyed by document primary identifier
- Check freshness using TTL (configurable, default 30 days)
- Return cached sources if fresh, None if missing or stale
- Support per-identifier cache invalidation
- Support bulk cache clearing (all entries or by age)
- Use local file system for storage (~/.cache/agentic-mbse/source_discovery/)

## Acceptance Criteria
- **Given** sources cached for "doi:10.1234/foo" 10 days ago and TTL=30 days, **when** `get()` is called, **then** return cached sources
- **Given** sources cached 31 days ago and TTL=30 days, **when** `get()` is called, **then** return None (stale)
- **Given** identifier not in cache, **when** `get()` is called, **then** return None
- **Given** successful discovery, **when** `put()` is called, **then** write cache file with timestamp
- **Given** cached identifier, **when** `invalidate()` is called, **then** remove cache file and return True
- **Given** non-cached identifier, **when** `invalidate()` is called, **then** return False
- **Given** cache with 100 entries, **when** `clear(max_age_days=30)` is called, **then** remove only entries older than 30 days and return count

## Interfaces
**API:**
```python
class DiscoveryCache:
    def __init__(self, cache_dir: Path, ttl_days: int):
        """Initialize cache with directory and TTL."""
    
    def get(self, identifier_key: str) -> list[SourceCandidate] | None:
        """Return cached sources if fresh, None if missing or stale."""
    
    def put(self, identifier_key: str, sources: list[SourceCandidate]) -> None:
        """Cache discovered sources with current timestamp."""
    
    def invalidate(self, identifier_key: str) -> bool:
        """Remove specific entry. Returns True if existed."""
    
    def clear(self, max_age_days: int | None = None) -> int:
        """Remove all entries (or only old ones). Returns count removed."""

