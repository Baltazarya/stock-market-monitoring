import requests
import pandas as pd
from dotenv import load_dotenv  
import os

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"


# Função para buscar cotações de ações
def get_stock_data(symbol, interval="5min"):
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if "Time Series (5min)" in data:
            time_series = data["Time Series (5min)"]
            # Adiciona o símbolo da ação nos dados
            df = pd.DataFrame.from_dict(time_series, orient="index")
            df.index.name = "Timestamp"
            df.reset_index(inplace=True)
            df["Symbol"] = symbol
            return df
        else:
            print(f"Dados indisponíveis para {symbol}.")
            return pd.DataFrame()  # Retorna DataFrame vazio
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar dados da ação {symbol}: {e}")
        return pd.DataFrame()

# Função para salvar os dados de várias ações em um único arquivo CSV
def save_multiple_stocks_to_csv(symbols, filename):
    all_data = pd.DataFrame()
    
    for symbol in symbols:
        print(f"Buscando dados para {symbol}...")
        stock_data = get_stock_data(symbol)
        if not stock_data.empty:
            all_data = pd.concat([all_data, stock_data], ignore_index=True)
    
    if not all_data.empty:
        all_data.to_csv(filename, index=False)
        print(f"Dados de {len(symbols)} ações salvos em {filename}")
    else:
        print("Nenhum dado disponível para salvar.")

# Exemplo de uso
if __name__ == "__main__":
    stock_symbols = ["AAPL", "MSFT", "GOOGL"]  # Lista de tickers (Apple, Microsoft, Google)
    save_multiple_stocks_to_csv(stock_symbols, "stock_data.csv")