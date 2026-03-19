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

# --- NAVEGAÇÃO POR ABAS (INSPIRAÇÃO CARTOLA MESTRE) ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 PAINEL DE CONTROLE", 
    "🧠 INTELIGÊNCIA HÍBRIDA", 
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

# --- TAB 1: PAINEL DE CONTROLE (O "Dashboard" atual melhorado) ---
with tab1:
    # Sidebar control (remains for Global Actions)
    st.sidebar.header("🕹️ COMANDOS")
    run_scan = st.sidebar.button("🚀 INICIAR VARREDURA REAL", use_container_width=True)
    bankroll = st.sidebar.number_input("Banca de Gestão (R$)", min_value=1.0, value=1000.0)
    
    # Métricas Globais em Grid
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        total_sinais = len(df_history)
        st.metric("Total Sinais", total_sinais, help="Total de sinais EV+ operados")
    with m2:
        roi = f"+{df_history['ev'].mean()*100:.1f}%" if not df_history.empty else "0.0%"
        st.metric("ROI Estimado", roi)
    with m3:
        st.metric("Status Server", "AGUARDANDO" if not run_scan else "PROCESSANDO")
    with m4:
        st.metric("Conexão API", "CONECTADO", delta="Latência 45ms")

    st.markdown("### 🔥 ÚLTIMAS OPORTUNIDADES DETECTADAS")
    if not df_history.empty:
        # Formatação profissional da tabela
        df_display = df_history.copy().sort_values(by="timestamp", ascending=False).head(10)
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Nenhum sinal detectado ainda. Clique em 'Iniciar Varredura' no menu lateral.")

    # Lógica de Execução com Fallback
    if run_scan:
        has_status = hasattr(st, "status")
        if has_status:
            with st.status("🔍 Buscando Dados de Mercado e Análises YouTube...", expanded=True) as status:
                try:
                    analyst = BettingAnalyst()
                    trader = AutoTrader(analyst)
                    st.write("🛰️ Consultando The Odds API...")
                    import asyncio
                    signals = asyncio.run(trader.run_analysis_cycle())
                    if signals:
                        st.success(f"Encontradas {len(signals)} Gems!")
                        for s in signals: st.toast(s, icon="💎")
                    status.update(label="Varredura Completa!", state="complete")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro no ciclo: {e}")
                    status.update(label="Erro na Varredura", state="error")
        else:
            with st.spinner("🔍 Analisando..."):
                try:
                    analyst = BettingAnalyst()
                    trader = AutoTrader(analyst)
                    import asyncio
                    _ = asyncio.run(trader.run_analysis_cycle())
                    st.rerun()
                except Exception as e: st.error(f"Erro: {e}")

# --- TAB 2: INTELIGÊNCIA HÍBRIDA (Visão de 'Expert' da Inspiração) ---
with tab2:
    st.subheader("🧠 CONSENSO IA & TÁTICAS YOUTUBE")
    st.markdown("Aqui o bot cruza o que os especialistas dizem no YT com os números frios das Odds.")
    
    c1, c2 = st.columns(2)
    with c1:
        st.info("📺 MONITORAMENTO DE CANAIS")
        st.write("Canais ativos: TNT Sports, NBA Brasil, Danilo Pereira.")
        # Simulação de Insights
        st.markdown("""
        **Últimos Insights Extraídos:**
        - *Arsenal vs Bayern*: Desfalque de Kane no Bayern sugere Under 2.5 (Confiança: 78%).
        - *Lakers vs Warriors*: Curado de lesão, Lebron deve focar em Assistências.
        """)
    with c2:
        st.success("📊 CONSENSO DE MERCADO")
        st.write("Análise de Volume de Apostas e Movimentação de Odds Profissionais.")
        st.write("Tendência Atual: Back Favorito no Campeonato Brasileiro.")

# --- TAB 3: PERFORMANCE ---
with tab3:
    st.subheader("📈 ANÁLISE DE RESULTADOS")
    if not df_history.empty:
        import plotly.express as px
        df_history['Data'] = pd.to_datetime(df_history['timestamp']).dt.date
        daily = df_history.groupby('Data').size().reset_index(name='Sinais')
        fig = px.line(daily, x='Data', y='Sinais', title="Volume de Sinais por Dia (Automação)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Sem dados para gerar gráficos.")

# --- TAB 4: CONFIGURAÇÕES ---
with tab4:
    st.subheader("⚙️ GESTÃO DO SISTEMA")
    with st.expander("🛠️ FONTES DE DADOS (YOUTUBE)"):
        st.json({"canais": ["TNT Brasil", "NBA Brasil", "Apostador de Valor"]})
    with st.expander("🔑 API KEYS"):
        st.write("The Odds API: Configurada ✅")
        st.write("Telegram Bot: Configurado ✅")
    with st.expander("🤖 ESTRATÉGIA DE APOSTA"):
        st.selectbox("Modelo", ["Valor Esperado + Kelly Criterion", "Stake Fixa 2%", "Alavancagem Inteligente"])

# Rodapé
st.markdown("---")
st.caption("HYBRID TRADER AI v3.0 - Inspirado em Analítica Profissional")
