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
Se expondrán:
- Gateway HTTP: http://localhost:8080
- gRPC IpLocator: localhost:50051
- gRPC Weather: localhost:50052

## Probar
- **Salud:** `curl http://localhost:8080/health`
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

## Notas de diseño
- **gRPC proto único** compartido por los 3 servicios.
- Los servicios Python generan stubs en tiempo de build con `grpcio-tools`.
- El gateway exporta sólo **HTTP**, cumpliendo con el enunciado.
- Manejo básico de errores y timeouts.
- Se envía `x-forwarded-for` como metadata al IpLocator (opcional).

## Extensiones sugeridas (opcionales)
- Cache de respuestas (Redis) en el gateway.
- Métricas/Tracing (Prometheus + OpenTelemetry).
- Tests unitarios para cada servicio.
- Agregar endpoint `/weather/by-location?lat=&lon=` directo (evita IP).
- Agregar más variables meteorológicas desde Open‑Meteo.
```