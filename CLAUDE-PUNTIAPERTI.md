# CLAUDE-PUNTIAPERTI.md — punti di lavoro

Vedi [CLAUDE.md](CLAUDE.md) per il modello di collaborazione e [CLAUDE-SPEC.md](CLAUDE-SPEC.md) per architettura e convenzioni. Quando un punto si chiude, si toglie (la cronologia sta nella chat/nei commit, non qui).

## Punti di lavoro

- [ ] **Nessuna autenticazione su `/api/ask`, CORS aperto a `*`, nessun rate limit** — chiunque trovi l'URL può interrogarlo liberamente e ogni domanda costa token OpenAI veri; `GET`/`DELETE /api/session/{id}` non verificano nemmeno la proprietà della sessione (basta conoscere/indovinare lo UUID). Da chiudere prima di consegnare l'app a un cliente reale (bastano poche righe: una API key statica in header + restringere `allow_origins`).
- [ ] **Sessioni solo in-memory, singolo processo** — corretto per come gira oggi, ma non sopravvive a un riavvio e non funziona se mai si scalasse a più worker/istanze (sessione creata sul worker A, richiesta successiva sul worker B → "sessione non trovata").
- [ ] **`knowledge_base.md` non viene ricaricato a caldo** — il system prompt in `agent.py` lo legge una sola volta a import-time; `uvicorn --reload` non se ne accorge (watcha i `.py`, non i `.md`), serve riavviare l'app a mano dopo ogni modifica al file.
- [ ] **Paginazione risultati non comunicata all'utente** — `find_order` (`LIMIT 10`) e `get_order_lines` (`LIMIT 200`) troncano silenziosamente senza indicare nella risposta se esistono altri risultati oltre il limite. Da decidere: alzare i limiti, aggiungere un conteggio totale nel JSON di risposta, o supportare una paginazione esplicita lato tool.
- [ ] **`get_order_lines` non legge mai lo stato "confermato" vero (`c_ordcli`/`c_riorcl`)** — solo il mirror chiuso `ordcli_open`/`riorcl_open`. Manca quindi l'accesso a `RoaStarig` (flag "balance"/riga spedita per intero, esiste solo su `c_riorcl` — verificato, non è una colonna di `riorcl_open`) e a eventuali scritture che alcuni clienti fanno solo lì (es. mabi aggiorna `RoaQuanti` anche su `c_riorcl` per una riga confermata modificata). Da valutare se/quando estendere il tool a interrogare anche le tabelle confermate (e magari `c_evasoc`/`dettagli_consegna` per lo stato spedizioni).
