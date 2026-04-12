import pandas as pd
import mplfinance as mpf
import os
import glob
import numpy as np

# ==========================================
# --- Configuration ---
# ==========================================
# Your data path (ensure this path is correct)
INPUT_DIR = r"C:\Users\jazz1\OneDrive\桌面\作業資料夾\大四下\生成式AI\台股歷史資料"

# Output directory for synthetic charts
OUTPUT_DIR = "Synthetic_Market_Charts"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Defining Stock Groups (Preset Categories)
# --- 修正後的類股定義，補回封裝測試 (Packaging_and_Testing) ---
STOCK_GROUPS = {
    "Semiconductor_Foundry": ["2330", "2303", "5347", "6770"],
    "IC_Design": ["2454", "2379", "3034", "3661", "3443", "3680", "6223"],
    "Packaging_and_Testing": ["3711", "6257", "2449", "6239"], # 補回這一行
    "Equipment_and_Others": ["2404", "6196", "1560"]
}

# ==========================================
# --- Helper Functions ---
# ==========================================
def load_ohlc_data(stock_id):
    """Loads full OHLC data for a single stock from CSV."""
    file_path = os.path.join(INPUT_DIR, f"{stock_id}.csv")
    if not os.path.exists(file_path):
        return None
    
    try:
        # Load the CSV data
        df = pd.read_csv(file_path)
        
        # Standardize Date column
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        # Required columns for candlestick charts
        required_cols = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_cols):
            # Missing necessary price columns
            return None
            
        # Select and sort by date
        return df[required_cols].sort_index()
    except Exception:
        # Error loading specific file
        return None

def standardize_ohlc_df(df):
    """
    Standardizes Open, High, Low, and Close prices using Z-score.
    Uses 'Close' price mean and std to maintain the relative relationships
    between prices within the same day (e.g., High is always >= Close).
    """
    # Use Close price as the baseline for normalization statistics
    mean = df['Close'].mean()
    std = df['Close'].std()
    
    # Check to avoid division by zero (if std is 0)
    if std == 0:
        return df - mean
    
    # Standardize all price columns using the same mean and std baseline
    # Formula: z = (x - mean) / std
    norm_df = (df - mean) / std
    return norm_df

def generate_synthetic_ohlc(stock_list):
    """
    Generates a synthetic market OHLC DataFrame by averaging 
    standardized price data from multiple stocks on a daily basis.
    """
    norm_data_list = []
    
    for sid in stock_list:
        # Load raw data for individual stock
        df = load_ohlc_data(sid)
        
        if df is not None:
            # Step 1: Standardize the individual stock's prices
            norm_df = standardize_ohlc_df(df)
            norm_data_list.append(norm_df)
    
    if not norm_data_list:
        # No valid data found for the input stocks
        return None
        
    # Step 2: Combine all normalized DataFrames
    combined_all = pd.concat(norm_data_list)
    
    # Step 3: Group by the Date index and calculate the mean for each column
    # This derives the synthetic daily average Open, High, Low, and Close
    synthetic_market_ohlc = combined_all.groupby(level=0).mean()
    
    return synthetic_market_ohlc

def plot_synthetic_candlestick(df, group_name):
    """
    Plots a Red/Green Candlestick chart for the synthetic market data.
    The chart is saved as a PNG file in the output directory.
    """
    print(f"📈 Plotting Candlestick Chart for synthetic market: {group_name}...")
    
    # Configure colors: Up=Red (上涨), Down=Green (下跌) (Taiwanese style)
    market_colors = mpf.make_marketcolors(up='red', down='green',
                                          edge='inherit', wick='inherit',
                                          volume='inherit', ohlc='inherit')
    
    # Configure overall style with grid and market colors
    plot_style = mpf.make_mpf_style(marketcolors=market_colors, gridstyle='--')
    
    # Define the output save path
    save_filename = f"Synthetic_{group_name}_Candlestick.png"
    save_path = os.path.join(OUTPUT_DIR, save_filename)
    
    try:
        # Plot the chart (without showing the interactive window)
        mpf.plot(df, 
                 type='candle',         # Candlestick Chart type
                 style=plot_style,      # The defined market style
                 title=f"\nSynthetic Market Index: {group_name}\n(Z-score Standardized)",
                 ylabel='Standardized Price Index',
                 mav=(5, 20),           # Add 5-day and 20-day moving averages
                 savefig=save_path)     # Save the output to a file
                
                 
        print(f"💾 Chart successfully saved to: {save_path}")
    except Exception as e:
        # Error during plotting
        print(f"❌ Error while plotting {group_name}: {e}")

# ==========================================
# --- Main Execution ---
# ==========================================
def main():
    print("--- Synthetic Market Candlestick Chart Generation System ---")
    
    # 1. Show available stock IDs to the user
    # Search for all CSV files in the input directory
    available_files = glob.glob(os.path.join(INPUT_DIR, "*.csv"))
    # Extract just the IDs from the filenames
    available_stocks = [os.path.basename(f).replace(".csv", "") for f in available_files]
    
    if not available_stocks:
        print(f"❌ Error: No CSV files found in {INPUT_DIR}.")
        print("Please ensure you have stock data files (e.g., 2330.csv) in that folder.")
        return
        
    print(f"Available Stock IDs: {', '.join(sorted(available_stocks))}")
    print("-" * 50)
    
    # 2. User Input: Collect and validate stock IDs
    user_input_raw = input("\nEnter Stock IDs to analyze (separate by spaces, e.g., 2330 2454): ")
    user_input_list = user_input_raw.split()
    # Keep only the valid inputs that are present in our available files
    selected_valid_stocks = [s for s in user_input_list if s in available_stocks]
    
    # Check if there are any valid inputs left
    if not selected_valid_stocks:
        print("❌ Error: No valid stock IDs entered, or none of the entered IDs are available.")
        print("Exiting analysis.")
        return

    print(f"✅ Starting analysis for: {', '.join(selected_valid_stocks)}")
    print("-" * 50)

    # 3. Analyze and Plot data, group by group
    for group_name, group_members in STOCK_GROUPS.items():
        # Check which of the user-selected stocks belong to the current preset group
        matched_stocks_in_group = [s for s in selected_valid_stocks if s in group_members]
        
        # If no stocks in the user's selection belong to this group, skip it
        if not matched_stocks_in_group:
            continue
            
        print(f"\nProcessing Group: {group_name} ({len(matched_stocks_in_group)} stocks matched)...")
        
        # Core: Generate the daily Synthetic Market OHLC data (the "虛擬大盤股票")
        synthetic_ohlc_df = generate_synthetic_ohlc(matched_stocks_in_group)
        
        # If data was generated successfully, plot the candlestick chart
        if synthetic_ohlc_df is not None:
            # Core: Plot the Red/Green Candlestick Chart for this synthetic market
            plot_synthetic_candlestick(synthetic_ohlc_df, group_name)
        else:
            print(f"❌ Failed to generate synthetic data for group: {group_name}.")

    # 4. Final output and cleanup
    print(f"\n✨ Task complete. Please check the '{OUTPUT_DIR}' folder on your Desktop.")
    print("If you do not see the folder, it may be in your Documents or Users root directory, depending on VS Code settings.")
    
    # Try to automatically open the output directory (Windows only)
    try:
        os.startfile(OUTPUT_DIR)
    except Exception:
        # Silent fail if os.startfile doesn't work (e.g., on different OS)
        pass

if __name__ == "__main__":
    main()