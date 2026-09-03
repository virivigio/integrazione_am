import json
from app.database import execute_query

BRAND_IDS = {
    "BESTE": 66,
    "MABI": 62,
    "GENTILI-MOSCONI": 60,
}

# Non paginiamo: prendiamo un risultato in più del massimo mostrato per capire
# se ce ne sono altri oltre quelli restituiti, senza dover fare COUNT(*) a parte.
MAX_RESULTS = 20
_FETCH_LIMIT = MAX_RESULTS + 1

TRUNCATED_MESSAGE = (
    f"Ci sono altri risultati oltre ai {MAX_RESULTS} mostrati: il sistema è "
    "limitato a un massimo di 20 righe per richiesta. Prova a fare una domanda "
    "più selettiva."
)


def _limit_results(rows: list) -> tuple[list, bool]:
    truncated = len(rows) > MAX_RESULTS
    return rows[:MAX_RESULTS], truncated


def find_order(brand: str, po_number: str) -> str:
    brand_id = BRAND_IDS.get(brand.upper())
    if brand_id is None:
        return json.dumps({"error": f"Brand '{brand}' non riconosciuto. Usa: BESTE, MABI, GENTILI-MOSCONI"})

    rows = execute_query(
        """
        SELECT RolCodEst, RolIdBrand, RolRivoor, RolRiferimento, RolChiuso, RolDelete,
               RolSeason, RolTotord, varian_type_id, modified_at, updated_at
        FROM ordcli_open
        WHERE RolIdBrand = %s
          AND RolRivoor = %s
          AND RolRiferimento = '0'
        LIMIT %s
        """,
        (brand_id, po_number, _FETCH_LIMIT),
    )

    if not rows:
        return json.dumps({
            "found": False,
            "message": f"Nessun ordine trovato per brand={brand}, PO={po_number}",
        })

    rows, truncated = _limit_results(rows)
    result = {"found": True, "count": len(rows), "orders": rows}
    if truncated:
        result["truncated"] = True
        result["truncated_message"] = TRUNCATED_MESSAGE
    return json.dumps(result)


def get_order_lines(rol_cod_est: str) -> str:
    rows = execute_query(
        """
        SELECT r.RoaCodEst, r.RoaNumrig, r.RolIdBrand, r.RoaQuanti, r.RoaPrezzo, r.RoaUnimis,
               r.RoaChiuso, r.RoaDelete, r.confirmed_id_rif, r.confirmed_row_rif,
               r.supplier_article, r.supplier_color, r.updated_at,
               c.RoaStarig
        FROM riorcl_open r
        LEFT JOIN c_riorcl c
          ON c.RoaCodEst = r.confirmed_id_rif
         AND c.RoaNumrig = r.confirmed_row_rif
        WHERE r.RoaCodEst = %s
        ORDER BY r.RoaNumrig
        LIMIT %s
        """,
        (rol_cod_est, _FETCH_LIMIT),
    )

    if not rows:
        return json.dumps({
            "found": False,
            "message": f"Nessuna riga trovata per ordine {rol_cod_est}",
        })

    rows, truncated = _limit_results(rows)
    result = {
        "rol_cod_est": rol_cod_est,
        "total_lines": len(rows),
        "lines": rows,
    }
    if truncated:
        result["truncated"] = True
        result["truncated_message"] = TRUNCATED_MESSAGE
    return json.dumps(result)


TOOL_FUNCTIONS = {
    "find_order": lambda args: find_order(**args),
    "get_order_lines": lambda args: get_order_lines(**args),
}


def execute_tool(name: str, arguments: dict) -> str:
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return json.dumps({"error": f"Tool '{name}' non esistente"})
    try:
        return fn(arguments)
    except Exception as e:
        return json.dumps({"error": str(e)})
