from concurrent import futures
import time

import grpc

from rearpb import  rearpb_pb2_grpc,rearpb_pb2

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class Rear(rearpb_pb2_grpc.RearServicer):

    """ Implement all GRPC server methods here"""

    def HealthCheck(self,request,context):
        return rearpb_pb2.HealthCheckReply(ok=True)

    def SayHello(self, request, context):
        return rearpb_pb2.HelloReply(message='Hello, this is rear server %s!' % request.name)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rearpb_pb2_grpc.add_RearServicer_to_server(Rear(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
