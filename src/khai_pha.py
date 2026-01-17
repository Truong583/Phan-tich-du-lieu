# %% =========================================================
# 1. IMPORT & CẤU HÌNH
# =========================================================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# Cấu hình giao diện "Sạch" và "Rõ"
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 6) # Kích thước mặc định lớn cho từng ảnh
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 14

# %% =========================================================
# 2. LOAD & PREPARE DATA
# =========================================================
# Thay đường dẫn của bạn vào đây
file_path = r'D:\PHAN_TICH_DU_LIEU\data\bitcoin_processed.csv' 
df = pd.read_csv(file_path)

# Xử lý ngày tháng
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp').reset_index(drop=True)
df = df.set_index('timestamp')

# Tạo các biến cơ bản để phân tích
# Log Return: Dùng để phân tích phân phối chuẩn
df['log_return'] = np.log(df['close'] / df['close'].shift(1))

# Relative Volume: Volume so với trung bình 20 phiên
df['vol_ma_20'] = df['volume'].rolling(window=20).mean()
df['relative_vol'] = df['volume'] / (df['vol_ma_20'] + 1e-9)

# Loại bỏ NaN sinh ra do shift/rolling
df.dropna(inplace=True)

print(f"Dữ liệu sẵn sàng: {df.shape}")

# Danh sách các biến quan trọng cần soi kính hiển vi
features = ['log_return', 'relative_vol', 'RSI_14', 'ATRr_14', 'BBP_20_2.0_2.0']

# %% =========================================================
# 3. TRỰC QUAN HÓA: PHÂN PHỐI (HISTOGRAM & KDE)
# =========================================================
# Mục tiêu: Xem dữ liệu có bị lệch (Skewed) không?
# Nếu lệch quá nhiều -> Model sẽ học thiên kiến.

print("Đang vẽ biểu đồ Phân phối (Distribution)...")
for col in features:
    if col in df.columns:
        plt.figure(figsize=(12, 6)) # Tạo cửa sổ mới riêng biệt
        sns.histplot(df[col], kde=True, bins=100, color='royalblue', stat="density")
        
        # Vẽ thêm đường trung bình (Mean) và trung vị (Median)
        plt.axvline(df[col].mean(), color='red', linestyle='--', label='Mean')
        plt.axvline(df[col].median(), color='green', linestyle='-', label='Median')
        
        plt.title(f'Phân phối chi tiết của: {col}')
        plt.legend()
        plt.show() # Show xong mới vẽ cái tiếp theo

# %% =========================================================
# 4. TRỰC QUAN HÓA: ĐIỂM NGOẠI LAI (BOXPLOT)
# =========================================================
# Mục tiêu: Tìm "Cá mập" hoặc lỗi dữ liệu.
# Các điểm chấm đen nằm ngoài râu (whiskers) là ngoại lai.

print("Đang vẽ biểu đồ Hộp (Boxplot)...")
for col in features:
    if col in df.columns:
        plt.figure(figsize=(12, 4)) # Boxplot cần chiều ngang dài
        sns.boxplot(x=df[col], color='orange', linewidth=1.5)
        plt.title(f'Phát hiện ngoại lai (Outliers) của: {col}')
        plt.show()

# %% =========================================================
# 5. TRỰC QUAN HÓA: TƯƠNG QUAN (HEATMAP)
# =========================================================
# Mục tiêu: Loại bỏ đa cộng tuyến (Các biến giống hệt nhau).

print("Đang vẽ Heatmap...")
corr_features = features + ['num_trades', 'close'] # Thêm vài biến check thử
corr_matrix = df[corr_features].corr()

plt.figure(figsize=(10, 8)) # Heatmap cần vuông vức
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm', 
            vmin=-1, vmax=1, linewidths=1, linecolor='white')
plt.title('Ma trận Tương quan (Correlation Matrix)')
plt.show()

# %% =========================================================
# 6. TRỰC QUAN HÓA: TÍNH DỪNG (ACF & PACF)
# =========================================================
# Mục tiêu: Chọn Model (LSTM hay Random Forest).
# Tách riêng ACF và PACF ra 2 ảnh to đùng.

print("Đang vẽ ACF/PACF cho Log Return...")

# Ảnh 1: Autocorrelation (ACF)
plt.figure(figsize=(12, 6))
plot_acf(df['log_return'], lags=50, ax=plt.gca(), title='Autocorrelation (ACF) - Tính nhớ của chuỗi giá')
plt.show()

# Ảnh 2: Partial Autocorrelation (PACF)
plt.figure(figsize=(12, 6))
plot_pacf(df['log_return'], lags=50, ax=plt.gca(), title='Partial Autocorrelation (PACF) - Tương quan riêng phần')
plt.show()

# %% =========================================================
# 7. CHUẨN HÓA DỮ LIỆU (STANDARD SCALER) & SO SÁNH
# =========================================================
# Mục tiêu: Chứng minh tại sao phải chuẩn hóa.
# Ta sẽ vẽ 2 ảnh riêng biệt: Trước và Sau khi scale.

# Chọn features input cho mô hình
X_raw = df[features]

# Thực hiện Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_raw)
df_scaled = pd.DataFrame(X_scaled, columns=features)

# ẢNH 1: Dữ liệu thô (Chưa chuẩn hóa)
plt.figure(figsize=(14, 8))
for col in features:
    sns.kdeplot(df[col], fill=True, label=col, alpha=0.3)
plt.title('Dữ liệu GỐC (Chưa chuẩn hóa) - Các biến đè lên nhau, lệch thang đo')
plt.xlabel('Giá trị gốc')
plt.legend()
plt.show()

# ẢNH 2: Dữ liệu đã chuẩn hóa (Z-Score)
plt.figure(figsize=(14, 8))
for col in features:
    sns.kdeplot(df_scaled[col], fill=True, label=col, alpha=0.3)
plt.title('Dữ liệu ĐÃ CHUẨN HÓA (Standard Scaler) - Cùng quy về tâm 0')
plt.xlabel('Z-Score (Độ lệch chuẩn)')
plt.legend()
plt.show()

print("Hoàn tất trực quan hóa!")
# %%
