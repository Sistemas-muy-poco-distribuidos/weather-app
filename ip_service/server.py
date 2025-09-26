import os
import json
from concurrent import futures

import grpc
import requests

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from protos import weatherapp_pb2, weatherapp_pb2_grpc

IPWHO_ENDPOINT = "https://ipwho.is/"

class IpLocatorServicer(weatherapp_pb2_grpc.IpLocatorServicer):
    def GetLocation(self, request, context):
        ip = request.ip.strip()
        if not ip:
            # If no IP provided, try to get from x-forwarded-for passed via metadata (optional)
            ip = dict(context.invocation_metadata()).get("x-forwarded-for", "")
            ip = ip.split(",")[0].strip() if ip else ""

        if ip.lower() in ("", "me", "self"):
            # ipwho.is allows empty for auto? It doesn't. We'll fallback to 'jsonip' style - not applicable.
            # Require explicit IP if not provided; return error.
            return weatherapp_pb2.LocationResponse(error="No IP provided to IpLocator service.")

        try:
            resp = requests.get(IPWHO_ENDPOINT + ip, timeout=5)
            data = resp.json()
            if not data.get("success", False):
                return weatherapp_pb2.LocationResponse(error=f"ipwho.is error: {data.get('message','unknown')}")
            loc = weatherapp_pb2.Location(
                ip=data.get("ip",""),
                city=data.get("city",""),
                region=data.get("region",""),
                country=data.get("country",""),
                latitude=float(data.get("latitude", 0.0)),
                longitude=float(data.get("longitude", 0.0)),
            )
            return weatherapp_pb2.LocationResponse(location=loc)
        except Exception as e:
            return weatherapp_pb2.LocationResponse(error=f"Exception contacting ipwho.is: {e}")

def serve():
    port = os.environ.get("IP_SERVICE_PORT", "50051")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    weatherapp_pb2_grpc.add_IpLocatorServicer_to_server(IpLocatorServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"IpLocator service listening on {port}", flush=True)
    server.wait_for_termination()

if __name__ == "__main__":
    serve()