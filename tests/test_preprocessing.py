"""Tests for markdown_to_pdf.preprocessing."""

from markdown_to_pdf.preprocessing import (
    fix_blockquote_continuation_lists,
    preprocess_strikethrough,
    preprocess_markdown,
)


class TestBlockquoteContinuationLists:
    """Ensure ``>`` is prepended to bare continuation list items."""

    def test_bare_dash_needs_indent(self):
        """Items need 4+ spaces indent to be captured into the blockquote."""
        text = "> Title\n    - item 1\n    - item 2\n"
        result = fix_blockquote_continuation_lists(text)
        assert "> - item 1" in result
        assert "> - item 2" in result

    def test_bare_dash_no_indent_unchanged(self):
        """Unindented items are NOT captured (< 4 spaces)."""
        text = "> Title\n- item 1\n"
        result = fix_blockquote_continuation_lists(text)
        assert result == text

    def test_bare_ordered_after_blockquote(self):
        text = "> Title\n    1. first\n    2. second\n"
        result = fix_blockquote_continuation_lists(text)
        assert "> 1. first" in result
        assert "> 2. second" in result

    def test_already_prefixed_lines_unchanged(self):
        text = "> Title\n> - item 1\n> - item 2\n"
        result = fix_blockquote_continuation_lists(text)
        # Should not double-prefix
        assert "> > - item 1" not in result

    def test_no_blockquote_context(self):
        text = "Normal paragraph\n- item\n"
        result = fix_blockquote_continuation_lists(text)
        assert result == text  # nothing changes


class TestStrikethrough:
    def test_double_tilde_converted(self):
        result = preprocess_strikethrough("Hello ~~world~~!")
        assert "<del>world</del>" in result

    def test_no_tilde_unchanged(self):
        text = "Nothing to strike."
        assert preprocess_strikethrough(text) == text


class TestPreprocessMarkdown:
    def test_applies_both_transforms(self):
        text = "> Title\n    - item\n\n~~deleted~~"
        result = preprocess_markdown(text)
        assert "> - item" in result
        assert "<del>deleted</del>" in result
