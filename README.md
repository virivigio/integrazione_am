# Assistente Ordini AI

Agente AI conversazionale per interrogare gli ordini dei brand BESTE, MABI e GENTILI-MOSCONI su database MySQL.

## Prerequisiti

- Python 3.11+
- Accesso al database MySQL (credenziali già configurate in `.claude/settings.json`)
- API key OpenAI

## Setup

### 1. Installa le dipendenze

```bash
pip install -r requirements.txt
```

### 2. Configura le variabili d'ambiente

Compila i file con i secrets

```bash
cp .env.example .env
cp .claude/settings.json.example .claude/settings.json
```

### 3. Avvia l'applicazione

```bash
uvicorn app.main:app --reload --port 9000
```

## Utilizzo

Apri il browser su `http://localhost:9000` e scrivi le tue domande nella chat.

### Esempi di domande

| Domanda | Tool usato |
|---------|-----------|
| "Qual è lo stato dell'ordine V2400438 di GENTILI-MOSCONI?" | `find_order` |
| "L'ordine F2400438 di GENTILI-MOSCONI è chiuso o eliminato?" | `find_order` |
| "Mostrami le righe dell'ordine V2400438" | `find_order` + `get_order_lines` |
| "Quali righe dell'ordine V2400438 sono ancora aperte?" | `find_order` + `get_order_lines` |

## API

### `POST /api/ask`

```json
{
  "session_id": "...",   // opzionale, se omesso viene creata una nuova sessione
  "message": "Qual è lo stato dell'ordine V2400438 di GENTILI-MOSCONI?"
}
```

Risposta:

```json
{
  "session_id": "uuid-della-sessione",
  "response": "L'ordine V2400438 di GENTILI-MOSCONI è presente nel sistema...",
  "conversation": [...]
}
```

### `GET /api/session/{session_id}`

Restituisce la cronologia della conversazione.

### `DELETE /api/session/{session_id}`

Azzera la sessione (equivale a "Nuova chat").

## Struttura del progetto

```
app/
├── main.py                # Entry point FastAPI
├── config.py              # Configurazione da variabili d'ambiente
├── database.py            # Connection pool MySQL (read-only)
├── agent.py               # Loop OpenAI function calling
├── session_manager.py     # Gestione sessioni in-memory (TTL 24h)
├── tools/
│   ├── tool_registry.py   # Definizioni tools JSON per OpenAI
│   └── database_tools.py  # Implementazione query SQL
├── routers/
│   ├── api.py             # Endpoint /api/*
│   └── web.py             # Endpoint / (chat UI)
└── templates/
    └── index.html         # Interfaccia chat HTML
```

## Note tecniche

- Le sessioni sono gestite in-memory con TTL di 24 ore; al riavvio dell'app vengono perse.
- Il database è acceduto in sola lettura (solo query SELECT).
- I flag `RolChiuso` / `RolDelete` usano `'S'` (sì) e `'N'` (no).
