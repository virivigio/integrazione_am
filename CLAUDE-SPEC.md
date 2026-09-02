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

**Scope volutamente locale, non di progetto**: aggiunti con `claude mcp add` (scope `local`, default), quindi vivono in `~/.claude.json` sotto il path di questo progetto — **mai in un `.mcp.json` committato**. L'MCP è uno strumento di lavoro di Claude Code su questa macchina, non un artefatto del prodotto: chi altro clona questo repo deve configurarsi i propri MCP allo stesso modo (non li eredita da git). Stesso pattern già in uso da Virgilio sul progetto [idf-hop](../idf-hop) (`mysql-idf-test`/`mysql-idf-stage`) — stesse credenziali `integration_user`, dato che le utenze dedicate `portal`/`portal_user` sono in dismissione.

**Deciso esplicitamente con Virgilio**: l'agente runtime non deve mai avere accesso MCP/SQL diretto — resta sui due tool fissi (`find_order`, `get_order_lines`) scritti a mano. Motivo: è un prototipo destinato a essere venduto a un cliente terzo, quindi la superficie di rischio (SQL libero in mano a un LLM) va tenuta minima e auditabile.

Se in futuro servirà un agente più esplorativo di questo, l'approccio previsto è un MCP separato con viste read-only scoped per lo scopo, non SQL arbitrario sulle tabelle. Le regole di quella policy di accesso andranno scritte qui quando/se si deciderà di disegnarle davvero — oggi non esistono ancora.

## Convenzioni runtime dell'agente (system prompt, `agent.py`)

- **Modello**: `gpt-5-nano` con `reasoning_effort="minimal"` (impostato solo per modelli `gpt-5*`, vedi `agent.py`). **Verificato empiricamente (2026-09-02)**, non dedotto dal solo prezzo a listino: senza `reasoning_effort` esplicito, `gpt-5-nano` fa reasoning implicito che genera token di output nascosti e fatturati — su una singola tool call banale, 229 token di completion di cui 192 di solo reasoning, contro i 28 totali di `gpt-4o-mini` per lo stesso prompt (quindi *più caro*, non più economico, nonostante il prezzo per token più basso). Con `reasoning_effort="minimal"` il reasoning nascosto sparisce (37 token totali) e il costo reale scende sotto quello di `gpt-4o-mini` (~24% in meno sullo stesso test) — tool calling verificato corretto in entrambi i casi. **Se si cambia modello, non fidarsi del prezzo a listino da solo**: va sempre verificato il comportamento reale con tool calling.
- **`gpt-5.6-luna` valutato e scartato (2026-09-02)**: prezzo per token 3-4 volte più alto di `gpt-5-nano`, e soprattutto **non supporta tool calling insieme a `reasoning_effort` diverso da `"none"`/`"minimal"` su `/v1/chat/completions`** (l'API rifiuta la richiesta — serve la nuova API `/v1/responses`, non solo un cambio di config). Non riconsiderarlo senza prima valutare la migrazione a `/v1/responses`.
- Tono: risponde sempre in italiano, in modo chiaro e conciso — oggi è l'unica istruzione di tono presente in `SYSTEM_PROMPT`, non ancora raffinata oltre questo.
- **`knowledge_base.md` viene riletto a ogni turno** (`_build_system_prompt()` in `agent.py`, non più una costante calcolata all'import): una modifica al file è effettiva alla richiesta successiva, senza riavviare uvicorn.
- **Nessuna paginazione, deliberatamente** (deciso con Virgilio, 2026-09-02): `find_order` e `get_order_lines` non hanno più `LIMIT` — restituiscono tutte le righe trovate e la chat le mostra come tabella lunga, invece di troncare in silenzio o gestire pagine.

## Decisioni di scope per questa fase demo (non riproporre)

**Deciso con Virgilio (2026-09-02)**: finché il progetto resta una demo (non ancora consegnato a un cliente reale), restano deliberatamente fuori scope:
- Autenticazione/rate limit su `/api/ask` e verifica proprietà sessione su `GET`/`DELETE /api/session/{id}` (CORS aperto a `*`).
- Persistenza delle sessioni oltre l'in-memory a singolo processo (TTL 24h, perse al riavvio, non scalano a più worker).

Da riconsiderare solo quando si passa a una consegna cliente reale — non sono più punti aperti da segnalare nel frattempo.

## Mapping brand

`BRAND_IDS` in `app/tools/database_tools.py` è la fonte unica per nome brand → `RolIdBrand` (BESTE=66, MABI=62, GENTILI-MOSCONI=60). Se cambia, aggiornare anche l'enum in `tool_registry.py` e la tabella corrispondente in `knowledge_base.md`.
