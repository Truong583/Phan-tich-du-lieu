# %% PHASE 1: PREPROCESSING (DỰA TRÊN EDA)
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

def engineer_features_final(df_input):
    df = df_input.copy()
    
    # 1. LOG TRANSFORM (Giải quyết biểu đồ Lệch phải của Volume & ATR)
    # Thay vì dùng số thô (1, 2... 16), ta chuyển về Log để AI không bị sốc số liệu.
    # Ta dùng log1p (log(1+x)) để tránh lỗi chia cho 0.
    df['log_relative_vol'] = np.log1p(df['relative_vol'])
    df['log_atr'] = np.log1p(df['ATRr_14'])
    
    # 2. FEATURE SELECTION (Giải quyết biểu đồ Heatmap tương quan cao)
    # Bỏ BBP (vì tương quan 0.89 với RSI), giữ RSI (vì phân phối chuẩn đẹp hơn).
    # Giữ Log Return (dù nhọn, nhưng là tín hiệu giá duy nhất).
    
    # 3. CONTEXT WINDOW (Tạo bối cảnh)
    # Dù ACF = 0 (giá không có tính nhớ), nhưng chỉ báo kỹ thuật cần bối cảnh.
    # Ví dụ: RSI hiện tại là 70, nhưng 5 phút trước là 30 -> Tín hiệu rất mạnh.
    features = ['log_return', 'log_relative_vol', 'RSI_14', 'log_atr']
    
    for col in features:
        for lag in [1, 2, 3]: # Nhìn lại 3 cây nến gần nhất
            df[f'{col}_lag_{lag}'] = df[col].shift(lag)
            
    df.dropna(inplace=True)
    return df

# LOAD VÀ XỬ LÝ
df_raw = pd.read_csv(r'D:\PHAN_TICH_DU_LIEU\data\bitcoin_processed.csv')
df_raw['timestamp'] = pd.to_datetime(df_raw['timestamp'])
df_raw.set_index('timestamp', inplace=True)

# Tính lại các cột cơ bản nếu chưa có
df_raw['log_return'] = np.log(df_raw['close'] / df_raw['close'].shift(1))
df_raw['vol_ma_20'] = df_raw['volume'].rolling(20).mean()
df_raw['relative_vol'] = df_raw['volume'] / (df_raw['vol_ma_20'] + 1e-9)

# Áp dụng hàm Engineering
df_eng = engineer_features_final(df_raw)

print("Đã xử lý xong Log Transform và Lag Features!")
print(df_eng[['log_relative_vol', 'relative_vol']].head()) # So sánh thử

# %% PHASE 2: DYNAMIC TARGETING
def create_targets(df, multiplier=1.0):
    """
    Chỉ vào lệnh nếu lợi nhuận tiềm năng > Độ biến động (ATR) * multiplier
    """
    data = df.copy()
    
    # Lấy giá trị ATR tại thời điểm t (đã biết)
    current_atr = data['ATRr_14'] 
    
    # Tính biến động giá tương lai (t+1)
    future_change = data['close'].shift(-1) - data['close']
    
    # Logic Gán Nhãn:
    # Nếu giá tăng mạnh hơn ATR -> Class 1 (Mua)
    # Nếu giá giảm mạnh hơn ATR -> Class -1 (Bán)
    # Còn lại (nằm trong hộp Boxplot) -> Class 0 (Hold/Nhiễu)
    
    conditions = [
        (future_change > current_atr * multiplier),  # Tăng mạnh
        (future_change < -current_atr * multiplier)  # Giảm mạnh
    ]
    choices = [1, -1]
    
    data['target'] = np.select(conditions, choices, default=0)
    
    # Shift target về đúng hàng (vì ta dự đoán cho tương lai)
    # Lưu ý: Code trên đã dùng shift(-1) để tính change, nên target nằm đúng dòng t.
    
    return data.dropna()

df_labeled = create_targets(df_eng, multiplier=1.5) # Yêu cầu lợi nhuận > 1.5 lần rủi ro ATR

print("Phân phối nhãn (Target Distribution):")
print(df_labeled['target'].value_counts())
# Bạn sẽ thấy số lượng nhãn 0 rất nhiều, nhãn 1 và -1 ít. 
# Đây chính là cấu trúc "Mỏ Vàng trong Rác" mà ta đã phân tích.
# %% PHASE 3: MODEL TRAINING & COMPARISON
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, precision_score

