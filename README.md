# Crypto Price Tracker

A simple project to track Bitcoin prices.

## Requirements
- Python 3.8+
- See [requirements.txt](requirements.txt)

## Installation
1. (Optional) Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage
- Run the command below from the project root to start the tracker:

```bash
python3 src/main.py
```

- To run the optional UI (if provided), run:

```bash
python3 src/ui.py
```

## Notes
- The project dependencies are listed in [requirements.txt](requirements.txt).
- If you prefer, install into your system Python (not recommended) using the same `pip` command above.

# API Documentation

## Endpoints

### `/price`
- **Method**: GET
- **Description**: Get current prices for specified cryptocurrencies in USD.
- **Query Parameters**:
  - `ids` (string, optional): Comma-separated list of cryptocurrency IDs. Default: `bitcoin,ethereum`.
- **Response**:
  ```json
  {
    "bitcoin": {"price": 45000, "change_24h": 2.5},
    "ethereum": {"price": 3000, "change_24h": -1.2}
  }
  ```

### `/price/history/{coin}`
- **Method**: GET
- **Description**: Get price history for a specific cryptocurrency for the last N days.
- **Path Parameters**:
  - `coin` (string): Cryptocurrency ID.
- **Query Parameters**:
  - `days` (integer, optional): Number of days. Default: 7.
- **Response**:
  ```json
  {
    "prices": [[timestamp, price], ...]
  }
  ```

### `/exchange-rate`
- **Method**: GET
- **Description**: Get exchange rate between two currencies.
- **Query Parameters**:
  - `base` (string, optional): Base currency. Default: `usd`.
  - `target` (string, optional): Target currency. Default: `eur`.
- **Response**:
  ```json
  {
    "rate": 0.85
  }
  ```