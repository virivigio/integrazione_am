import json
from app.database import execute_query

BRAND_IDS = {
    "BESTE": 66,
    "MABI": 62,
    "GENTILI-MOSCONI": 60,
}


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
        LIMIT 10
        """,
        (brand_id, po_number),
    )

    if not rows:
        return json.dumps({
            "found": False,
            "message": f"Nessun ordine trovato per brand={brand}, PO={po_number}",
        })

    return json.dumps({"found": True, "count": len(rows), "orders": rows})


def get_order_lines(rol_cod_est: str) -> str:
    rows = execute_query(
        """
        SELECT RoaCodEst, RoaNumrig, RolIdBrand, RoaQuanti, RoaPrezzo, RoaUnimis,
               RoaChiuso, RoaDelete, confirmed_id_rif, confirmed_row_rif,
               supplier_article, supplier_color, updated_at
        FROM riorcl_open
        WHERE RoaCodEst = %s
        ORDER BY RoaNumrig
        LIMIT 200
        """,
        (rol_cod_est,),
    )

    if not rows:
        return json.dumps({
            "found": False,
            "message": f"Nessuna riga trovata per ordine {rol_cod_est}",
        })

    return json.dumps({
        "rol_cod_est": rol_cod_est,
        "total_lines": len(rows),
        "lines": rows,
    })


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