# 1. CHUẨN BỊ DỮ LIỆU
# Chỉ lấy các cột Feature (đầu vào) và Target (đầu ra)
feature_cols = [c for c in df_labeled.columns if 'lag' in c or 'log_' in c]
# Loại bỏ chính log_return hiện tại ra khỏi feature để tránh data leakage (nếu muốn chặt chẽ hơn chỉ dùng lag)
# Ở đây ta dùng lag features là chính.

X = df_labeled[feature_cols]
y = df_labeled['target']

# Mapping lại target cho XGBoost (nó cần 0, 1, 2 thay vì -1, 0, 1)
y_xgb = y + 1  # -1->0 (Sell), 0->1 (Hold), 1->2 (Buy)

# Split theo thời gian (Không shuffle)
split = int(len(X) * 0.8)
X_train, X_test = X.iloc[:split], X.iloc[split:]
y_train, y_test = y.iloc[:split], y.iloc[split:]
y_train_xgb, y_test_xgb = y_xgb.iloc[:split], y_xgb.iloc[split:]

# SCALE DỮ LIỆU (QUAN TRỌNG VỚI RSI)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- MODEL 1: RANDOM FOREST (BASELINE) ---
print("\n--- TRAINING RANDOM FOREST ---")
# class_weight='balanced': Vũ khí chống lại sự mất cân bằng dữ liệu
rf_model = RandomForestClassifier(
    n_estimators=200, 
    max_depth=5, 
    class_weight='balanced', # Tự động tăng trọng số cho lớp hiếm (Mua/Bán)
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train_scaled, y_train)
y_pred_rf = rf_model.predict(X_test_scaled)

# --- MODEL 2: XGBOOST (CHALLENGER) ---
print("\n--- TRAINING XGBOOST ---")
# XGBoost cần tính tay scale_pos_weight cho bài toán multi-class, hơi phức tạp.
# Ở đây ta dùng kỹ thuật đơn giản hơn: max_delta_step để ổn định trọng số.
xgb_model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    random_state=42,
    n_jobs=-1,
    # objective='multi:softmax', num_class=3 # Nếu muốn chạy đa lớp
)
# Lưu ý: XGBoost mặc định không hỗ trợ tốt class_weight tự động như RF trong mode multi-class
# Nên ta sẽ xem xét kết quả RF trước.
xgb_model.fit(X_train_scaled, y_train_xgb)
y_pred_xgb = xgb_model.predict(X_test_scaled)
# Convert ngược lại về -1, 0, 1 để so sánh
y_pred_xgb = y_pred_xgb - 1 

# --- ĐÁNH GIÁ HIỆU SUẤT (TẬP TRUNG VÀO PRECISION) ---
def evaluate_model(name, y_true, y_pred):
    print(f"\nKẾT QUẢ CỦA {name}:")
    report = classification_report(y_true, y_pred, output_dict=True)
    
    # Ta chỉ quan tâm: Khi máy bảo MUA (1), tỷ lệ đúng là bao nhiêu?
    precision_buy = report['1']['precision'] if '1' in report else 0
    precision_sell = report['-1']['precision'] if '-1' in report else 0
    
    print(f"Độ chính xác lệnh MUA (Precision Class 1): {precision_buy:.2%}")
    print(f"Độ chính xác lệnh BÁN (Precision Class -1): {precision_sell:.2%}")
    print("-" * 30)

evaluate_model("Random Forest", y_test, y_pred_rf)
evaluate_model("XGBoost", y_test, y_pred_xgb)

