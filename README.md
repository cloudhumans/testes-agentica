# QA de Agentes · CloudHumans

Ferramenta para testar agentes LangGraph/LangSmith com conversas fictícias e avaliações automáticas de qualidade.

## Como funciona

1. Você informa o escopo do agente, o ID do assistente e quantas conversas quer simular
2. O GPT-5 gera uma persona de cliente e um objetivo único para cada conversa
3. O cliente fictício conversa com o agente alvo (via LangSmith/LangGraph)
4. Ao final, o GPT-5 avalia cada conversa e atribui uma nota de 0–100
5. Um resumo geral com pontos fortes e melhorias prioritárias é exibido

## Pré-requisitos

- Python 3.10+
- Conta OpenAI com acesso ao GPT-5
- Conta LangSmith com um agente deployado no LangGraph

## Passo a passo para rodar

### 1. Clone o repositório

```bash
git clone https://github.com/cloudhumans/testes-agentica.git
cd testes-agentica
```

### 2. Crie e ative um ambiente virtual

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Abra o `.env` e preencha com suas chaves:

```
OPENAI_API_KEY=sk-...
LANGSMITH_API_KEY=lsv2_pt_...
```

### 5. (Opcional) Ajuste o URL do LangGraph

Se o seu agente estiver em uma URL diferente da padrão, edite a constante `LANGGRAPH_URL` em `app.py`:

```python
LANGGRAPH_URL = "https://seu-agente.us.langgraph.app"
```

---

## Rodando a interface web (Streamlit)

```bash
streamlit run app.py
```

Acesse em: **http://localhost:8501**

Na interface, preencha:
- **Escopo do agente** — descreva o que o agente faz, o que pode e o que não pode responder
- **ID do agente** — o `assistant_id` do LangSmith
- **Persona do cliente** (opcional) — perfil do usuário fictício; se vazio, o GPT gera automaticamente
- **Número de conversas** — de 1 a 10; todas rodam em paralelo

---

## Rodando pelo terminal (script simples)

Para um teste rápido sem interface, use `testar.py`:

1. Edite as três variáveis no topo do arquivo:

```python
ESCOPO = "Descrição do que o agente faz..."
ASSISTANT_ID = "seu-assistant-id"
LANGGRAPH_URL = "https://seu-agente.us.langgraph.app"
```

2. Execute:

```bash
python testar.py
```

O script imprime a conversa completa e a nota final no terminal.

---

## Estrutura do projeto

```
.
├── app.py              # Interface Streamlit (recomendado)
├── testar.py           # Script de teste via terminal
├── requirements.txt    # Dependências Python
├── .env.example        # Modelo de variáveis de ambiente
├── .streamlit/
│   └── config.toml     # Tema e configurações do Streamlit
└── logo.png            # Logo CloudHumans
```
