import yfinance as yf
import os

# 強制建立一個絕對看得到的資料夾
output_dir = "test_data"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"資料夾 {output_dir} 建立成功！")

print("正在嘗試抓取台積電 (2330.TW)...")

# 抓取資料
df = yf.download("2330.TW", period="1mo", progress=False)

if not df.empty:
    file_path = os.path.join(output_dir, "2330.csv")
    df.to_csv(file_path)
    print(f"✅ 成功了！檔案就在這裡：{os.path.abspath(file_path)}")
else:
    print("❌ 抓不到資料，Yahoo 還在鎖定你的 IP，請換個網路（如手機熱點）再試。")