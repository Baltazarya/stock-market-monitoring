import requests
import pandas as pd
from dotenv import load_dotenv  
import os
from sqlalchemy import create_engine, text

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


def fetch_stock_data(symbol):
    """
    Função para buscar dados de ações da API Alpha Vantage e retornar um DataFrame.
    :param symbol: Símbolo da ação (ex: AAPL, MSFT, TSLA)  
    :return: DataFrame com os dados da ação
    """
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" not in data:
        raise ValueError(f"Erro na API para o símbolo {symbol}: {data.get('Error Message', 'Resposta inválida da API.')}")

    df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
    df = df.rename(columns={
        '1. open': 'open',
        '2. high': 'high',
        '3. low': 'low',
        '4. close': 'close',
        '5. volume': 'volume'
    })
    df = df.astype({
        'open': 'float',
        'high': 'float',
        'low': 'float',
        'close': 'float',
        'volume': 'int'
    })
    return df

# LOAD dos dados
# Configuração e criação do banco de dados PostgreSQL

DB_CONFIG = {
    'dbname': 'stock_data',
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'host': os.getenv("DB_HOST"),
    'port': os.getenv("DB_PORT")
}

DATABASE_URL = f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"


engine = create_engine(DATABASE_URL)

def init_db():
    with engine.begin() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS stocks (
                symbol TEXT,
                date DATE,
                open FLOAT,
                high FLOAT,
                low FLOAT,
                close FLOAT,
                volume BIGINT,
                PRIMARY KEY (symbol, date)
            )
        '''))



def insert_data(symbol, df):
    # Função para inserir dados no banco de dados PostgreSQL
    df = df.copy()
    df['symbol'] = symbol
    df = df.reset_index().rename(columns={'index': 'date'})
    df.to_sql('stocks', engine, if_exists='append', index=False, method='multi')

def get_symbols():
    # Função para obter todos os símbolos de ações disponíveis no banco de dados, utilizado para os gráficos e um selectbox do streamlit.
    query = 'SELECT DISTINCT symbol FROM stocks'
    df = pd.read_sql(query, engine)
    return df

def get_stock_data(symbol):
    # Função para obter os dados de uma ação específica do banco de dados, utilizado para os gráficos do streamlit
    query = 'SELECT * FROM stocks WHERE symbol = :symbol ORDER BY date'
    df = pd.read_sql(text(query), engine, params={'symbol': symbol})
    return df