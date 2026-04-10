import os
import re

folder = r'c:\Users\sveliza\Documents\bb_repos\feature-store-bb\notebooks\production\FEATURE_STORE'
files = sorted([f for f in os.listdir(folder) if f.endswith('.py')])

for fname in files:
    path = os.path.join(folder, fname)
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Find source_tables dict definitions (handle nested dicts with multiple levels)
    # Use a more robust approach: find the full dict by tracking braces
    source_tables_raw = []
    for m in re.finditer(r'source_tables\s*=\s*\{', content):
        start = m.start()
        brace_start = content.index('{', m.start())
        depth = 0
        end = brace_start
        for i in range(brace_start, len(content)):
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i
                    break
        source_tables_raw.append(content[start:end+1])

    # Extract keys from source_tables dicts (keys ARE the table names; values are True/False)
    source_tables_keys = []
    for block in source_tables_raw:
        # Match "db.table": or 'db.table': (keys with dots)
        keys = re.findall(r'["\']([^"\']+)["\']\s*:', block)
        source_tables_keys.extend(keys)

    # Find all SQL strings inside spark.sql("""...""") or spark.sql(f"""...""")
    sql_strings = re.findall(r'spark\.sql\s*\(\s*f?(?:""")(.*?)(?:""")', content, re.DOTALL)
    sql_strings += re.findall(r"spark\.sql\s*\(\s*f?(?:''')(.*?)(?:''')", content, re.DOTALL)

    # Extract FROM/JOIN table references from SQL strings
    sql_table_refs = []
    for sql in sql_strings:
        # Find db.table or catalog.db.table patterns after FROM or JOIN
        refs = re.findall(r'(?:FROM|JOIN)\s+([\w]+\.[\w]+(?:\.[\w]+)?)', sql, re.IGNORECASE)
        sql_table_refs.extend(refs)
        # Also find standalone table-like patterns (word.word) anywhere - but only capture FROM/JOIN

    # Find spark.read.table(), spark.table(), .table() calls  
    table_calls = re.findall(r'(?:spark\.read\.table|spark\.table)\s*\(\s*f?["\']([^"\']+)["\']', content)
    # Also find .table("...") calls
    table_calls += re.findall(r'\.table\s*\(\s*f?["\']([^"\']+)["\']', content)

    # Find all db.table patterns in the whole file (variable context - source_tables[key] values)
    # by looking for quoted strings with dot notation
    all_quoted_table_refs = re.findall(r'["\'](\w+\.\w+(?:\.\w+)?)["\']', content)
    # Filter to only those that look like table references (2 or 3 parts)
    all_quoted_table_refs = [r for r in all_quoted_table_refs if '.' in r and not r.startswith('.') and not r.endswith('.')]

    # source_tables values (right-hand side of key: "value")
    source_tables_values = []
    for block in source_tables_raw:
        vals = re.findall(r':\s*["\']([^"\']+)["\']', block)
        source_tables_values.extend(vals)

    # source_tables values are booleans (True/False); the KEYS are the table references
    # Use source_tables_keys as the set of declared tables
    source_tables_values = source_tables_keys  # alias for clarity below

    # All table refs: from SQL + from .table() calls
    all_sql_table_refs = sorted(set([r.lower() for r in sql_table_refs + table_calls]))

    # Tables in SQL/DataFrame not in source_tables keys
    source_tables_keys_lower = [k.lower() for k in source_tables_keys]
    missing = sorted(set([r for r in all_sql_table_refs if r not in source_tables_keys_lower]))

    print(f"\n{'='*70}")
    print(f"FILE: {fname}")
    print(f"\n  source_tables KEYS (declared tables): {sorted(set(source_tables_keys))}")
    print(f"\n  SQL FROM/JOIN table refs: {sorted(set([r for r in sql_table_refs]))}")
    print(f"  .table() / spark.table() calls: {sorted(set(table_calls))}")
    print(f"\n  ALL SQL/DF table refs (normalized): {all_sql_table_refs}")
    print(f"\n  MISSING from source_tables: {missing}")
    print()
    for i, blk in enumerate(source_tables_raw):
        print(f"  [source_tables block {i+1}]:\n{blk}\n")
