import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from stock_utils import fetch_stock_data


HORIZONS = [1, 2, 3, 4, 5, 6, 7]


def predict_next_7_days(symbol: str):
    df = fetch_stock_data(symbol, period="10y")

    df = df[["Date", "Close", "High", "Low"]].copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)

    # -------------------------
    # Feature engineering
    # -------------------------
    df["return_1d"] = df["Close"].pct_change()

    for i in range(1, 6):
        df[f"lag{i}"] = df["Close"].shift(i)

    df["ma5"] = df["Close"].rolling(5).mean()
    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma50"] = df["Close"].rolling(50).mean()

    df["rsi"] = calculate_rsi(df["Close"])
    df["bollinger_width"] = calculate_bollinger_width(df["Close"])

    df.dropna(inplace=True)

    feature_cols = [
        "lag1", "lag2", "lag3", "lag4", "lag5",
        "ma5", "ma20", "ma50",
        "return_1d", "rsi", "bollinger_width"
    ]

    X = df[feature_cols]
    last_close = df["Close"].iloc[-1]

    predictions = {}

    # -------------------------
    # Train one model per horizon
    # -------------------------
    for h in HORIZONS:
        df[f"target_{h}"] = (
            df["Close"].shift(-h) - df["Close"]
        ) / df["Close"]

        horizon_df = df.dropna(subset=[f"target_{h}"])
        y = horizon_df[f"target_{h}"]
        X_h = horizon_df[feature_cols]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_h)

        model = RandomForestRegressor(
            n_estimators=300,
            max_depth=12,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1
        )

        model.fit(X_scaled, y)

        # Predict horizon h
        last_features = scaler.transform(X.tail(1))
        predicted_return = model.predict(last_features)[0]

        predictions[h] = predicted_return

    # -------------------------
    # Convert returns to prices
    # -------------------------
    future_prices = []
    future_dates = pd.bdate_range(
        start=df["Date"].iloc[-1] + pd.Timedelta(days=1),
        periods=7
    )

    for i, h in enumerate(HORIZONS):
        price = last_close * (1 + predictions[h])
        future_prices.append(round(price, 2))

    # -------------------------
    # Output formatting
    # -------------------------
    prediction_data = [
        {
            "date": str(future_dates[i].date()),
            "predicted_close": future_prices[i]
        }
        for i in range(7)
    ]

    historical_data = [
        {
            "date": str(row["Date"].date()),
            "close": round(row["Close"], 2),
            "is_prediction": False
        }
        for _, row in df.tail(7).iterrows()
    ]

    return {
        "historical": historical_data,
        "prediction": prediction_data,
        "combined": historical_data + prediction_data
    }


# -------------------------
# Indicators
# -------------------------
def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = -delta.clip(upper=0).rolling(window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_bollinger_width(prices, window=20):
    ma = prices.rolling(window).mean()
    std = prices.rolling(window).std()
    return (4 * std) / ma
