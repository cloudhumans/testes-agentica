import os, json
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from langgraph_sdk import get_sync_client

load_dotenv()

LANGGRAPH_URL = "https://claudia-e86fe2e91a435c59a69e1a70599e2914.us.langgraph.app"

st.set_page_config(page_title="QA de Agentes · CloudHumans", page_icon="🤖", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #f5f6fa !important;
    color: #1a1a2e !important;
}
[data-testid="stHeader"] { background: transparent !important; }
.stApp * { color-scheme: light !important; }

/* Container centralizado — 60% width */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton { display: none !important; }
[data-testid="stHeader"] { height: 0 !important; min-height: 0 !important; }
.block-container {
    max-width: 60% !important;
    padding: 0 0 60px 0 !important;
    margin: 0 auto !important;
}

/* Labels */
label, [data-testid="stWidgetLabel"] p {
    color: #1a1a2e !important;
    font-weight: 500 !important;
    font-size: 13px !important;
}

h1, h2, h3, h4, h5, h6 { color: #1a1a2e !important; }

.stTextInput input, .stTextArea textarea {
    background: white !important;
    color: #1a1a2e !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 8px !important;
}

/* Layout principal */
.main-layout {
    display: flex;
    height: 100vh;
    overflow: hidden;
}

/* Sidebar esquerda */
.sidebar-left {
    width: 260px;
    background: #1a1a2e;
    color: white;
    padding: 24px 16px;
    flex-shrink: 0;
}
.sidebar-logo {
    color: #FF6B00;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 32px;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Área de conteúdo */
.content-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background: #f5f6fa;
}

/* Header */
.top-header {
    background: white;
    padding: 16px 32px;
    border-bottom: 1px solid #e8e8e8;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.top-header h1 {
    font-size: 20px;
    font-weight: 600;
    color: #1a1a2e;
    margin: 0;
}

/* Cards de input */
.input-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}

/* Botão principal (▶ Iniciar testes) */
.stButton > button {
    background: #FF6B00 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 28px !important;
    font-weight: 600 !important;
    font-size: 15px !important;
    cursor: pointer !important;
    transition: background 0.2s !important;
}
.stButton > button:hover {
    background: #e05e00 !important;
}

/* Pills de número — override para ficarem compactos */
[data-testid="column"] .stButton > button {
    background: white !important;
    color: #888 !important;
    border: 2px solid #e0e0e0 !important;
    border-radius: 10px !important;
    padding: 6px 4px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    min-height: 42px !important;
    transition: all 0.15s ease !important;
}
[data-testid="column"] .stButton > button:hover {
    border-color: #FF6B00 !important;
    color: #FF6B00 !important;
    background: #fff3e8 !important;
}

/* Inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    border: 1px solid #e0e0e0 !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #FF6B00 !important;
    box-shadow: 0 0 0 2px rgba(255,107,0,0.15) !important;
}

/* Labels */
.stTextInput label, .stTextArea label {
    font-weight: 500 !important;
    color: #1a1a2e !important;
    font-size: 13px !important;
}

/* Pill number selector */
.n-selector {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 4px;
}
.n-pill {
    width: 42px;
    height: 42px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    border: 2px solid #e0e0e0;
    background: white;
    color: #888;
    transition: all 0.15s ease;
    user-select: none;
}
.n-pill:hover {
    border-color: #FF6B00;
    color: #FF6B00;
    background: #fff3e8;
}
.n-pill.active {
    background: #FF6B00;
    border-color: #FF6B00;
    color: white;
    box-shadow: 0 4px 12px rgba(255,107,0,0.3);
}
.n-selector-label {
    font-size: 13px;
    font-weight: 500;
    color: #1a1a2e;
    margin-bottom: 8px;
}

/* Card de conversa */
.conversa-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
.conversa-header {
    font-size: 13px;
    color: #888;
    margin-bottom: 4px;
}
.conversa-title {
    font-size: 15px;
    font-weight: 600;
    color: #1a1a2e;
    margin-bottom: 16px;
}

/* Balões de chat */
.chat-wrap { display: flex; flex-direction: column; gap: 10px; margin-bottom: 16px; }

