"""
File selector — open a GUI file dialog or fall back to console input.

Attempts to use ``tkinter.filedialog`` (bundled with most Python installs)
to present a native file picker filtered to Markdown files.  If tkinter
is unavailable or the dialog does not work (e.g. headless server), the
user is prompted to paste the full absolute path in the terminal.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _validate_markdown(path: Path) -> Path:
    """Raise *ValueError* if *path* is not an existing Markdown file."""
    if not path.exists():
        raise ValueError(f"El archivo no existe: {path}")
    if not path.is_file():
        raise ValueError(f"La ruta no es un archivo: {path}")
    if path.suffix.lower() not in (".md", ".markdown", ".mdown", ".mkd"):
        raise ValueError(
            f"El archivo no es Markdown (extensión '{path.suffix}'): {path}"
        )
    return path


def _ask_console() -> Path:
    """Prompt the user to enter the absolute path via stdin."""
    print("\nNo se pudo abrir el explorador de archivos.")
    print("Ingrese la ruta absoluta del archivo Markdown:")
    raw = input("  > ").strip().strip('"').strip("'")
    if not raw:
        print("No se proporcionó ninguna ruta. Saliendo.")
        sys.exit(1)
    return _validate_markdown(Path(raw))


def select_markdown_file() -> Path:
    """Open a file-picker dialog for ``.md`` files, with console fallback.

    Returns the validated ``Path`` to the selected Markdown file.
    """
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        filepath = filedialog.askopenfilename(
            title="Seleccione un archivo Markdown",
            filetypes=[
                ("Archivos Markdown", "*.md *.markdown *.mdown *.mkd"),
                ("Todos los archivos", "*.*"),
            ],
        )
        root.destroy()

        if not filepath:
            print("No se seleccionó ningún archivo. Saliendo.")
            sys.exit(1)

        return _validate_markdown(Path(filepath))

    except Exception:
        return _ask_console()
