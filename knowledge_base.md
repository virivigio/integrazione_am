# Knowledge Base — Dominio Ordini

Questo file documenta le regole di business, lo schema dati e le convenzioni
del sistema ordini, usate dall'agente AI come contesto per rispondere correttamente.

---

## Brand supportati

| Nome | RolIdBrand |
|------|-----------|
| BESTE | 66 |
| MABI | 62 |
| GENTILI-MOSCONI | 60 |

---

## Schema database

**Database:** `theidfactory_ordini`

### Tabella `ordcli_open` — Testate ordini

| Colonna | Tipo | Significato |
|---------|------|-------------|
| `RolCodEst` | varchar(25) PK | ID interno ordine (generato dal sistema) |
| `RolIdBrand` | int | Brand ID (vedi tabella sopra) |
| `RolRivoor` | varchar(40) | **PO number del cliente** — usare per la ricerca |
| `RolRiferimento` | varchar(25) | `'0'` = ordine aperto/non approvato; altrimenti = `RolCodEst` dell'ordine aperto da cui deriva (vedi ciclo di approvazione) |
| `RolChiuso` | char(1) | `'S'` = chiuso, `'N'` = aperto |
| `RolDelete` | char(1) | `'S'` = eliminato/cancellato, `'N'` = attivo |
| `RolSeason` | varchar(6) | Stagione (es. `SS25`, `FW24`) |
| `RolTotord` | float | Importo totale ordine |
| `varian_type_id` | int | Categoria merceologica (es. pellame, tessuto, bottoni) |
| `modified_at` | datetime | Data ultima modifica |
| `updated_at` | datetime | Data aggiornamento |

### Tabella `riorcl_open` — Righe ordine

