import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from stock_utils import fetch_stock_data

def predict_next_7_days(symbol: str):
    """
    Predicts stock prices for the next 7 days using enhanced features
    and adds realistic variability to predictions.
    Returns both recent historical data and future predictions.
    """
    # Fetch 10 years of historical data as defined in stock_utils
    df = fetch_stock_data(symbol, period="10y")
    
    # Copy needed columns and sort by date
    df = df[["Date", "Close", "Volume", "High", "Low"]].copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    
    # Calculate daily returns and volatility
    df["daily_return"] = df["Close"].pct_change()
    df["volatility"] = df["daily_return"].rolling(window=21).std() * np.sqrt(252)  # Annualized volatility
    
    # Create lag features
    for i in range(1, 6):  # Use 5 previous days' closing prices
        df[f"lag{i}"] = df["Close"].shift(i)
    
    # Technical indicators
    # Moving averages
    df["ma5"] = df["Close"].rolling(window=5).mean()
    df["ma20"] = df["Close"].rolling(window=20).mean()
    df["ma50"] = df["Close"].rolling(window=50).mean()
    
    # Momentum indicators
    df["price_change_pct"] = df["Close"].pct_change(5)  # 5-day return
    df["rsi"] = calculate_rsi(df["Close"], window=14)
    
    # Volatility indicators
    df["high_low_range"] = (df["High"] - df["Low"]) / df["Close"]  # Normalized daily range
    df["bollinger_width"] = calculate_bollinger_width(df["Close"], window=20)
    
    # Volume indicators
    df["volume_change"] = df["Volume"].pct_change()
    df["volume_ma_ratio"] = df["Volume"] / df["Volume"].rolling(window=20).mean()
    
    # Clean data
    df.dropna(inplace=True)
    
    # Store the last 7 days of historical data for return
    last_7_days = df.iloc[-7:].copy()
    
    # Select features for prediction
    feature_columns = [
        "lag1", "lag2", "lag3", "lag4", "lag5", 
        "ma5", "ma20", "ma50", 
        "price_change_pct", "rsi", 
        "high_low_range", "volatility", "bollinger_width",
        "volume_change", "volume_ma_ratio"
    ]
    
    X = df[feature_columns]
    y = df["Close"]
    
    # Scale features for better model performance
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train RandomForest model with more trees and deeper
    model = RandomForestRegressor(
        n_estimators=150, 
        max_depth=15,
        min_samples_split=5,
        random_state=42
    )
    model.fit(X_scaled, y)
    
    # Get feature importance for debugging/analysis
    feature_importance = dict(zip(feature_columns, model.feature_importances_))
    
    # Get the last known values for prediction
    last_values = df[feature_columns].iloc[-1].values.reshape(1, -1)
    last_values_scaled = scaler.transform(last_values)
    
    # Get recent volatility for realistic prediction
    recent_volatility = df["volatility"].iloc[-1] / np.sqrt(252)  # Daily volatility
    
    # Generate predictions with realistic variability
    prediction_values = []
    current_scaled_input = last_values_scaled.copy()
    
    recent_close = df["Close"].iloc[-1]
    recent_high_low_range = df["high_low_range"].iloc[-1]
    
    for i in range(7):
        # Base prediction
        base_prediction = model.predict(current_scaled_input)[0]
        
        # Add realistic variability based on recent volatility
        # More variance for further out predictions
        variability_factor = (i + 1) / 7  # Increases with each step
        noise = np.random.normal(0, recent_volatility * recent_close * variability_factor)
        prediction = base_prediction + noise
        
        # Ensure prediction is reasonable (not too far from previous)
        if i > 0:
            max_change = recent_close * recent_volatility * 2  # Max reasonable daily change
            if abs(prediction - prediction_values[-1]) > max_change:
                # Limit change to be reasonable
                direction = 1 if prediction > prediction_values[-1] else -1
                prediction = prediction_values[-1] + direction * max_change
        
        prediction_values.append(round(prediction, 2))
        
        # Update inputs for next prediction - simple approach for demo
        if i < 6:  # Update the lag values
            # Rolling the lag values (lag1 becomes lag2, etc.)
            current_scaled_input[0, 1:5] = current_scaled_input[0, 0:4]  # Shift lags
            
            # Normalize the new prediction before adding as lag1
            # This is a simplified approach; in production you'd compute all features properly
            current_scaled_input[0, 0] = (prediction - np.mean(df["Close"])) / np.std(df["Close"])
    
    # Generate dates for predictions
    last_date = df["Date"].max()
    future_dates = [last_date + pd.Timedelta(days=i+1) for i in range(7)]
    
    # Format prediction data - maintaining original format for frontend compatibility
    prediction_data = [
        {"date": str(future_dates[i].date()), "predicted_close": prediction_values[i]}
        for i in range(7)
    ]
    
    # Format historical data
    historical_data = [
        {"date": str(row["Date"].date()), "close": round(row["Close"], 2), "is_prediction": False}
        for _, row in last_7_days.iterrows()
    ]
    
    # Combine both datasets
    combined_data = {
        "historical": historical_data,
        "prediction": prediction_data,
        "combined": historical_data + prediction_data
    }
    
    return combined_data

def calculate_rsi(prices, window=14):
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_width(prices, window=20):
    """Calculate Bollinger Band width"""
    ma = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    upper_band = ma + (std * 2)
    lower_band = ma - (std * 2)
    width = (upper_band - lower_band) / ma  # Normalized width
    return width