# %% PHASE 4 (FIX): HẠ TIÊU CHUẨN ĐỂ CÓ TÍN HIỆU
def upgrade_data_strategy_fixed(df_input):
    df = df_input.copy()
    
    # 1. TREND FILTER (Giữ nguyên)
    df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
    df['trend_dir'] = np.where(df['close'] > df['ema_200'], 1, -1)
    df['dist_ema200'] = (df['close'] - df['ema_200']) / df['ema_200']

    # 2. TARGET MỚI (HẠ ĐỘ KHÓ)
    horizon = 12  # 60 phút
    
    # --- THAY ĐỔI QUAN TRỌNG Ở ĐÂY ---
    # Giảm từ 2.0 xuống 1.0 hoặc 1.2
    # Nghĩa là: Chỉ cần lãi bằng đúng rủi ro (1R) là chốt.
    atr_multiplier = 1.0 
    
    indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=horizon)
    df['future_high'] = df['high'].rolling(window=indexer).max()
    df['future_low'] = df['low'].rolling(window=indexer).min()
    
    current_close = df['close']
    current_atr = df['ATRr_14']
    
    conditions = [
        (df['future_high'] > current_close + current_atr * atr_multiplier) & (df['trend_dir'] == 1),
        (df['future_low'] < current_close - current_atr * atr_multiplier) & (df['trend_dir'] == -1)
    ]
    choices = [1, -1]
    
    df['target_smart'] = np.select(conditions, choices, default=0)
    
    return df.dropna()

# --- CHẠY LẠI QUY TRÌNH ---
print(">>> Đang tái cấu trúc dữ liệu với độ khó thấp hơn...")
df_upgraded = upgrade_data_strategy_fixed(df_eng)

print("\nPHÂN PHỐI TARGET MỚI (Kiểm tra xem có đủ mẫu không):")
counts = df_upgraded['target_smart'].value_counts()
print(counts)

# Kiểm tra nhanh: Nếu Class 1 hoặc -1 dưới 1000 mẫu thì vẫn quá khó
if counts.get(1, 0) < 1000:
    print("CẢNH BÁO: Số lượng lệnh MUA quá ít! AI sẽ không học được.")
else:
    print("OK: Số lượng mẫu đủ tốt để train.")

# --- CẬP NHẬT LẠI DỮ LIỆU TRAIN ---
X_new = df_upgraded[feature_cols_new] # feature_cols_new lấy từ code trước
y_new = df_upgraded['target_smart']

split = int(len(X_new) * 0.8)
X_train_new, X_test_new = X_new.iloc[:split], X_new.iloc[split:]
y_train_new, y_test_new = y_new.iloc[:split], y_new.iloc[split:]

# --- HUẤN LUYỆN LẠI (Dùng Random Forest cho lành) ---
print("\n>>> Đang Training lại mô hình...")
rf_smart = RandomForestClassifier(
    n_estimators=200,
    max_depth=6,             # Giảm độ sâu một chút để tránh học vẹt
    min_samples_leaf=50,     # Tăng lên để chỉ bắt các pattern thực sự phổ biến
    class_weight='balanced', 
    random_state=42,
    n_jobs=-1
)

rf_smart.fit(X_train_new, y_train_new)
y_pred_smart = rf_smart.predict(X_test_new)

# --- IN KẾT QUẢ ---
print("\n=== KẾT QUẢ SAU KHI HẠ ĐỘ KHÓ ===")
report = classification_report(y_test_new, y_pred_smart, output_dict=True)

if '1' in report:
    print(f"Precision Lệnh MUA: {report['1']['precision']:.2%}")
    print(f"Số lệnh MUA dự kiến: {report['1']['support']}")
else:
    print("Vẫn chưa bắt được lệnh MUA nào.")

if '-1' in report:
    print(f"Precision Lệnh BÁN: {report['-1']['precision']:.2%}")
# %% PHASE 5: RETRAINING WITH STRONGER FEATURES
# =========================================================
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

# Cập nhật Features: Thêm thông tin Trend
feature_cols_new = ['log_return', 'log_relative_vol', 'RSI_14', 'log_atr', 'dist_ema200']
# Thêm các lag của RSI và Vol như cũ
for col in ['RSI_14', 'log_relative_vol']:
    for lag in [1, 2, 3]:
        feature_cols_new.append(f'{col}_lag_{lag}')

X_new = df_upgraded[feature_cols_new]
y_new = df_upgraded['target_smart']

# Chia train/test
split = int(len(X_new) * 0.8)
X_train_new, X_test_new = X_new.iloc[:split], X_new.iloc[split:]
y_train_new, y_test_new = y_new.iloc[:split], y_new.iloc[split:]

