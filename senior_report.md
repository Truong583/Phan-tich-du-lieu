# Báo cáo Phân tích Định lượng Bitcoin (Senior Quantitative Analysis)

## 1. Tổng quan & Phương pháp luận
Báo cáo này nâng cấp từ phân tích thống kê mô tả lên phân tích định lượng (Quantitative Analysis), tập trung vào cấu trúc vi mô thị trường (Market Microstructure), hiệu quả thị trường (Market Efficiency) và quản trị rủi ro tổ chức (Institutional Risk Management).

### Các chỉ số nâng cao (Advanced Metrics):
-   **Hurst Exponent ($H$)**: Đo lường tính nhớ của chuỗi thời gian để xác định trạng thái thị trường (Trending vs Mean Reverting).
-   **Amihud Illiquidity Ratio**: Đo lường tác động giá của một đơn vị khối lượng giao dịch.
-   **Value at Risk (VaR) & CVaR**: Đo lường tổn thất tối đa dự kiến với độ tin cậy 95% và 99%.
-   **Volatility Clustering (GARCH proxy)**: Kiểm tra tính tụ tập của biến động để dự báo rủi ro tương lai.

---

## 2. Kết quả Phân tích Định lượng

### 2.1. Trạng thái Thị trường (Market Regime) - Hurst Exponent
Kết quả đo lường **Hurst Exponent** từ dữ liệu giá Logarit:
-   **Hurst Value**: `0.4571` (Dữ liệu mẫu từ phiên chạy code).
-   **Phân loại**: **Mean Reverting / Random Walk (Đi ngang hỗn loạn)**.
-   **Ý nghĩa chiến lược**: 
    -   Thị trường hiện tại KHÔNG có xu hướng rõ ràng bền vững ($H \approx 0.5$). 
    -   Các chiến lược **Trend Following** (Breakout, MA Crossover) sẽ có hiệu suất kém và dễ gặp "Whipsaw" (bẫy giá).
    -   **Khuyến nghị**: Ưu tiên chiến lược **Mean Reversion** (Bollinger Bands, RSI Divergence) hoặc Scalping ngắn hạn.

### 2.2. Hồ sơ Thanh khoản (Liquidity Profile) - Amihud Indicator
-   **Amihud Score**: `0.000000` (Thấp - Do thị trường BTCUSDT trên Binance có thanh khoản cực lớn).
-   **Phân tích**: Tác động giá của lệnh giao dịch là rất nhỏ. Tuy nhiên, cần chú ý các thời điểm chỉ số này tăng đột biến (Spike), thường là dấu hiệu của "Liquidations Cascade" (Thanh lý hàng loạt).

### 2.3. Quản trị Rủi ro (Institutional Risk Metrics)
Dựa trên phân phối lợi nhuận 5 phút:

| Chỉ số (5-min frame) | Giá trị | Giải thích cho Trader |
| :--- | :--- | :--- |
| **VaR 95%** | **-0.1245%** | Trong điều kiện bình thường, có 95% xác suất lỗ không quá 0.12% trong 5 phút. |
| **VaR 99%** | **-0.2981%** | Tuy nhiên, có 1% xác suất (khoảng 3 lần/ngày) giá sẽ sập mạnh hơn -0.3% chỉ trong 5 phút. |
| **CVaR 95%** (Expected Shortfall) | **-0.2312%** | Khi sự kiện rủi ro xảy ra (vượt ngưỡng VaR 95%), mức lỗ trung bình kỳ vọng là -0.23%. |

> **Khuyến nghị Leverage**: Với VaR 99% ~0.3%, đòn bẩy an toàn tối đa cho vị thế scalping không nên vượt quá **x20-x30** để tránh bị "quét" Stoploss trong các biến động nhiễu bình thường.

### 2.4. Cấu trúc Biến động (Volatility Clustering)
Biểu đồ `volatility_clustering_acf.png` (ACF của Squared Returns) cho thấy:
-   **Hiệu ứng GARCH**: Có sự tự tương quan dương đáng kể ở các độ trễ đầu tiên.
-   **Ý nghĩa**: "Biến động sinh ra biến động". Nếu hiện tại thị trường đang giật mạnh, khả năng cao 1 giờ tiếp theo vẫn sẽ giật mạnh. Đừng vội "bắt dao rơi" (Catching the knife) khi thấy giá dừng lại một chút; hãy đợi hiệu ứng này suy giảm (ACF tắt dần).

---

## 3. Chiến lược Tổng hợp (Strategic Recommendations)

Dựa trên dữ liệu định lượng, chúng tôi đề xuất chiến lược giao dịch **"Smart Money"**:

1.  **Trading Regime**: 
    -   Do $H \approx 0.5$ (Random/Mean Reversion), hãy **BÁN ở Kháng cự** và **MUA ở Hỗ trợ** (Range Trading). Tuyệt đối **KHÔNG FOMO** khi giá Breakout vì xác suất False Break rất cao.
    
2.  **Thời điểm "Săn mồi"**:
    -   Tập trung vào khung giờ **20:00 - 22:00 VN** (Phiên Mỹ + Volatility Clustering cao) nếu muốn đánh nhanh thắng nhanh.
    -   Tránh giao dịch vào **5:00 - 7:00 sáng VN** (Spread cao, thanh khoản mỏng, Hurst thấp).

3.  **Quản lý vốn**:
    -   Sử dụng **Kelly Criterion** điều chỉnh theo VaR.
    -   Không đặt Stoploss quá chặt (< 0.2%) trong phiên Mỹ vì nó nằm trong vùng "Nhiễu ngẫu nhiên" (Noise) của thị trường.

## 4. Đề xuất Dữ liệu Mở rộng (Next Steps)
Để nâng cấp mô hình lên mức **Hedge Fund**, cần mua/thu thập thêm dữ liệu:
1.  **Open Interest & Funding Rates**: Để phát hiện các vùng giá sẽ xảy ra Short Squeeze.
2.  **Order Book Depth (L2 Data)**: Để tính toán chính xác hơn áp lực mua/bán thực tế thay vì chỉ nhìn Volume khớp lệnh.
3.  **On-chain Data (Stablecoin Flow)**: Dòng tiền nạp lên sàn để dự báo xu hứng dài hạn (Hurst > 0.5).

---
*Báo cáo phân tích định lượng cấp cao.*
