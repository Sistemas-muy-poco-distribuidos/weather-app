# TP 1 – Weather App (gRPC + Docker Compose)

Este repo cumple con los requisitos:
- **IpLocator** en **Python** (gRPC) usando `ipwho.is` para convertir IP -> ubicación.
- **Weather** en **Python** (gRPC) usando `open-meteo` para obtener temperatura actual.
- **Gateway** en **Node.js** expone **API HTTP** y coordina llamadas a ambos servicios por **gRPC**.
- Orquestado con **Docker Compose**.

## Estructura
```text
protos/weatherapp.proto
ip_service/ (Python gRPC)
weather_service/ (Python gRPC)
gateway/ (Node.js HTTP + gRPC clients)
docker-compose.yml
```

## Requisitos previos
- Docker y Docker Compose
- Conexión a Internet (para que los servicios consulten `ipwho.is` y `open-meteo`).

## Cómo correr
```bash
docker compose up --build
```
## Probar
- **Con IP explícita:** `curl "http://localhost:8080/weather?ip=1.1.1.1"`
- **Sin IP:** `curl "http://localhost:8080/weather"` (usa la IP del cliente vista por el gateway; en local puede devolver una IP privada o 127.0.0.1, por lo que es preferible pasar `?ip=`).

### Respuesta ejemplo
```json
{
  "ip": "1.1.1.1",
  "city": "Los Angeles",
  "region": "California",
  "country": "United States",
  "latitude": -33.494,
  "longitude": 143.2104,
  "weather": {
    "temperature_c": 18.4,
    "unit": "C",
    "source": "open-meteo",
    "time_iso": "2025-09-09T12:00"
  }
}
```
