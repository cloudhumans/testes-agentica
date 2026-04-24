import os, json
from dotenv import load_dotenv
from openai import OpenAI
from langgraph_sdk import get_sync_client

load_dotenv()

gpt = OpenAI()
alvo = get_sync_client(url=LANGGRAPH_URL, api_key=os.environ["LANGSMITH_API_KEY"])


def chamar_gpt(prompt, json_mode=False):
    kwargs = {"model": "gpt-5", "messages": [{"role": "user", "content": prompt}]}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    return gpt.chat.completions.create(**kwargs).choices[0].message.content


def gerar_cenario():
    p = f"Escopo do agente:\n{ESCOPO}\n\nCrie 1 ficha de cliente ficticio pra testar esse agente. Retorne JSON: {{\"persona\":\"...\",\"objetivo\":\"...\"}}"
    return json.loads(chamar_gpt(p, json_mode=True))


def fala_cliente(cenario, historico):
    h = "\n".join(f"{m['quem']}: {m['txt']}" for m in historico) or "(inicio)"
    p = f"Voce e um cliente. Persona: {cenario['persona']}. Objetivo: {cenario['objetivo']}.\n\nHistorico:\n{h}\n\nEscreva SUA proxima mensagem (curta, como cliente real). Se objetivo foi atendido, termine com FIM."
    return chamar_gpt(p)


def fala_alvo(thread_id, msg):
    r = alvo.runs.wait(thread_id=thread_id, assistant_id=ASSISTANT_ID,
                       input={"messages": [{"role": "user", "content": msg}]})
    msgs = r.get("messages", []) if isinstance(r, dict) else []
    for m in reversed(msgs):
        if m.get("type") == "ai" or m.get("role") == "assistant":
            c = m.get("content", "")
            return c if isinstance(c, str) else " ".join(x.get("text", "") for x in c if x.get("type") == "text")
    return ""


def julgar(cenario, historico):
    transcricao = "\n".join(f"{m['quem']}: {m['txt']}" for m in historico)
    p = f"Avalie o ATENDENTE nesta conversa. Escopo esperado:\n{ESCOPO}\n\nCenario: {cenario}\n\nConversa:\n{transcricao}\n\nRetorne JSON: {{\"nota\":0-100,\"pontos_fortes\":[],\"melhorias\":[]}}"
    return json.loads(chamar_gpt(p, json_mode=True))


def main():
    print("1. Gerando cenario..."); cenario = gerar_cenario(); print(f"   {cenario}\n")
    print("2. Conversando..."); thread = alvo.threads.create()["thread_id"]; print(f"   Thread ID: {thread}\n"); historico = []
    for _ in range(8):
        c = fala_cliente(cenario, historico); historico.append({"quem": "CLIENTE", "txt": c}); print(f"   CLIENTE: {c}")
        if "FIM" in c: break
        a = fala_alvo(thread, c); historico.append({"quem": "ATENDENTE", "txt": a}); print(f"   ATENDENTE: {a}")
    print("\n3. Avaliando...")
    r = julgar(cenario, historico)
    print(f"\n=== NOTA: {r['nota']}/100 ===")
    print("Fortes:", r['pontos_fortes'])
    print("Melhorias:", r['melhorias'])


if __name__ == "__main__":
    main()
