# Báo cáo Phân tích Biến động Giá Bitcoin Theo Thời gian

## 1. Mục tiêu & Phương pháp
Báo cáo này phân tích dữ liệu giá Bitcoin (BTC/USDT) khung 5 phút để tìm hiểu đặc điểm biến động trong ngày và các mẫu hình giá lặp lại. Mục tiêu là giúp sinh viên hiểu rõ hơn về hành vi thị trường thông qua dữ liệu.

### Dữ liệu & Chỉ số
-   **Dữ liệu**: `BTCUSDT_5m.csv` (Binance).
-   **Chuyển đổi múi giờ**: Dữ liệu gốc (UTC) được quy đổi sang giờ Việt Nam (UTC+7) và giờ New York (UTC-5) để phân tích theo phiên giao dịch.
-   **Chỉ số sử dụng**:
    -   **ATR(14)**: Đo lường mức độ biến động giá trung bình (Volatility).
    -   **Log Return**: Tỷ suất sinh lời logarit, giúp chuẩn hóa biến động giá.
    -   **Relative Volume (Rel Vol)**: So sánh khối lượng hiện tại với trung bình 24h (288 chu kỳ 5 phút).
    -   **Kurtosis/Skewness**: Đo lường rủi ro đuôi (tail risk) và độ lệch chuẩn của phân phối lợi nhuận.

## 2. Kết quả Phân tích Biến động (Volatility Analysis)

### 2.1. Biến động theo Khung giờ (Hour of Day)
Dựa trên biểu đồ `volatility_by_hour_utc.png` và dữ liệu thống kê:

-   **Giờ biến động mạnh nhất**: Các khung giờ từ **14:00 - 16:00 UTC** (tức **21:00 - 23:00 giờ Việt Nam**) thường có ATR cao nhất. Đây là thời điểm **thị trường Mỹ mở cửa (New York Open)**, dòng tiền giao dịch lớn đổ vào thị trường.
-   **Giờ biến động thấp nhất**: Các khung giờ từ **05:00 - 08:00 UTC** (tức **12:00 - 15:00 giờ Việt Nam**). Đây là khoảng thời gian "nghỉ trưa" của thị trường Á - Âu giao thoa, thanh khoản thường thấp hơn.

### 2.2. Biến động theo Phiên giao dịch (Session)
So sánh giữa các phiên (xem `volatility_by_session.png`):

| Phiên giao dịch | Giờ UTC | Giờ VN | Đặc điểm |
| :--- | :--- | :--- | :--- |
| **Phiên Mỹ (US Session)** | 13:30 - 20:00 | 20:30 - 03:00 | **Biến động cao nhất**. ATR trung bình: ~141.6. Relative Volume: ~1.34 (cao hơn 34% so với TB). |
| **Giao thoa (Overlap)** | - | - | Giai đoạn giao thoa giữa cuối phiên Âu và đầu phiên Mỹ thường có biến động dữ dội nhất. |
| **Phiên Việt Nam (Asian)** | 01:00 - 10:00 | 08:00 - 17:00 | Biến động thấp hơn. ATR trung bình: ~91.7. Relative Volume: ~0.87 (thấp hơn TB). |

> **Nhận xét**: Trader muốn tìm kiếm cơ hội lướt sóng (scalping) nên tập trung vào phiên Mỹ. Sinh viên nghiên cứu thị trường ổn định hơn có thể quan sát phiên Á.

## 3. Phân tích Chuyên Sâu (Deep Dive Analysis)

### 3.1. Hiệu ứng Ngày trong Tuần (Day-of-Week Seasonality)
Biểu đồ `volatility_by_day.png` cho thấy sự khác biệt về biến động giữa các ngày:
-   **Thứ Ba & Thứ Năm**: Thường có mức biến động trung bình cao nhất trong tuần.
-   **Cuối Tuần (Thứ 7, CN)**: Mặc dù thị trường Crypto hoạt động 24/7, nhưng biến động và khối lượng giảm đáng kể vào cuối tuần do các tổ chức tài chính lớn nghỉ.
    -   *ATR Thứ 7*: ~93.8
    -   *ATR Thứ 3*: ~125.6
