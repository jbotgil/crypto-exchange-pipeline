# CryptoExchange - Real-Time Cryptocurrency Data Pipeline

Sistema de procesamiento de datos de criptomonedas en tiempo real que captura información desde Binance, la procesa mediante Apache Spark, y la visualiza en Grafana.

## 🏗️ Arquitectura

```
┌─────────────┐     ┌─────────┐     ┌─────────────────┐     ┌──────────
│   Binance   │────▶│  Kafka  │────▶│  Spark Streaming│────▶│   HDFS   │
│ WebSocket   │     │         │     │                 │     │          │
└─────────────┘     └─────────     └─────────────────     └──────────┘
                         │
                         ▼
                   ┌─────────────┐     ┌─────────────┐     ┌──────────┐
                   │  Prometheus │◀────│   Ingest    │     │ Grafana  │
                   │  (Métricas) │     │ (Métricas)  │     │(Dashboard)│
                   └─────────────┘     └─────────────┘     └──────────┘
```

## 📋 Componentes

| Servicio | Descripción |
|----------|-------------|
| **Ingest** | Captura datos de Binance WebSocket (BTC, ETH) |
| **Kafka** | Message broker para streaming de datos |
| **Spark Streaming** | Procesa y agrega datos en ventanas de tiempo |
| **HDFS** | Almacenamiento distribuido de datos históricos |
| **Prometheus** | Monitoreo y métricas del sistema |
| **Grafana** | Dashboard de visualización en tiempo real |
| **Node Exporter** | Métricas del sistema |
| **cAdvisor** | Métricas de contenedores |

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose
- 4GB RAM mínimo recomendado
- Puertos disponibles: 2181, 9092, 9090, 3000, 8080, 9870

### Ejecutar

```bash
# Iniciar todos los servicios
docker compose up -d --build

# Ver logs
docker compose logs -f

# Ver estado de servicios
docker compose ps
```

### Acceder a los servicios

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| Grafana | http://localhost:3000 | admin / admin123 |
| Prometheus | http://localhost:9090 | - |
| Spark Master UI | http://localhost:8080 | - |
| HDFS NameNode | http://localhost:9870 | - |
| cAdvisor | http://localhost:8082 | - |

## 📊 Dashboard

El dashboard de Grafana incluye:

- **Crypto Prices**: Precio actual de BTC y ETH en USD
- **Price Change %**: Variación porcentual en 24h
- **24h Volume**: Volumen de trading en 24 horas
- **Messages/sec**: Tasa de mensajes procesados por segundo
- **Price History**: Gráfico temporal del precio

## 🛠️ Configuración

### Cambiar criptomonedas

Editar `docker-compose.yml`:

```yaml
environment:
  SYMBOLS: BTCUSDT,ETHUSDT,SOLUSDT  # Agregar más símbolos
```

### Modificar intervalo de Spark

Editar `spark/jobs/streaming_job.py`:

```python
windowed_df = parsed_df.groupBy(
    window(col("timestamp_dt"), "5 minutes", "1 minute"),  # Ventana de 5 min, slide de 1 min
    col("symbol")
)
```

## 📁 Estructura del Proyecto

```
CryptoExchange/
├── docker-compose.yml          # Orquestación de contenedores
├── ingest/
│   ├── Dockerfile
│   ├── main.py                 # Captura datos de Binance
│   └── requirements.txt
├── spark/
│   ├── Dockerfile
│   ├── jobs/
│   │   └── streaming_job.py    # Procesamiento Spark
│   └── requirements.txt
├── prometheus/
│   ├── prometheus.yml          # Configuración de scraping
│   └── alerts.yml              # Reglas de alertas
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/        # Configuración de datasource
│   │   └── dashboards/         # Auto-provisioning
│   └── dashboards/
│       └── crypto-dashboard.json
└── README.md
```

## 🔍 Métricas Disponibles

| Métrica | Descripción |
|---------|-------------|
| `crypto_price_current` | Precio actual por símbolo |
| `crypto_price_change_pct` | Cambio porcentual 24h |
| `crypto_volume_24h` | Volumen de trading 24h |
| `crypto_messages_sent_total` | Total de mensajes a Kafka |

## 🚨 Alertas Configuradas

| Alerta | Condición | Severidad |
|--------|-----------|-----------|
| HighPriceVolatility | \|change_pct\| > 5% | Warning |
| IngestDown | Servicio caído > 1min | Critical |
| KafkaDown | Broker caído > 1min | Critical |
| HighMessageRate | > 100 msg/s por 5min | Info |

## 🧪 Comandos Útiles

```bash
# Ver logs de un servicio específico
docker compose logs -f ingest
docker compose logs -f spark-streaming

# Reiniciar un servicio
docker compose restart prometheus

# Detener todo
docker compose down

# Detener y limpiar volúmenes
docker compose down -v

# Ver datos en HDFS
docker exec namenode hdfs dfs -ls /data/cripto
```

## 📝 Notas

- Los datos se almacenan en HDFS particionados por símbolo: `/data/cripto/symbol=BTCUSDT/`
- El checkpoint de Spark está en `/tmp/spark_checkpoint`
- Prometheus retiene datos por 15 días

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit (`git commit -m 'Añadir nueva funcionalidad'`)
4. Push (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Proyecto educativo para Big Data y procesamiento de streaming.

## 📧 Contacto

Para preguntas o issues, abrir un ticket en GitHub.
