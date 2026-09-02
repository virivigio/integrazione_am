# Assistente Ordini AI

Agente AI conversazionale per interrogare gli ordini dei brand BESTE, MABI e GENTILI-MOSCONI su database MySQL.

> Per contribuire al codice, leggere anche [CLAUDE.md](CLAUDE.md) (modello di collaborazione e dove vive la conoscenza di dominio) e [CLAUDE-SPEC.md](CLAUDE-SPEC.md) (architettura e convenzioni tecniche di questo repo).

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

## Ambienti disponibili e come cambiarli

L'app si collega sempre a **un solo database MySQL per volta**, quello indicato da `DB_HOST`/`DB_USERNAME`/`DB_PASSWORD` nel file d'ambiente caricato. Oggi sono pronti due ambienti, entrambi in `theidfactory_ordini`:

| Ambiente | File | Uso |
|---|---|---|
| **stage** | `.env.stage` | dati più recenti/vicini a produzione |
| **test** | `.env.test` | dati di test |

Il modo più comodo per scegliere è impostare `ENV_FILE` all'avvio, senza toccare `.env`:

```bash
ENV_FILE=.env.stage uvicorn app.main:app --reload --port 9000
ENV_FILE=.env.test uvicorn app.main:app --reload --port 9000
```

Senza `ENV_FILE`, l'app usa `.env` (di default allineato a stage). Questi file (`.env`, `.env.stage`, `.env.test`) non sono su git: crearli a mano copiando `.env.example` e compilando le credenziali per l'ambiente voluto.

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

## Note tecniche

- Le sessioni sono gestite in-memory con TTL di 24 ore; al riavvio dell'app vengono perse.
- Il database è acceduto in sola lettura (solo query SELECT).
- I flag `RolChiuso` / `RolDelete` usano `'S'` (sì) e `'N'` (no).
