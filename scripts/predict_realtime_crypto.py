import os
import sys
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Add this to fix the '_tkinter' error on Mac
import matplotlib.pyplot as plt

# Add the root directory to path to import from 'model'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.kronos import Kronos, KronosTokenizer, KronosPredictor

# Configuration
SYMBOLS = ['DOGE/USDT', 'TAO/USDT', 'ETH/USDT']
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'figures')

def plot_prediction(symbol, historical_df, pred_df):
    pred_df.index = [historical_df['timestamps'].iloc[-1] + pd.Timedelta(hours=i+1) for i in range(len(pred_df))]
    
    historical_close = historical_df.set_index('timestamps')['close']
    pred_close = pred_df['close']
    
    fig, ax1 = plt.subplots(1, 1, figsize=(10, 5))
    ax1.plot(historical_close, label='Historical', color='blue', linewidth=1.5)
    ax1.plot(pred_close, label='Prediction', color='red', linewidth=1.5)
    ax1.set_title(f'{symbol} Price Forecast')
    ax1.set_ylabel('Close Price', fontsize=14)
    ax1.legend(loc='lower left', fontsize=12)
    ax1.grid(True)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_symbol = symbol.replace('/', '_')
    save_path = os.path.join(OUTPUT_DIR, f'prediction_{safe_symbol}.png')
    plt.tight_layout()
    plt.savefig(save_path)
    print(f"Saved prediction plot to {save_path}")
    # plt.show() # Uncomment if you want to view the plot immediately 

def main():
    print("Loading Kronos-base (102.3M) and Tokenizer onto Apple Silicon (MPS)...")
    
    # Load Model and Tokenizer
    # NeoQuasar/Kronos-base is the 102.3M parameter model
    tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
    model = Kronos.from_pretrained("NeoQuasar/Kronos-base")
    
    # For Apple Silicon, use 'mps'
    predictor = KronosPredictor(model, tokenizer, device='mps', max_context=512)

    pred_len = 24  # Let's predict the next 24 hours (assuming 1h timeframe)
    
    for symbol in SYMBOLS:
        safe_symbol = symbol.replace('/', '_')
        data_file = os.path.join(DATA_DIR, f'realtime_feed_{safe_symbol}.csv')
        
        if not os.path.exists(data_file):
            print(f"Data file not found for {symbol} at {data_file}. Skipping...")
            continue
            
        print(f"\n--- Processing {symbol} ---")
        df = pd.read_csv(data_file)
        df['timestamps'] = pd.to_datetime(df['timestamps'])
        
        # Ensure we have enough data and truncate to max context
        lookback = min(len(df), 512)
        
        # We take the most recent 'lookback' candles
        historical_df = df.iloc[-lookback:].copy()
        historical_df = historical_df.reset_index(drop=True)
        
        x_df = historical_df[['open', 'high', 'low', 'close', 'volume']]
        x_timestamp = historical_df['timestamps']
        
        # Generate dummy future timestamps for prediction range
        last_timestamp = x_timestamp.iloc[-1]
        y_timestamp = pd.Series([last_timestamp + pd.Timedelta(hours=i+1) for i in range(pred_len)])

        # Make Prediction
        print(f"Running inference for next {pred_len} periods...")
        pred_df = predictor.predict(
            df=x_df,
            x_timestamp=x_timestamp,
            y_timestamp=y_timestamp,
            pred_len=pred_len,
            T=1.0,
            top_p=0.9,
            sample_count=1,
            verbose=True
        )
        
        print(f"Prediction Complete for {symbol}. First 5 forecasts:")
        print(pred_df.head(5))
        
        plot_prediction(symbol, historical_df, pred_df)

if __name__ == "__main__":
    main()
