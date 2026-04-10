"""Tests for markdown_to_pdf.constants — sanity checks on style values."""

from markdown_to_pdf.constants import (
    rgb_hex,
    rgb_hex_upper,
    rgb_docx,
    HEADING_COLORS,
    HEADING_SIZE,
    HEADING_BOLD,
    HEADING_SPACE_BEFORE,
    HEADING_SPACE_AFTER,
    COLOR_BODY,
    CIRCLE_EMOJI,
    EMOJI_COLOR,
    EMOJI_RE,
    FONT_FILES,
    FONT_SPECS,
)


class TestColorHelpers:
    def test_rgb_hex(self):
        assert rgb_hex((0xFF, 0x00, 0x80)) == "#ff0080"

    def test_rgb_hex_upper(self):
        assert rgb_hex_upper((0x1E, 0x40, 0xAF)) == "1E40AF"

    def test_rgb_docx(self):
        c = rgb_docx((0x1E, 0x40, 0xAF))
        assert str(c) == "1E40AF"


class TestHeadingMaps:
    def test_all_levels_defined(self):
        for level in range(1, 7):
            assert level in HEADING_COLORS
            assert level in HEADING_SIZE
            assert level in HEADING_BOLD
            assert level in HEADING_SPACE_BEFORE
            assert level in HEADING_SPACE_AFTER

    def test_h1_is_largest(self):
        assert HEADING_SIZE[1] > HEADING_SIZE[2]


class TestEmoji:
    def test_circle_emoji_keys_exist(self):
        assert len(CIRCLE_EMOJI) > 0

    def test_emoji_regex_matches_known(self):
        for em in list(CIRCLE_EMOJI.keys())[:3]:
            assert EMOJI_RE.search(em)


class TestFontSpecs:
    def test_font_files_match_specs(self):
        assert len(FONT_FILES) == len(FONT_SPECS)
