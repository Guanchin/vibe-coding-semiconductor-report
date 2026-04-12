import pandas as pd
import mplfinance as mpf
import os
import glob

# --- 1. 路徑設定 (直接使用你提供的路徑) ---
# 注意：在 Python 中路徑斜線建議改為正斜線 / 以免出錯
input_dir = r"C:\Users\jazz1\OneDrive\桌面\作業資料夾\大四下\生成式AI\台股歷史資料"

# 圖片存檔位置：我們直接存在桌面，方便你查看
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
output_dir = os.path.join(desktop, "台股K線圖結果")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# --- 2. 設定台股風格 (紅漲綠跌) ---
mc = mpf.make_marketcolors(up='red', down='green',
                           edge='inherit',
                           wick='inherit',
                           volume='inherit')
s = mpf.make_mpf_style(marketcolors=mc, gridstyle='--')

# --- 3. 讀取並繪圖 ---
print(f"🚀 開始讀取路徑：{input_dir}")
csv_files = glob.glob(os.path.join(input_dir, "*.csv"))

if not csv_files:
    print("❌ 找不到 CSV 檔案！請檢查路徑是否正確。")
else:
    for file_path in csv_files:
        stock_id = os.path.basename(file_path).replace(".csv", "")
        print(f"正在繪製 {stock_id}...", end=" ")
        
        try:
            # 讀取資料
            df = pd.read_csv(file_path)
            
            # 轉換 Date 為索引 (這是 mplfinance 的強制要求)
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
            
            # 確保資料格式正確 (Open, High, Low, Close)
            df = df[['Open', 'High', 'Low', 'Close']]
            
            # 繪圖並儲存
            save_path = os.path.join(output_dir, f"{stock_id}.png")
            mpf.plot(df, 
                     type='candle', 
                     style=s, 
                     title=f"\nStock ID: {stock_id}",
                     mav=(5, 20),           # 畫出 5日與 20日均線
                     volume=False,          # 若 CSV 有 Volume 欄位可改為 True
                     savefig=save_path)
            
            print(f"✅ 完成！存於 {save_path}")
            
        except Exception as e:
            print(f"❌ 失敗: {e}")

    print(f"\n✨ 全部繪製完畢！圖片在桌面的『台股K線圖結果』資料夾中。")
    # 自動打開存圖的資料夾
    os.startfile(output_dir)