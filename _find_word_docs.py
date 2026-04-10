"""
For each distinct source table in the consolidated JSON (excluding saiku tables),
derive a search name, then search for Word files in \\fsbb2k22srv\Administracion
using substring match and Levenshtein distance.
"""
import os, re, json

# ---------------------------------------------------------------------------
# Consolidated JSON (current state)
# ---------------------------------------------------------------------------
consolidated = {
    "fs_acc_checking_account": [
        "silver_dwbolivariano.dw_oper_pasivos_ctacte",
        "silver_dwbolivariano.dw_fecha",
        "silver_dwbolivariano.dw_estado_operacion"
    ],
    "fs_acc_credit_card_consumption": [
        "silver_dwtdcbb.dw_fact_tc_facturacion",
        "silver_dwtdcbb.dw_dim_tarjeta_propia_hist",
        "silver_dwtdcbb.dw_dim_cliente_hist",
        "silver_dwtdcbb.dw_dim_tipo_transaccion",
        "silver_dwtdcbb.dw_dim_cat2_comercio"
    ],
    "fs_acc_portfolio": [
        "silver_dwtdcbb.dw_fact_tc_cartera",
        "silver_dwtdcbb.dw_dim_calificacion_bb",
        "silver_dwtdcbb.dw_dim_cliente_hist",
        "silver_dwtdcbb.dw_dim_tarjeta_propia_hist"
    ],
    "fs_acc_savings_account": [
        "silver_dwbolivariano.dw_oper_pasivos_ctaah",
        "silver_dwbolivariano.dw_fecha",
        "silver_dwbolivariano.dw_estado_operacion"
    ],
    "fs_cus_beneficiary_sat": [
        "silver_dwbolivariano.dw_detalle_sat_his",
        "silver_dwbolivariano.dw_empresas_sat_dim",
        "silver_dwbolivariano.dw_productos_servicios_sat",
        "silver_dwbolivariano.dw_beneficiarios_sat"
    ],
    "fs_cus_certificate_deposit": [
        "silver_dwbolivariano.dw_oper_pasivos_cdp"
    ],
    "fs_cus_channel_usage": [
        "silver_dwbolivariano.dwh_h_anl_resu_canal_trx"
    ],
    "fs_cus_check": [
        "silver_dwbolivariano.dwh_h_anl_resu_canal_trx"
    ],
    "fs_cus_checking_account": [
        "silver_dwbolivariano.dw_oper_pasivos_ctacte",
        "silver_dwbolivariano.dw_fecha",
        "silver_dwbolivariano.dw_estado_operacion"
    ],
    "fs_cus_company_inter_transfers_sat": [
        "silver_dwbolivariano.dw_detalle_sat_his",
        "silver_dwbolivariano.dw_empresas_sat_dim",
        "silver_dwbolivariano.dw_productos_servicios_sat",
        "silver_dwbolivariano.dw_beneficiarios_sat"
    ],
    "fs_cus_company_provider_sat": [
        "silver_dwbolivariano.dw_detalle_sat_his",
        "silver_dwbolivariano.dw_empresas_sat_dim",
        "silver_dwbolivariano.dw_productos_servicios_sat",
        "silver_dwbolivariano.dw_beneficiarios_sat"
    ],
    "fs_cus_company_roll_sat": [
        "silver_dwbolivariano.dw_detalle_sat_his",
        "silver_dwbolivariano.dw_empresas_sat_dim",
        "silver_dwbolivariano.dw_productos_servicios_sat",
        "silver_dwbolivariano.dw_beneficiarios_sat",
        "silver_dwbolivariano.dw_ente_his"
    ],
    "fs_cus_company_sat": [
        "silver_dwbolivariano.dw_detalle_sat_his",
        "silver_dwbolivariano.dw_empresas_sat_dim",
        "silver_dwbolivariano.dw_productos_servicios_sat",
        "silver_dwbolivariano.dw_beneficiarios_sat"
    ],
    "fs_cus_complaints": [
        "silver_dwbolivariano.dwh_h_reclamos",
        "silver_dwbolivariano.dwh_d_ente_reclamos",
        "silver_dwbolivariano.dwh_d_estado_reclamo"
    ],
    "fs_cus_credit_card_consumption": [
        "silver_dwtdcbb.dw_fact_tc_facturacion",
        "silver_dwtdcbb.dw_dim_cat2_comercio",
        "silver_dwtdcbb.dw_dim_tarjeta_propia_hist",
        "silver_dwtdcbb.dw_dim_cliente_hist"
    ],
    "fs_cus_credit_portfolio": [
        "silver_dwbolivariano.dw_riesgo_semanal",
        "silver_dwbolivariano.dw_tipo_operacion",
        "silver_dwbolivariano.dwh_h_oper_activa_conced",
        "silver_dwbolivariano.dw_tipo_credito"
    ],
    "fs_cus_credit_risk": [
        "silver_dwbolivariano.dw_ente_central_riesgo",
        "silver_dwbolivariano.dw_tipo_credito",
        "silver_dwbolivariano.dw_central_riesgo_historico"
    ],
    "fs_cus_credit_risk_holder": [
        "silver_dwbolivariano.dw_ente_central_riesgo",
        "silver_dwbolivariano.dw_tipo_credito",
        "silver_dwbolivariano.dw_central_riesgo_historico"
    ],
    "fs_cus_debit_card": [
        "silver_dwbolivariano.dwh_h_visa_deb_autoriza_his",
        "silver_dwtdcbb.dw_dim_comercio_hist",
        "silver_dwtdcbb.dw_fact_tc_facturacion"
    ],
    "fs_cus_demographic": [
        "silver_dwbolivariano.dwh_r_fastbi_inf_clie",
        "silver_dwbolivariano.dw_segmentos",
        "silver_dwexternas.dw_sdc_empresa",
        "silver_dwexternas.dwe_e_estad_financ_emp",
        "silver_odsdb.cl_catalogo",
        "silver_dwbolivariano.dw_accionista_anterior",
        "silver_dwbolivariano.dw_accionista_actual",
        "silver_dwbolivariano.dw_administrador_anterior",
        "silver_dwbolivariano.dw_administrador_actual",
        "silver_dwexternas.dwe_importaciones_detalle",
        "silver_dwexternas.dwe_exportaciones_detalle",
        "silver_dwbolivariano.dw_riesgo_semanal",
        "silver_dwbolivariano.dwh_h_oper_activa_conced",
        "silver_dwbolivariano.dw_tipo_operacion",
        "saiku_ciiu_dim_seccion",
        "saiku_ciiu_dim_division",
        "saiku_ciiu_dim_grupo"
    ],
    "fs_cus_deposit": [
        "silver_dwbolivariano.dwh_h_anl_resu_canal_trx"
    ],
    "fs_cus_deposit_liabilities": [
        "silver_dwbolivariano.dw_oper_pasivos_ctaah",
        "silver_dwbolivariano.dw_oper_pasivos_ctacte",
        "silver_dwbolivariano.dw_fecha",
        "silver_dwbolivariano.dw_estado_operacion"
    ],
    "fs_cus_exports": [
        "silver_dwexternas.dwe_exportaciones_detalle"
    ],
    "fs_cus_ext_credit_risk": [
        "silver_dwexternas.dwh_e_central_riesgo"
    ],
    "fs_cus_financial_statement": [
        "silver_dwexternas.dwe_e_estad_financ_emp"
    ],
    "fs_cus_holding_products": [
        "silver_dwbolivariano.dw_agrupacion_productos_ivc",
        "silver_dwbolivariano.dw_clientes_productos"
    ],
    "fs_cus_imports": [
        "silver_dwexternas.dwe_importaciones_detalle"
    ],
    "fs_cus_ivc": [
        "silver_dwbolivariano.dw_ejercicio_ivc_hist"
    ],
    "fs_cus_jupiter": [
        "silver_dwexternas.dwe_e_jupiter"
    ],
    "fs_cus_payment": [
        "silver_dwbolivariano.dwh_t_canal_24online_n",
        "silver_dwbolivariano.dwh_t_canal_24movil_n_his",
        "silver_dwbolivariano.dw_trn_canal_homologado",
        "silver_dwbolivariano.dw_trn_homologado",
        "silver_dwbolivariano.dwh_r_fastbi_inf_clie",
        "silver_dwbolivariano.dwh_h_anl_resu_canal_trx"
    ],
    "fs_cus_portfolio": [
        "silver_dwtdcbb.dw_fact_tc_cartera",
        "silver_dwtdcbb.dw_dim_calificacion_bb",
        "silver_dwtdcbb.dw_dim_cliente_hist"
    ],
    "fs_cus_resul_campaign_credimax": [
        "silver_dwbolivariano.dwh_h_resul_camp_credimax"
    ],
    "fs_cus_sac_procedure": [
        "silver_odsdb.dlh_h_sac_deudor",
        "silver_odsdb.dlh_h_sac_gestion"
    ],
    "fs_cus_savings_account": [
        "silver_dwbolivariano.dw_oper_pasivos_ctaah",
        "silver_dwbolivariano.dw_fecha",
        "silver_dwbolivariano.dw_estado_operacion"
    ],
    "fs_cus_transfer": [
        "silver_dwbolivariano.dwh_h_anl_transferencias",
        "silver_dwbolivariano.dwh_r_fastbi_inf_clie"
    ],
    "fs_cus_withdrawal": [
        "silver_dwbolivariano.dwh_h_anl_resu_canal_trx"
    ],
    "fs_op_credit_portfolio": [
        "silver_dwbolivariano.dw_riesgo_semanal",
        "silver_dwbolivariano.dwh_h_oper_activa_conced",
        "silver_dwbolivariano.dw_tipo_credito",
        "silver_dwbolivariano.dw_tipo_operacion"
    ],
    "fs_op_credit_portfolio_payment": [
        "silver_dwbolivariano.dw_recuperacion_cartera",
        "silver_dwbolivariano.dw_fecha",
        "silver_dwbolivariano.dw_tipo_credito",
        "silver_dwbolivariano.dw_tipo_operacion"
    ]
}

