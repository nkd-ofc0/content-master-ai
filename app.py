import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq
from urllib.parse import urlparse, parse_qs
from datetime import datetime 
# CORREÇÃO DEFINITIVA: Importamos o módulo inteiro para evitar conflitos de nomes.
import youtube_transcript_api 

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Content Master AI", page_icon="💡", layout="wide")

# --- LINKS DE FERRAMENTAS ---
LINK_ASSINATURA = "https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id=SEU_LINK_AQUI"
LINK_CARROSSEL_IA = "https://www.manus.ai"
LINK_EDICAO_VIDEO = "https://www.capcut.com"

# --- BACKEND E SEGURANÇA ---
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
    CLIENTES_ATIVOS = [email.strip().lower() for email in st.secrets["CLIENTES_ATIVOS"].split(",")]
except Exception:
    CLIENTES_ATIVOS = []
    GROQ_API_KEY = ""
    
# --- FUNÇÕES DE BUSCA DE DADOS ---

def extract_youtube_id(url):
    """Extrai o ID do vídeo de uma URL do YouTube."""
    if 'youtu.be' in url:
        return url.split('/')[-1].split('?')[0]
    if 'youtube.com' in url:
        query = urlparse(url).query
        params = parse_qs(query)
        if 'v' in params:
            return params['v'][0]
    return None

def get_video_transcript(video_url):
    """Retorna a transcrição completa do YouTube."""
    video_id = extract_youtube_id(video_url)
    if not video_id:
        return "URL inválida.", False
    try:
        # CHAMADA CORRIGIDA: Usamos o caminho completo do módulo para a função.
        transcript_list = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])
        transcript_text = " ".join([item['text'] for item in transcript_list])
        return transcript_text, True
    except Exception as e:
        return f"Erro ao obter transcrição: {str(e)}", False

def generate_content(transcript, content_type, user_style):
    client = Groq(api_key=GROQ_API_KEY)
    
    # ------------------ ENGENHARIA DE PROMPT DIFERENCIADA ------------------
    if content_type == "Carrossel Instagram":
        prompt_especifico = f"""
        OBJETIVO: Criar uma sequência de 5 a 7 slides para um Carrossel de Instagram de alta conversão.
        INSTRUÇÃO: Gere o texto EXATO que o usuário deve copiar e colar no Manus AI ou Canva.
        FORMATO: Apresente o resultado em uma lista numerada.
        - Slide 1 (Capa): Título Chamativo e Subtítulo.
        - Slides 2-6 (Conteúdo): Tópicos com bullet points extraídos da transcrição.
        - Último Slide: Chamada para Ação (CTA).
        ESTILO DE DESIGN: {user_style}.
        TRANSCRICÃO: {transcript}
        """
        link_externo = f"Ferramenta sugerida (Carrossel): [Manus AI]({LINK_CARROSSEL_IA})"

    elif content_type == "Reel (Roteiro Dinâmico)":
        prompt_especifico = f"""
        OBJETIVO: Criar um ROTEIRO de 30 segundos (Reel/Short) que viralize.
        INSTRUÇÃO: Analise a transcrição e identifique os 3 pontos mais impactantes. Crie um script de cortes dinâmicos.
        FORMATO: Gere um script para o usuário usar no CapCut/InVideo.
        - CENA 1 (3s): Hook (Frase de Efeito tirada do vídeo).
        - CENA 2-5 (20s): Cortes dinâmicos (Frases Chave).
        - CENA 6 (7s): CTA (O que o espectador deve fazer).
        ESTILO DE EDIÇÃO: {user_style}.
        TRANSCRICÃO: {transcript}
        """
        link_externo = f"Ferramenta sugerida (Edição e Cortes): [CapCut Online]({LINK_EDICAO_VIDEO})"

    else: # SEO Blog Post
        prompt_especifico = f"""
        OBJETIVO: Criar um Artigo de Blog de 500 palavras otimizado para SEO (otimizado para Google) a partir da transcrição.
        ESTRUTURA: Título H1, Subtítulos H2, Parágrafos curtos, Meta Description (resumo de 160 caracteres).
        ESTILO: {user_style}.
        TRANSCRICÃO: {transcript}
        """
        link_externo = "Ferramenta sugerida (Otimização SEO): [Semrush Writing Tools]"


    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt_especifico}],
        model="llama-3.3-70b-versatile",
        temperature=0.7
    )
    return chat_completion.choices[0].message.content, link_externo

# --- INTERFACE E LOGIN ---

