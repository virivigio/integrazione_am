# CLAUDE-SPEC.md — integrazione_am, architettura e convenzioni tecniche

Vedi [CLAUDE.md](CLAUDE.md) per il modello di collaborazione e per dove vive la conoscenza di dominio (idf-hop). Questo file raccoglie solo le convenzioni tecniche specifiche di questo progetto — non conoscenza di dominio ordini/spedizioni.

## Architettura

```
app/
├── main.py                # Entry point FastAPI
├── config.py               # Configurazione da variabili d'ambiente (pydantic-settings)
├── database.py              # Connection pool MySQL (read-only)
├── agent.py                 # Loop OpenAI function calling; system prompt = knowledge_base.md
├── session_manager.py       # Sessioni in-memory, TTL 24h (perse al riavvio)
├── tools/
│   ├── tool_registry.py    # Definizioni JSON dei tool per OpenAI
│   └── database_tools.py   # Implementazione query SQL + mapping brand→RolIdBrand
├── routers/
│   ├── api.py                # Endpoint /api/*
│   └── web.py                 # Endpoint / (chat UI)
└── templates/
    └── index.html             # Interfaccia chat HTML
```

## MCP — solo dev-time, mai a runtime, mai nel repo git

Configurati due MCP MySQL read-only (`mysql-am-test`, `mysql-am-stage`, server `@benborla29/mcp-server-mysql` via npx, nessun `ALLOW_*` di scrittura impostato) per verificare lo schema/dati reali mentre si scrive o corregge `knowledge_base.md` o i SELECT in `database_tools.py` — usano le stesse credenziali read-only già presenti in `.env.test`/`.env.stage` di questo progetto, mai credenziali di produzione. **Deliberatamente non in `.claude/settings.json`**: quelle variabili diventerebbero env OS reali nelle sessioni Claude Code, con priorità sui file `.env*` letti da `pydantic-settings` — romperebbero silenziosamente lo switch `ENV_FILE` (vedi README).

**Scope volutamente locale, non di progetto**: aggiunti con `claude mcp add` (scope `local`, default), quindi vivono in `~/.claude.json` sotto il path di questo progetto — **mai in un `.mcp.json` committato**. L'MCP è uno strumento di lavoro di Claude Code su questa macchina, non un artefatto del prodotto: chi altro clona questo repo deve configurarsi i propri MCP allo stesso modo (non li eredita da git). Stesso pattern già in uso da Virgilio sul progetto [idf-hop](../idf-hop) (`mysql-idf-test`/`mysql-idf-stage`, credenziali diverse — lì con `integration_user`, qui con l'utente read-only `portal`/`portal_user` di questo progetto).

**Deciso esplicitamente con Virgilio**: l'agente runtime non deve mai avere accesso MCP/SQL diretto — resta sui due tool fissi (`find_order`, `get_order_lines`) scritti a mano. Motivo: è un prototipo destinato a essere venduto a un cliente terzo, quindi la superficie di rischio (SQL libero in mano a un LLM) va tenuta minima e auditabile.

Se in futuro servirà un agente più esplorativo (vedi il progetto "problem determination ordini+caricamenti" discusso con Virgilio, concettualmente distinto da questo prototipo — messo in pausa per ora, non tracciato qui), l'approccio previsto è un MCP separato con viste read-only scoped per lo scopo, non SQL arbitrario sulle tabelle. Le regole di quella policy di accesso andranno scritte qui quando/se si deciderà di disegnarle davvero — oggi non esistono ancora.

## Convenzioni runtime dell'agente (system prompt, `agent.py`)

- Tono: risponde sempre in italiano, in modo chiaro e conciso — oggi è l'unica istruzione di tono presente in `SYSTEM_PROMPT`, non ancora raffinata oltre questo.
- Paginazione: i tool troncano oggi silenziosamente con `LIMIT 10` (`find_order`) e `LIMIT 200` (`get_order_lines`), senza segnalare all'utente se esistono altri risultati oltre il limite — punto da rivedere, vedi [CLAUDE-PUNTIAPERTI.md](CLAUDE-PUNTIAPERTI.md).

## Mapping brand

`BRAND_IDS` in `app/tools/database_tools.py` è la fonte unica per nome brand → `RolIdBrand` (BESTE=66, MABI=62, GENTILI-MOSCONI=60). Se cambia, aggiornare anche l'enum in `tool_registry.py` e la tabella corrispondente in `knowledge_base.md`.
