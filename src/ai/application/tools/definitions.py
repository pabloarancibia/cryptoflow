
# Tool Definition for execute_trade
execute_trade_def = {
    "name": "execute_trade",
    "description": "Executes a trade order on the exchange.",
    "parameters": {
        "type": "object",
        "properties": {
            "symbol": {
                "type": "string",
                "description": "The trading pair symbol, e.g., 'BTC/USD'."
            },
            "side": {
                "type": "string",
                "enum": ["buy", "sell"],
                "description": "The side of the trade: 'buy' or 'sell'."
            },
            "quantity": {
                "type": "number",
                "description": "The amount to trade."
            }
        },
        "required": ["symbol", "side", "quantity"]
    }
}
