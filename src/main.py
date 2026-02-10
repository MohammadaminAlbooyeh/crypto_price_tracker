from fastapi import FastAPI, HTTPException
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="Bitcoin Price Tracker", description="API for tracking Bitcoin prices")

COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

@app.get("/price")
def get_current_price(ids: str = "bitcoin,ethereum,binancecoin,cardano,solana,ripple,dogecoin,polkadot,chainlink,polygon-ecosystem-token,avalanche-2,litecoin,bitcoin-cash,stellar,tron,cosmos,algorand,vechain,iota,monero,eos"):
    """Get current prices for specified cryptocurrencies in USD."""
    try:
        logger.info(f"Fetching current prices for: {ids}")
        response = requests.get(f"{COINGECKO_BASE_URL}/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true")
        response.raise_for_status()
        data = response.json()
        logger.info("Successfully fetched prices.")
        return {coin: {"price": info["usd"], "change_24h": info.get("usd_24h_change", 0)} for coin, info in data.items()}
    except requests.RequestException as e:
        logger.error(f"Error fetching prices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching prices: {str(e)}")

@app.get("/price/history/{coin}")
def get_price_history(coin: str, days: int = 7):
    """Get price history for a specific cryptocurrency for the last N days."""
    try:
        logger.info(f"Fetching price history for {coin} over {days} days.")
        response = requests.get(f"{COINGECKO_BASE_URL}/coins/{coin}/market_chart?vs_currency=usd&days={days}")
        response.raise_for_status()
        data = response.json()
        logger.info("Successfully fetched price history.")
        return {"prices": data["prices"]}  # List of [timestamp, price]
    except requests.RequestException as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@app.get("/exchange-rate")
def get_exchange_rate(base: str = "usd", target: str = "eur"):
    """Get exchange rate between two currencies."""
    try:
        logger.info(f"Fetching exchange rate from {base} to {target}.")
        response = requests.get(f"https://api.exchangerate.host/convert?from={base}&to={target}")
        response.raise_for_status()
        data = response.json()
        logger.info("Successfully fetched exchange rate.")
        return {"rate": data["result"]}
    except requests.RequestException as e:
        logger.error(f"Error fetching exchange rate: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching exchange rate: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)