| Colonna | Tipo | Significato |
|---------|------|-------------|
| `RoaCodEst` | varchar(25) PK | FK → `ordcli_open.RolCodEst` |
| `RoaNumrig` | int PK | Numero riga all'interno dell'ordine |
| `RolIdBrand` | int | Brand ID (ridondante, identico all'header) |
| `RoaQuanti` | float | Quantità ordinata |
| `RoaPrezzo` | float | Prezzo unitario |
| `RoaUnimis` | varchar | Unità di misura |
| `RoaChiuso` | char(1) | `'S'` = riga chiusa, `'N'` = aperta |
| `RoaDelete` | char(1) | `'S'` = riga eliminata, `'N'` = attiva |
| `confirmed_id_rif` | varchar(25) | `RolCodEst` della testata approvata in cui questa riga è stata promossa (NULL se non ancora approvata) |
| `confirmed_row_rif` | int | `RoaNumrig` della riga clonata nella testata approvata (NULL se non ancora approvata) |
| `supplier_article` | varchar(255) | Codice articolo fornitore |
| `supplier_color` | varchar(255) | Colore fornitore |
| `updated_at` | datetime | Data aggiornamento |

---

## Regole di business

### Flag S/N
Tutti i flag booleani usano la convenzione italiana:
- `'S'` = Sì (true / yes)
- `'N'` = No (false / no)

### Stagioni
Il campo `RolSeason` usa codici tipo `SS25` (Spring/Summer 2025), `FW24` (Fall/Winter 2024).

### Ciclo di vita di un ordine: apertura e approvazione

Quando un ordine entra nel sistema viene creata una testata con `RolRiferimento = '0'` e N righe che puntano al suo `RolCodEst`. A questo punto l'ordine e tutte le sue righe sono **aperte** (non ancora approvate).

L'approvazione avviene **per righe, anche parzialmente**, e può avvenire in più tornate:

1. Vengono selezionate alcune righe da approvare.
2. Viene creata una **nuova testata clone** con un nuovo `RolCodEst` (es. `RolCodEstNEW`) e `RolRiferimento = RolCodEst originale`. La testata clone riceve `RolChiuso = 'S'`, `RolDelete = 'N'`.
3. Le righe approvate vengono **clonate** nella testata clone con nuovi `RoaNumrig`. Le righe clonate ricevono `RoaChiuso = 'S'`, `RoaDelete = 'N'`.
4. Le righe originali appena approvate ricevono `RoaChiuso = 'S'` (**restano `RoaDelete = 'N'`**: a livello di riga la cancellazione non è mai un effetto dell'approvazione, solo `RoaChiuso` cambia), più:
   - `confirmed_id_rif = RolCodEstNEW` (il `RolCodEst` della testata clone)
   - `confirmed_row_rif = RoaNumrig` della riga clonata corrispondente
5. Le righe non ancora approvate rimangono sulla testata originale con `RoaChiuso = 'N'`, `RoaDelete = 'N'` e `confirmed_id_rif = NULL`.
6. La **testata originale** riceve `RolChiuso = 'S'`, `RolDelete = 'S'` a ogni evento di approvazione (anche parziale) — osservato sia su ordini approvati in un solo evento sia su ordini con più tornate parziali.

Ogni tornata di approvazione (anche parziale) genera una nuova testata clone distinta, con un proprio `RolCodEst` che le righe via via approvate in quell'evento referenziano tramite `confirmed_id_rif`. Al termine, l'ordine originale (`RolRiferimento = '0'`) può avere ancora righe aperte (non approvate) insieme a quelle già approvate.

**Riepilogo rapido:**

| Livello | Stato | `RolChiuso` / `RoaChiuso` | `RolDelete` / `RoaDelete` | `confirmed_id_rif` | `confirmed_row_rif` |
|---|---|---|---|---|---|
| Testata | Aperta (bozza), `RolRiferimento = '0'` | `'N'` | `'N'` | — | — |
| Testata | Originale, dopo almeno un'approvazione | `'S'` | `'S'` | — | — |
| Testata | Clone (una per evento di approvazione) | `'S'` | `'N'` | — | — |
| Riga | Ancora aperta | `'N'` | `'N'` | `NULL` | `NULL` |
| Riga | Originale, approvata | `'S'` | `'N'` | `RolCodEst` della testata clone | `RoaNumrig` della riga clonata |
| Riga | Clone (nella testata clone) | `'S'` | `'N'` | `NULL` | `NULL` |

### Come cercare un ordine
```sql
SELECT RolCodEst, RolIdBrand, RolRivoor, RolRiferimento, RolChiuso, RolDelete,
       RolSeason, RolTotord, varian_type_id, modified_at, updated_at
FROM ordcli_open
WHERE RolIdBrand = <brand_id>
  AND RolRivoor = '<po_number>'
  AND RolRiferimento = '0'
```

### Righe ancora aperte di un ordine
```sql
SELECT RoaCodEst, RoaNumrig, RolIdBrand, RoaQuanti, RoaPrezzo, RoaUnimis,
       RoaChiuso, RoaDelete, confirmed_id_rif, confirmed_row_rif,
       supplier_article, supplier_color, updated_at
FROM riorcl_open
WHERE RoaCodEst = '<rol_cod_est>'
  AND RoaDelete = 'N'
  AND RoaChiuso = 'N'
ORDER BY RoaNumrig
```

### Righe approvate di un ordine (clone nelle testate derivate)
```sql
SELECT h.RolCodEst, h.RolIdBrand, h.RolRivoor, h.RolRiferimento, h.RolChiuso, h.RolDelete,
       h.RolSeason, h.RolTotord, h.varian_type_id, h.modified_at, h.updated_at,
       r.RoaCodEst, r.RoaNumrig, r.RolIdBrand, r.RoaQuanti, r.RoaPrezzo, r.RoaUnimis,
       r.RoaChiuso, r.RoaDelete, r.confirmed_id_rif, r.confirmed_row_rif,
       r.supplier_article, r.supplier_color, r.updated_at
FROM ordcli_open h
JOIN riorcl_open r ON r.RoaCodEst = h.RolCodEst
WHERE h.RolRiferimento = '<rol_cod_est_originale>'
ORDER BY h.RolCodEst, r.RoaNumrig
```
