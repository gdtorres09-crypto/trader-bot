import streamlit as st
import pandas as pd
import json
import os
import sys
import plotly.express as px
from datetime import datetime
import logging

# Configuração de Página Luxuosa
st.set_page_config(
    page_title="HYBRID TRADER AI - PRO",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SISTEMA DE DESIGN PREMIUM (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #0E1117;
    }

    /* Glassmorphism Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        color: white;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: #00FF00;
        transform: translateY(-5px);
    }

    /* Branded Header */
    .app-header {
        background: linear-gradient(90deg, #00FF00 0%, #008000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0px;
    }
    
    .status-badge {
        background: rgba(0, 255, 0, 0.1);
        border: 1px solid #00FF00;
        color: #00FF00;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
    }

    /* Customizing sidebar */
    .stSidebar {
        background-color: #161B22 !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #00FF00 !important;
        color: #000 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Adicionar raiz do projeto ao path
root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

from agents.betting_analyst import BettingAnalyst
from core.auto_trader import AutoTrader

# --- HEADER PROFISSIONAL ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<p class="app-header">HYBRID TRADER AI</p>', unsafe_allow_html=True)
    st.markdown('<span class="status-badge">● LIVE MARKET SCANNER</span>', unsafe_allow_html=True)
with col_h2:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=80)

st.markdown("<br>", unsafe_allow_html=True)

# --- NAVEGAÇÃO POR ABAS (INSPIRAÇÃO NOTEBOOKLM / CARTOLA MESTRE) ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 PAINEL DE CONTROLE", 
    "🧠 INTELIGÊNCIA HÍBRIDA", 
    "🎨 ESTÚDIO IA",
    "📈 PERFORMANCE & ROI", 
    "⚙️ CONFIGURAÇÕES"
])

# --- FUNÇÕES DE DADOS ---
def load_history():
    path = os.path.join(root_path, "data", "signals_history.json")
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                if not data: return pd.DataFrame()
                df = pd.DataFrame(data)
                return df
        except Exception: return pd.DataFrame()
    return pd.DataFrame()

df_history = load_history()

