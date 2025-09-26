import os
import datetime as dt
from concurrent import futures

import grpc
import requests

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from protos import weatherapp_pb2, weatherapp_pb2_grpc

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

class WeatherServicer(weatherapp_pb2_grpc.WeatherServicer):
    def GetWeather(self, request, context):
        lat = request.latitude
        lon = request.longitude
        if lat == 0.0 and lon == 0.0:
            return weatherapp_pb2.WeatherResponse(error="Latitude/Longitude required")

        try:
            weather_source = "open-meteo"
            temperature_key = "temperature_2m"
            temperature_unit = "C"
            relative_humidity = "relative_humidity_2m"
            precipitation = "precipitation"
            apparent_temperature = "apparent_temperature"
            current_weather_key = "current"
            params = {
                "latitude": lat,
                "longitude": lon,
                current_weather_key: [temperature_key, relative_humidity, precipitation, apparent_temperature],
                "timezone": "auto"
            }
            resp = requests.get(OPEN_METEO_URL, params=params, timeout=7)
            j = resp.json()
            current = j.get(current_weather_key, {})
            info = weatherapp_pb2.WeatherInfo(
                temperature_c=float(current.get(temperature_key, 0.0)),
                unit=temperature_unit,
                source=weather_source,
                time_iso=current.get("time", ""),
                humidity=float(current.get(relative_humidity, 0.0)),
                precipitation=float(current.get(precipitation, 0.0)),
                apparent_temperature=float(current.get(apparent_temperature, 0.0))
            )
            return weatherapp_pb2.WeatherResponse(weather=info)
        except Exception as e:
            return weatherapp_pb2.WeatherResponse(error=f"Exception contacting open-meteo: {e}")

def serve():
    port = os.environ.get("WEATHER_SERVICE_PORT", "50052")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    weatherapp_pb2_grpc.add_WeatherServicer_to_server(WeatherServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"Weather service listening on {port}", flush=True)
    server.wait_for_termination()

if __name__ == "__main__":
    serve()