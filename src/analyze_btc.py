
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import os

import scipy.stats as stats

# Configuration
DATA_PATH = r'd:\PHAN_TICH_DU_LIEU\BTCUSDT_5m.csv'
OUTPUT_DIR = r'd:\PHAN_TICH_DU_LIEU\output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------
# 1. Data Loading & Cleaning
# --------------------------
def load_data(path):
    print(f"Loading data from {path}...")
    df = pd.read_csv(path)
    # Parse timestamp - assuming 'timestamp' column exists and is yyyy-mm-dd hh:mm:ss
    # Based on file preview: 2023-01-01 00:00:00 -> This looks like UTC if from Binance usually
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp').sort_index()
    # Ensure no duplicates
    df = df[~df.index.duplicated(keep='first')]
    return df

# --------------------------
# 2. Timezone Conversion
# --------------------------
def process_timezones(df):
    print("Processing timezones...")
    # Assume input is UTC (standard for crypto data)
    # If index is naively tz-unaware, localize to UTC first
    if df.index.tz is None:
        df.index = df.index.tz_localize('UTC')
    
    # Convert to VN (UTC+7) and US (EDT/EST is UTC-4/-5, we'll use 'America/New_York')
    df['time_vn'] = df.index.tz_convert('Asia/Bangkok')
    df['time_us'] = df.index.tz_convert('America/New_York')
    
    df['hour_vn'] = df['time_vn'].dt.hour
    df['hour_us'] = df['time_us'].dt.hour
    
    return df

# --------------------------
# 3. Metric Calculation
# --------------------------
def calculate_atr(df, period=14):
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    return true_range.rolling(period).mean()

def calculate_metrics(df):
    print("Calculating metrics...")
    # Log Returns
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    
    # ATR(14)
    df['atr_14'] = calculate_atr(df, 14)
    
    # Relative Volume (Volume / 24h Moving Average Volume)
    # 5m candles -> 24h = 12 * 24 = 288 periods
    df['vol_ma_288'] = df['volume'].rolling(window=288).mean()
    df['rel_vol'] = df['volume'] / df['vol_ma_288']
    
    # Realized Volatility (Rolling Std Dev of returns)
    df['volatility_24h'] = df['log_return'].rolling(window=288).std()
    
    # Absolute Return for correlation
    df['abs_return'] = df['log_return'].abs()
    
    df.dropna(inplace=True)
    return df

# --------------------------
# 4. Step 2: Advanced Statistics (Day-of-Week & Risk)
# --------------------------
def analyze_advanced_stats(df):
    print("Performing advanced statistical analysis...")
    
    # --- 1. Day of Week Analysis ---
    # 0=Monday, 6=Sunday
    df['day_of_week'] = df.index.dayofweek
    dow_stats = df.groupby('day_of_week')[['atr_14', 'volume', 'rel_vol']].mean()
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    dow_stats.index = days
    
    plt.figure(figsize=(10, 6))
    dow_stats['atr_14'].plot(kind='bar', color='teal', alpha=0.8)
    plt.title('Average Volatility (ATR) by Day of Week')
    plt.ylabel('ATR')
    plt.savefig(os.path.join(OUTPUT_DIR, 'volatility_by_day.png'))
    plt.close()
    
    # --- 2. Risk Profile (Skewness & Kurtosis) ---
    # Group by Session
    sessions = df['session'].unique()
    risk_data = []
    
    plt.figure(figsize=(12, 6))
    for session in sessions:
        if session == 'Other': continue
        
        subset = df[df['session'] == session]['log_return']
        kurt = stats.kurtosis(subset)
        skew = stats.skew(subset)
        risk_data.append({'session': session, 'kurtosis': kurt, 'skewness': skew})
        
        # Plot distribution
        sns.kdeplot(subset, label=f'{session} (Kurt={kurt:.2f})', clip=(-0.01, 0.01))
        
    plt.title('Return Distribution by Session (Tail Risk Analysis)')
    plt.xlabel('Log Return')
    plt.legend()
    plt.savefig(os.path.join(OUTPUT_DIR, 'return_distribution_risk.png'))
    plt.close()
    
    # Save Risk Stats
    risk_df = pd.DataFrame(risk_data)
    print("\nRisk Profile:")
    print(risk_df)
    
    # --- 3. Correlation Heatmap ---
    corr_cols = ['atr_14', 'volume', 'rel_vol', 'abs_return', 'volatility_24h']
    corr_matrix = df[corr_cols].corr()
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Correlation Matrix: Volume vs Volatility')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_heatmap.png'))
    plt.close()
    
    # --- 4. Anomaly Detection (Outliers) ---
    # Def: Return > 3 * Rolling StdDev (Bollinger Band logic approx)
    # Or simple Z-score of entire dataset
    z_scores = stats.zscore(df['log_return'])
    df['is_outlier'] = np.abs(z_scores) > 3
    
    outliers_by_hour = df[df['is_outlier']].groupby('hour_vn').size()
    
    plt.figure(figsize=(10, 6))
    outliers_by_hour.plot(kind='bar', color='red')
    plt.title('Number of "Black Swan" Events (>3 Sigma) by Hour (VN)')
    plt.ylabel('Count')
    plt.xlabel('Hour (VN)')
    plt.savefig(os.path.join(OUTPUT_DIR, 'outliers_by_hour.png'))
    plt.close()
    
    return dow_stats, risk_df, outliers_by_hour

