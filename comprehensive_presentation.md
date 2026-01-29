---
marp: true
theme: default
paginate: true
header: 'Bitcoin Technical & Quantitative Analysis - Master Report'
footer: 'Antigravity AI Research'
style: |
  section { font-family: 'Arial', sans-serif; }
  h1 { color: #2c3e50; }
  h2 { color: #34495e; }
  strong { color: #e74c3c; }
  img { box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 8px; }
---

# Báo Cáo Phân Tích Toàn Diện: Bitcoin (BTC/USDT)
## Từ Chỉ Báo Kỹ Thuật (Technical) đến Định Lượng (Quantitative)

**Môn học**: Phân tích Dữ liệu Tài chính
**Dữ liệu**: Binance 5-minute Data
**Phương pháp**: Hybrid (Technical Indicators + Machine Learning Stats)

---

# 1. Tổng Quan Dữ Liệu & Phương Pháp

Chúng tôi tiếp cận bài toán theo 3 lớp (layers):
1.  **Lớp Cơ bản (Legacy)**: Sử dụng các chỉ báo kinh điển (RSI, Bollinger Bands, ATR) để đánh giá trạng thái thị trường.
2.  **Lớp Thời gian (Time-Series)**: Phân tích tính mùa vụ (Seasonality) theo Giờ và Tuần.
3.  **Lớp Định lượng (Deep Quant)**: Đo lường rủi ro đuôi (VaR) và tính hiệu quả thị trường (Hurst).

---

# 2. Phân Tích Kỹ Thuật (Technical Analysis)

### Phân phối RSI (Relative Strength Index)
*   **Quan sát**: Phần lớn thời gian RSI dao động trong vùng **40-60**.
*   **Ý nghĩa**: Thị trường chủ yếu ở trạng thái cân bằng (Equilibirum). Các điểm quá mua (>70) và quá bán (<30) xuất hiện ít nhưng xác suất đảo chiều cao.
*   *(Tham chiếu file: `Phan_phoi_chi_tiet_RSI_14.png`)*

### Dải Bollinger (Volatility Bands)
*   **Quan sát**: Giá bám sát dải giữa (Mean).
*   **Ngoại lai**: Các điểm vượt ra ngoài Band 2.0 (2 độ lệch chuẩn) thường bị kéo ngược lại rất nhanh (Mean Reversion).
*   *(Tham chiếu file: `BBP_20_2.0_2.0.png`)*

---

# 3. Cấu Trúc Biến Động (Volatility Structure)

### "Giờ Vàng" Giao Dịch
*   **Đỉnh biến động**: `20:00 - 22:00 VN`. Đây là lúc **Phiên Mỹ (New York)** mở cửa, dòng tiền Wall Street đổ vào.
*   **Đáy biến động**: `05:00 - 08:00 VN`. Thị trường "ngủ đông".

![bg right:40% fit](output/volatility_by_hour_utc.png)

### Hiệu ứng Ngày trong Tuần
*   **Thứ 7 & CN**: Thanh khoản giảm ~40%.
*   **Rủi ro**: Dễ dính bẫy giá (Fakeout) do thiếu thanh khoản.

---

# 4. Định Lượng Nâng Cao (Quantitative Metrics)

Chúng tôi sử dụng thuật toán để đo lường các chỉ số mà mắt thường không thấy được:

| Chỉ số | Giá trị | Ý nghĩa Chiến lược |
| :--- | :---: | :--- |
| **Hurst Exponent** | **0.49** | Thị trường **Random Walk**. Không có xu hướng (Trend) rõ ràng trong dài hạn. **-> Đánh Swing/Scalp.** |
| **VaR 99% (5m)** | **-0.41%** | Rủi ro sập >0.4% trong 5 phút xảy ra ~3 lần/ngày. **-> Cẩn trọng leverage > x20.** |
| **Amihud Ratio** | **0.18** | Thanh khoản tốt, khó bị thao túng bởi lệnh nhỏ. |

*(Dữ liệu từ: `senior_metrics.txt`)*

---

# 5. Phân Cụm Hành Vi Giá (Pattern Clustering)

Sử dụng **K-Means Clustering** để tìm các mẫu hình lặp lại trong khung 1H:

1.  **V-Shape**: Giật xuống rồi kéo lên nhanh (Quét Stoploss).
2.  **Steady Trend**: Xu hướng bền vững (thường vào phiên Mỹ).
3.  **Sideway**: Đi ngang (chiếm đa số phiên Á).

![w:700](output/price_patterns_clusters.png)

---

# 6. Tương Quan (Correlation)

Dựa trên biểu đồ nhiệt (`tuong_quan.png` và `correlation_heatmap.png`):

*   **Volume vs Volatility**: Tương quan dương mạnh ($R > 0.6$).
*   **Kết luận**: Biến động giá lớn LUÔN đi kèm khối lượng lớn. Nếu giá tăng mà Volume thấp -> **Bẫy tăng giá (Bull Trap)**.

---

# 7. Kết Luận & Khuyến Nghị

Từ việc tổng hợp tất cả các file dữ liệu, chúng tôi đề xuất:

1.  **Chiến lược Chủ đạo**: **Mean Reversion** (Mua thấp Bán cao trong biên độ). Hạn chế Breakout.
2.  **Thời gian**: Chỉ trade tích cực vào phiên Mỹ. Nghỉ ngơi cuối tuần.
3.  **Quản trị rủi ro**: Đặt Stoploss dựa trên biến động (ATR) thay vì số điểm cố định. Tránh xa các giờ ra tin (nơi có nhiều Ngoại lai - Outliers).

---

# Q&A

**Antigravity AI Research**
*Báo cáo được tổng hợp tự động từ d:\PHAN_TICH_DU_LIEU*
