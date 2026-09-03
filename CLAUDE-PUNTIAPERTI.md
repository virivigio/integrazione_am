# CLAUDE-PUNTIAPERTI.md — punti di lavoro

Vedi [CLAUDE.md](CLAUDE.md) per il modello di collaborazione e [CLAUDE-SPEC.md](CLAUDE-SPEC.md) per architettura e convenzioni. Quando un punto si chiude, si toglie (la cronologia sta nella chat/nei commit, non qui).

## Punti di lavoro

- [ ] **`get_order_lines` legge `RoaQuanti` solo dal mirror `riorcl_open`, non da `c_riorcl`** — per mabi (unico brand con questa eccezione, confermata da idf-hop) una riga già confermata può essere aggiornata anche su `c_riorcl.RoaQuanti` quando il cliente modifica una riga già approvata; l'agente oggi mostra sempre il valore di `riorcl_open`, che per beste/GM è sempre corretto ma per mabi potrebbe non riflettere l'ultimo aggiornamento sul confermato vero. Non urgente per la demo (RoaStarig, il pezzo principale, è già stato aggiunto — vedi query "Tutte le righe di un ordine" in `knowledge_base.md`); da valutare se leggere anche `c_riorcl.RoaQuanti` e mostrare entrambi i valori quando divergono, solo per mabi.
