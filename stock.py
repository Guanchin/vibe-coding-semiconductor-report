import pandas as pd
from FinMind.data import DataLoader
import os
import time

# 1. 自動取得「桌面」路徑，確保你一定找得到檔案
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
output_dir = os.path.join(desktop, "台股歷史資料")

# 如果桌面沒有這個資料夾，就建立一個
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 2. 你的 18 檔股票清單
stock_ids = [
    '2330', '2303', '5347', '6770', 
    '2454', '2379', '3034', '3661', '3443', 
    '3711', '6257', '2449', '6239', 
    '2404', '3680', '6196', '1560', '6223'
]

# 初始化下載器
dl = DataLoader()

print(f"🚀 啟動抓取任務...")
print(f"📂 檔案將存放在桌面：{output_dir}")
print("-" * 30)

# 3. 開始循環抓取
for sid in stock_ids:
    print(f"正在抓取股票 {sid}...", end=" ", flush=True)
    try:
        # 抓取最近一年的資料
        # start_date 設為 2025-04-11, end_date 為今天 2026-04-11
        df = dl.taiwan_stock_daily(
            stock_id=sid,
            start_date='2025-04-11',
            end_date='2026-04-11'
        )

        if not df.empty:
            # 整理欄位：只取 日期、開、高、低、收
            df = df[['date', 'open', 'max', 'min', 'close']]
            # 重新命名欄位為英文
            df.columns = ['Date', 'Open', 'High', 'Low', 'Close']
            
            # 存成 CSV
            save_path = os.path.join(output_dir, f"{sid}.csv")
            df.to_csv(save_path, index=False)
            print("✅ 成功！")
        else:
            print("⚠️ 抓取成功但沒資料 (可能是新股或代號錯誤)")
        
        # 稍微停 0.5 秒防止被伺服器誤判攻擊
        time.sleep(0.5)
            
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")

print("-" * 30)
print(f"🎉 大功告成！共處理 {len(stock_ids)} 檔股票。")
print(f"現在幫你打開桌面資料夾...")

# 4. 自動開啟桌面上的那個資料夾視窗
os.startfile(output_dir)