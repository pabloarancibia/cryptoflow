import re
from src.infrastructure.adapters.mock_exchange import MockExchangeAdapter

# Tool Definition
def execute_trade(symbol: str, side: str, quantity: float, price: float = None):
    """
    Executes a trade on the exchange.
    """
    print(f"\n[TOOL CALLED] execute_trade(symbol='{symbol}', side='{side}', quantity={quantity}, price={price})")
    
    # Simulate execution
    adapter = MockExchangeAdapter()
    # In a real scenario, we might await this. For demo, we just print.
    print(f"  -> Connecting to Exchange...")
    print(f"  -> Order Placed Successfully!")
    return {"status": "success", "order_id": "simulated_id_123"}


class SimulatedAgent:
    def __init__(self):
        self.system_prompt = "You are an intelligent trading assistant. You can execute trades based on user commands."

    def run(self, prompt: str):
        print(f"\n[AGENT] Received prompt: '{prompt}'")
        print("[AGENT] Thinking...")
        
        # Simulated parsing logic (Parsing natural language via Regex)
        # Supports patterns like: "Buy/Sell 10 ETH", "Place a SELL order for 5 BTC"
        
        # Normalize
        p = prompt.lower()
        
        side = None
        if "buy" in p: side = "BUY"
        elif "sell" in p: side = "SELL"
        
        quantity = None
        # Extract number
        match_qty = re.search(r'(\d+(\.\d+)?)', p)
        if match_qty:
            quantity = float(match_qty.group(1))
            
        symbol = None
        # Simple heuristic for symbol (3-4 uppercase letters)
        # scan original prompt for uppercase words
        words = prompt.split()
        for w in words:
            clean_w = w.strip(".,")
            if clean_w.isupper() and 3 <= len(clean_w) <= 5 and clean_w not in ["BUY", "SELL"]:
                symbol = clean_w
                break
        
        if side and quantity and symbol:
            print(f"[AGENT] Intent detected: {side} {quantity} {symbol}")
            print(f"[AGENT] Invoking tool 'execute_trade'...")
            result = execute_trade(symbol, side, quantity)
            print(f"[AGENT] Tool Output: {result}")
            return f"I have executed your order to {side} {quantity} {symbol}. Order ID: {result['order_id']}"
        else:
            return "I understood the command but couldn't extract all parameters (Side, Quantity, Symbol). Please clarify."
