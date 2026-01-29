import os

# Define the HTML content structure
html_content = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Báo cáo Phân tích Định lượng Bitcoin</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }
        .container { background-color: white; padding: 40px; box-shadow: 0 0 15px rgba(0,0,0,0.1); border-radius: 8px; }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { color: #2980b9; margin-top: 30px; }
        h3 { color: #16a085; }
        img { max-width: 100%; height: auto; display: block; margin: 20px auto; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        .caption { text-align: center; font-style: italic; color: #7f8c8d; margin-bottom: 20px; font-size: 0.9em; }
        code { background-color: #f1f2f6; padding: 2px 5px; border-radius: 3px; font-family: Consolas, monospace; }
        .math { background-color: #ecf0f1; padding: 10px; border-left: 4px solid #3498db; margin: 10px 0; font-style: italic; }
        .abstract { font-style: italic; background-color: #e8f6f3; padding: 20px; border-radius: 5px; border-left: 5px solid #1abc9c; margin-bottom: 30px; }
        ul, ol { margin-left: 20px; }
        li { margin-bottom: 8px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #2c3e50; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
    </style>
</head>
<body>

<div class="container">

    <div style="text-align: center; margin-bottom: 50px;">
        <h1>PHÂN TÍCH ĐỊNH LƯỢNG VÀ CẤU TRÚC VI MÔ THỊ TRƯỜNG BITCOIN</h1>
        <h3>Báo cáo Chuyên sâu (Thesis Level)</h3>
        <p><strong>Antigravity AI Research</strong> | Ngày: 28/01/2026</p>
    </div>

    <div class="abstract">
        <strong>Tóm tắt:</strong> Báo cáo này trình bày một nghiên cứu toàn diện về cấu trúc vi mô của thị trường Bitcoin 
        thông qua dữ liệu giao dịch tần suất cao (5 phút). Sử dụng kết hợp các chỉ báo kỹ thuật truyền thống và các phương pháp 
        thống kê định lượng tiên tiến, chúng tôi xác định được các chế độ thị trường đặc thù. Kết quả cho thấy thị trường Bitcoin 
        tại khung thời gian ngắn hạn tuân theo bước đi ngẫu nhiên nhưng vẫn tồn tại các cửa sổ cơ hội dựa trên tính mùa vụ 
        và các bất thường thống kê tại các biên độ cực trị (>3 sigma).
    </div>

    <h2>1. Giới thiệu</h2>
    <p>Thị trường tiền mã hóa, đặc biệt là Bitcoin, nổi tiếng với độ biến động cực đoan và rủi ro đuôi (tail risk) lớn. 
    Vấn đề đặt ra là làm thế nào để định lượng hóa các rủi ro này và tìm kiếm lợi nhuận dựa trên các bằng chứng thống kê vững chắc.</p>

    <h2>3. Dữ liệu & Phương pháp Nghiên cứu</h2>
    
    <h3>3.1. Mô tả Dữ liệu</h3>
    <p>Nghiên cứu sử dụng dữ liệu thị trường từ sàn giao dịch <strong>Binance</strong> - sàn Crypto lớn nhất thế giới.</p>
    <ul>
        <li><strong>Cặp giao dịch:</strong> BTC/USDT.</li>
        <li><strong>Khung thời gian:</strong> 5 phút (High-Frequency Trading context).</li>
        <li><strong>Cấu trúc:</strong> Chuỗi thời gian bao gồm OHLC (Open, High, Low, Close) và Volume (Khối lượng).</li>
    </ul>

    <h3>3.2. Phương pháp Nghiên cứu (Hybrid Approach)</h3>
    <p>Chúng tôi áp dụng quy trình 4 bước chuẩn khoa học dữ liệu:</p>
    <ol>
        <li><strong>Tiền xử lý (Preprocessing):</strong> Làm sạch dữ liệu, xử lý Missing Values bằng phương pháp Forward Fill, và chuyển đổi giá sang Lợi nhuận Logarit (Log Returns) để đảm bảo tính dừng.</li>
        <li><strong>Trích chọn đặc trưng (Feature Engineering):</strong> Tính toán các chỉ báo kỹ thuật (RSI, Bollinger Bands, ATR) và các chỉ số thống kê trượt (Rolling Skewness/Kurtosis).</li>
        <li><strong>Phân tích Định lượng (Quantitative Analysis):</strong> Sử dụng các kiểm định thống kê như Jarque-Bera (kiểm tra phân phối chuẩn), Hurst Exponent (đo lường tính nhớ của chuỗi), và ACF (đo lường biến động tụ tập).</li>
        <li><strong>Học máy (Machine Learning):</strong> Áp dụng thuật toán K-Means Clustering để tự động phân loại các chế độ thị trường (Market Regimes) mà không cần gán nhãn thủ công.</li>
    </ol>

    <h2>3. Thống kê Mô tả & Phân phối</h2>
    
    <h3>3.1. Phân phối RSI</h3>
    <img src="Phan_phoi_chi_tiet_RSI_14.png" alt="Phân phối RSI">
    <div class="caption">Hình 1: Phân phối xác suất của chỉ số RSI. Dữ liệu tập trung vùng 40-60.</div>

    <h3>3.2. Cấu trúc Thanh khoản (Volume)</h3>
    <img src="Phan_phoi_chi_tiet_relative_vol.png" alt="Volume Distribution">
    <div class="caption">Hình 2: Phân phối Log-normal của khối lượng giao dịch.</div>

    <h3>3.3. Dải Bollinger & ATR</h3>
    <div style="display: flex; gap: 10px;">
        <div style="width: 50%;">
            <img src="BBP_20_2.0_2.0.png" alt="Bollinger Bands">
            <div class="caption">Hình 3: Bollinger Bands %</div>
        </div>
        <div style="width: 50%;">
            <img src="ATRr_14.png" alt="ATR">
            <div class="caption">Hình 4: ATR Distribution</div>
        </div>
    </div>

    <h2>4. Phân tích Chuỗi thời gian (Temporal Dynamics)</h2>
    
    <h3>4.1. "Giờ Vàng" Giao dịch</h3>
    <img src="output/volatility_by_hour_utc.png" alt="Volatility by Hour">
    <div class="caption">Hình 5: Biến động trung bình theo giờ (UTC). Đỉnh cao tại phiên Mỹ mở cửa.</div>

    <h3>4.2. Cấu trúc Vĩ mô (Ngày & Phiên)</h3>
    <div style="display: flex; gap: 10px;">
        <div style="width: 50%;">
            <img src="output/volatility_by_session.png" alt="Session Volatility">
            <div class="caption">Hình 6: Biến động theo Phiên</div>
        </div>
        <div style="width: 50%;">
            <img src="output/volatility_by_day.png" alt="Day Volatility">
            <div class="caption">Hình 7: Biến động theo Thứ</div>
        </div>
    </div>
    <p><strong>Nhận xét:</strong> Tránh giao dịch Breakout vào cuối tuần do thanh khoản thấp.</p>

    <h2>5. Rủi ro & Định lượng Nâng cao</h2>
    
    <h3>5.1. Rủi ro Đuôi (Tail Risk)</h3>
    <img src="output/return_distribution_risk.png" alt="Risk Distribution">
    <div class="caption">Hình 8: Kurtosis rất cao (Fat-tails) tại phiên Mỹ.</div>

    <h3>5.2. Biến động Tụ tập (Volatility Clustering)</h3>
    <img src="output/volatility_clustering_acf.png" alt="GARCH Effect">
    <div class="caption">Hình 9: Hiệu ứng GARCH - Biến động sinh ra biến động.</div>

    <h3>5.3. Tương quan Đa biến</h3>
    <img src="output/correlation_heatmap.png" alt="Correlation Heatmap">
    <div class="caption">Hình 10: Tương quan mạnh giữa Volume và Volatility (R > 0.6).</div>

    <h2>6. Phân cụm & Phát hiện Bất thường</h2>
    
    <h3>6.1. Phân cụm K-Means</h3>
    <img src="output/price_patterns_clusters.png" alt="Price Patterns">
    <div class="caption">Hình 11: 4 Chế độ thị trường: Tăng, Giảm, Sideway, và Biến động mạnh (V-Shape).</div>

    <h3>6.2. Phân tích Ngoại lai (Outliers)</h3>
    <img src="output/outliers_by_hour.png" alt="Outliers Context">
    <div class="caption">Hình 12: Thời điểm xuất hiện các cú sập giá (Flash Crash).</div>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
        <img src="ngoai_lai_rsi_14.png" alt="RSI Outliers">
        <img src="ngoai_lai_log_return.png" alt="Return Outliers">
        <img src="ngoai_lai_BBP_2.0.png" alt="BBP Outliers">
        <img src="ngoai_lai_relative_vol.png" alt="Volume Outliers">
    </div>
    <div class="caption">Hình 13: Chi tiết các điểm dị biệt (3-Sigma Events).</div>

    <h2>7. Kết luận & Chiến lược</h2>
    <ul>
        <li><strong>Timing:</strong> Tập trung giao dịch 14:00 - 22:00 UTC.</li>
        <li><strong>Risk:</strong> Dùng Stoploss theo ATR để tránh bị quét trong phiên Mỹ.</li>
        <li><strong>Chiến lược:</strong> 
            <ul>
                <li>Phiên Á: Đánh Mean Reversion (Mua thấp bán cao).</li>
                <li>Phiên Mỹ: Chờ tín hiệu Volume lớn để Follow Trend.</li>
            </ul>
        </li>
    </ul>

</div>

</body>
</html>
"""

with open("bao_cao_bitcoin.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Đã tạo file báo cáo HTML thành công: bao_cao_bitcoin.html")
