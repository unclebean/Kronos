import os
import time
import pandas as pd
import ccxt
from datetime import datetime

# Configuration
SYMBOL = 'DOGE/USDT'
TIMEFRAME = '1h'
LIMIT = 1000
POLL_INTERVAL = 3600  # seconds
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'realtime_feed.csv')

def fetch_and_save_data():
    try:
        # Initialize Binance exchange
        exchange = ccxt.binance({
            'enableRateLimit': True,
        })
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching latest {LIMIT} candles of {SYMBOL} ({TIMEFRAME})...")
        
        # Fetch OHLCV (Open, High, Low, Close, Volume)
        ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=LIMIT)
        
        if not ohlcv:
            print("No data received.")
            return
            
        # Drop the last element as it represents the current incomplete candle
        ohlcv = ohlcv[:-1]

        # Format into Pandas DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamps', 'open', 'high', 'low', 'close', 'volume'])
        
        # Convert timestamp to datetime (Kronos webui expects 'timestamps' column as datetime)
        df['timestamps'] = pd.to_datetime(df['timestamps'], unit='ms')
        
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Save to CSV (Overwriting with latest N candles)
        # Kronos webui expects oldest first if it's default, we keep it chronological
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data saved to {OUTPUT_FILE} ({len(df)} rows)")
        
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    print(f"Starting real-time data fetcher for {SYMBOL} ({TIMEFRAME})...")
    print(f"Saving to: {OUTPUT_FILE}")
    print("Press Ctrl+C to stop.")
    
    while True:
        fetch_and_save_data()
        time.sleep(POLL_INTERVAL)
