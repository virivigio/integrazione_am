# CLAUDE.md — Assistente Ordini AI (integrazione_am)

Prototipo di agente conversazionale (FastAPI + OpenAI function calling) che permette di interrogare in linguaggio naturale lo stato di ordini/righe ordine su `theidfactory_ordini` — lo stesso schema ERP che il progetto [idf-hop](../idf-hop) scrive via pipeline Apache Hop. Vedi [README.md](README.md) per setup/uso e [CLAUDE-SPEC.md](CLAUDE-SPEC.md) per architettura e convenzioni tecniche di questo repo.

## Due livelli di conoscenza, da non confondere

- **Conoscenza di dominio** (cos'è un ordine, una spedizione, il ciclo aperto→confermato, quali tabelle ERP sono coinvolte) **non vive qui**: la fonte di verità è [idf-hop](../idf-hop), il progetto che scrive quei dati via ETL e la mantiene verificata sul codice reale (`idf-hop/CLAUDE-SPEC.md`, ed eventuali `CLAUDE-SPEC-<cliente>.md`). Consultarla on-demand quando serve capire un campo o una regola di business — non dedurla qui, non copiarla. **idf-hop è un repo indipendente che evolve per conto suo**: se si riusa un'informazione da lì, segnalare a Virgilio che potrebbe nel frattempo essere cambiata (stessa cautela che idf-hop applica alle sue fonti esterne).
- **`knowledge_base.md`** (in questo repo) è invece la conoscenza di dominio **auto-contenuta per l'agente runtime**: viene caricata per intero nel system prompt di OpenAI ad ogni turno (`app/agent.py`), quindi deve restare comprensibile e completa da sola — l'agente deployato non ha accesso al filesystem di idf-hop. Va scritta/aggiornata usando idf-hop (e verifica diretta dello schema, vedi CLAUDE-SPEC.md) come fonte di verità, mai a memoria o per deduzione.

## Dove scrivere una scoperta nuova

Obiettivo esplicito di Virgilio per questo repo: deve restare pronto a ricevere conoscenza da sessioni future, instradata correttamente invece che accumulata alla rinfusa. Quando emerge qualcosa di nuovo (un dubbio chiarito, un comportamento verificato sul DB, un bug), instradarlo così:

- **Rilevanza di dominio/business** (ordini, spedizioni, schema ERP, comportamento delle pipeline — utile anche a chi scrive l'ETL, non solo a questo chatbot) → va scritta in [idf-hop](../idf-hop) (`CLAUDE-SPEC.md`, l'eventuale `CLAUDE-SPEC-<cliente>.md`, o `CLAUDE-PUNTIAPERTI.md` se è un punto aperto), seguendo le convenzioni di quel repo — non qui. Sì, questo significa scrivere davvero in idf-hop quando emerge dal lavoro su integrazione_am, non solo leggerlo.
- **Specifica di questo progetto** (l'agente, i tool, l'uso di MCP, convenzioni runtime, bug del codice di questo repo) → resta qui, in [CLAUDE-SPEC.md](CLAUDE-SPEC.md) o [CLAUDE-PUNTIAPERTI.md](CLAUDE-PUNTIAPERTI.md).
- Nel dubbio, la domanda guida è: *questa informazione sarebbe utile anche a chi lavora sulle pipeline Hop, o riguarda solo questo chatbot?*

## Convenzioni di sviluppo

- **Ogni query di esempio in `knowledge_base.md` deve selezionare tutti i campi rilevanti della tabella**, anche quelli usati solo come filtro nella WHERE — deve restituire un risultato completo senza dover tornare a modificare il SELECT.
- **Quando cambia lo schema documentato in `knowledge_base.md`, aggiornare subito anche i SELECT in `app/tools/database_tools.py`** (e viceversa) — non lasciare i due disallineati in attesa che qualcuno se ne accorga.
- **Nuove incoerenze in `knowledge_base.md` vanno verificate contro idf-hop (e/o il DB reale via MCP) prima di correggerle** — non fidarsi di conoscenza dedotta a memoria. Il file è stato riletto e verificato per intero il 2026-09-02 (schema, tipi colonna, mapping brand, ciclo di vita ordine): eventuali nuovi dubbi vanno controllati con lo stesso rigore, non assunti.
- Non usare la memoria locale di Claude per contenuti su questo progetto: quello che deve sopravvivere tra sessioni va in questo file, in [CLAUDE-SPEC.md](CLAUDE-SPEC.md) o in [CLAUDE-PUNTIAPERTI.md](CLAUDE-PUNTIAPERTI.md), così è visibile anche a chi altro lavora sul repo.
- I file `CLAUDE*.md` di questo repo sono file locali (non symlink) in un repo git privato — a differenza di idf-hop, dove sono symlink a Google Drive condiviso.
