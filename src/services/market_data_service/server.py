from concurrent import futures
import time
import grpc
import logging
import random

from src.generated import market_data_pb2
from src.generated import market_data_pb2_grpc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MarketDataService")

class MarketDataService(market_data_pb2_grpc.MarketDataServiceServicer):
    def StreamMarketData(self, request, context):
        symbol = request.symbol.upper()
        logger.info(f"Received subscription for {symbol}")
        
        try:
            while True:
                price = 100.0 + random.uniform(-1, 1)
                volume = random.uniform(1, 10)
                timestamp = int(time.time() * 1000)
                
                response = market_data_pb2.MarketDataResponse(
                    symbol=symbol,
                    price=price,
                    volume=volume,
                    timestamp=timestamp
                )
                
                yield response
                time.sleep(1)
                
        except Exception as e:
            logger.error(f"Error streaming data: {e}")
            context.abort(grpc.StatusCode.INTERNAL, str(e))

def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_data_pb2_grpc.add_MarketDataServiceServicer_to_server(MarketDataService(), server)
    server.add_insecure_port('[::]:' + port)
    logger.info(f"Market Data Service started on port {port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