# ---------------------------------------------------------------------------
# 1. Distinct source tables (no saiku)
# ---------------------------------------------------------------------------
all_source_tables = sorted({
    t
    for tables in consolidated.values()
    for t in tables
    if not t.startswith("saiku_")
})

# ---------------------------------------------------------------------------
# 2. Derive search name per table (strip prefix from table part)
# ---------------------------------------------------------------------------
PREFIXES = [
    "dwe_e_", "dwh_h_", "dwh_r_", "dwh_t_", "dlh_h_",  # longer first
    "dwe_", "dwh_", "dw_", "dlh_",
]

def get_search_name(source_table: str) -> str:
    table_part = source_table.split(".")[-1]   # e.g. "dwh_h_reclamos"
    for prefix in PREFIXES:
        if table_part.startswith(prefix):
            return table_part[len(prefix):]    # e.g. "reclamos"
    return table_part

# ---------------------------------------------------------------------------
# 3. Levenshtein distance
# ---------------------------------------------------------------------------
def levenshtein(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s2:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]

# ---------------------------------------------------------------------------
# 4. Walk the network share and collect all Word files
# ---------------------------------------------------------------------------
SEARCH_ROOT = r"\\fsbb2k22srv\Administracion"
WORD_EXTS   = {".doc", ".docx"}

