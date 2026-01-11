import requests 
import pandas as pd 
import time 
from datetime import datetime 

def get_data(symbol, interval, start_date):
    print(f"--> Đang tải {symbol} khung {interval} từ ngày {start_date}...")
    

    url = "https://data-api.binance.vision/api/v3/klines"
    try:
        start_ts = int(pd.Timestamp(start_date).timestamp() * 1000)
        end_ts = int(pd.Timestamp(datetime.now()).timestamp() * 1000)
    except:
        print("Lỗi ngày tháng (Dùng định dạng Năm-Tháng-Ngày, vd: 2023-01-01)")
        return 

    all_data = []
    

    while start_ts < end_ts:
        params = {
            'symbol': symbol,
            'interval': interval,
            'limit': 1000,
            'startTime': start_ts
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                
             
                if not data: break
                

                all_data.extend(data)
                
                
                start_ts = data[-1][6] + 1
      
                if len(all_data) % 5000 == 0:
                    print(f"   Đã tải được {len(all_data)} dòng...")

                time.sleep(0.5)
            else:
                print("Lỗi kết nối, thử lại...")
                time.sleep(1)
        except Exception as e:
            print(f"Lỗi: {e}")
            break
    

    print("--> Đang xử lý và lưu file...")
    
    
    cot_du_lieu = [
        'open_time', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'qav', 'num_trades', 'tbv', 'tqv','ignore'
    ]
    
    df = pd.DataFrame(all_data, columns=cot_du_lieu)

    df.insert(0, 'timestamp', pd.to_datetime(df['open_time'], unit='ms'))
    

    cols_float = ['open', 'high', 'low', 'close', 'volume', 'qav', 'tbv', 'tqv']
    df[cols_float] = df[cols_float].apply(pd.to_numeric)
    df['num_trades'] = pd.to_numeric(df['num_trades'])
    


    file_name = f"{symbol}_{interval}.csv"
    df.to_csv(file_name, index=False)
    
    print(f"XONG! Đã lưu file: {file_name} ({len(df)} dòng)")


if __name__ == "__main__":
    get_data(symbol="BTCUSDT", interval="5m", start_date="2023-01-01")