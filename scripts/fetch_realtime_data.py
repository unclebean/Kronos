import os
import time
import pandas as pd
import ccxt
from datetime import datetime

# Configuration
SYMBOLS = ['DOGE/USDT', 'TAO/USDT', 'ETH/USDT']
TIMEFRAME = '1h'
LIMIT = 1000
POLL_INTERVAL = 3600  # seconds
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def fetch_and_save_data():
    # Initialize Binance exchange
    exchange = ccxt.binance({
        'enableRateLimit': True,
    })
    
    for symbol in SYMBOLS:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching latest {LIMIT} candles of {symbol} ({TIMEFRAME})...")
            
            # Fetch OHLCV (Open, High, Low, Close, Volume)
            ohlcv = exchange.fetch_ohlcv(symbol, TIMEFRAME, limit=LIMIT)
            
            if not ohlcv:
                print(f"No data received for {symbol}.")
                continue
                
            # Drop the last element as it represents the current incomplete candle
            ohlcv = ohlcv[:-1]

            # Format into Pandas DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamps', 'open', 'high', 'low', 'close', 'volume'])
            
            # Convert timestamp to datetime (Kronos webui expects 'timestamps' column as datetime)
            df['timestamps'] = pd.to_datetime(df['timestamps'], unit='ms')
            
            # Ensure output directory exists
            os.makedirs(OUTPUT_DIR, exist_ok=True)
            
            # Save to CSV (Overwriting with latest N candles)
            # Create a safe filename for the symbol
            safe_symbol = symbol.replace('/', '_')
            output_file = os.path.join(OUTPUT_DIR, f'realtime_feed_{safe_symbol}.csv')
            
            # Kronos webui expects oldest first if it's default, we keep it chronological
            df.to_csv(output_file, index=False)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data saved to {output_file} ({len(df)} rows)")
            
            # brief sleep properly space out rate limits for ccxt
            time.sleep(1)
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

if __name__ == "__main__":
    print(f"Starting real-time data fetcher for {SYMBOLS} ({TIMEFRAME})...")
    print(f"Saving to directory: {OUTPUT_DIR}")
    print("Press Ctrl+C to stop.")
    
    while True:
        fetch_and_save_data()
        time.sleep(POLL_INTERVAL)