.bubble-user {
    align-self: flex-start;
    background: #f0f0f5;
    color: #1a1a2e;
    padding: 10px 14px;
    border-radius: 0 12px 12px 12px;
    max-width: 70%;
    font-size: 14px;
    line-height: 1.5;
}
.bubble-bot {
    align-self: flex-end;
    background: #FF6B00;
    color: white;
    padding: 10px 14px;
    border-radius: 12px 0 12px 12px;
    max-width: 70%;
    font-size: 14px;
    line-height: 1.5;
}
.bubble-label {
    font-size: 11px;
    color: #aaa;
    margin-bottom: 2px;
}
.bubble-label-right {
    font-size: 11px;
    color: #FF6B00;
    margin-bottom: 2px;
    text-align: right;
}

/* Badge de status */
.badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 12px;
}
.badge-green { background: #e8f5e9; color: #2e7d32; }
.badge-blue  { background: #e3f2fd; color: #1565c0; }
.badge-gray  { background: #f0f0f0; color: #555; }

/* Nota */
.nota-box {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 10px;
    background: #fff8f3;
    border: 1px solid #ffe0c0;
    margin-bottom: 12px;
}
.nota-num {
    font-size: 28px;
    font-weight: 700;
    color: #FF6B00;
}
.nota-label { font-size: 13px; color: #888; }

/* Resumo */
.resumo-card {
    background: white;
    color: #1a1a2e;
    border-radius: 12px;
    padding: 32px;
    margin-top: 8px;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    border: 1px solid #f0f0f0;
}
.resumo-nota { font-size: 56px; font-weight: 800; color: #FF6B00; }
.resumo-label { font-size: 14px; color: #888; margin-top: 4px; }

/* Info/warning boxes */
.stAlert { border-radius: 8px !important; font-size: 13px !important; }

/* Divider */
hr { border: none; border-top: 1px solid #e8e8e8; margin: 24px 0; }

/* Persona badge */
.persona-pill {
    background: #fff3e8;
    border: 1px solid #ffd0a0;
    color: #FF6B00;
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 500;
    display: inline-block;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Header com logo
import base64, pathlib

_logo_path = pathlib.Path(__file__).parent / "logo.png"
if _logo_path.exists():
    _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
    _logo_html = f'<img src="data:image/png;base64,{_logo_b64}" style="height:48px;width:auto;" />'
else:
    # fallback: nuvem SVG até o arquivo logo.png ser adicionado
    _logo_html = """
    <svg width="52" height="44" viewBox="0 0 52 44" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="14" cy="30" r="13" fill="#FDDBC7"/>
      <circle cx="22" cy="20" r="17" fill="#F9A07A"/>
      <circle cx="37" cy="28" r="15" fill="#FF6B00"/>
    </svg>"""

st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:center;gap:14px;
            padding:32px 0 12px 0;">
  {_logo_html}
  <div>
    <div style="font-size:20px;font-weight:800;color:#1a1a2e;letter-spacing:-0.5px;">
      cloudhumans
    </div>
    <div style="font-size:11px;color:#888;font-weight:500;letter-spacing:1px;text-transform:uppercase;">
      Testes da Agêntica
    </div>
  </div>
</div>
<div style="text-align:center;margin-bottom:32px;color:#666;font-size:14px;">
  Teste seus agentes com conversas fictícias e obtenha notas de qualidade
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="font-size:16px;font-weight:700;color:#1a1a2e;margin-bottom:20px;">⚙️ Configuração do teste</div>', unsafe_allow_html=True)

escopo = st.text_area("Escopo do agente", height=130,
    placeholder="Descreva o que o agente faz, o que pode e o que não pode responder...")

assistant_id = st.text_input("ID do agente (LangSmith Assistant ID)",
    placeholder="Ex: 814f9860-e30f-44c3-a3d2-2102cc3c8c83")

persona_input = st.text_input("Persona do cliente (opcional)",
    placeholder="Ex: cliente impaciente que não lembra o número do pedido")

if "n_conversas" not in st.session_state:
    st.session_state.n_conversas = 3

n_conversas = st.session_state.n_conversas

# CSS dinâmico que pinta o pill ativo de laranja
st.markdown(f"""
<style>
[data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child({n_conversas}) .stButton > button {{
    background: #FF6B00 !important;
    color: white !important;
    border-color: #FF6B00 !important;
    box-shadow: 0 4px 12px rgba(255,107,0,0.3) !important;
}}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="n-selector-label">Número de conversas</div>', unsafe_allow_html=True)
pill_cols = st.columns(10)
for i, col in enumerate(pill_cols):
    num = i + 1
    with col:
        if st.button(str(num), key=f"pill_{num}", use_container_width=True):
            st.session_state.n_conversas = num
            st.rerun()

st.markdown(
    f'<div style="margin-top:6px;font-size:13px;color:#aaa;">'
    f'<span style="color:#FF6B00;font-weight:600;">{n_conversas}</span> '
    f'conversa{"s" if n_conversas > 1 else ""} selecionada{"s" if n_conversas > 1 else ""}'
    f'</div>',
    unsafe_allow_html=True
)

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    rodar = st.button("▶  Iniciar testes", type="primary", use_container_width=True)

if not rodar:
    st.stop()

if not escopo or not assistant_id:
    st.error("Preencha o escopo e o ID do agente.")
    st.stop()

openai_key = os.environ.get("OPENAI_API_KEY", "")
langsmith_key = os.environ.get("LANGSMITH_API_KEY", "")
if not openai_key or not langsmith_key:
    st.error("Chaves OPENAI_API_KEY e LANGSMITH_API_KEY não configuradas no servidor.")
    st.stop()

gpt = OpenAI(api_key=openai_key)
alvo = get_sync_client(url=LANGGRAPH_URL, api_key=langsmith_key)

def chamar_gpt(prompt, json_mode=False):
    kwargs = {"model": "gpt-5", "messages": [{"role": "user", "content": prompt}]}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    return gpt.chat.completions.create(**kwargs).choices[0].message.content

def gerar_persona():
    if persona_input.strip():
        return persona_input.strip()
    p = (
        f"Escopo do agente:\n{escopo}\n\n"
        f"Crie UMA persona de cliente ficticio para testar esse agente. "
        f"Use apenas dados coerentes com o escopo acima. "
        f"Seja breve: nome, perfil em 1 frase e tom emocional. "
        f"Retorne JSON: {{\"persona\": \"...\"}}"
    )
    return json.loads(chamar_gpt(p, json_mode=True))["persona"]

def gerar_objetivo(persona):
    p = (
        f"Escopo do agente:\n{escopo}\n\n"
        f"Persona do cliente: {persona}\n\n"
        f"Crie UM objetivo diferente para essa persona testar o agente. "
        f"Realista, dentro do escopo, especifico. 1 frase curta. "
        f"Retorne JSON: {{\"objetivo\": \"...\"}}"
    )
    return json.loads(chamar_gpt(p, json_mode=True))["objetivo"]

def fala_cliente(persona, objetivo, historico):
    h = "\n".join(f"{m['quem']}: {m['txt']}" for m in historico) or "(inicio)"
    p = (
        f"Voce e um USUARIO enviando mensagem para um SISTEMA DE ATENDIMENTO AUTOMATIZADO (bot).\n"
        f"Nao e um humano do outro lado. E um sistema.\n\n"
        f"Sua persona: {persona}\n"
        f"Seu objetivo: {objetivo}\n\n"
        f"Regras:\n"
        f"- Mensagens CURTAS. Maximo 1 frase.\n"
        f"- NAO revele tudo de uma vez. So responda o que o sistema pediu.\n"
        f"- Primeira mensagem: so diga o que quer, nada mais.\n"
        f"- Linguagem informal e natural.\n"
        f"- Use apenas dados coerentes com o escopo: {escopo}\n"
        f"- NAO pergunte dados do sistema (nome, email, telefone do bot).\n"
        f"- Se objetivo resolvido: agradeca em 1 frase e termine com FIM.\n\n"
        f"Historico:\n{h}\n\nSua proxima mensagem:"
    )
    return chamar_gpt(p)

def fala_alvo(aid, thread_id, msg):
    r = alvo.runs.wait(thread_id=thread_id, assistant_id=aid,
                       input={"messages": [{"role": "user", "content": msg}]})
    msgs = r.get("messages", []) if isinstance(r, dict) else []
    for m in reversed(msgs):
        if m.get("type") == "ai" or m.get("role") == "assistant":
            c = m.get("content", "")
            return c if isinstance(c, str) else " ".join(x.get("text", "") for x in c if x.get("type") == "text")
    return ""

def julgar(persona, objetivo, historico):
    transcricao = "\n".join(f"{m['quem']}: {m['txt']}" for m in historico)
    p = (
        f"Avalie o ATENDENTE (sistema de suporte) nesta conversa.\n\n"
        f"Escopo esperado:\n{escopo}\n\n"
        f"Persona: {persona}\nObjetivo: {objetivo}\n\n"
        f"Conversa:\n{transcricao}\n\n"
        f"Retorne JSON: nota (0-100), pontos_fortes (lista), melhorias (lista), "
        f"trechos_de_falha (lista de trechos literais ruins, vazia se nao houver)."
    )
    return json.loads(chamar_gpt(p, json_mode=True))

SINAIS_ENCERRAMENTO = [
    "transferir", "transferindo", "humano", "atendente humano",
    "agente humano", "falar com humano", "passar para", "encaminhar"
]

st.markdown("---")

with st.spinner("Gerando persona..."):
    persona = gerar_persona()

st.markdown(f'<div class="persona-pill">👤 Persona: {persona}</div>', unsafe_allow_html=True)


def rodar_conversa_completa(indice):
    objetivo = gerar_objetivo(persona)
    thread_id = alvo.threads.create()["thread_id"]

    historico = []
    motivo_parada = ("badge-gray", "⏱️ Limite de mensagens atingido")
    for _ in range(8):
        c = fala_cliente(persona, objetivo, historico)
        historico.append({"quem": "CLIENTE", "txt": c})
        if "FIM" in c:
            motivo_parada = ("badge-green", "✅ Problema resolvido")
            break
        a = fala_alvo(assistant_id, thread_id, c)
        historico.append({"quem": "ATENDENTE", "txt": a})
        if any(s in a.lower() for s in SINAIS_ENCERRAMENTO):
            motivo_parada = ("badge-blue", "🔀 Transferência para humano")
            break

    avaliacao = julgar(persona, objetivo, historico)
    return {
        "indice": indice,
        "objetivo": objetivo,
        "thread_id": thread_id,
        "historico": historico,
        "motivo_parada": motivo_parada,
        "avaliacao": avaliacao,
    }


st.info(f"🚀 Rodando {n_conversas} conversa(s) em paralelo...")
progress = st.progress(0)
resultados_raw = []

with ThreadPoolExecutor(max_workers=min(n_conversas, 5)) as ex:
    futures = [ex.submit(rodar_conversa_completa, i) for i in range(n_conversas)]
    concluidas = 0
    for fut in as_completed(futures):
        resultados_raw.append(fut.result())
        concluidas += 1
        progress.progress(concluidas / n_conversas)

progress.empty()
resultados_raw.sort(key=lambda x: x["indice"])

resultados = []
for dados in resultados_raw:
    i = dados["indice"]
    objetivo = dados["objetivo"]
    thread_id = dados["thread_id"]
    historico = dados["historico"]
    motivo_parada = dados["motivo_parada"]
    r = dados["avaliacao"]
    nota = r.get("nota", 0)

    badge_cls, badge_txt = motivo_parada
    chat_html = '<div class="chat-wrap">'
    for msg in historico:
        txt = msg["txt"].replace("FIM", "").strip()
        if msg["quem"] == "CLIENTE":
            chat_html += f'<div><div class="bubble-label">Cliente</div><div class="bubble-user">{txt}</div></div>'
        else:
            chat_html += f'<div style="display:flex;flex-direction:column;align-items:flex-end"><div class="bubble-label-right">Agente</div><div class="bubble-bot">{txt}</div></div>'
    chat_html += '</div>'

    cor_nota = "#2e7d32" if nota >= 70 else "#e65100" if nota >= 50 else "#c62828"

    st.markdown(f"""
    <div class="conversa-card">
      <div class="conversa-header">Conversa {i+1} de {n_conversas} · <code style="font-size:11px;color:#aaa">{thread_id}</code></div>
      <div class="conversa-title">🎯 {objetivo}</div>
      <span class="badge {badge_cls}">{badge_txt}</span>
      {chat_html}
      <div class="nota-box">
        <div class="nota-num" style="color:{cor_nota}">{nota}</div>
        <div>
          <div style="font-weight:600;color:#1a1a2e;font-size:14px;">Nota /100</div>
          <div class="nota-label">Avaliação do agente</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    resultados.append(nota)

# Melhorias gerais com base em todas as conversas
with st.spinner("Gerando análise geral..."):
    todas_transcricoes = "\n\n---\n\n".join(
        f"Conversa {d['indice']+1} (nota {d['avaliacao'].get('nota',0)}):\n" +
        "\n".join(f"{m['quem']}: {m['txt']}" for m in d["historico"])
        for d in resultados_raw
    )
    p_geral = (
        f"Você analisou {n_conversas} conversa(s) de teste de um agente de suporte.\n\n"
        f"Escopo do agente:\n{escopo}\n\n"
        f"Todas as conversas:\n{todas_transcricoes}\n\n"
        f"Com base em TODAS as conversas, identifique padrões e retorne JSON com:\n"
        f"melhorias (lista de melhorias prioritárias que se repetem ou são críticas), "
        f"pontos_fortes (lista de comportamentos consistentemente bons)."
    )
    analise_geral = json.loads(chamar_gpt(p_geral, json_mode=True))

media = sum(resultados) / len(resultados)
cor_media = "#2e7d32" if media >= 70 else "#e65100" if media >= 50 else "#c62828"
placar_html = "".join(
    '<span style="background:#f5f6fa;border:1px solid #e8e8e8;border-radius:8px;padding:6px 14px;font-size:13px;color:#1a1a2e;">'
    f"C{idx+1}: <b style='color:#FF6B00'>{n}</b></span>"
    for idx, n in enumerate(resultados)
)
ml_geral = "".join(f"<li style='margin-bottom:6px'>{m}</li>" for m in analise_geral.get("melhorias", []))
pf_geral = "".join(f"<li style='margin-bottom:6px'>{p}</li>" for p in analise_geral.get("pontos_fortes", []))

st.markdown(f"""
<div class="resumo-card">
  <div style="font-size:12px;font-weight:600;letter-spacing:1px;text-transform:uppercase;color:#aaa;margin-bottom:8px;">Resultado Geral · {n_conversas} conversa(s)</div>
  <div class="resumo-nota" style="color:{cor_media}">{media:.0f}<span style="font-size:22px;color:#bbb;font-weight:400">/100</span></div>
  <div class="resumo-label">Nota média do agente</div>
  <div style="margin-top:20px;display:flex;justify-content:center;gap:10px;flex-wrap:wrap;">
    {placar_html}
  </div>
  <hr style="border:none;border-top:1px solid #f0f0f0;margin:28px 0 20px 0;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;text-align:left;">
    <div style="background:#f9fdf9;border:1px solid #d4edda;border-radius:10px;padding:18px;">
      <div style="font-size:13px;font-weight:700;color:#2e7d32;margin-bottom:10px;">✅ Pontos fortes gerais</div>
      <ul style="margin:0;padding-left:18px;font-size:13px;color:#444;line-height:1.9">{pf_geral}</ul>
    </div>
    <div style="background:#fffaf5;border:1px solid #ffe0c0;border-radius:10px;padding:18px;">
      <div style="font-size:13px;font-weight:700;color:#e05e00;margin-bottom:10px;">⚠️ Melhorias prioritárias</div>
      <ul style="margin:0;padding-left:18px;font-size:13px;color:#444;line-height:1.9">{ml_geral}</ul>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
