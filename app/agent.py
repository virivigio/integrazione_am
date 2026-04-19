import json
import logging
from pathlib import Path
from openai import OpenAI
from app.config import get_settings
from app.tools.tool_registry import TOOLS
from app.tools.database_tools import execute_tool

# Metti a True per vedere il flusso completo di domande, tool call e risposte
# nel terminale dove gira uvicorn.
DEBUG = True

logger = logging.getLogger(__name__)

_KB = Path(__file__).parent.parent / "knowledge_base.md"

SYSTEM_PROMPT = f"""Sei un assistente AI specializzato nella gestione degli ordini.
Hai accesso a un database MySQL. Rispondi sempre in italiano in modo chiaro e conciso.

{_KB.read_text()}
"""


def run_agent(history: list, user_message: str) -> str:
    """
    Esegue un turno di conversazione con l'agente AI.

    Riceve la cronologia della conversazione e il nuovo messaggio dell'utente,
    chiama OpenAI in un loop finché l'assistente non smette di invocare tool,
    e restituisce il testo finale della risposta.
    """
    settings = get_settings()
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Aggiunge il messaggio dell'utente alla cronologia persistente della sessione.
    # `history` è una lista condivisa con il session_manager: modificarla qui
    # significa che il prossimo turno "ricorderà" questo messaggio.
    history.append({"role": "user", "content": user_message})

    if DEBUG:
        logger.debug("[USER] %s", user_message)

    # Costruisce la lista di messaggi da inviare a OpenAI.
    # Il system prompt va SEMPRE in testa (istruzioni fisse all'agente),
    # seguito dalla cronologia (domande e risposte precedenti + quella attuale).
    # Nota: `messages` è una copia locale usata solo per questa chiamata;
    # la cronologia persistente è `history`.
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    # Loop di "function calling": OpenAI può rispondere con una richiesta
    # di eseguire uno o più tool (es. find_order), oppure con il testo finale.
    # Il loop continua finché l'assistente non dà una risposta testuale.
    while True:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            tools=TOOLS,           # lista dei tool disponibili (tool_registry.py)
            tool_choice="auto",    # OpenAI decide da solo se usare un tool o rispondere direttamente
        )

        # OpenAI restituisce sempre almeno una "scelta"; prendiamo la prima
        # (con n=1, che è il default, ce n'è sempre esattamente una).
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls":
            # L'assistente vuole chiamare uno o più tool prima di rispondere.

            # Aggiungiamo il messaggio dell'assistente (che contiene le richieste
            # di tool call) a `messages`, perché OpenAI ha bisogno di vedere
            # il contesto completo nel turno successivo.
            assistant_msg = choice.message
            messages.append(assistant_msg)

            # Eseguiamo ogni tool richiesto e aggiungiamo il risultato a `messages`.
            for tool_call in assistant_msg.tool_calls:
                tool_name = tool_call.function.name
                # Gli argomenti arrivano come stringa JSON; li convertiamo in dict.
                tool_args = json.loads(tool_call.function.arguments)
                tool_result = execute_tool(tool_name, tool_args)

                if DEBUG:
                    logger.debug("[TOOL CALL] %s(%s)", tool_name, tool_args)
                    logger.debug("[TOOL RESULT] %s", tool_result)

                # Il risultato del tool va associato all'ID della tool call
                # (tool_call_id) così OpenAI sa a quale richiesta corrisponde.
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,   # stringa JSON con i dati dal DB
                })

            # Dopo aver aggiunto tutti i risultati, il loop riparte:
            # OpenAI riceverà i risultati e potrà rispondere con testo
            # oppure richiedere altri tool.

        else:
            # finish_reason != "tool_calls" significa che l'assistente
            # ha prodotto una risposta testuale definitiva.
            final_text = choice.message.content

            # Salviamo la risposta nella cronologia persistente della sessione,
            # così il prossimo turno potrà riferirsi a ciò che è stato detto.
            history.append({"role": "assistant", "content": final_text})

            if DEBUG:
                logger.debug("[ASSISTANT] %s", final_text)

            return final_text
