import pandas as pd
import pandas_ta as ta
import os

# --- CẤU HÌNH ĐƯỜNG DẪN (SỬA LẠI CHO ĐÚNG) ---
# 1. Thêm chữ r đằng trước để Python hiểu đường dẫn Windows
# 2. Đảm bảo file đầu vào (INPUT) đúng tên file bạn đã tải về
INPUT_FILE = r"D:\PHAN_TICH_DU_LIEU\BTCUSDT_5m.csv"

# 3. File đầu ra (OUTPUT) phải có đuôi .csv (Ví dụ: bitcoin_processed.csv)
OUTPUT_FILE = r"D:\PHAN_TICH_DU_LIEU\data\bitcoin_processed.csv"

def process_data():
    print(f"⏳ Đang đọc file từ: {INPUT_FILE}")

    # Kiểm tra file tồn tại chưa
    if not os.path.exists(INPUT_FILE):
        print(f"❌ LỖI TO: Không tìm thấy file '{INPUT_FILE}'")
        print("👉 Bạn hãy kiểm tra lại xem file csv tải về đang nằm ở đâu nhé!")
        return

    df = pd.read_csv(INPUT_FILE)

    # Chọn cột
    try:
        keep_cols = [
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 
            'qav', 'num_trades', 'tbv'
        ]
        df = df[keep_cols]
    except KeyError as e:
        print(f"❌ Lỗi thiếu cột dữ liệu: {e}")
        print("File của bạn có các cột:", df.columns.tolist())
        return

    print("⚙️ Đang tính toán chỉ báo (RSI, MACD, BB)...")
    
    # Tính chỉ báo
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    df.ta.bbands(length=20, std=2, append=True)
    df.ta.atr(length=14, append=True)

    # Tạo Target
    df['target'] = df['close'].shift(-1)

    # Làm sạch
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)

    # --- TỰ ĐỘNG TẠO THƯ MỤC NẾU CHƯA CÓ ---
    # Lấy tên thư mục cha từ đường dẫn file output
    thu_muc_luu = os.path.dirname(OUTPUT_FILE)
    os.makedirs(thu_muc_luu, exist_ok=True)

    # Lưu file
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"✅ XONG! Dữ liệu đã xử lý lưu tại: {OUTPUT_FILE}")
    print(f"📊 Tổng số dòng sạch: {len(df)}")
    print(df.tail())

if __name__ == "__main__":
    process_data()