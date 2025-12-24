import asyncio
import re
from src.infrastructure.adapters.mock_exchange import MockExchangeAdapter
from src.infrastructure.uow_postgres import SqlAlchemyUnitOfWork
from src.application.use_cases.place_order import PlaceOrderUseCase
from src.application.dtos import OrderCreate

# --- REAL IMPLEMENTATION ---
def execute_trade(symbol: str, side: str, quantity: float, price: float = None):
    """
    Executes a REAL trade by calling the Application Layer.
    Persists data to PostgreSQL.
    """
    print(f"\n[TOOL CALLED] execute_trade(symbol='{symbol}', side='{side}', quantity={quantity}, price={price})")
    
    async def run_backend_logic():
        # 1. Setup Dependencies (Manually, since no FastAPI Dependency Injection here)
        uow = SqlAlchemyUnitOfWork()
        exchange = MockExchangeAdapter()
        use_case = PlaceOrderUseCase(uow, exchange)
        
        # 2. Get Current Market Price (Required for the Order)
        # Note: We ignore the passed 'price' arg for simplicity and treat as Market Order
        # or use it if provided (but logic below uses current_price)
        current_price = await exchange.get_current_price(symbol)
        
        # 3. Create the Data Transfer Object (DTO)
        order_dto = OrderCreate(
            symbol=symbol,
            quantity=quantity,
            side=side,
            price=current_price # Market Order behavior
        )
        
        # 4. Execute the Use Case (Write to DB)
        response = await use_case.execute(order_dto)
        return response

    try:
        # Bridge Sync -> Async
        result = asyncio.run(run_backend_logic())
        
        print(f"  -> ✅ DB COMMIT SUCCESS")
        print(f"  -> Real Order ID: {result.order_id}")
        
        return {"status": "success", "order_id": result.order_id, "price": result.price}
        
    except Exception as e:
        print(f"  -> ❌ ERROR: {e}")
        return {"status": "error", "message": str(e)}


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
