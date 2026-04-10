from pathlib import Path
import re

content = Path("dashboard_riesgo_juridico.md").read_text("utf-8-sig")
print("Total chars:", len(content))

# Find any inline HTML with style attributes
html_tags = re.findall(r"<[^>]+style=[^>]+>", content)
print("Inline style tags found:", len(html_tags))
for t in html_tags[:10]:
    print(" ", repr(t[:120]))

# Find font-size or size references
size_refs = re.findall(r".{30}font-size.{30}|.{30}font:.{30}", content, re.IGNORECASE)
print("font-size refs:", len(size_refs))
for s in size_refs[:5]:
    print(" ", repr(s))

# Count heading distribution
for h in ["# ", "## ", "### ", "#### ", "##### ", "###### "]:
    n = sum(1 for line in content.splitlines() if line.startswith(h))
    print(f"  {len(h.strip())*'#'}: {n}")

# Check first 500 chars
print("\nFirst 500 chars:\n", repr(content[:500]))