MAX_LEVENSHTEIN = 3   # max allowed distance for fuzzy match
MIN_SEARCH_LEN  = 5   # don't fuzzy-match very short names (too many false positives)

OUTPUT_FILE = r"c:\Users\sveliza\Documents\bb_repos\feature-store-bb\_find_word_docs_output.txt"

import sys

# Write directly to file so no stdout redirection needed
out = open(OUTPUT_FILE, "w", encoding="utf-8")

def log(msg=""):
    print(msg)
    out.write(msg + "\n")
    out.flush()

log(f"Scanning Word files under {SEARCH_ROOT} ...")
word_files = []   # list of (filename_no_ext_lower, full_path)
errors = []

for root, dirs, files in os.walk(SEARCH_ROOT):
    # Skip hidden / system folders
    dirs[:] = [d for d in dirs if not d.startswith('$') and not d.startswith('.')]
    for fname in files:
        ext = os.path.splitext(fname)[1].lower()
        if ext in WORD_EXTS:
            name_no_ext = os.path.splitext(fname)[0].lower()
            full_path = os.path.join(root, fname)
            word_files.append((name_no_ext, full_path))

log(f"Found {len(word_files)} Word files.\n")

# ---------------------------------------------------------------------------
# 5. Match each source table to Word file(s)
# ---------------------------------------------------------------------------
result = {}

for source_table in all_source_tables:
    search_name = get_search_name(source_table).lower()
    matches = []

    for name_no_ext, full_path in word_files:
        # Substring match
        if search_name in name_no_ext:
            matches.append(full_path)
            continue
        # Fuzzy: only for names long enough, compare against the full filename
        if len(search_name) >= MIN_SEARCH_LEN:
            dist = levenshtein(search_name, name_no_ext)
            if dist <= MAX_LEVENSHTEIN:
                matches.append(full_path)

    if not matches:
        result[source_table] = None
    elif len(matches) == 1:
        result[source_table] = matches[0]
    else:
        result[source_table] = sorted(set(matches))
log("=" * 80)
log("SOURCE TABLE → WORD DOCUMENT(S)")
log("=" * 80)

found     = {k: v for k, v in result.items() if v is not None}
not_found = {k: v for k, v in result.items() if v is None}

log(f"\n✓ Found ({len(found)}):")
for st, paths in found.items():
    search_name = get_search_name(st)
    if isinstance(paths, list):
        log(f"\n  {st}  [search: '{search_name}']")
        for p in paths:
            log(f"    → {p}")
    else:
        log(f"  {st}  [search: '{search_name}']")
        log(f"    → {paths}")

log(f"\n✗ Not found ({len(not_found)}):")
for st in not_found:
    log(f"  {st}  [search: '{get_search_name(st)}']")

log("\n" + "=" * 80)
log("JSON OUTPUT")
log("=" * 80)
log(json.dumps(result, indent=4, ensure_ascii=False))
out.close()
