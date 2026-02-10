import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import requests
import plotly.graph_objects as go
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

CRYPTO_IDS = ["bitcoin", "ethereum", "binancecoin", "cardano", "solana", "ripple", "dogecoin", "polkadot", "chainlink", "polygon-ecosystem-token", "avalanche-2", "litecoin", "bitcoin-cash", "stellar", "tron", "cosmos", "algorand", "vechain", "iota", "monero", "eos"]
CRYPTO_NAMES = ["Bitcoin", "Ethereum", "Binance Coin", "Cardano", "Solana", "Ripple", "Dogecoin", "Polkadot", "Chainlink", "Polygon", "Avalanche", "Litecoin", "Bitcoin Cash", "Stellar", "Tron", "Cosmos", "Algorand", "VeChain", "IOTA", "Monero", "EOS"]
CRYPTO_ICONS = ["₿", "Ξ", "BNB", "ADA", "SOL", "XRP", "DOGE", "DOT", "LINK", "MATIC", "AVAX", "LTC", "BCH", "XLM", "TRX", "ATOM", "ALGO", "VET", "MIOTA", "XMR", "EOS"]

app.layout = dbc.Container([
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col(dbc.Button("Refresh Prices", id="refresh-btn", color="primary", n_clicks=0), width="auto"),
                dbc.Col(dbc.NavbarBrand("", className="ms-2"), width="auto"),
                dbc.Col(html.Div("Based on recent 24 hours", className="text-muted small ms-2"), width="auto")
            ], align="center", className="w-100"),
        ]),
        color="dark",
        dark=True,
        className="mb-4"
    ),

    dbc.Row([
        # Left sidebar: Exchange + Top movers
        dbc.Col([
            # Exchange widget
            dbc.Card([
                dbc.CardHeader(html.H6("Exchange", className="mb-0 text-light"), style={"backgroundColor": "#162029", "border": "none"}),
                dbc.CardBody([
                    dbc.Label("You will send", className="text-muted small"),
                    dbc.Input(id="send-amount", placeholder="0.00", type="number", value=1),
                    dbc.Row([
                        dbc.Col(dcc.Dropdown(id="send-coin", options=[{"label": name, "value": id} for name, id in zip(CRYPTO_NAMES, CRYPTO_IDS)], value="bitcoin"), width=5),
                        dbc.Col(html.Button("↔", className="btn btn-outline-light w-100"), width=2, style={"display": "flex", "alignItems": "center", "justifyContent": "center"}),
                        dbc.Col(dcc.Dropdown(id="receive-coin", options=[{"label": name, "value": id} for name, id in zip(CRYPTO_NAMES, CRYPTO_IDS)] + [{"label": "USD", "value": "usd"}, {"label": "EUR", "value": "eur"}], value="ethereum"), width=5)
                    ], className="my-2"),
                    dbc.Label("You will receive", className="text-muted small"),
                    dbc.Row([
                        dbc.Col(dbc.Input(id="receive-amount", placeholder="0.00", type="text", disabled=True, value=""), width=12)
                    ], className="mb-2"),
                    dbc.Button("Exchange", color="danger", className="mt-3 w-100")
                ])
            ], style={"backgroundColor": "#1b2228", "border": "none"}, className="mb-4"),

            # Top movers
            dbc.Card([
                dbc.CardHeader(html.H6("Top Movers", className="mb-0 text-light"), style={"backgroundColor": "#162029", "border": "none"}),
                dbc.CardBody(html.Div(id="top-movers"))
            ], style={"backgroundColor": "#162029", "border": "none"})
        ], width=3),

        # Right main area: small cards, chart, prices
        dbc.Col([
            # Top small cards row
            dcc.Loading(
                id="loading-prices",
                type="default",
                children=dbc.Row(id="prices-row", className="mb-4 g-2")
            ),

            # Large chart card
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(html.Div([html.H5(id="chart-title", className="text-light mb-0"), html.Div(id="chart-sub", className="text-muted small")])),
                        dbc.Col(dcc.Dropdown(id="crypto-dropdown", options=[{"label": name, "value": id} for name, id in zip(CRYPTO_NAMES, CRYPTO_IDS)], value="bitcoin", clearable=False), width=3)
                    ], align="center"),
                    dcc.Loading(id="loading-chart", type="default", children=dcc.Graph(id="price-chart", config={"displayModeBar": False}))
                ]),
            ], className="mb-4", style={"backgroundColor": "#1f2630", "border": "none"}),

            # Prices list / table
            dbc.Card([
                dbc.CardHeader(html.H6("Crypto Prices", className="mb-0 text-light"), style={"backgroundColor": "#162029", "border": "none"}),
                dbc.CardBody(html.Div(id="prices-list"))
            ], style={"backgroundColor": "#162029", "border": "none"})
        ], width=9)
    ]),

    dcc.Interval(id="interval-component", interval=60000, n_intervals=0)  # Refresh every 60 seconds
], fluid=True)

