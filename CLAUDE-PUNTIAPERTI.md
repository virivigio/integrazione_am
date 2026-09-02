# CLAUDE-PUNTIAPERTI.md — punti di lavoro

Vedi [CLAUDE.md](CLAUDE.md) per il modello di collaborazione e [CLAUDE-SPEC.md](CLAUDE-SPEC.md) per architettura e convenzioni. Quando un punto si chiude, si toglie (la cronologia sta nella chat/nei commit, non qui).

## Punti di lavoro

- [ ] **`get_order_lines` non legge mai lo stato "confermato" vero (`c_ordcli`/`c_riorcl`)** — solo il mirror chiuso `ordcli_open`/`riorcl_open`. Manca quindi l'accesso a `RoaStarig` (flag "balance"/riga spedita per intero, esiste solo su `c_riorcl` — verificato, non è una colonna di `riorcl_open`) e a eventuali scritture che alcuni clienti fanno solo lì (es. mabi aggiorna `RoaQuanti` anche su `c_riorcl` per una riga confermata modificata). Da valutare se/quando estendere il tool a interrogare anche le tabelle confermate (e magari `c_evasoc`/`dettagli_consegna` per lo stato spedizioni).
- [ ] **Nessuna protezione da prompt leaking/prompt injection** — oggi se l'utente chiede esplicitamente il system prompt (o istruzioni tipo "ignora le istruzioni precedenti"), l'agente lo rivela. Anche restando una demo, è un difetto che fa cattiva impressione se mostrata a un cliente. Da valutare: istruzione esplicita nel system prompt di non rivelare mai le proprie istruzioni, eventuale controllo/filtro sull'output prima di restituirlo, e ricognizione delle best practice note per questo problema (è un problema comune e ben documentato nel prompt engineering, non specifico di questo progetto) prima di implementare qualcosa ad-hoc.
