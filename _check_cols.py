from pathlib import Path
from bs4 import BeautifulSoup

html = Path("scripts/pdf_generator/propuesta_nuevas_features.html").read_text("utf-8")
soup = BeautifulSoup(html, "lxml")

for i, tbl in enumerate(soup.find_all("table")):
    cg = tbl.find("colgroup")
    first_row = tbl.find("tr")
    headers = [th.get_text(strip=True)[:20] for th in first_row.find_all(["th", "td"])] if first_row else []
    first_col_vals = [
        row.find_all(["th", "td"])[0].get_text(strip=True)
        for row in tbl.find_all("tr")
        if row.find_all(["th", "td"])
    ]
    max_len = max(len(v) for v in first_col_vals) if first_col_vals else 0
    col_style = cg.find("col")["style"] if cg and cg.find("col") else "no colgroup"
    print(f"Table {i+1}: hdrs={headers[:3]} | first_col_max_len={max_len} | assigned={col_style}")
