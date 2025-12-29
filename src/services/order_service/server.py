import asyncio
import logging
import uuid
import json
import os
import aio_pika
import grpc

from src.generated import order_pb2
from src.generated import order_pb2_grpc
from src.generated import market_data_pb2
from src.generated import market_data_pb2_grpc

from src.infrastructure.uow_postgres import SqlAlchemyUnitOfWork
from src.domain.entities import Order

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OrderService")

# Configuration
MARKET_DATA_SERVICE_ADDRESS = "localhost:50051"
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

class OrderService(order_pb2_grpc.OrderServiceServicer):
    def __init__(self):
        self.uow = SqlAlchemyUnitOfWork()
        self.market_channel = None
        self.market_stub = None
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self.exchange = None

    async def _ensure_infrastructure(self):
        """Lazy initialization of infrastructure connections"""
        if not self.market_channel:
            self.market_channel = grpc.aio.insecure_channel(MARKET_DATA_SERVICE_ADDRESS)
            self.market_stub = market_data_pb2_grpc.MarketDataServiceStub(self.market_channel)
            logger.info(f"Connected to Market Data Service at {MARKET_DATA_SERVICE_ADDRESS}")

        if not self.rabbitmq_connection:
            try:
                self.rabbitmq_connection = await aio_pika.connect_robust(RABBITMQ_URL)
                self.rabbitmq_channel = await self.rabbitmq_connection.channel()
                # Declare exchange if needed, or just use default. For now, assuming direct or default.
                # Let's declare a topic exchange for events
                self.exchange = await self.rabbitmq_channel.declare_exchange(
                    "order_events", aio_pika.ExchangeType.TOPIC, durable=True
                )
                logger.info("Connected to RabbitMQ")
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ: {e}")
                raise

    async def _get_current_price(self, symbol: str) -> float:
        """Fetch current price from Market Data Service"""
        try:
            # market_data.proto defines StreamMarketData, but for single price check we might need to
            # just consume the first item or assuming there is a Unary call. 
            # The user prompt said: "Call the Market Data Service (stub.StreamMarketData) or a new Unary method GetPrice (if available) to get the current price. For now, you can just consume one item from the stream or mock it."
            # Since I didn't see a GetPrice in the proto, I will consume one item from stream.
            request = market_data_pb2.MarketDataRequest(symbol=symbol)
            async for response in self.market_stub.StreamMarketData(request):
                return response.price
                # We only need one
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            # Fallback or re-raise. For HFT, maybe fallback to a recent cache or reject.
            # Choosing to reject for safety in this demo.
            raise ValueError(f"Could not fetch price for {symbol}")

    async def PlaceOrder(self, request, context):
        logger.info(f"Received order: {request.side} {request.quantity} {request.symbol}")

        # 1. Validation
        if request.quantity <= 0:
             await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Quantity must be positive")

        await self._ensure_infrastructure()

        try:
            # 2. Market Check
            current_price = await self._get_current_price(request.symbol)
            
            # Use the fetched price or limit price? 
            # If it's a MARKET order (implied if price is 0 or ignored), use current. 
            # If LIMIT, check if price <= current (for BUY) etc.
            # User requirement: "Call the Market Data Service ... to get the current price."
            # It doesn't explicitly say to USE it for the order price, but usually we validate or use it.
            # Let's assume we use the request price if provided, but maybe just Validate it against market?
            # "If request.quantity <= 0, abort... Market Check... Persistence... Event"
            # The prompt is a bit vague on HOW to use the price. 
            # Let's assume we store the order with the request price, but maybe we just log the market price for now 
            # OR better, if request.price is 0, we treat as market order and use current_price.
            
            final_price = request.price
            if final_price <= 0:
                final_price = current_price

            order_id = str(uuid.uuid4())
            
            # 3. Persistence
            async with self.uow:
                new_order = Order(
                    order_id=order_id,
                    symbol=request.symbol,
                    quantity=request.quantity,
                    price=final_price,
                    side=request.side
                )
                await self.uow.orders.add(new_order)
                # auto-commit on exit
            
            # 4. Event Publishing
            event_message = {
                "event": "order_created",
                "order_id": order_id,
                "symbol": request.symbol,
                "quantity": request.quantity,
                "price": final_price,
                "side": request.side,
                "status": "ACCEPTED"
            }
            
            await self.exchange.publish(
                aio_pika.Message(
                    body=json.dumps(event_message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key="order.created"
            )
            logger.info(f"Order {order_id} persisted and event published.")

            return order_pb2.OrderResponse(
                order_id=order_id,
                status="ACCEPTED",
                message="Order processing started"
            )

        except ValueError as ve:
             await context.abort(grpc.StatusCode.UNAVAILABLE, str(ve))
        except Exception as e:
            logger.error(f"Internal error: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, "Internal server error")


async def serve():
    port = "50052"
    server = grpc.aio.server()
    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:' + port)
    logger.info(f"Order Service started on port {port}")
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())