# --------------------------
# 5. Step 3: Senior Quantitative Metrics (Hurst, VaR, Liquidity)
# --------------------------
def calculate_hurst(series, min_window=10, max_window=None):
    """
    Calculate Hurst Exponent to determine if series is Trending, Mean Reverting, or Random.
    H < 0.5: Mean Reverting
    H = 0.5: Random Walk (Geometric Brownian Motion)
    H > 0.5: Trending
    """
    if max_window is None:
        max_window = len(series) - 1
    
    lags = range(2, 100) # Fast approximation range
    # Standard deviation of differences
    tau = [np.sqrt(np.std(np.subtract(series[lag:], series[:-lag]))) for lag in lags]
    
    # Fit line to log-log plot
    # polyfit returns [slope, intercept]
    # slope of log(tau) vs log(lag) approximates H
    try:
        m = np.polyfit(np.log(lags), np.log(tau), 1)
        hurst = m[0] * 2.0 # Correction for price series vs returns
        return hurst
    except:
        return 0.5

def analyze_senior_metrics(df):
    print("Calculating Senior Quantitative Metrics...")
    
    # 1. Hurst Exponent (on Price Log Prices)
    # Use log price for scale invariance
    log_prices = np.log(df['close'])
    hurst = calculate_hurst(log_prices.values)
    
    # 2. Amihud Illiquidity Ratio
    # |Return| / (Volume * Price) -> Scale up by 1e6 for readability
    # Note: Volume in crypto is usually Base Asset (BTC). So Volume * Price = Quote Asset Volume (USDT).
    # If df['volume'] is BTC, then Quote Vol ~ Volume * Close
    # Check if 'qav' exists (Quote Asset Volume) in data, usually Binance has it.
    # Looking at load_data output step 4: "qav" column exists! Use it for precision.
    if 'qav' in df.columns:
        dollar_vol = df['qav']
    else:
        dollar_vol = df['volume'] * df['close']
        
    df['amihud'] = (df['log_return'].abs() / dollar_vol) * 1e9 # Scaling factor
    avg_amihud = df['amihud'].mean()
    
    # 3. Value at Risk (VaR) & CVaR (Historical Method)
    # 5m VaR at 95% and 99% confidence
    var_95 = np.percentile(df['log_return'], 5)
    var_99 = np.percentile(df['log_return'], 1)
    
    cvar_95 = df[df['log_return'] <= var_95]['log_return'].mean()
    
    print(f"\n--- SENIOR METRICS ---")
    print(f"Hurst Exponent: {hurst:.4f} ({'Trending' if hurst > 0.55 else 'Mean Reverting' if hurst < 0.45 else 'Random'})")
    print(f"Amihud Illiquidity: {avg_amihud:.4f} (Higher = Less Liquid)")
    print(f"VaR (5m, 95%): {var_95:.4%}")
    print(f"VaR (5m, 99%): {var_99:.4%}")
    print(f"CVaR (Expected Shortfall): {cvar_95:.4%}")
    
    # 4. Volatility Clustering (Autocorrelation of Squared Returns)
    squared_returns = df['log_return'] ** 2
    autocorr = [squared_returns.autocorr(lag=i) for i in range(1, 51)]
    
    plt.figure(figsize=(10, 5))
    plt.bar(range(1, 51), autocorr, color='purple', alpha=0.7)
    plt.title('Volatility Clustering: Autocorrelation of Squared Returns')
    plt.xlabel('Lag (5m periods)')
    plt.ylabel('Autocorrelation')
    plt.savefig(os.path.join(OUTPUT_DIR, 'volatility_clustering_acf.png'))
    plt.close()
    
    # Save Metrics
    with open(os.path.join(OUTPUT_DIR, 'senior_metrics.txt'), 'w') as f:
        f.write(f"Hurst Exponent: {hurst:.4f}\n")
        f.write(f"Interpret: {'Trending' if hurst > 0.55 else 'Mean Reverting' if hurst < 0.45 else 'Random'}\n")
        f.write(f"Amihud Illiquidity Score: {avg_amihud:.6f}\n")
        f.write(f"VaR 95% (5m): {var_95:.6f}\n")
        f.write(f"VaR 99% (5m): {var_99:.6f}\n")
        f.write(f"Expected Shortfall (CVaR 95%): {cvar_95:.6f}\n")
        
    return hurst, avg_amihud, var_95

# --------------------------
# 6. Session Definition
# --------------------------
def define_sessions(row):
    # Heuristic definitions based on typical working hours
    # VN: 8:00 - 17:00 (UTC+7)
    # US: 9:30 - 16:00 (UTC-4/-5) -> New York Time
    
    h_vn = row['hour_vn']
    h_us = row['hour_us']
    
    is_vn_active = 8 <= h_vn <= 17
    # Simple NYSE core hours approximation (9-16)
    is_us_active = 9 <= h_us <= 16
    
    if is_vn_active and is_us_active:
        return 'Overlap'
    elif is_us_active:
        return 'US Session'
    elif is_vn_active:
        return 'VN Session'
    else:
        return 'Other'

