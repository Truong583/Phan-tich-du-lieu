import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
import joblib
import os

# --- CẤU HÌNH ---
FILE_DATA = r"D:\PHAN_TICH_DU_LIEU\data\bitcoin_processed.csv"
MODEL_PATH = "models/bitcoin_lstm.h5"
SCALER_PATH = "models/scaler.pkl"
LOOKBACK = 60  # Phải khớp với lúc train

def ve_bieu_do():
    print("🎨 Đang chuẩn bị dữ liệu để vẽ tranh...")

    # 1. Load các thành phần
    if not os.path.exists(MODEL_PATH):
        print(f"❌ Không tìm thấy model tại {MODEL_PATH}")
        return

    model = load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    
    # 2. Xử lý dữ liệu (Giống hệt quy trình Train)
    df = pd.read_csv(FILE_DATA)
    # Bỏ cột thời gian để lấy đúng ma trận số
    df_numeric = df.drop(columns=['timestamp']) 
    
    # Scale dữ liệu
    scaled_data = scaler.transform(df_numeric)

    # Cắt dữ liệu thành chuỗi (Time Series)
    X, y = [], []
    for i in range(len(scaled_data) - LOOKBACK):
        X.append(scaled_data[i:i+LOOKBACK, :-1])
        y.append(scaled_data[i+LOOKBACK, -1])
    
    X, y = np.array(X), np.array(y)

    # Lấy 20% dữ liệu cuối để Test (Tương ứng với phần AI chưa học)
    test_split = int(len(X) * 0.8)
    X_test = X[test_split:]
    y_test = y[test_split:]
    
    # 3. Cho AI dự đoán
    print(f"🔮 AI đang dự đoán trên {len(X_test)} cây nến...")
    y_pred = model.predict(X_test)

    # 4. Đổi số về giá trị thật (Inverse Scale)
    # Tạo ma trận giả để khớp kích thước với scaler
    so_cot = scaled_data.shape[1]
    
    # Bung giá thật
    dummy_true = np.zeros((len(y_test), so_cot))
    dummy_true[:, -1] = y_test
    gia_that = scaler.inverse_transform(dummy_true)[:, -1]
    
    # Bung giá dự báo
    dummy_pred = np.zeros((len(y_pred), so_cot))
    dummy_pred[:, -1] = y_pred.flatten()
    gia_du_bao = scaler.inverse_transform(dummy_pred)[:, -1]

    # 5. VẼ BIỂU ĐỒ (VISUALIZATION)
    print("📈 Đang vẽ biểu đồ...")
    
    plt.figure(figsize=(15, 10))
    
    # --- Biểu đồ 1: Toàn cảnh ---
    plt.subplot(2, 1, 1) # 2 hàng, 1 cột, hình thứ 1
    plt.plot(gia_that, color='blue', label='Giá Thực Tế', linewidth=1)
    plt.plot(gia_du_bao, color='red', label='AI Dự Báo', linewidth=1, alpha=0.7)
    plt.title('TOÀN CẢNH: GIÁ BITCOIN vs AI DỰ BÁO', fontsize=14)
    plt.ylabel('Giá (USDT)')
    plt.legend()
    plt.grid(True)

    # --- Biểu đồ 2: Zoom vào 100 cây nến cuối ---
    plt.subplot(2, 1, 2) # 2 hàng, 1 cột, hình thứ 2
    zoom = 100
    plt.plot(range(zoom), gia_that[-zoom:], color='blue', marker='o', markersize=4, label='Thực Tế')
    plt.plot(range(zoom), gia_du_bao[-zoom:], color='red', marker='x', markersize=4, linestyle='--', label='AI Dự Báo')
    plt.title(f'CẬN CẢNH: {zoom} CÂY NẾN CUỐI CÙNG', fontsize=14)
    plt.xlabel('Thời gian (Nến)')
    plt.ylabel('Giá (USDT)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show() # Hiện cửa sổ
    print("✅ Xong! Hãy xem cửa sổ biểu đồ vừa hiện lên.")

if __name__ == "__main__":
    ve_bieu_do()