import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam

# --- CẤU HÌNH ---
FILE_DATA = r"D:\PHAN_TICH_DU_LIEU\data\bitcoin_processed.csv"
MODEL_PATH = "models/bitcoin_lstm.h5"
SCALER_PATH = "models/scaler.pkl"

# Tham số mô hình
LOOKBACK = 60       # Nhìn lại 60 cây nến (5 tiếng)
BATCH_SIZE = 64     # Học 64 dòng cùng lúc (Tăng tốc độ)
EPOCHS = 100        # Cho phép học tối đa 100 lần (Sẽ tự dừng nếu đã giỏi)
TEST_SIZE = 0.2     # 20% dữ liệu để thi

def create_sequences(data, lookback):
    """Hàm cắt dữ liệu thành các đoạn 60 nến"""
    X, y = [], []
    # Dữ liệu vào: Tất cả các cột TRỪ cột cuối (target)
    # Dữ liệu ra: Chỉ cột cuối (target)
    for i in range(len(data) - lookback):
        X.append(data[i:i+lookback, :-1]) 
        y.append(data[i+lookback, -1])    
    return np.array(X), np.array(y)

def train_best_model():
    print("🚀 BẮT ĐẦU HUẤN LUYỆN (CHẾ ĐỘ CHUYÊN NGHIỆP)...")

    # 1. Đọc dữ liệu
    if not os.path.exists(FILE_DATA):
        print(f"❌ Lỗi: Không tìm thấy file {FILE_DATA}")
        return

    df = pd.read_csv(FILE_DATA)
    
    # Bỏ cột thời gian, chỉ giữ lại số liệu
    if 'timestamp' in df.columns:
        df = df.drop(columns=['timestamp'])
    
    # 2. CHIA TẬP TRAIN/TEST TRƯỚC (QUAN TRỌNG)
    # Để tránh việc Scaler "nhìn trộm" dữ liệu tương lai
    train_size = int(len(df) * (1 - TEST_SIZE))
    train_df = df.iloc[:train_size]
    test_df = df.iloc[train_size:]
    
    print(f"📊 Dữ liệu Train: {len(train_df)} dòng | Test: {len(test_df)} dòng")

    # 3. Chuẩn hóa dữ liệu (Scaling)
    # Chỉ học từ tập Train, sau đó áp dụng kiến thức đó lên tập Test
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(train_df) 
    
    scaled_train = scaler.transform(train_df)
    scaled_test = scaler.transform(test_df)
    
    # Lưu Scaler lại để dùng cho Bot thực tế
    os.makedirs("models", exist_ok=True)
    joblib.dump(scaler, SCALER_PATH)
    print("💾 Đã lưu bộ chuẩn hóa Scaler.")

    # 4. Tạo chuỗi dữ liệu (Sliding Window)
    print("⚙️ Đang cắt dữ liệu thành chuỗi...")
    X_train, y_train = create_sequences(scaled_train, LOOKBACK)
    X_test, y_test = create_sequences(scaled_test, LOOKBACK)
    
    # Kiểm tra kích thước lần cuối
    print(f"   -> Input Train: {X_train.shape} (Mẫu, Thời gian, Đặc trưng)")
    print(f"   -> Output Train: {y_train.shape}")

    # 5. Xây dựng bộ não LSTM (Architecture)
    model = Sequential()
    
    # Lớp 1: LSTM mạnh mẽ
    model.add(LSTM(units=64, return_sequences=True, input_shape=(LOOKBACK, X_train.shape[2])))
    model.add(Dropout(0.3)) # Quên 30% để tránh học vẹt
    
    # Lớp 2: LSTM tinh chỉnh
    model.add(LSTM(units=64, return_sequences=False))
    model.add(Dropout(0.3))
    
    # Lớp 3: Đầu ra
    model.add(Dense(25)) # Lớp trung gian
    model.add(Dense(1))  # Giá dự báo
    
    # Dùng Adam với learning rate nhỏ để học kỹ
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mean_squared_error')

    # 6. Các cơ chế tự động (Callbacks) - VŨ KHÍ BÍ MẬT
    callbacks = [
        # Lưu lại model tại thời điểm tốt nhất (val_loss thấp nhất)
        ModelCheckpoint(MODEL_PATH, save_best_only=True, monitor='val_loss', mode='min', verbose=1),
        
        # Nếu sau 10 lần học mà không tiến bộ -> Dừng lại
        EarlyStopping(monitor='val_loss', patience=10, verbose=1, restore_best_weights=True),
        
        # Nếu sau 5 lần học mà không tiến bộ -> Giảm tốc độ học xuống 2 lần
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1)
    ]

    # 7. Bắt đầu Train
    print("🔥 Đang train... (AI sẽ tự động dừng khi học xong)")
    history = model.fit(
        X_train, y_train,
        batch_size=BATCH_SIZE,
        epochs=EPOCHS,
        validation_data=(X_test, y_test),
        callbacks=callbacks,
        verbose=1
    )

    print("-" * 50)
    print(f"✅ HUẤN LUYỆN XONG! Model xịn nhất đã lưu tại: {MODEL_PATH}")

if __name__ == "__main__":
    train_best_model()