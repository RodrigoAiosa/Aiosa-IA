import streamlit as st
import google.generativeai as genai
import os
import base64

# ---------------------------------------------------
# CONFIGURAÇÃO DA API DO GOOGLE
# ---------------------------------------------------
# O token é lido do Streamlit Secrets configurado no painel
GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Utilizamos o modelo flash para maior velocidade
model = genai.GenerativeModel('gemini-1.5-flash')

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

img_base64 = get_base64_img("eu_ia_foto.jpg")

# ---------------------------------------------------
# CONFIGURAÇÃO E ESTILO (UI WHATSAPP)
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
    
    /* BOLHAS DE CHAT */
    .bubble {{ padding: 12px; border-radius: 10px; margin-bottom: 10px; max-width: 85%; font-family: sans-serif; }}
    
    /* USUÁRIO: TEXTO BRANCO */
    .user {{ background-color: #075E54; color: #FFFFFF !important; margin-left: auto; }}
    .user p, .user span {{ color: #FFFFFF !important; }}
    
    /* BOT: TEXTO PRETO */
    .bot {{ background-color: #FFFFFF; color: #000000 !important; margin-right: auto; border: 1px solid #e6e6e6; }}
    
    /* AJUSTE DO INPUT */
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
# LÓGICA DE CONTEXTO E PERSONA (GEMINI)
# ---------------------------------------------------
def carregar_instrucoes():
    """Lê as instruções de persona do arquivo txt"""
    if os.path.exists("instrucoes.txt"):
        with open("instrucoes.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "Você é o Alosa, assistente comercial estratégico do Rodrigo Aiosa."

def perguntar_ia(mensagens_historico):
    """Envia o histórico de chat para o Gemini"""
    try:
        instrucoes_persona = carregar_instrucoes()
        chat = model.start_chat(history=[])
        
        # Constrói o prompt unindo as instruções com a pergunta atual
        full_prompt = f"{instrucoes_persona}\n\nPERGUNTA DO USUÁRIO: {mensagens_historico[-1]['content']}"
        
        response = chat.send_message(full_prompt)
        return response.text
    except Exception as e:
        return f"Erro de conexão. Tente novamente mais tarde. (Detalhe: {str(e)})"

# ---------------------------------------------------
# EXIBIÇÃO DAS MENSAGENS E INTERAÇÃO
# ---------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe o histórico
for msg in st.session_state.messages:
    tipo = "user" if msg["role"] == "user" else "bot"
    st.markdown(f'<div class="bubble {tipo}">{msg["content"]}</div>', unsafe_allow_html=True)

# Entrada do usuário
if prompt := st.chat_input("Como posso ajudar em seu projeto de dados?"):
    # Exibe a mensagem do usuário
    st.markdown(f'<div class="bubble user">{prompt}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Processa a resposta da IA
    with st.spinner("Alosa analisando..."):
        resposta = perguntar_ia(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
    
    st.rerun()
