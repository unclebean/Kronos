import os
import time
import pandas as pd
import yfinance as yf
from datetime import datetime

# Configuration
SYMBOLS = ['AAPL', 'MSFT', 'NVDA', 'TSLA', 'SPY', 'QQQ']
INTERVAL = '1h'  # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
PERIOD = '2y'    # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
POLL_INTERVAL = 3600  # seconds
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def fetch_and_save_data():
    for symbol in SYMBOLS:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching latest data for {symbol} ({INTERVAL})...")
            
            # Fetch data using yfinance
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=PERIOD, interval=INTERVAL)
            
            if df.empty:
                print(f"No data received for {symbol}.")
                continue
                
            # Rename columns to match Kronos format
            df = df.reset_index()
            # yfinance returns 'Datetime' or 'Date'
            if 'Datetime' in df.columns:
                df = df.rename(columns={'Datetime': 'timestamps'})
            elif 'Date' in df.columns:
                df = df.rename(columns={'Date': 'timestamps'})
            
            # Lowercase columns
            df.columns = [c.lower() for c in df.columns]
            
            # Ensure required columns exist
            required_cols = ['timestamps', 'open', 'high', 'low', 'close', 'volume']
            df = df[required_cols]
            
            # Ensure timestamps column is datetime
            df['timestamps'] = pd.to_datetime(df['timestamps'])
            
            # Remove timezone if exists (Kronos prefers naive datetime)
            if df['timestamps'].dt.tz is not None:
                df['timestamps'] = df['timestamps'].dt.tz_localize(None)
            
            # Ensure output directory exists
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Save to CSV
            output_file = os.path.join(OUTPUT_DIR, f'realtime_feed_{symbol}.csv')
            df.to_csv(output_file, index=False)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data saved to {output_file} ({len(df)} rows)")
            
            # brief sleep to avoid rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

if __name__ == "__main__":
    print(f"Starting real-time US Equity data fetcher for {SYMBOLS} ({INTERVAL})...")
    print(f"Saving to directory: {OUTPUT_DIR}")
    print("Press Ctrl+C to stop.")
    
    while True:
        fetch_and_save_data()
        print(f"Waiting {POLL_INTERVAL} seconds for next update...")
        time.sleep(POLL_INTERVAL)
