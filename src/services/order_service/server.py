from concurrent import futures
import logging
import uuid
import grpc

from src.generated import order_pb2
from src.generated import order_pb2_grpc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OrderService")

class OrderService(order_pb2_grpc.OrderServiceServicer):
    def PlaceOrder(self, request, context):
        logger.info(f"Received order: {request.side} {request.quantity} {request.symbol} @ {request.price}")
        
        if request.quantity <= 0:
             context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Quantity must be positive")

        order_id = str(uuid.uuid4())
        
        return order_pb2.OrderResponse(
            order_id=order_id,
            status="ACCEPTED",
            message="Order placed successfully via gRPC"
        )

def serve():
    port = "50052"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    order_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)
    server.add_insecure_port('[::]:' + port)
    logger.info(f"Order Service started on port {port}")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