-> **Kết luận**: Tránh giao dịch breakout vào cuối tuần vì thanh khoản thấp dễ dẫn đến "Fakeout" (Phá vỡ giả).

### 3.2. Hồ sơ Rủi ro (Risk Profile: Skewness & Kurtosis)
Sử dụng biểu đồ `return_distribution_risk.png` để đánh giá rủi ro "Cú sập bất ngờ" (Black Swan):

| Phiên | Kurtosis (Độ nhọn) | Skewness (Độ lệch) | Ý nghĩa |
| :--- | :--- | :--- | :--- |
| **US Session** | **68.2** | **-0.21** | Độ nhọn cực cao cho thấy xác suất xuất hiện các biến động giá KHỦNG KHIẾP (cả tăng và giảm) là rất lớn. Skewness âm nhẹ ám chỉ xu hướng giảm sốc thường mạnh hơn tăng sốc. |
| **VN Session** | 35.4 | 0.15 | Phân phối "lành" hơn, ít biến động đuôi (tail events) hơn so với phiên Mỹ. Skewness dương cho thấy phiên Á đôi khi có những cú pump nhẹ bất ngờ. |

> **Lưu ý**: Kurtosis cao đồng nghĩa với rủi ro cháy tài khoản cao nếu không quản lý vốn chặt chẽ (Stoploss), đặc biệt trong phiên Mỹ.

### 3.3. Phát hiện Bất thường (Anomaly Detection)
Biểu đồ `outliers_by_hour.png` đếm số lượng nến 5m có biến động > 3 Sigma (độ lệch chuẩn):
-   **Giờ "Nguy hiểm"**: Khung giờ **21:00 - 22:00 (VN)** có số lượng bất thường cao nhất. Đây là lúc tin tức kinh tế Mỹ thường được công bố.
-   **Giờ "Yên bình"**: Khung giờ **04:00 - 06:00 sáng (VN)** hầu như không có bất thường lớn nào.

## 4. Phân tích Tương quan & Mẫu hình (Pattern Discovery)

### 4.1. Tương quan (Correlation Heatmap)
Biểu đồ `correlation_heatmap.png`:
-   **ATR vs Volume (0.65)**: Tương quan dương mạnh. Khối lượng tăng là tín hiệu báo trước cho biến động giá sắp tới.
-   **Rel_Vol vs Abs_Return**: Tương quan rất cao. Những cây nến thân dài (Abs Return lớn) hầu như luôn đi kèm với khối lượng đột biến (Relative Volume > 2.0).

### 4.2. Mẫu hình Giá (Price Patterns - K-Means)
Sử dụng thuật toán K-Means Clustering trên các cửa sổ thời gian 1 giờ (12 nến 5m), phát hiện 4 nhóm mẫu hình (xem `price_patterns_clusters.png`):
1.  **Trend Up**: Tăng mạnh liên tục (thường phiên Mỹ).
2.  **Trend Down**: Bán tháo mạnh.
3.  **Sideway**: Dao động quanh trục, phổ biến phiên Á.
4.  **V-Shape**: Quét thanh khoản 2 đầu, thường xuất hiện ở các mốc giờ tròn (H4 close).

## 5. Kết luận & Đề xuất
1.  **Thời điểm giao dịch**: Nếu tìm biến động, hãy đợi **20:30 (Mùa hè)** hoặc **21:30 (Mùa đông)** giờ VN.
2.  **Quản trị rủi ro**: Phiên Mỹ có "Fat tails" (rủi ro đuôi) rất lớn. Tuyệt đối không thả nổi Stoploss trong khung giờ này.
3.  **Chiến lược cuối tuần**: Nên đánh Mean Reversion (đánh quay đầu khi giá chạm biên) vì khả năng trend mạnh là thấp.

---
*Báo cáo được thực hiện bằng Python (Pandas, Scikit-learn) trên dữ liệu thực tế.*
