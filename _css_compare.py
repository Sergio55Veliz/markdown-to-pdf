from pathlib import Path
import re

h1 = Path("scripts/pdf_generator/propuesta_nuevas_features.html").read_text("utf-8")
h2 = Path("scripts/pdf_generator/dashboard_riesgo_juridico.html").read_text("utf-8")

css1 = re.search(r"<style>(.*?)</style>", h1, re.DOTALL)
css2 = re.search(r"<style>(.*?)</style>", h2, re.DOTALL)

if css1 and css2:
    if css1.group(1) == css2.group(1):
        print("CSS IS IDENTICAL in both HTMLs")
    else:
        lines1 = css1.group(1).splitlines()
        lines2 = css2.group(1).splitlines()
        for i, (a, b) in enumerate(zip(lines1, lines2)):
            if a != b:
                print(f"First diff at line {i}:")
                print(f"  propuesta: {repr(a[:100])}")
                print(f"  dashboard: {repr(b[:100])}")
                break
        print(f"propuesta CSS lines: {len(lines1)}, dashboard CSS lines: {len(lines2)}")
else:
    print("Could not find style block")

# Also count headings in each document
for label, html in [("propuesta", h1), ("dashboard", h2)]:
    counts = {}
    for tag in re.findall(r"<h([1-6])[^>]*>", html):
        n = int(tag)
        counts[n] = counts.get(n, 0) + 1
    print(f"\n{label} heading counts:", counts)
