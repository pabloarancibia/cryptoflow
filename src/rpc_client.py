import grpc
import time
import sys

from src.generated import market_data_pb2
from src.generated import market_data_pb2_grpc
from src.generated import order_pb2
from src.generated import order_pb2_grpc

def run_market_data_client():
    print("--- Market Data Client (Streaming) ---")
    try:
        with grpc.insecure_channel('localhost:50051') as channel:
            stub = market_data_pb2_grpc.MarketDataServiceStub(channel)
            request = market_data_pb2.MarketDataRequest(symbol="BTC/USD")
            
            print("Subscribing to BTC/USD...")
            
            start_time = time.time()
            for response in stub.StreamMarketData(request):
                print(f"Update: {response.symbol} | Price: {response.price:.2f} | Vol: {response.volume:.2f}")
                
                if time.time() - start_time > 3:
                    break
                    
    except Exception as e:
        print(f"Market Data Error: {e}")

def run_order_client():
    print("\n--- Order Client (Unary) ---")
    try:
        with grpc.insecure_channel('localhost:50052') as channel:
            stub = order_pb2_grpc.OrderServiceStub(channel)
            
            request = order_pb2.OrderRequest(
                symbol="ETH/USD",
                quantity=1.5,
                price=2500.00,
                side="BUY"
            )
            
            response = stub.PlaceOrder(request)
            print(f"Order Response: ID={response.order_id}, Status={response.status}, Msg={response.message}")
            
    except Exception as e:
        print(f"Order Error: {e}")

if __name__ == '__main__':
    run_order_client()
    run_market_data_client()
