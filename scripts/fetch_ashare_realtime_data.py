import os
import time
import pandas as pd
import akshare as ak
from datetime import datetime

# Configuration
SYMBOLS = ['300308', '300184', '002975', '300475', '000973', '002439']
PERIOD = 'daily'
ADJUST = 'qfq'
POLL_INTERVAL = 3600 * 4 # A-share updates daily, polling every 4 hours is enough, but configurable
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

def get_full_symbol(symbol):
    if symbol.startswith('6'):
        return 'sh' + symbol
    elif symbol.startswith('8') or symbol.startswith('4'):
        return 'bj' + symbol
    else:
        return 'sz' + symbol

def fetch_and_save_data():
    for symbol in SYMBOLS:
        retry_count = 3
        for attempt in range(retry_count):
            try:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fetching daily candles of A-Share {symbol} (Attempt {attempt+1}/{retry_count})...")
                
                # Fetch daily data using Sina API to avoid Eastmoney connection drops
                full_symbol = get_full_symbol(symbol)
                df = ak.stock_zh_a_daily(symbol=full_symbol, adjust=ADJUST)
                
                if df is None or df.empty:
                    print(f"No data received for {symbol}.")
                    break
                    
                # Rename columns to match Kronos format
                # akshare Sina format: ['date', 'open', 'high', 'low', 'close', 'volume', 'amount', 'outstanding_share', 'turnover']
                rename_map = {
                    'date': 'timestamps'
                }
                df = df.rename(columns=rename_map)
                
                # Keep only the required columns
                df = df[['timestamps', 'open', 'high', 'low', 'close', 'volume']]
                
                # Ensure timestamps column is datetime
                df['timestamps'] = pd.to_datetime(df['timestamps'])
                
                # Ensure output directory exists
                os.makedirs(OUTPUT_DIR, exist_ok=True)
                
                # Save to CSV
                output_file = os.path.join(OUTPUT_DIR, f'realtime_feed_{symbol}.csv')
                df.to_csv(output_file, index=False)
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Data saved to {output_file} ({len(df)} rows)")
                break # Success, so break the retry loop
                
            except Exception as e:
                print(f"Error fetching data for {symbol}: {e}")
                if attempt < retry_count - 1:
                    time.sleep(2)  # Wait before retry
        time.sleep(1) # sleep briefly between different symbols to avoid rate limits


if __name__ == "__main__":
    print(f"Starting real-time A-Share data fetcher for {SYMBOLS} ({PERIOD})...")
    print(f"Saving to: {OUTPUT_DIR}")
    print("Press Ctrl+C to stop.")
    
    while True:
        fetch_and_save_data()
        time.sleep(POLL_INTERVAL)