# --------------------------
# 5. Analysis & Visualization
# --------------------------
def analyze_volatility(df):
    print("Analyzing volatility...")
    
    # Hourly Analysis (UTC+0 basis for standardization in plot, but labeled with session context)
    hourly_stats = df.groupby(df.index.hour)[['atr_14', 'log_return', 'volume', 'rel_vol']].agg({
        'atr_14': 'mean',
        'volume': 'mean',
        'rel_vol': 'mean',
        'log_return': lambda x: x.abs().mean() # Mean absolute return = magnitude of move
    })
    
    # Plot Average Volatility by Hour (UTC)
    plt.figure(figsize=(12, 6))
    sns.barplot(x=hourly_stats.index, y=hourly_stats['atr_14'], palette='viridis')
    plt.title('Average Bitcoin Volatility (ATR 14) by Hour (UTC)')
    plt.xlabel('Hour (UTC)')
    plt.ylabel('Average ATR')
    plt.savefig(os.path.join(OUTPUT_DIR, 'volatility_by_hour_utc.png'))
    plt.close()
    
    # Session Analysis
    df['session'] = df.apply(define_sessions, axis=1)
    session_stats = df.groupby('session')[['atr_14', 'rel_vol']].mean()
    
    print("\nSession stats:")
    print(session_stats)
    
    # Save stats to file
    with open(os.path.join(OUTPUT_DIR, 'stats.txt'), 'w') as f:
        f.write("Hourly Stats (UTC):\n")
        f.write(hourly_stats.to_string())
        f.write("\n\nSession Stats:\n")
        f.write(session_stats.to_string())
    
    plt.figure(figsize=(10, 6))
    session_stats['atr_14'].plot(kind='bar', color='skyblue')
    plt.title('Average Volatility by Market Session')
    plt.ylabel('ATR')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'volatility_by_session.png'))
    plt.close()

# --------------------------
# 6. Pattern Discovery (Clustering)
# --------------------------
def find_patterns(df, n_clusters=4, window_size=12): # window_size=12 -> 1 hour (5m * 12)
    print("Discovering patterns...")
    # We want to cluster the *shape* of price movements over 1 hour windows
    # Normalize each window to start at 0 or scale 0-1
    
    sequences = []
    # Sampling: take every 12th window to avoid massive overlap redundancy for demo
    # For production: sliding window stride 1
    stride = 12 
    
    # Use close prices
    closes = df['close'].values
    
    for i in range(0, len(closes) - window_size, stride):
        seq = closes[i : i + window_size]
        # Normalize: (x - min) / (max - min) to capture shape, ignoring absolute price level
        # Or simpler: percent change from start
        seq_norm = (seq - seq[0]) / seq[0]
        sequences.append(seq_norm)
    
    X = np.array(sequences)
    
    # Remove flat lines/outliers if any (std=0)
    # stds = np.std(X, axis=1)
    # X = X[stds > 0]
    
    if len(X) > 10000: # Downsample if too big
        idx = np.random.choice(len(X), 10000, replace=False)
        X_sample = X[idx]
    else:
        X_sample = X
        
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
    labels = kmeans.fit_predict(X_sample)
    
    # Visualize Cluster Centers
    plt.figure(figsize=(12, 8))
    for i, center in enumerate(kmeans.cluster_centers_):
        plt.plot(center, label=f'Pattern {i}')
    
    plt.title(f'Common 1-Hour Price Patterns (K-Means, K={n_clusters})')
    plt.xlabel('Time Steps (5m)')
    plt.ylabel('Normalized Price Change')
    plt.legend()
    plt.savefig(os.path.join(OUTPUT_DIR, 'price_patterns_clusters.png'))
    plt.close()
    
    return kmeans

# --------------------------
# Main
# --------------------------
def main():
    df = load_data(DATA_PATH)
    df = process_timezones(df)
    df = calculate_metrics(df) # Calculates session implicitly if I move it? No, need session col first?
    # Note: define_sessions is called inside analyze_volatility currently. 
    # Let's apply session definition globally here for advanced stats to use
    df['session'] = df.apply(define_sessions, axis=1)
    
    analyze_volatility(df)
    
    # Phase 2: Advanced Analysis
    dow_stats, risk_df, outliers = analyze_advanced_stats(df)
    
    # Save advanced stats
    with open(os.path.join(OUTPUT_DIR, 'advanced_stats.txt'), 'w') as f:
        f.write("Day of Week Stats:\n")
        f.write(dow_stats.to_string())
        f.write("\n\nRisk Profile (Kurtosis/Skewness):\n")
        f.write(risk_df.to_string())
        f.write("\n\nOutliers by Hour (VN):\n")
        f.write(outliers.to_string())

    # Phase 3: Senior Metrics
    analyze_senior_metrics(df)

    find_patterns(df)
    
    print("Analysis complete. Check 'output' directory.")

if __name__ == "__main__":
    main()