# Huấn luyện lại Random Forest
print("\n--- RETRAINING (SMARTER MODEL) ---")
rf_smart = RandomForestClassifier(
    n_estimators=300,        # Tăng số lượng cây
    max_depth=7,             # Tăng độ sâu nhẹ vì target giờ đã rõ ràng hơn
    min_samples_leaf=20,     # Giảm nhiễu
    class_weight='balanced_subsample', # Cân bằng trọng số mạnh hơn
    random_state=42,
    n_jobs=-1
)

rf_smart.fit(X_train_new, y_train_new)
y_pred_smart = rf_smart.predict(X_test_new)

# Đánh giá lại
print("\nKẾT QUẢ MỚI:")
report = classification_report(y_test_new, y_pred_smart, output_dict=True)

if '1' in report:
    print(f"Precision Lệnh MUA (Trend Follow): {report['1']['precision']:.2%}")
    print(f"Số lượng lệnh MUA tìm được: {report['1']['support']}")
else:
    print("Không tìm thấy cơ hội MUA nào (Quá an toàn).")

if '-1' in report:
    print(f"Precision Lệnh BÁN (Trend Follow): {report['-1']['precision']:.2%}")
# %% PHASE 6: BACKTEST SIMULATION (KIỂM TRA TIỀN THẬT)
# =========================================================
import matplotlib.pyplot as plt

def simple_backtest(y_true, y_pred, initial_capital=10000, bet_size=100):
    """
    Hàm giả lập giao dịch:
    - Vốn khởi điểm: 10.000 USD
    - Mỗi lệnh đánh: 100 USD
    - Phí giao dịch: 0.1% (Mua + Bán) ~ 2 USD cho volume 2000 USD (Margin 20x)
      Để an toàn, ta trừ cứng 2$ phí cho mỗi lệnh.
    """
    capital = [initial_capital]
    wins = 0
    losses = 0
    
    # Phí giao dịch ước tính (Conservative)
    fee = 2.0 
    
    # Biến để vẽ biểu đồ
    equity_curve = [initial_capital]
    
    for true, pred in zip(y_true, y_pred):
        pnl = 0
        
        # Chỉ vào lệnh khi AI dự đoán khác 0
        if pred != 0:
            if pred == true: 
                # AI đoán đúng (Mua đúng hoặc Bán đúng)
                # Lãi 1R (100$) trừ phí
                pnl = bet_size - fee
                wins += 1
            else:
                # AI đoán sai (Giá chạy ngược hoặc đi ngang)
                # Lỗ 1R (100$) trừ phí
                # Lưu ý: Ở đây ta giả định cứ sai là dính Stoploss mất 100$.
                pnl = -bet_size - fee
                losses += 1
            
            # Cập nhật tài khoản
            new_cap = equity_curve[-1] + pnl
            equity_curve.append(new_cap)
            
    return equity_curve, wins, losses

# --- CHẠY BACKTEST ---
print(">>> Đang chạy giả lập Trading trên tập Test...")
# Lưu ý: y_test_new và y_pred_smart lấy từ bước trước
equity, w, l = simple_backtest(y_test_new, y_pred_smart, initial_capital=10000, bet_size=100)

# --- VẼ BIỂU ĐỒ TÀI SẢN ---
plt.figure(figsize=(12, 6))
plt.plot(equity, label='AI Strategy Equity', color='green', linewidth=2)
plt.axhline(y=10000, color='red', linestyle='--', label='Vốn Gốc (10k$)')

plt.title(f'KẾT QUẢ BACKTEST: Từ 10.000$ -> {int(equity[-1]):,}$')
plt.xlabel('Số lượng lệnh đã khớp')
plt.ylabel('Số dư tài khoản ($)')
plt.legend()
plt.grid(True)
plt.show()

# --- THỐNG KÊ CHI TIẾT ---
total_trades = w + l
win_rate = w / total_trades * 100 if total_trades > 0 else 0
profit = equity[-1] - 10000

print(f"\n=== TỔNG KẾT HIỆU SUẤT ===")
print(f"Tổng số lệnh: {total_trades}")
print(f"Số lệnh Thắng: {w}")
print(f"Số lệnh Thua:  {l}")
print(f"Tỷ lệ Thắng thực tế: {win_rate:.2f}%")
print(f"Lợi nhuận ròng: ${profit:,} USD")

# %%
