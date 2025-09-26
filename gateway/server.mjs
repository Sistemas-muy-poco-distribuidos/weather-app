import express from "express";
import cors from "cors";
import * as grpc from "@grpc/grpc-js";
import * as protoLoader from "@grpc/proto-loader";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PROTO_PATH = path.resolve(__dirname, "./protos/weatherapp.proto");

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});
const weatherapp = grpc.loadPackageDefinition(packageDefinition).weatherapp;

// gRPC clients (point to docker-compose service names)
const IP_LOCATOR_ADDR = process.env.IP_LOCATOR_ADDR || "ip-service:50051";
const WEATHER_ADDR = process.env.WEATHER_ADDR || "weather-service:50052";

const ipClient = new weatherapp.IpLocator(IP_LOCATOR_ADDR, grpc.credentials.createInsecure());
const weatherClient = new weatherapp.Weather(WEATHER_ADDR, grpc.credentials.createInsecure());

const app = express();
app.use(cors());

function getClientIp(req) {
  const xf = req.header("x-forwarded-for");
  if (xf) return xf.split(",")[0].trim();
  const ip = req.socket.remoteAddress || "";
  return ip.replace("::ffff:", "");
}

app.get("/weather", (req, res) => {
  const ip = (req.query.ip || "").toString().trim();
  const meta = new grpc.Metadata();
  meta.set("x-forwarded-for", getClientIp(req));

  ipClient.GetLocation({ ip }, meta, (err, locResp) => {
    if (err) return res.status(502).json({ error: "gRPC IpLocator error", detail: err.message });
    if (locResp.error) return res.status(400).json({ error: locResp.error });

    const loc = locResp.location || {};
    weatherClient.GetWeather({ latitude: loc.latitude, longitude: loc.longitude }, (werr, wresp) => {
      if (werr) return res.status(502).json({ error: "gRPC Weather error", detail: werr.message });
      if (wresp.error) return res.status(400).json({ error: wresp.error });
      return res.json({
        ip: loc.ip,
        city: loc.city,
        region: loc.region,
        country: loc.country,
        latitude: loc.latitude,
        longitude: loc.longitude,
        weather: wresp.weather
      });
    });
  });
});

const PORT = process.env.PORT || 8080;
app.listen(PORT, () => {
  console.log(`Gateway listening on ${PORT}`);
});