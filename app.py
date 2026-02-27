import streamlit as st
import requests
import os
import base64

# ---------------------------------------------------
# FUNÇÃO PARA CARREGAR IMAGEM LOCAL (BASE64)
# ---------------------------------------------------
def get_base64_img(img_path):
    try:
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

# Tenta carregar a imagem que está na sua pasta do Hugging Face
img_base64 = get_base64_img("eu_ia_foto.jpg")

# ---------------------------------------------------
# CONFIGURAÇÃO E ESTILO
# ---------------------------------------------------
st.set_page_config(page_title="Alosa IA", page_icon="💬", layout="wide")

st.markdown(f"""
<style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #ECE5DD; }}
    
    /* HEADER FIXO WHATSAPP */
    .wa-header {{
        background-color: #075E54;
        padding: 10px 20px;
        display: flex;
        align-items: center;
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: 999;
    }}
    .profile-pic {{
        width: 40px; height: 40px;
        background-color: #f0f0f0;
        border-radius: 50%;
        margin-right: 15px;
        display: flex; justify-content: center; align-items: center;
        overflow: hidden;
    }}
    .profile-pic img {{
        width: 100%; height: 100%;
        object-fit: cover;
    }}
    .contact-info {{ color: white; font-family: sans-serif; }}
    .contact-name {{ font-weight: bold; font-size: 14px; margin: 0; }}
    .contact-status {{ font-size: 11px; margin: 0; opacity: 0.8; }}
    .chat-space {{ margin-top: 80px; }}
    
    /* BOLHAS ORIGINAIS */
    html, body, [class*="st-"], p, div, span {{ color: #000000; }}
    .bubble {{ padding: 12px; border-radius: 10px; margin-bottom: 10px; max-width: 85%; font-family: sans-serif; }}
    
    /* USUÁRIO: TEXTO BRANCO */
    .user {{ background-color: #075E54; color: #FFFFFF !important; margin-left: auto; }}
    .user p, .user span {{ color: #FFFFFF !important; }}
    
    /* BOT: TEXTO PRETO */
    .bot {{ background-color: #FFFFFF; color: #000000 !important; margin-right: auto; border: 1px solid #e6e6e6; }}
    
    /* AJUSTE DO INPUT (PARA ENXERGAR O QUE DIGITA) */
    [data-testid="stChatInput"] textarea {{
        color: #000000 !important;
        background-color: #ffffff !important;
    }}
</style>
<div class="wa-header">
    <div class="profile-pic">
        <img src="data:image/jpeg;base64,{img_base64}">
    </div>
    <div class="contact-info">
        <p class="contact-name">Alosa — Assistente do Rodrigo Aiosa</p>
        <p class="contact-status">online</p>
    </div>
</div>
<div class="chat-space"></div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LÓGICA E DIRETRIZES
# ---------------------------------------------------
def carregar_contexto():
    if os.path.exists("instrucoes.txt"):
        with open("instrucoes.txt", "r", encoding="utf-8") as f:
            base = f.read()
    else:
        base = "Você é o Alosa, assistente técnico."

    reforco = (
        "\n\n### REGRA DE LINK:\n"
        "Sempre que o usuário falar de cursos online, responda com este link exato: "
        "https://rodrigoaiosa.streamlit.app/cursos_online\n"
        "Escreva o link normalmente no texto, o sistema irá reconhecer."
    )
    return base + reforco

def perguntar_ia(messages):
    token = st.secrets.get("HF_TOKEN")
    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct",
        "messages": messages,
        "temperature": 0.2
    }
    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=25)
        return r.json()["choices"][0]["message"]["content"]
    except Exception:
        return "Erro de conexão. Tente novamente."

# ---------------------------------------------------
# EXIBIÇÃO DAS MENSAGENS
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": carregar_contexto()}]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        tipo = "user" if msg["role"] == "user" else "bot"
        st.markdown(f'<div class="bubble {tipo}">{msg["content"]}</div>', unsafe_allow_html=True)

placeholder = st.empty()

if prompt := st.chat_input("Como posso ajudar em seu projeto de dados?"):
    with placeholder:
        st.markdown(f'<div class="bubble user">{prompt}</div>', unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.spinner("Alosa analisando..."):
        resposta = perguntar_ia(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
    
    st.rerun()