# CSS ADICIONAL PARA ESTÚDIO
st.markdown("""
<style>
    .studio-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        cursor: pointer;
        transition: 0.2s;
    }
    .studio-card:hover {
        background: rgba(0, 255, 0, 0.05);
        border-color: #00FF00;
    }
    .studio-icon {
        font-size: 1.5rem;
        margin-bottom: 5px;
    }
    .studio-title {
        font-weight: 600;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# --- TAB 1: PAINEL DE CONTROLE ---
with tab1:
    # Sidebar control (remains for Global Actions)
    st.sidebar.header("🕹️ COMANDOS")
    run_scan = st.sidebar.button("🚀 INICIAR VARREDURA REAL", use_container_width=True)
    bankroll = st.sidebar.number_input("Banca de Gestão (R$)", min_value=1.0, value=1000.0)
    
    # Métricas Globais em Grid
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        total_sinais = len(df_history)
        st.metric("Total Sinais", total_sinais)
    with m2:
        roi = f"+{df_history['ev'].mean()*100:.1f}%" if not df_history.empty else "0.0%"
        st.metric("ROI Estimado", roi)
    with m3:
        st.metric("Status Server", "IDLE" if not run_scan else "RUNNING")
    with m4:
        st.metric("Latência", "42ms", delta="-5ms")

    st.markdown("### 🔥 ÚLTIMAS OPORTUNIDADES DETECTADAS")
    if not df_history.empty:
        st.dataframe(df_history.copy().sort_values(by="timestamp", ascending=False).head(10), use_container_width=True)
    else:
        st.info("Nenhum sinal detectado ainda. Inicie a varredura.")

    if run_scan:
        has_status = hasattr(st, "status")
        if has_status:
            with st.status("🔍 Buscando Dados...", expanded=True) as status:
                try:
                    analyst = BettingAnalyst()
                    trader = AutoTrader(analyst)
                    import asyncio
                    signals = asyncio.run(trader.run_analysis_cycle())
                    status.update(label="Varredura Completa!", state="complete")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")
                    status.update(label="Erro", state="error")
        else:
            with st.spinner("Analisando..."):
                try:
                    analyst = BettingAnalyst()
                    trader = AutoTrader(analyst)
                    import asyncio
                    _ = asyncio.run(trader.run_analysis_cycle())
                    st.rerun()
                except Exception as e: st.error(f"Erro: {e}")

# --- TAB 2: INTELIGÊNCIA HÍBRIDA ---
with tab2:
    st.subheader("🧠 CONSENSO YOUTUBE & MERCADO")
    # Mostrar fontes ativas (NotebookLM Style)
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.info("📺 **FONTES YOUTUBE**: 11 Canais (Tifo, NBA, AVBETS...)")
    c2.success("📊 **FONTES MERCADO**: Odds Live (Betano/Kaizen)")
    c3.warning("🧠 **CÉREBRO IA**: GPT-4o / Claude Analysis")
    
    st.markdown("#### Últimos Insights Cross-Reference")
    st.markdown("""
    - **Lakers vs Warriors**: NBA Official + Thinking Basketball reportam fadiga de Curry. (Confiança: 82%)
    - **Arsenal v Bayern**: Tifo Football destaca vulnerabilidade tática do Bayern em transição. (Confiança: 75%)
    """)

# --- TAB 3: ESTÚDIO IA (NOTEBOOKLM STYLE) ---
with tab3:
    st.markdown("### 🎨 ESTÚDIO DE CRIAÇÃO")
    st.markdown("Transforme dados brutos em inteligência digerível.")
    
    # Sub-menu NotebookLM
    sm1, sm2, sm3 = st.columns([1, 1, 4])
    sm1.markdown("**Fontes**")
    sm2.markdown("<span style='border-bottom: 2px solid #00FF00'>**Estúdio**</span>", unsafe_allow_html=True)
    st.markdown("---")

    # Mock de seleção de jogo para o estúdio
    selected_game = None
    if not df_history.empty:
        game_list = [f"{r['home']} vs {r['away']}" for _, r in df_history.head(5).iterrows()]
        choice = st.selectbox("Escolha um Jogo para Analisar no Estúdio:", game_list)
        selected_game = df_history.iloc[0].to_dict() # Simples para o exemplo
    
    # Grid de Cards (NotebookLM)
    row1 = st.columns(4)
    with row1[0]:
        st.markdown('<div class="studio-card"><div class="studio-icon">✨</div><div class="studio-title">Resumo em Áudio</div></div>', unsafe_allow_html=True)
        if st.button("Gerar Podcast", key="audio"):
             analyst = BettingAnalyst()
             res = analyst.generate_studio_content("audio", selected_game)
             st.info(res)
    with row1[1]:
        st.markdown('<div class="studio-card"><div class="studio-icon">📖</div><div class="studio-title">Apresentação</div></div>', unsafe_allow_html=True)
        if st.button("Gerar Slides", key="slides"): st.code(f"# Slides: {selected_game['home'] if selected_game else 'Geral'}\n- Key Metrics\n- Top Picks")
    with row1[2]:
        st.markdown('<div class="studio-card"><div class="studio-icon">📽️</div><div class="studio-title">Resumo em Vídeo</div></div>', unsafe_allow_html=True)
        if st.button("Recortar YT", key="video"): st.write("Highlighting top segments from connected channels...")
    with row1[3]:
        st.markdown('<div class="studio-card"><div class="studio-icon">🧠</div><div class="studio-title">Mapa Mental</div></div>', unsafe_allow_html=True)
        if st.button("Gerar Mapa", key="mindmap"): 
            analyst = BettingAnalyst()
            mermaid_code = analyst.generate_studio_content("mindmap", selected_game)
            st.code(mermaid_code, language="mermaid")

    row2 = st.columns(4)
    with row2[0]:
        st.markdown('<div class="studio-card"><div class="studio-icon">📄</div><div class="studio-title">Relatórios</div></div>', unsafe_allow_html=True)
        if st.button("PDF Pro", key="pdf"): st.success("Relatório PDF pronto para download.")
    with row2[1]:
        st.markdown('<div class="studio-card"><div class="studio-icon">📇</div><div class="studio-title">Cartões Didáticos</div></div>', unsafe_allow_html=True)
        if st.button("Gerar Flashcards", key="flash"): 
            analyst = BettingAnalyst()
            cards = analyst.generate_studio_content("flashcards", selected_game)
            for c in cards: st.write(f"**Q:** {c['Q']}\n**A:** {c['A']}")
    with row2[2]:
        st.markdown('<div class="studio-card"><div class="studio-icon">📝</div><div class="studio-title">Teste</div></div>', unsafe_allow_html=True)
        if st.button("Check Knowledge", key="test"): st.radio("Qual o mercado EV+ sugerido?", ["Vencedor", "Gols", "Handicap"])
    with row2[3]:
        st.markdown('<div class="studio-card"><div class="studio-icon">📊</div><div class="studio-title">Infográfico</div></div>', unsafe_allow_html=True)
        if st.button("Dashboard Visual", key="info"): st.bar_chart(pd.DataFrame({"Prob": [0.6, 0.2, 0.2]}, index=["Home", "Draw", "Away"]))

# --- TAB 4: PERFORMANCE ---
with tab4:
    st.subheader("📈 PERFORMANCE & ROI")
    if not df_history.empty:
        import plotly.express as px
        df_history['Data'] = pd.to_datetime(df_history['timestamp']).dt.date
        daily = df_history.groupby('Data').size().reset_index(name='Sinais')
        st.plotly_chart(px.line(daily, x='Data', y='Sinais', title="Volume de Sinais"), use_container_width=True)
    else:
        st.write("Aguardando dados para gerar performance...")

with tab5:
    st.subheader("⚙️ CONFIGURAÇÕES")
    st.write("Gerencie suas chaves e fontes de dados.")
    with st.expander("📺 Canais de YouTube Conectados"):
        try:
            with open(os.path.join(root_path, "app_config", "youtube_channels.json"), 'r') as f:
                channels = json.load(f)
                st.table(pd.DataFrame(channels))
        except Exception: st.error("Erro ao carregar canais.")

# Rodapé
st.markdown("---")
st.caption("HYBRID TRADER AI - NotebookLM Edition v3.5")
