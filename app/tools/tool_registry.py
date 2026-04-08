TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_order",
            "description": (
                "Cerca un ordine nel sistema per nome brand e PO number del cliente. "
                "Restituisce i dati della testata ordine inclusi i flag RolChiuso (S=chiuso, N=aperto) "
                "e RolDelete (S=eliminato, N=attivo), e il RolCodEst (ID interno) "
                "da usare per recuperare le righe con get_order_lines."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "brand": {
                        "type": "string",
                        "enum": ["BESTE", "MABI", "GENTILI-MOSCONI"],
                        "description": "Nome del brand/cliente",
                    },
                    "po_number": {
                        "type": "string",
                        "description": "PO number del cliente (es. V2400438, F2400438)",
                    },
                },
                "required": ["brand", "po_number"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_lines",
            "description": (
                "Recupera tutte le righe di un ordine dato il suo ID interno (RolCodEst). "
                "Ogni riga include: numero riga, quantità, prezzo, unità di misura, "
                "flag chiusura/cancellazione, riferimento all'eventuale approvazione "
                "(confirmed_id_rif / confirmed_row_rif), articolo e colore fornitore."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "rol_cod_est": {
                        "type": "string",
                        "description": "ID interno dell'ordine (RolCodEst), ottenuto da find_order",
                    },
                },
                "required": ["rol_cod_est"],
            },
        },
    },
]
