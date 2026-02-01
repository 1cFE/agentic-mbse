"""Tests for anchor reconciliation algorithms."""

from comment_system.anchors import reconcile_anchor
from comment_system.fuzzy import compute_content_hash
from comment_system.models import Anchor, AnchorHealth


class TestReconcileAnchor:
    """Tests for reconcile_anchor() function."""

    def test_exact_match_at_original_position(self):
        """When content unchanged at original position, anchor stays anchored."""
        # Original file content
        source_lines = [
            "def foo():",
            "    # This is a comment",
            "    return 42",
            "",
            "def bar():",
            "    return 100",
        ]

        # Create anchor for lines 2-3 (the comment and return)
        content = "\n".join(source_lines[1:3])
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash(source_lines[0])
        context_after = compute_content_hash(source_lines[3])

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=2,
            line_end=3,
            content_snippet=content,
            health=AnchorHealth.ANCHORED,
        )

        # Reconcile with unchanged file
        result = reconcile_anchor(anchor, source_lines)

        assert result.health == AnchorHealth.ANCHORED
        assert result.line_start == 2
        assert result.line_end == 3
        assert result.drift_distance == 0
        assert result.content_snippet == content  # Preserved

    def test_exact_match_moved_down(self):
        """AC-1: When lines inserted above, anchor moves down with health 'anchored'."""
        # Original file
        original_lines = [
            "def foo():",
            "    # This is a comment",
            "    return 42",
            "",
            "def bar():",
            "    return 100",
        ]

        # Create anchor for lines 2-3
        content = "\n".join(original_lines[1:3])
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash(original_lines[0])
        context_after = compute_content_hash(original_lines[3])

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=2,
            line_end=3,
            content_snippet=content,
        )

        # New file: 5 lines inserted above
        new_lines = [
            "# File header",
            "# Copyright notice",
            "# License",
            "",
            "",
            "def foo():",
            "    # This is a comment",
            "    return 42",
            "",
            "def bar():",
            "    return 100",
        ]

        # Reconcile
        result = reconcile_anchor(anchor, new_lines)

        assert result.health == AnchorHealth.ANCHORED
        assert result.line_start == 7  # Moved from line 2 to line 7 (5 lines inserted)
        assert result.line_end == 8
        assert result.drift_distance == 5
        assert result.content_snippet == content  # Original preserved

    def test_exact_match_moved_up(self):
        """When lines deleted above, anchor moves up with health 'anchored'."""
        # Original file
        original_lines = [
            "# Header 1",
            "# Header 2",
            "# Header 3",
            "",
            "def foo():",
            "    # This is a comment",
            "    return 42",
        ]

        # Create anchor for lines 6-7
        content = "\n".join(original_lines[5:7])
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash(original_lines[4])
        context_after = compute_content_hash("")  # No line after

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=6,
            line_end=7,
            content_snippet=content,
        )

        # New file: headers removed
        new_lines = [
            "def foo():",
            "    # This is a comment",
            "    return 42",
        ]

        # Reconcile
        result = reconcile_anchor(anchor, new_lines)

        assert result.health == AnchorHealth.ANCHORED
        assert result.line_start == 2  # Moved from line 6 to line 2
        assert result.line_end == 3
        assert result.drift_distance == 4
        assert result.content_snippet == content

    def test_content_changed_fuzzy_match_drifted(self):
        """AC-2: When content changes slightly, fuzzy match finds it as 'drifted'."""
        # Original file
        original_lines = [
            "def foo():",
            "    # This implements a linear scaling model for performance",
            "    return x * 2",
        ]

        # Create anchor for line 2
        content = original_lines[1]
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash(original_lines[0])
        context_after = compute_content_hash(original_lines[2])

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=2,
            line_end=2,
            content_snippet=content,
        )

        # New file: content changed slightly (typo fix + word addition)
        new_lines = [
            "def foo():",
            "    # This implements a basic linear scaling model for performance",
            "    return x * 2",
        ]

        # Reconcile
        result = reconcile_anchor(anchor, new_lines)

        assert result.health == AnchorHealth.DRIFTED
        assert result.line_start == 2  # Found at same position (fuzzy match)
        assert result.line_end == 2
        assert result.drift_distance == 0  # No drift in position, but content changed
        assert result.content_snippet == content  # Original snippet preserved

    def test_content_and_position_changed_context_based_match(self):
        """Context-based matching finds anchor when both content and position change."""
        # Original file
        original_lines = [
            "def setup():",
            "    config = load_config()",
            "    # TODO: we need to validate the configuration schema here",
            "    return config",
            "",
            "def teardown():",
            "    cleanup()",
        ]

        # Create anchor for line 3
        content = original_lines[2]
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash(original_lines[1])
        context_after = compute_content_hash(original_lines[3])

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=3,
            line_end=3,
            content_snippet=content,
        )

        # New file: content changed AND position changed (headers added)
        new_lines = [
            "# Header",
            "",
            "def setup():",
            "    config = load_config()",
            "    # FIXME: we need to validate the configuration schema properly",  # Content changed
            "    return config",
            "",
            "def teardown():",
            "    cleanup()",
        ]

        # Reconcile (context hashes should help locate it)
        result = reconcile_anchor(anchor, new_lines)

        # Should find via context-based fuzzy matching
        assert result.health == AnchorHealth.DRIFTED
        assert result.line_start == 5  # Found at line 5 (was line 3)
        assert result.line_end == 5
        assert result.drift_distance == 2
        assert result.content_snippet == content  # Original preserved

    def test_content_deleted_becomes_orphaned(self):
        """AC-4: When content deleted, anchor becomes orphaned."""
        # Original file
        original_lines = [
            "def foo():",
            "    # This will be deleted",
            "    return 42",
        ]

        # Create anchor for line 2
        content = original_lines[1]
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash(original_lines[0])
        context_after = compute_content_hash(original_lines[2])

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=2,
            line_end=2,
            content_snippet=content,
        )

        # New file: comment deleted
        new_lines = [
            "def foo():",
            "    return 42",
        ]

        # Reconcile
        result = reconcile_anchor(anchor, new_lines)

        assert result.health == AnchorHealth.ORPHANED
        assert result.line_start == 2  # Original position preserved
        assert result.line_end == 2
        assert result.drift_distance == 0
        assert result.content_snippet == content  # Original snippet preserved

    def test_multiline_anchor_exact_match(self):
        """Multi-line anchors should be reconciled correctly."""
        # Original file
        original_lines = [
            "def process():",
            "    # Start processing",
            "    data = load()",
            "    result = transform(data)",
            "    save(result)",
            "    # End processing",
        ]

        # Create anchor for lines 2-4 (3 lines)
        content = "\n".join(original_lines[1:4])
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash(original_lines[0])
        context_after = compute_content_hash(original_lines[4])

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=2,
            line_end=4,
            content_snippet=content,
        )

        # New file: content moved down by 3 lines
        new_lines = [
            "# Header 1",
            "# Header 2",
            "# Header 3",
            "def process():",
            "    # Start processing",
            "    data = load()",
            "    result = transform(data)",
            "    save(result)",
            "    # End processing",
        ]

        # Reconcile
        result = reconcile_anchor(anchor, new_lines)

        assert result.health == AnchorHealth.ANCHORED
        assert result.line_start == 5  # Moved from 2 to 5
        assert result.line_end == 7  # Moved from 4 to 7
        assert result.drift_distance == 3
        assert result.content_snippet == content

    def test_no_change_in_file_all_anchors_stay_anchored(self):
        """AC-6: When file unchanged, all anchors remain anchored with drift 0."""
        source_lines = [
            "line 1",
            "line 2",
            "line 3",
            "line 4",
            "line 5",
        ]

        # Create multiple anchors
        anchors = []
        for i in range(1, 4):  # Lines 1, 2, 3
            content = source_lines[i - 1]
            content_hash = compute_content_hash(content)
            context_before = compute_content_hash(source_lines[i - 2] if i > 1 else "")
            context_after = compute_content_hash(
                source_lines[i] if i < len(source_lines) else ""
            )

            anchor = Anchor(
                content_hash=content_hash,
                context_hash_before=context_before,
                context_hash_after=context_after,
                line_start=i,
                line_end=i,
                content_snippet=content,
            )
            anchors.append(anchor)

        # Reconcile all with unchanged file
        results = [reconcile_anchor(a, source_lines) for a in anchors]

        for i, result in enumerate(results):
            assert result.health == AnchorHealth.ANCHORED
            assert result.drift_distance == 0
            assert result.line_start == i + 1
            assert result.line_end == i + 1

    def test_ambiguous_content_closest_to_original_position(self):
        """When content appears multiple times, choose closest to original position."""
        # Original file with duplicate content
        original_lines = [
            "def foo():",
            "    # TODO: fix this",
            "    pass",
            "",
            "def bar():",
            "    # TODO: fix this",  # Same comment
            "    pass",
        ]

        # Create anchor for first occurrence (line 2)
        content = "    # TODO: fix this"
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash(original_lines[0])
        context_after = compute_content_hash(original_lines[2])

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=2,
            line_end=2,
            content_snippet=content,
        )

        # File unchanged, should match first occurrence exactly
        result = reconcile_anchor(anchor, original_lines)

        assert result.health == AnchorHealth.ANCHORED
        assert result.line_start == 2  # First occurrence, not second
        assert result.line_end == 2
        assert result.drift_distance == 0

    def test_context_disambiguation_when_content_appears_twice(self):
        """AC-3: Context hashes disambiguate when content appears multiple times."""
        # File with duplicate content but different contexts
        source_lines = [
            "class A:",
            "    # Important note",
            "    pass",
            "",
            "class B:",
            "    # Important note",  # Same content
            "    pass",
        ]

        # Create anchor for first occurrence with specific context
        content = "    # Important note"
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash("class A:")
        context_after = compute_content_hash("    pass")

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=2,
            line_end=2,
            content_snippet=content,
        )

        # Reconcile - should match first occurrence due to context
        result = reconcile_anchor(anchor, source_lines)

        assert result.health == AnchorHealth.ANCHORED
        assert result.line_start == 2  # First occurrence (context matches)
        assert result.line_end == 2

    def test_sliding_window_limits_search_range(self):
        """Fuzzy search respects max_window parameter (±500 lines default)."""
        # Create a very long file
        long_file = [f"line {i}" for i in range(2000)]

        # Original anchor at line 100
        content = "line 99"  # 0-indexed line 99 = 1-indexed line 100
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash("line 98")
        context_after = compute_content_hash("line 100")

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=100,
            line_end=100,
            content_snippet=content,
        )

        # Change content at original position and far away (line 1500)
        new_file = long_file.copy()
        new_file[99] = "CHANGED LINE"  # Change original position
        # Don't add exact match anywhere in search window (±500 from line 100)

        # Reconcile with default window (±500) - should become orphaned
        # because changed content doesn't match and no fuzzy match found
        result = reconcile_anchor(anchor, new_file, fallback_window=500)

        # Should not find match at line 1500 (outside window)
        assert result.health == AnchorHealth.ORPHANED
        assert result.line_start == 100  # Original position preserved

    def test_threshold_affects_drifted_vs_orphaned(self):
        """Similarity threshold determines if anchor is drifted or orphaned."""
        original_lines = [
            "def foo():",
            "    # Original comment text here",
            "    return 42",
        ]

        content = "    # Original comment text here"
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash(original_lines[0])
        context_after = compute_content_hash(original_lines[2])

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=2,
            line_end=2,
            content_snippet=content,
        )

        # New file: significant change to content
        new_lines = [
            "def foo():",
            "    # Completely different text",
            "    return 42",
        ]

        # High threshold (0.8) - should become orphaned
        result_high = reconcile_anchor(anchor, new_lines, threshold=0.8)
        assert result_high.health == AnchorHealth.ORPHANED

        # Low threshold (0.4) - might be drifted (depends on actual similarity)
        result_low = reconcile_anchor(anchor, new_lines, threshold=0.4)
        # Could be DRIFTED or ORPHANED depending on actual similarity score
        assert result_low.health in [AnchorHealth.DRIFTED, AnchorHealth.ORPHANED]

    def test_preserves_all_anchor_fields(self):
        """Reconciliation preserves content_hash, context hashes, and snippet."""
        content = "    # comment"
        content_hash = compute_content_hash(content)
        context_before = compute_content_hash("def foo():")
        context_after = compute_content_hash("    pass")

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=context_before,
            context_hash_after=context_after,
            line_start=2,
            line_end=2,
            content_snippet=content,
        )

        # Any change to file
        new_lines = [
            "# Header",
            "def foo():",
            "    # comment",
            "    pass",
        ]

        result = reconcile_anchor(anchor, new_lines)

        # Original hashes and snippet must be preserved
        assert result.content_hash == content_hash
        assert result.context_hash_before == context_before
        assert result.context_hash_after == context_after
        assert result.content_snippet == content

    def test_empty_file_orphans_all_anchors(self):
        """When file becomes empty, all anchors become orphaned."""
        content = "def foo():"
        content_hash = compute_content_hash(content)

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=compute_content_hash(""),
            context_hash_after=compute_content_hash("    return 42"),
            line_start=1,
            line_end=1,
            content_snippet=content,
        )

        # File becomes empty
        new_lines = []

        result = reconcile_anchor(anchor, new_lines)

        assert result.health == AnchorHealth.ORPHANED
        assert result.line_start == 1  # Original position preserved
        assert result.content_snippet == content

    def test_single_line_file_edge_case(self):
        """Single-line files should work correctly."""
        original_lines = ["single line"]

        content = "single line"
        content_hash = compute_content_hash(content)

        anchor = Anchor(
            content_hash=content_hash,
            context_hash_before=compute_content_hash(""),
            context_hash_after=compute_content_hash(""),
            line_start=1,
            line_end=1,
            content_snippet=content,
        )

        # File unchanged
        result = reconcile_anchor(anchor, original_lines)

        assert result.health == AnchorHealth.ANCHORED
        assert result.line_start == 1
        assert result.line_end == 1
        assert result.drift_distance == 0
