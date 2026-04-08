import json
from openai import OpenAI
from app.config import get_settings
from app.tools.tool_registry import TOOLS
from app.tools.database_tools import execute_tool

SYSTEM_PROMPT = """Sei un assistente AI specializzato nella gestione degli ordini.
Hai accesso a un database MySQL che contiene ordini di materiali (tessuti, pellami, bottoni, ecc.) per i brand BESTE, MABI e GENTILI-MOSCONI.

## Struttura dati

**Testata ordine** (ordcli_open):
- RolCodEst: ID interno dell'ordine
- RolRivoor: PO number del cliente (usato per la ricerca)
- RolRiferimento: '0' = ordine aperto/non ancora approvato; altrimenti contiene il RolCodEst dell'ordine originale da cui deriva
- RolChiuso / RolDelete: flag S/N (S=sì, N=no)
- varian_type_id: categoria merceologica (es. pellame, tessuto, bottoni)

**Righe ordine** (riorcl_open):
- RoaCodEst: FK verso la testata
- RoaChiuso / RoaDelete: flag S/N sulla singola riga
- confirmed_id_rif: RolCodEst della testata approvata in cui questa riga è stata promossa (NULL = non ancora approvata)
- confirmed_row_rif: RoaNumrig della riga clonata nella testata approvata

## Ciclo di approvazione
Un ordine entra nel sistema con RolRiferimento='0' e le righe sono aperte (RoaDelete='N', RoaChiuso='N').
Quando alcune righe vengono approvate viene creata una nuova testata (RolRiferimento = RolCodEst originale) e le righe approvate vengono clonate lì. Le righe originali approvate ricevono RolDelete='S', RolChiuso='S' e i campi confirmed_id_rif / confirmed_row_rif valorizzati. Le righe non ancora approvate rimangono sulla testata originale con i flag a 'N'. L'approvazione può avvenire in più tornate parziali.

## Istruzioni operative
- Per cercare un ordine per brand e PO number usa `find_order` (restituisce la testata con RolRiferimento='0')
- Per vedere le righe di un ordine usa `get_order_lines` con il RolCodEst ottenuto da `find_order`
- Le righe ancora aperte hanno RoaDelete='N' e RoaChiuso='N'; quelle approvate hanno entrambi i flag a 'S'
- I flag usano 'S'/'N' (italiano Sì/No)
- Rispondi sempre in italiano in modo chiaro e conciso
- Se un ordine non viene trovato, comunicalo chiaramente
"""


def run_agent(history: list, user_message: str) -> str:
    """
    Add user_message to history, run OpenAI with function calling loop,
    append assistant response to history, return the final text response.
    """
    settings = get_settings()
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    while True:
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        choice = response.choices[0]

        if choice.finish_reason == "tool_calls":
            assistant_msg = choice.message
            messages.append(assistant_msg)

            for tool_call in assistant_msg.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                tool_result = execute_tool(tool_name, tool_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

        else:
            final_text = choice.message.content
            history.append({"role": "assistant", "content": final_text})
            return final_text
