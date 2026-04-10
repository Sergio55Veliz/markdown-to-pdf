"""
Shared Markdown preprocessing functions.

These transformations are applied to raw Markdown text before passing it
to the markdown-it parser.  Both the PDF and Word pipelines use them.
"""

from __future__ import annotations

import re


def fix_blockquote_continuation_lists(text: str) -> str:
    """Re-indent list items following a blockquote into the blockquote.

    Some blockquotes end with a colon and their list items are written on
    the following lines with 8-space indentation but without a ``>``
    prefix.  CommonMark does not consider those continuation lines part of
    the blockquote, so this function rewrites them as proper blockquote
    list items.
    """
    lines = text.split("\n")
    result: list[str] = []
    after_blockquote = False

    for line in lines:
        if line.startswith(">"):
            after_blockquote = True
            result.append(line)
        elif after_blockquote and line.strip():
            stripped = line.strip()
            leading = len(line) - len(line.lstrip())
            is_list = bool(re.match(r"^\d+\.\s+", stripped)) or bool(
                re.match(r"^[-*+]\s+", stripped)
            )
            if leading >= 4 and is_list:
                result.append("> " + stripped)
            else:
                after_blockquote = False
                result.append(line)
        else:
            if line.strip():
                after_blockquote = False
            result.append(line)

    return "\n".join(result)


def preprocess_strikethrough(text: str) -> str:
    """Convert ``~~text~~`` Markdown strikethrough to ``<del>text</del>``."""
    return re.sub(
        r"~~(.+?)~~",
        lambda m: f"<del>{m.group(1)}</del>",
        text,
        flags=re.DOTALL,
    )


def preprocess_markdown(text: str) -> str:
    """Apply all shared Markdown preprocessing steps."""
    text = fix_blockquote_continuation_lists(text)
    text = preprocess_strikethrough(text)
    return text