@app.callback(
    Output("prices-row", "children"),
    Output("prices-list", "children"),
    Output("top-movers", "children"),
    Output("chart-title", "children"),
    Output("chart-sub", "children"),
    Input("refresh-btn", "n_clicks"),
    Input("interval-component", "n_intervals")
)
def update_prices(n_clicks, n_intervals):
    try:
        ids = ",".join(CRYPTO_IDS)
        response = requests.get(f"http://localhost:8000/price?ids={ids}")
        response.raise_for_status()
        data = response.json()
        cards = []
        list_items = []
        movers = []
        # Build cards and lists
        for crypto_id, info in data.items():
            price = info.get("price", 0)
            change = info.get("change_24h", 0)
            name = CRYPTO_NAMES[CRYPTO_IDS.index(crypto_id)]
            icon = CRYPTO_ICONS[CRYPTO_IDS.index(crypto_id)]
            change_color = "text-success" if change >= 0 else "text-danger"
            change_symbol = "▲" if change >= 0 else "▼"
            card = dbc.Col(
                dbc.Card(
                    dbc.CardBody([
                        html.H5([html.Span(icon, className="me-2"), name], className="card-title text-light"),
                        html.P(f"${price:,.2f}", className="card-text text-light font-weight-bold h5"),
                        html.P(f"{change_symbol} {change:.2f}%", className=f"card-text {change_color} small"),
                    ]),
                    className="mb-3 shadow",
                    style={"backgroundColor": "#2c3e50"}
                ),
                width=2
            )
            cards.append(card)
            # prices list item
            list_items.append(html.Div([
                html.Span(icon, className="me-2"), html.Strong(name), html.Span(f" — ${price:,.2f}", className="ms-2 text-muted"), html.Span(f"  {change_symbol} {change:.2f}%", className=f"ms-3 {change_color}")
            ], className="d-flex justify-content-between align-items-center mb-2 text-light"))
            # top movers (take top 5 by absolute change)
            movers.append((abs(change), html.Div([html.Span(icon, className="me-2"), html.Span(name), html.Span(f" {change:.2f}%", className=f"ms-2 {change_color}")], className="text-light mb-2")))

        movers_sorted = [m[1] for m in sorted(movers, key=lambda x: x[0], reverse=True)[:6]]

        # Chart title/sub
        chart_title = f"{CRYPTO_NAMES[0]} (overview)"
        chart_sub = "Trend and recent activity"

        return cards, list_items, movers_sorted, chart_title, chart_sub
    except requests.RequestException:
        alert = dbc.Col(dbc.Alert("Error fetching prices. Ensure FastAPI backend is running.", color="danger"))
        return alert, html.Div(""), html.Div(""), "", ""

@app.callback(
    Output("price-chart", "figure"),
    Input("crypto-dropdown", "value"),
    Input("refresh-btn", "n_clicks"),
    Input("interval-component", "n_intervals")
)
def update_chart(selected_crypto, n_clicks, n_intervals):
    try:
        response = requests.get(f"http://localhost:8000/price/history/{selected_crypto}?days=7")
        response.raise_for_status()
        data = response.json()
        prices = data["prices"]
        timestamps = [p[0] for p in prices]
        values = [p[1] for p in prices]
        fig = go.Figure(data=[go.Scatter(x=timestamps, y=values, mode="lines", line=dict(color="#3498db"))])
        crypto_name = CRYPTO_NAMES[CRYPTO_IDS.index(selected_crypto)]
        fig.update_layout(
            title=f"{crypto_name} Price History (Last 7 Days)",
            xaxis_title="Time",
            yaxis_title="Price (USD)",
            plot_bgcolor="#2c3e50",
            paper_bgcolor="#2c3e50",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#34495e"),
            yaxis=dict(gridcolor="#34495e")
        )
        return fig
    except requests.RequestException:
        return go.Figure(layout=dict(
            title="Error loading chart",
            plot_bgcolor="#2c3e50",
            paper_bgcolor="#2c3e50",
            font=dict(color="white")
        ))


@app.callback(
    Output("receive-amount", "value"),
    Input("send-amount", "value"),
    Input("send-coin", "value"),
    Input("receive-coin", "value"),
    Input("refresh-btn", "n_clicks"),
    Input("interval-component", "n_intervals")
)
def compute_receive_amount(send_amount, send_coin, receive_coin, n_clicks, n_intervals):
    """Compute how much `receive_coin` you'd get for `send_amount` of `send_coin` using backend prices."""
    try:
        # guard
        if not send_coin or not receive_coin:
            return ""
        try:
            amt = float(send_amount or 0)
        except (TypeError, ValueError):
            amt = 0.0

        # If receiving fiat (usd/eur), fetch price of send_coin in that fiat
        if receive_coin in ("usd", "eur"):
            cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={send_coin}&vs_currencies={receive_coin}"
            resp = requests.get(cg_url)
            resp.raise_for_status()
            j = resp.json()
            price_in_fiat = j.get(send_coin, {}).get(receive_coin)
            if price_in_fiat is None:
                return ""
            receive_amount = amt * float(price_in_fiat)
            return f"{receive_amount:,.6f}"

        # If receiving crypto, fetch both coins' USD prices and compute
        ids = f"{send_coin},{receive_coin}"
        cg_url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
        resp = requests.get(cg_url)
        resp.raise_for_status()
        j = resp.json()
        price_send_usd = j.get(send_coin, {}).get("usd")
        price_receive_usd = j.get(receive_coin, {}).get("usd")
        if price_send_usd is None or price_receive_usd is None or float(price_receive_usd) == 0:
            return ""
        usd_value = amt * float(price_send_usd)
        receive_amount = usd_value / float(price_receive_usd)
        return f"{receive_amount:,.6f}"
    except requests.RequestException:
        return ""

@app.callback(
    Output("price-output", "children"),
    Input("refresh-btn", "n_clicks")
)
def refresh_prices(n_clicks):
    if n_clicks is None:
        return "Click refresh to get prices."
    try:
        logger.info("Refreshing prices.")
        response = requests.get(f"{COINGECKO_BASE_URL}/simple/price?ids={','.join(CRYPTO_IDS)}&vs_currencies=usd")
        response.raise_for_status()
        data = response.json()
        logger.info("Successfully refreshed prices.")
        return "Prices updated."
    except requests.RequestException as e:
        logger.error(f"Error refreshing prices: {str(e)}")
        return "Error refreshing prices. Please try again later."

if __name__ == "__main__":
    app.run(debug=True)