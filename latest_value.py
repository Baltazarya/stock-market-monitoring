import requests
import pandas as pd
from dotenv import load_dotenv  
import os

load_dotenv()

API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

# Function to get the latest daily stock value
def get_latest_daily_stock_data(symbol):
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            latest_date = max(time_series.keys())
            latest_data = time_series[latest_date]
            return {
                "Symbol": symbol,
                "Date": latest_date,
                "Open": float(latest_data["1. open"]),
                "High": float(latest_data["2. high"]),
                "Low": float(latest_data["3. low"]),
                "Close": float(latest_data["4. close"]),
                "Volume": int(latest_data["5. volume"]),
                "Variation (%)": f'{(float(latest_data["4. close"]) - float(latest_data["1. open"])) / float(latest_data["1. open"]) * 100:.2f} %'
            }
        else:
            print(f"Data unavailable for {symbol}. Message: {data.get('Note', 'No message.')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

# Function to fetch data for multiple stocks
def get_multiple_stocks_latest_data(symbols):
    all_data = []
    for symbol in symbols:
        print(f"Fetching data for {symbol}...")
        stock_data = get_latest_daily_stock_data(symbol)
        if stock_data:
            all_data.append(stock_data)
    return all_data

# Example usage
if __name__ == "__main__":
    stock_symbols = ["AAPL", "MSFT", "GOOGL"]  # List of tickers (Apple, Microsoft, Google)
    latest_data_list = get_multiple_stocks_latest_data(stock_symbols)

    if latest_data_list:
        # Convert the list of dictionaries to a DataFrame for tabular display
        df = pd.DataFrame(latest_data_list)
        print("\nLatest stock data:")
        print(df)

        # Optional: Save to CSV
        df.to_csv("latest_stock_data.csv", index=False)
        print("\nData saved to 'latest_stock_data.csv'.")