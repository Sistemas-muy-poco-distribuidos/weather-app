FROM python:3.11-slim

WORKDIR /app
COPY protos /app/protos
RUN touch /app/protos/__init__.py

COPY weather_service/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN python -m grpc_tools.protoc -I/app/protos \
    --python_out=/app/protos \
    --grpc_python_out=/app/protos \
    /app/protos/weatherapp.proto

COPY weather_service/server.py /app/server.py

ENV PYTHONPATH=/app/protos

EXPOSE 50052
CMD ["python", "server.py"]