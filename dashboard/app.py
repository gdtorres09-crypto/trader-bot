import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
from datetime import datetime

# Configuração da Página
st.set_page_config(
    page_title="SPORTS TRADER AI - Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Estilo Personalizado
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Título
st.title("🤖 SPORTS TRADER AI - PAINEL PROFISSIONAL")
st.markdown("---")

# Funções de Dados
def load_history():
    if os.path.exists("data/signals_history.json"):
        with open("data/signals_history.json", 'r') as f:
            data = json.load(f)
            # Transformar set em lista de dicts se necessário
            return pd.DataFrame(data, columns=["Home", "Away", "Mercado", "Odd"])
    return pd.DataFrame()

# Sidebar - Gestão de Banca
st.sidebar.header("💰 GESTÃO DE BANCA")
bankroll = st.sidebar.number_input("Banca Atual (R$)", min_value=0.0, value=1000.0)
st.sidebar.markdown(f"**Stake Alta (3%):** R$ {bankroll * 0.03:.2f}")
st.sidebar.markdown(f"**Stake Média (2%):** R$ {bankroll * 0.02:.2f}")
st.sidebar.markdown(f"**Stake Baixa (1%):** R$ {bankroll * 0.01:.2f}")

# Layout Principal - Três Colunas
col1, col2, col3 = st.columns(3)

df_history = load_history()

with col1:
    st.metric("Total de Sinais", len(df_history))
with col2:
    st.metric("Greens (Simulados)", f"{len(df_history) * 0.6:.0f}") # Mock stats
with col3:
    st.metric("ROI Estimado", "+12.5%", delta="+2.1%")

# Aba de Sinais Ativos
st.subheader("🔥 ÚLTIMAS OPORTUNIDADES DETECTADAS")
if not df_history.empty:
    # Exibir os últimos 10 sinais invertidos (mais recentes primeiro)
    st.table(df_history.tail(10).iloc[::-1])
else:
    st.info("Nenhum sinal detectado ainda. O robô está escaneando...")

# Gráfico de Crescimento
st.subheader("📈 PERFORMANCE DO SISTEMA")
if not df_history.empty:
    chart_data = pd.DataFrame({
        "Dia": range(1, len(df_history) + 1),
        "Banca": [bankroll * (1.01**i) for i in range(len(df_history))] # Simulação de crescimento
    })
    fig = px.line(chart_data, x="Dia", y="Banca", title="Evolução da Banca (Simulada)")
    st.plotly_chart(fig, use_container_width=True)

# Rodapé
st.markdown("---")
st.caption(f"Sistema Autônomo Ativo - Última verificação: {datetime.now().strftime('%H:%M:%S')}")
