# RSI Indicator Flask App

This Flask-based application fetches stock market data from the **IG Index REST API** and calculates the **Relative Strength Index (RSI)** for a given stock. The app provides an endpoint to retrieve RSI data for any stock symbol by fetching historical price data from IG Index and performing the calculation.

## Features

- Authenticate with the IG Index REST API.
- Fetch stock market data using the IG Index API.
- Calculate the **RSI (Relative Strength Index)** for any given stock symbol.
- Returns RSI data via a Flask API endpoint.
- Configurable stock resolution, page settings, and max results.

## Technologies Used

- **Python**
- **Flask** (Web framework)
- **aiohttp** (Asynchronous HTTP Client)
- **pandas** (Data manipulation)
- **IG Index REST API** (Market data)
- **datetime** (Date and time handling)

## How It Works

1. **Authentication:**
   The app authenticates with the **IG Index API** using your provided credentials (API Key, Username, and Password). This generates the necessary tokens for API requests.

2. **Fetch Market Data:**
   The app searches for a stock symbol using the API. Once the stock is found, it retrieves its "epic" key to fetch historical market data for that stock.

3. **Fetch Historical Price Data:**
   The app uses the epic key to retrieve historical stock price data, including close prices.

4. **RSI Calculation:**
   The app calculates the **Relative Strength Index (RSI)** based on the close prices retrieved from the historical data.

5. **API Endpoint:**
   A **Flask** API endpoint (`/rsi/<stock_symbol>`) is exposed to get RSI data for any stock symbol.

## Setup and Installation

To set up and run this Flask app locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/RSI-Indicator-Flask-App.git
    ```

2. Navigate to the project directory:
    ```bash
    cd RSI-Indicator-Flask-App
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory with your **IG API credentials**:
    ```env
    IG_API_KEY=your_ig_api_key
    IG_USERNAME=your_ig_username
    IG_PASSWORD=your_ig_password
    ```

5. Run the Flask app:
    ```bash
    python app.py
    ```

    By default, the app will run on `http://127.0.0.1:5000`.

## API Usage

Once the app is running, you can fetch RSI data for any stock symbol by making a GET request to the following endpoint:

