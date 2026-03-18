import streamlit as st
import pandas as pd
import sqlite3
from app_config.settings import DB_PATH
import plotly.express as px

def main():
    st.set_page_config(page_title="SPORTS_BETTING_ANALYST_AI Dashboard", layout="wide")
    
    st.title("🏆 Betting Analyst Dashboard")
    st.sidebar.header("Filtros")
    
    # Conectar ao DB
    try:
        conn = sqlite3.connect(DB_PATH)
        df_matches = pd.read_sql_query("SELECT * FROM matches", conn)
        df_history = pd.read_sql_query("SELECT * FROM bet_history", conn)
        conn.close()
    except:
        st.warning("Banco de dados não encontrado ou vazio. Mostrando dados de exemplo.")
        df_matches = pd.DataFrame(columns=["id", "home_team", "away_team", "value_detected", "league"])
        df_history = pd.DataFrame(columns=["match_id", "profit", "result"])

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Jogos Analisados", len(df_matches))
    with col2:
        st.metric("Value Bets Detectadas", len(df_matches[df_matches['value_detected'] == 1]))
    with col3:
        profit = df_history['profit'].sum() if not df_history.empty else 0
        st.metric("Lucro Acumulado", f"R$ {profit:.2f}", delta=f"{profit:.2f}")

    st.divider()
    
    st.subheader("📈 Performance por Liga")
    if not df_matches.empty:
        fig = px.bar(df_matches.groupby('league').size().reset_index(name='count'), x='league', y='count', title="Jogos por Liga")
        st.plotly_chart(fig)
    else:
        st.info("Nenhum dado para exibir no gráfico.")

    st.subheader("📋 Últimos Jogos Analisados")
    st.dataframe(df_matches.tail(10))

if __name__ == "__main__":
    main()
