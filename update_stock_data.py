import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

# Stock symbols
stocks = ['AMZN', 'DPZ', 'BTC-USD', 'NFLX']
csv_file = 'stock_data.csv'

# Read existing data to find the last date
if os.path.exists(csv_file):
    existing_df = pd.read_csv(csv_file)
    existing_df['Date'] = pd.to_datetime(existing_df['Date'], format='%m/%d/%Y')
    last_date = existing_df['Date'].max()
    print(f"Last date in existing data: {last_date.date()}")
else:
    last_date = pd.to_datetime('2013-05-01')
    print(f"No existing file found. Starting from: {last_date.date()}")

# Download latest data from last_date to today
end_date = datetime.now()
start_date = last_date + timedelta(days=1)

print(f"\nFetching data from {start_date.date()} to {end_date.date()}...")

try:
    # Fetch data for all stocks
    data_dict = {}
    for symbol in stocks:
        print(f"Downloading {symbol}...")
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_date, end=end_date)
        
        if len(hist) > 0:
            data_dict[symbol] = hist['Close']
        else:
            print(f"  No new data for {symbol}")
    
    if not data_dict:
        print("No new data available for any stock.")
    else:
        # Create DataFrame from downloaded data
        new_df = pd.DataFrame(data_dict)
        new_df.index.name = 'Date'
        new_df = new_df.reset_index()
        new_df['Date'] = pd.to_datetime(new_df['Date'])
        
        # Rename BTC-USD to BTC for consistency
        if 'BTC-USD' in new_df.columns:
            new_df = new_df.rename(columns={'BTC-USD': 'BTC'})
        
        # Reorder columns to match original format
        new_df = new_df[['Date', 'AMZN', 'DPZ', 'BTC', 'NFLX']]
        
        # Combine with existing data
        if os.path.exists(csv_file):
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
            combined_df['Date'] = pd.to_datetime(combined_df['Date'])
            combined_df = combined_df.drop_duplicates(subset=['Date'], keep='last')
            combined_df = combined_df.sort_values('Date')
            combined_df = combined_df.reset_index(drop=True)
        else:
            combined_df = new_df
        
        # Convert date back to MM/DD/YYYY format for CSV
        combined_df['Date'] = combined_df['Date'].dt.strftime('%m/%d/%Y')
        
        # Save to CSV
        combined_df.to_csv(csv_file, index=False)
        print(f"\n✅ Updated {csv_file} successfully!")
        print(f"Total rows: {len(combined_df)}")
        print(f"Date range: {combined_df['Date'].min()} to {combined_df['Date'].max()}")

except Exception as e:
    print(f"❌ Error: {e}")
