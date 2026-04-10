"""
1. Parse the JSON block from _find_word_docs_output.txt
2. Remove any path whose filename starts with '~$'
3. If a list becomes empty after cleaning, set it to None
4. Create folder structure under all_in_fs/{schema}/{table}/
5. Copy files (handle name collisions with _2, _3 suffixes)
"""
import json, os, re, shutil, sys

OUTPUT_FILE = r"c:\Users\sveliza\Documents\bb_repos\feature-store-bb\_find_word_docs_output.txt"
DEST_ROOT   = r"C:\Users\sveliza\OneDrive - Banco Bolivariano C.A\Documentaciones\all_in_fs"
LOG_FILE    = r"c:\Users\sveliza\Documents\bb_repos\feature-store-bb\_copy_docs_log.txt"

# Tee output to both stdout and log file
_log = open(LOG_FILE, "w", encoding="utf-8")
class Tee:
    def write(self, msg):
        sys.__stdout__.write(msg)
        _log.write(msg)
        _log.flush()
    def flush(self):
        sys.__stdout__.flush()
        _log.flush()
sys.stdout = Tee()

print(f"Python {sys.version}")
print(f"DEST_ROOT: {DEST_ROOT}")
print(f"DEST_ROOT exists: {os.path.exists(DEST_ROOT)}")
parent = os.path.dirname(DEST_ROOT)
print(f"Parent ({parent}) exists: {os.path.exists(parent)}")

# ---------------------------------------------------------------------------
# 1. Read the JSON block from the output file
# ---------------------------------------------------------------------------
with open(OUTPUT_FILE, encoding="utf-8") as f:
    content = f.read()

# The JSON block starts after the "JSON" header line
json_start = content.index("\n{")
raw_json = content[json_start:].strip()
data = json.loads(raw_json)

# ---------------------------------------------------------------------------
# 2. Clean: remove paths whose filename starts with '~$'
# ---------------------------------------------------------------------------
def is_temp(path: str) -> bool:
    return os.path.basename(path).startswith("~$")

cleaned = {}
for key, value in data.items():
    if value is None:
        cleaned[key] = None
    elif isinstance(value, str):
        cleaned[key] = None if is_temp(value) else value
    else:  # list
        filtered = [p for p in value if not is_temp(p)]
        cleaned[key] = filtered if filtered else None

# Print summary of removed temps
removed = sum(
    1 for k, v in data.items()
    for p in ([v] if isinstance(v, str) else (v or []))
    if is_temp(p)
)
print(f"Removed {removed} temporary (~$) file entries.")

# ---------------------------------------------------------------------------
# 3. Copy files into all_in_fs/{schema}/{table}/
# ---------------------------------------------------------------------------
total_copied = 0
total_skipped = 0
errors = []

for source_table, paths in cleaned.items():
    if not paths:
        continue

    # Parse schema and table name
    parts = source_table.split(".", 1)
    schema = parts[0]          # e.g. silver_dwbolivariano
    table  = parts[1]          # e.g. dw_fecha

    dest_dir = os.path.join(DEST_ROOT, schema, table)
    os.makedirs(dest_dir, exist_ok=True)

    file_list = [paths] if isinstance(paths, str) else paths

    for src_path in file_list:
        fname = os.path.basename(src_path)
        dest_path = os.path.join(dest_dir, fname)

        # Handle name collisions
        if os.path.exists(dest_path):
            base, ext = os.path.splitext(fname)
            counter = 2
            while os.path.exists(dest_path):
                dest_path = os.path.join(dest_dir, f"{base}_{counter}{ext}")
                counter += 1

        try:
            shutil.copy2(src_path, dest_path)
            print(f"  ✓  {source_table}  ←  {fname}")
            total_copied += 1
        except Exception as e:
            msg = f"  ✗  {source_table}  ←  {src_path}  |  {e}"
            print(msg)
            errors.append(msg)
            total_skipped += 1

# ---------------------------------------------------------------------------
# 4. Save cleaned JSON
# ---------------------------------------------------------------------------
json_out = r"c:\Users\sveliza\Documents\bb_repos\feature-store-bb\_word_docs_clean.json"
with open(json_out, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2, ensure_ascii=False)

print(f"\nDone. Copied: {total_copied}  |  Errors: {total_skipped}")
print(f"Clean JSON saved to {json_out}")
if errors:
    print("\nErrors:")
    for e in errors:
        print(e)
