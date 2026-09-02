# CLAUDE-PUNTIAPERTI.md — punti di lavoro

Vedi [CLAUDE.md](CLAUDE.md) per il modello di collaborazione e [CLAUDE-SPEC.md](CLAUDE-SPEC.md) per architettura e convenzioni. Quando un punto si chiude, si toglie (la cronologia sta nella chat/nei commit, non qui).

## Punti di lavoro

Nessuno al momento.
- [ ] **`get_order_lines` non legge mai lo stato "confermato" vero (`c_ordcli`/`c_riorcl`)** — solo il mirror chiuso `ordcli_open`/`riorcl_open`. Manca quindi l'accesso a `RoaStarig` (flag "balance"/riga spedita per intero, esiste solo su `c_riorcl` — verificato, non è una colonna di `riorcl_open`) e a eventuali scritture che alcuni clienti fanno solo lì (es. mabi aggiorna `RoaQuanti` anche su `c_riorcl` per una riga confermata modificata). Da valutare se/quando estendere il tool a interrogare anche le tabelle confermate (e magari `c_evasoc`/`dettagli_consegna` per lo stato spedizioni).
