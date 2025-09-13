from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from stock_utils import fetch_stock_data
from predictor import predict_next_7_days
from gemini_utils import get_gemini_reasoning

app = FastAPI()

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stock/{symbol}")
def get_stock_data(symbol: str):
    try:
        data = fetch_stock_data(symbol)
        data["Date"] = data["Date"].astype(str)
        return data.to_dict(orient="records")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        
@app.get("/combined/{symbol}")
def get_combined_data(symbol: str):
    """Get both recent historical data and predictions in one call"""
    try:
        # Get prediction data
        predict_data = predict_next_7_days(symbol)
        
        # Get recent stock data (last 7 days)
        df = fetch_stock_data(symbol)
        df["Date"] = pd.to_datetime(df["Date"])
        recent_data = df.tail(7)[["Date", "Close"]].copy()
        
        historical_list = [
            {"date": str(row["Date"].date()), "close": round(row["Close"], 2), "type": "historical"}
            for _, row in recent_data.iterrows()
        ]
        
        # Format prediction for visualization
        prediction_list = [
            {"date": item["date"], "close": item["predicted_close"], "type": "prediction"}
            for item in predict_data["prediction"]
        ]
        
        # Combine both lists
        combined_data = historical_list + prediction_list
        
        return {
            "historical": historical_list,
            "prediction": predict_data["prediction"],
            "combined": combined_data
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/predict/{symbol}")
def get_prediction(symbol: str):
    try:
        data = predict_next_7_days(symbol)
        # Return only the prediction part to maintain compatibility with frontend
        return data["prediction"]
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/reasoning/{symbol}")
def get_reasoning(symbol: str):
    try:
        # Get both recent and prediction data
        predict_data = predict_next_7_days(symbol)
        
        # Get the full stock data for the recent history
        df = fetch_stock_data(symbol)
        df["Date"] = pd.to_datetime(df["Date"])
        recent_data = df.tail(7)[["Date", "Close"]].copy()
        recent_data_list = [
            {"date": str(row["Date"].date()), "close": round(row["Close"], 2)}
            for _, row in recent_data.iterrows()
        ]
        
        # Use the prediction data
        prediction = predict_data["prediction"]
        
        # Get reasoning from Gemini
        reasoning = get_gemini_reasoning(symbol, recent_data_list, prediction)
        return {"reasoning": reasoning}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reasoning generation failed: {e}")