import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_gemini_reasoning(symbol: str, recent_data: list, prediction: list) -> str:
    """
    Get stock trend analysis from Gemini API based on historical and prediction data.
    
    Args:
        symbol: Stock ticker symbol
        recent_data: List of historical stock data points
        prediction: List of predicted stock data points
    
    Returns:
        String containing Gemini's analysis of the stock trend
    """
    if not GEMINI_API_KEY:
        return "Gemini API key not configured."

    # Format historical data for prompt
    historical_str = "\n".join([
        f"Date: {data['date']}, Close: ${data['close']}" 
        for data in recent_data
    ])
    
    # Format prediction data for prompt
    prediction_str = "\n".join([
        f"Date: {data['date']}, Predicted Close: ${data['predicted_close']}" 
        for data in prediction
    ])

    prompt = f"""Analyze the following recent stock data and 7-day prediction for {symbol}.
    
    Recent Historical Data:
    {historical_str}

    Prediction for Next 7 Days:
    {prediction_str}

    Provide a brief explanation of the stock's short-term trend, focusing on:
    1. Key patterns in the historical data
    2. The predicted direction and volatility
    3. Notable price levels or potential turning points
    4. Overall sentiment (bullish, bearish, or neutral)
    
    Keep your analysis concise (100-150 words) and focus on actionable insights.
    """

    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
        response.raise_for_status()
        gemini_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return gemini_text
    except Exception as e:
        return f"Gemini API error: {e}"