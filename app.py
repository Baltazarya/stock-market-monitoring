import streamlit as st
from ETL import fetch_stock_data, init_db, insert_data, get_symbols, get_stock_data
from symbols import symbols
import plotly.express as px

init_db() # Inicializa o DB

st.title('📈 Stock Dashboard (PostgreSQL)')

symbol = st.selectbox('Selecione uma ação:', options=symbols, index=0)

if st.button('Buscar e Salvar Dados'):
    try:
        df = fetch_stock_data(symbol) # Função para buscar os dados da ação pela API
        insert_data(symbol, df) # Função para inserir os dados no DB
        st.success('Dados inseridos com sucesso!')
    except ValueError as e:
        st.error(str(e))

st.subheader('Visualizar Dados Salvos')

symbols = get_symbols() # Função para obter os símbolos de ações disponíveis no DB

if not symbols.empty:
    selected_symbol = st.selectbox('Selecione a ação', symbols['symbol'])
    df = get_stock_data(selected_symbol) # Função para obter os dados de uma ação do DB apartir do símbolo selecionado

    if not df.empty:
        fig = px.line(df, x='date', y='close', title=f'Preço de Fechamento - {selected_symbol}')
        st.plotly_chart(fig)