import grpc
import logging
from src.generated import order_pb2_grpc
from src.generated import market_data_pb2_grpc

logger = logging.getLogger("GrpcInfrastructure")

class GrpcClientManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GrpcClientManager, cls).__new__(cls)
            cls._instance.order_channel = None
            cls._instance.market_channel = None
            cls._instance.order_stub = None
            cls._instance.market_stub = None
        return cls._instance

    async def initialize(self):
        """Initialize gRPC channels and stubs."""
        # Connect to Order Service (running on 50052)
        if not self.order_channel:
            self.order_channel = grpc.aio.insecure_channel('localhost:50052')
            self.order_stub = order_pb2_grpc.OrderServiceStub(self.order_channel)
            logger.info("Initialized connection to Order Service at localhost:50052")

        # Connect to Market Data Service (running on 50051)
        if not self.market_channel:
            self.market_channel = grpc.aio.insecure_channel('localhost:50051')
            self.market_stub = market_data_pb2_grpc.MarketDataServiceStub(self.market_channel)
            logger.info("Initialized connection to Market Data Service at localhost:50051")

    async def close(self):
        """Close all gRPC channels."""
        if self.order_channel:
            await self.order_channel.close()
            logger.info("Closed Order Service channel")
        if self.market_channel:
            await self.market_channel.close()
            logger.info("Closed Market Data Service channel")

    def get_order_stub(self):
        if not self.order_stub:
             # In case it's called before initialize, though lifespan should handle it.
             # Ideally, we rely on initialize being called. 
             # For robustness, we could throw error or lazy init (but lazy init async in sync property is hard).
             raise RuntimeError("GrpcClientManager not initialized. Call initialize() first.")
        return self.order_stub

    def get_market_data_stub(self):
        if not self.market_stub:
            raise RuntimeError("GrpcClientManager not initialized. Call initialize() first.")
        return self.market_stub

# Global instance
grpc_client_manager = GrpcClientManager()