st.markdown("<h1 class='hero-title'>Content Master AI 💡</h1>", unsafe_allow_html=True)
st.markdown("<p class='hero-sub'>Transforme 1 hora de vídeo em um mês de conteúdo vendável. Você é o Diretor de Criação, a IA faz o resto.</p>", unsafe_allow_html=True)

col_app, col_login = st.columns([2.5, 1])

# LADO DIREITO: LOGIN E VENDA
with col_login:
    with st.container(border=True):
        st.markdown("### 🔐 Área de Acesso Premium")
        email_input = st.text_input("E-mail de Assinante", key="login_email").strip().lower()
        
        if st.button("Validar Acesso", use_container_width=True):
            if email_input in CLIENTES_ATIVOS:
                st.session_state.email_usuario = email_input
                st.session_state.logado = True
                st.toast("Acesso Liberado! Bem-vindo.", icon="🎉")
                st.rerun()
            else:
                st.error("Assinatura não encontrada.")
        
        # Estado de Login
        if 'email_usuario' in st.session_state and st.session_state.email_usuario in CLIENTES_ATIVOS:
            st.success(f"✅ Logado como: {st.session_state.email_usuario}")
        
        st.markdown("---")
        st.markdown("#### 🚀 Assine para Produção Ilimitada")
        st.markdown("<h2 style='text-align:center; color:#00C853; margin:0;'>R$ 29,90<span style='font-size:1rem; color:#888'>/mês</span></h2>", unsafe_allow_html=True)
        st.link_button("ASSINAR AGORA", LINK_ASSINATURA, type="primary", use_container_width=True)

# LADO ESQUERDO: A MÁQUINA DE CONTEÚDO
with col_app:
    st.subheader("🛠️ Máquina de Geração de Conteúdo")
    
    if 'email_usuario' not in st.session_state or st.session_state.email_usuario not in CLIENTES_ATIVOS:
        st.warning("🔒 Assine ao lado para liberar a máquina.")
        st.image("https://placehold.co/800x400/eeeeee/cccccc?text=Area+Bloqueada.+Conteudo+Premium+para+Assinantes", use_column_width=True)
    else:
        # CONTROLES DE CRIAÇÃO (O NOVO DIFERENCIAL)
        st.caption(f"Olá, {st.session_state.email_usuario.split('@')[0]}! Qual tipo de conteúdo você precisa?")
        
        url_video = st.text_input("Cole a URL do Vídeo do YouTube", placeholder="https://www.youtube.com/watch?v=...")
        
        tipo_conteudo = st.selectbox("Formato de Saída (O que você quer criar?)", 
                                     ["Reel (Roteiro Dinâmico)", "Carrossel Instagram", "SEO Blog Post"],
                                     key="tipo_saida")
        
        estilo_prompt = st.text_area("Estilo, Nicho ou Instrução Específica", 
                                     placeholder="Ex: Tom formal, focado no nicho de finanças, e use a palavra 'alavancagem'.", 
                                     height=80)
        
        if st.button("GERAR BLUEPRINT PREMIUM", type="primary", use_container_width=True):
            if not url_video:
                st.error("Por favor, cole a URL do vídeo.")
            else:
                with st.spinner("Lendo a alma do seu vídeo e programando a criação..."):
                    # 1. Obter Transcrição
                    transcript, sucesso = get_video_transcript(url_video)
                    
                    if not sucesso:
                        st.error(f"Erro ao obter transcrição: {transcript}. Verifique se o vídeo tem legendas ativas ou se a URL está correta.")
                    else:
                        # 2. Gerar Prompt/Instruções
                        blueprint, link_ferramenta = generate_content(transcript, tipo_conteudo, estilo_prompt)
                        
                        st.success("✅ BLUEPRINT PREMIUM GERADO COM SUCESSO!")
                        st.markdown("---")
                        
                        st.markdown("### 📄 Instruções para a IA / Editor:")
                        st.code(blueprint, language="markdown")
                        
                        st.markdown("---")
                        st.markdown("### 🔗 PRÓXIMO PASSO (Ação do Cliente):")
                        st.link_button(f"Clique aqui para ir para a ferramenta sugerida ({tipo_conteudo})", link_ferramenta, type="secondary")

# --- RODAPÉ ---
st.markdown("<br><br><br><br>", unsafe_allow_html=True)
st.markdown(f"""
<div style='position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; font-size: 0.8rem; color: #888;'>
    Content Master AI © {datetime.now().year} • O Seu Novo Diretor de Criação.
</div>
""", unsafe_allow_html=True)
