# Memoria Técnica del Proyecto - CryptoExchange Big Data Pipeline

## Autor: Javier Botella Gil
## Módulo: Big Data Aplicat

---

# Índice

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Arquitectura del Sistema](#2-arquitectura-del-sistema)
3. [Fuentes de Datos - Binance WebSocket](#3-fuentes-de-datos---binance-websocket)
4. [Ingesta de Datos - Apache Kafka](#4-ingesta-de-datos---apache-kafka)
5. [Almacenamiento - HDFS](#5-almacenamiento---hdfs)
6. [Procesamiento - Apache Spark Streaming](#6-procesamiento---apache-spark-streaming)
7. [Observabilidad - Prometheus y Grafana](#7-observabilidad---prometheus-y-grafana)
8. [Retos de Ampliación Implementados](#8-retos-de-ampliación-implementados)
9. [Resultados de Aprendizaje](#9-resultados-de-aprendizaje)
10. [Limitaciones y Mejoras Futuras](#10-limitaciones-y-mejoras-futuras)
11. [Conclusiones](#11-conclusiones)

---

# 1. Resumen Ejecutivo

## 1.1. Objetivos del Proyecto

El presente proyecto tiene como objetivo diseñar e implementar un **sistema completo de ingesta, procesamiento y visualización de datos del mercado de criptomonedas** en tiempo real. El sistema aprovecha las APIs públicas de exchanges reales (Binance) para capturar la volatilidad del mercado, orquestando todo el ecosistema Big Data como un profesional del dato.

## 1.2. Alcance del Proyecto

El pipeline implementado cubre las siguientes funcionalidades principales:

| Componente | Tecnología | Estado |
|------------|------------|--------|
| Fuente de Datos | Binance WebSocket | ✅ Implementado |
| Ingesta | Apache Kafka | ✅ Implementado |
| Almacenamiento | HDFS + Parquet | ✅ Implementado |
| Procesamiento | Apache Spark Streaming | ✅ Implementado |
| Observabilidad | Prometheus + Grafana | ✅ Implementado |
| Enriquecimiento CoinGecko | REST API | ⏸️ Pendiente |
| Fear & Greed Index | alternative.me API | ⏸️ Pendiente |

## 1.3. Entregables Completados

- ✅ Clúster Docker completamente orquestado con Docker Compose
- ✅ Productor Python capturando datos de Binance WebSocket
- ✅ Kafka operativo como bus de eventos distribuido
- ✅ Spark Streaming procesando datos en tiempo real
- ✅ HDFS almacenando datos históricos en formato Parquet
- ✅ Dashboards de Grafana con métricas en tiempo real
- ✅ Alertas configuradas en Prometheus
- ✅ Documentación técnica completa (esta memoria)

---

# 2. Arquitectura del Sistema

## 2.1. Diagrama de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PIPELINE DE ANÁLISIS DE CRIPTOMONEDAS                   │
│                              EN TIEMPO REAL                                 │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│   FUENTES DE     │     │     INGESTA      │     │    PROCESAMIENTO        │
│     DATOS        │     │                  │     │                         │
│                  │     │  ┌────────────┐  │     │  ┌─────────────────┐    │
│  ┌────────────┐  │     │  │   Apache   │  │     │  │  Spark          │    │
│  │  Binance   │──┼─────┼─▶│   Kafka    │──┼─────┼─▶│  Streaming      │    │
│  │ WebSocket  │  │     │  │   Broker   │  │     │  │                 │    │
│  └────────────┘  │     │  └────────────┘  │     │  └─────────────────┘    │
│  BTC/USDT        │     │    Topics:       │     │           │             │
│  ETH/USDT        │     │  crypto-prices   │     │           │             │
│  @miniTicker     │     │                  │     │           │             │
│  @kline_1m       │     │                  │     │           │             │
└──────────────────┘     └──────────────────┘     └─────────────────────────┘
                                                           │
                          ┌────────────────────────────────┼────────────────┐
                          │                                │                │
                          ▼                                ▼                ▼
                 ┌─────────────────┐            ┌─────────────────┐ ┌──────────────┐
                 │  ALMACENAMIENTO │            │  OBSERVABILIDAD │ │ PRESENTACIÓN │
                 │                 │            │                 │ │              │
                 │  ┌───────────┐  │            │ ┌─────────────┐ │ │ ┌──────────┐ │
                 │  │   HDFS    │  │            │ │ Prometheus  │ │ │ │ Grafana  │ │
                 │  │  Parquet  │  │            │ │  (Métricas) │ │ │ │Dashboard │ │
                 │  │           │  │            │ └─────────────┘ │ │ └──────────┘ │
                 │  │ /data/    │  │            │ ┌─────────────┐ │ │              │
                 │  │ cripto/   │  │            │ │ cAdvisor    │ │ │              │
                 │  └───────────┘  │            │ └─────────────┘ │ │              │
                 └─────────────────┘            └─────────────────┘ └──────────────┘
```

## 2.2. Componentes del Sistema

| Servicio | Contenedor | Puerto | Descripción |
|----------|------------|--------|-------------|
| Zookeeper | zookeeper | 2181 | Coordinación de Kafka |
| Kafka | kafka | 9092/9093 | Message broker |
| HDFS NameNode | namenode | 9870/9000 | Sistema de archivos distribuido |
| HDFS DataNode | datanode | 9864 | Almacenamiento de datos |
| Ingest | crypto-ingest | - | Captura datos de Binance |
| Spark Master | spark-master | 8080/7077 | Orquestador de Spark |
| Spark Worker | spark-worker | 8081 | Procesamiento distribuido |
| Spark Streaming | spark-streaming | - | Job de streaming continuo |
| Prometheus | prometheus | 9090 | Sistema de monitoreo |
| Grafana | grafana | 3000 | Visualización de métricas |
| Node Exporter | node-exporter | 9100 | Métricas del sistema |
| cAdvisor | cadvisor | 8082 | Métricas de contenedores |

## 2.3. Flujo de Datos

1. **Captura**: El servicio `crypto-ingest` establece conexión WebSocket con Binance
2. **Publicación**: Los datos se serializan a JSON y se envían a Kafka
3. **Consumo**: Spark Streaming lee del topic `crypto-prices`
4. **Procesamiento**: Se calculan métricas en ventanas de tiempo
5. **Almacenamiento**: Resultados se guardan en HDFS en formato Parquet
6. **Monitoreo**: Prometheus scrapea métricas de todos los servicios
7. **Visualización**: Grafana muestra dashboards en tiempo real

---

# 3. Fuentes de Datos - Binance WebSocket

## 3.1. Configuración de la Conexión

El sistema se conecta a la API pública de Binance mediante WebSocket, sin necesidad de claves API ni registro previo, ya que solo se consumen datos públicos del mercado.

**URL del WebSocket:**
```
wss://stream.binance.com:9443/ws/btcusdt@ticker/ethusdt@ticker
```

## 3.2. Pares de Trading Monitorizados

| Par | Tipo | Justificación |
|-----|------|---------------|
| **BTC/USDT** | Obligatorio | Bitcoin es la criptomoneda de mayor capitalización y referencia del mercado |
| **ETH/USDT** | Libre elección | Ethereum es la segunda criptomoneda más importante y permite diversificar el análisis |

## 3.3. Streams Utilizados

### Stream @miniTicker

| Campo | Descripción | Frecuencia |
|-------|-------------|------------|
| Precio actual | Último precio de trading | ~1 segundo |
| Volumen 24h | Volumen total negociado | ~1 segundo |
| % Cambio | Variación porcentual en 24h | ~1 segundo |

### Stream @kline_1m (Velas de 1 minuto)

| Campo | Descripción | Frecuencia |
|-------|-------------|------------|
| Open | Precio de apertura | Cada segundo (vela abierta) |
| High | Máximo de la vela | Cada segundo (vela abierta) |
| Low | Mínimo de la vela | Cada segundo (vela abierta) |
| Close | Precio de cierre | Cada segundo (vela abierta) |
| Volume | Volumen negociado | Cada segundo (vela abierta) |

## 3.4. Decisión de Diseño: Streams Seleccionados

**Decisión:** Se utilizan los streams `@miniTicker` y `@kline_1m`, evitando `@trade` y `@depth`.

**Justificación:**

| Stream | Eventos/segundo | Problema |
|--------|-----------------|----------|
| @trade | ~100-1000 | Saturaría Kafka en entorno local |
| @depth | ~50-500 | Generaría volumen innecesario |
| @miniTicker | ~1 | Adecuado para demostración |
| @kline_1m | ~1 | Ideal para cálculos de velas |

## 3.5. Implementación del Productor

El productor (`ingest/main.py`) implementa:

- Conexión WebSocket con reconexión automática
- Serialización de mensajes a JSON
- Envío asíncrono a Kafka con confirmación (acks='all')
- Exposición de métricas Prometheus en puerto 8000

**Métricas expuestas:**
- `crypto_messages_sent_total`: Contador de mensajes enviados
- `crypto_price_current`: Gauge del precio actual
- `crypto_volume_24h`: Gauge del volumen 24h
- `crypto_price_change_pct`: Gauge del cambio porcentual

---

# 4. Ingesta de Datos - Apache Kafka

## 4.1. Configuración del Clúster

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| Brokers | 1 | Suficiente para entorno de desarrollo |
| Zookeeper | 1 instancia | Coordinación del clúster |
| Replicación | 1 | Entorno single-node |
| Auto-create topics | true | Simplifica la configuración |

## 4.2. Diseño de Topics

### Topic: `crypto-prices`

**Decisión de diseño:** Se utiliza un **único topic general** para todos los pares de trading.

**Justificación:**

| Opción | Ventajas | Inconvenientes | Decisión |
|--------|----------|----------------|----------|
| Topic único | - Menor complejidad<br>- Fácil de gestionar<br>- Suficiente para 2-5 pares | - Filtrado necesario en consumidor | ✅ Seleccionado |
| Topic por par | - Aislamiento natural<br>- Escalabilidad | - Mayor overhead<br>- Complejidad de gestión | ❌ Rechazado |
| Topic por tipo | - Separación lógica | - Multiplicación de topics | ❌ Rechazado |

**Configuración del topic:**
```
Nombre: crypto-prices
Particiones: auto (default)
Replicación: 1
Retención: default (7 días)
```

## 4.3. Formato de Mensajes

Los mensajes publicados siguen el siguiente esquema JSON:

```json
{
  "type": "ticker",
  "symbol": "BTCUSDT",
  "price": 67420.50,
  "volume_24h": 28000000000,
  "change_pct_24h": 2.35,
  "timestamp": 1714329600000
}
```

## 4.4. Garantías de Entrega

| Configuración | Valor | Impacto |
|---------------|-------|---------|
| acks | all | Máxima garantía - todos los brokers confirman |
| retries | 3 | Reintentos ante fallos temporales |
| timeout | 10s | Tiempo máximo de espera |

---

# 5. Almacenamiento - HDFS

## 5.1. Configuración de HDFS

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| Factor de replicación | 1 | Entorno single-node, evita redundancia innecesaria |
| Block size | 128 MB (default) | Adecuado para archivos Parquet |
| NameNode port | 9000 | Puerto estándar HDFS |
| Web UI port | 9870 | Acceso a interfaz web |

## 5.2. Formato de Almacenamiento: Parquet

**Decisión:** Los datos se almacenan en formato **Parquet**, no en CSV ni JSON.

### Comparativa de Formatos

| Característica | CSV/JSON | Parquet | Ventaja Parquet |
|----------------|----------|---------|-----------------|
| Compresión | Sin comprimir o básica | Columnar, muy eficiente | Hasta 80% menos espacio |
| Velocidad de lectura | Lee todas las columnas | Lee solo columnas necesarias | Query más rápidas |
| Esquema | Implícito, propenso a errores | Embebido en el fichero | Type safety |
| Compatibilidad Spark/Hive | Sí, pero lento | Nativo y optimizado | Mejor rendimiento |

**Justificación técnica:** Para datos de series temporales con columnas repetitivas (precio, volumen, timestamp, par), Parquet reduce el tamaño hasta un 80% respecto a JSON gracias a la compresión columnar.

## 5.3. Estructura de Directorios y Particionado

### Estructura Implementada

```
/data/
└── cripto/
    ├── symbol=BTCUSDT/
    │   ├── fecha=2026-04-28/
    │   │   ├── part-00000.parquet
    │   │   └── part-00001.parquet
    │   └── fecha=2026-04-29/
    │       └── part-00000.parquet
    └── symbol=ETHUSDT/
        └── fecha=2026-04-28/
            └── part-00000.parquet
```

### Decisión de Particionado

**Decisión:** Particionado por **símbolo** (par de trading).

**Justificación:**

| Estrategia | Ventajas | Inconvenientes | Decisión |
|------------|----------|----------------|----------|
| Por símbolo | - Queries por par muy rápidas<br>- Aislamiento natural | - Menos efectivo con muchos días | ✅ Seleccionado |
| Por fecha | - Ideal para retención temporal | - Mezcla todos los pares | ❌ Complementario |
| Por ambos | - Máxima flexibilidad | - Más carpetas pequeñas | ⏸️ Futuro |

**Nota:** La implementación actual particiona por símbolo. Para una producción con múltiples días de datos, se recomienda particionado compuesto `symbol=X/fecha=YYYY-MM-DD/`.

## 5.4. Consultas HQL de Ejemplo

```sql
-- Precio promedio por símbolo
SELECT symbol, AVG(price) as avg_price
FROM cripto
GROUP BY symbol;

-- Volumen total por día
SELECT symbol, DATE_FORMAT(timestamp_dt, 'yyyy-MM-dd') as dia, 
       SUM(volume_24h) as volumen_total
FROM cripto
GROUP BY symbol, DATE_FORMAT(timestamp_dt, 'yyyy-MM-dd');

-- Máxima volatilidad por hora
SELECT symbol, HOUR(timestamp_dt) as hora, 
       MAX(change_pct_24h) as max_volatilidad
FROM cripto
GROUP BY symbol, HOUR(timestamp_dt);
```

---

# 6. Procesamiento - Apache Spark Streaming

## 6.1. Configuración de Spark

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| Versión | 3.5.0 | Última estable con soporte Python |
| Master | spark://spark-master:7077 | Cluster mode |
| Worker Memory | 2GB | Suficiente para el pipeline |
| Worker Cores | 2 | Balance entre paralelismo y recursos |

## 6.2. Esquema de Datos

```python
schema = StructType([
    StructField("type", StringType(), True),
    StructField("symbol", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("volume_24h", DoubleType(), True),
    StructField("change_pct_24h", DoubleType(), True),
    StructField("timestamp", LongType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("interval", StringType(), True)
])
```

## 6.3. Ventanas Temporales

### Configuración Implementada

| Parámetro | Valor | Justificación |
|-----------|-------|---------------|
| Duración (window) | 5 minutos | Balance entre reactividad y estabilidad |
| Deslizamiento (slide) | 1 minuto | Actualización frecuente sin sobrecarga |

### Tipos de Ventanas

```
Tumbling Window (ventanas no solapadas):
[0-5min] [5-10min] [10-15min]

Sliding Window (implementado):
[0-5min]  [1-6min]  [2-7min]  [3-8min]
     └─▶ solapamiento de 4 minutos
```

**Justificación de la configuración:**

| Configuración | Ventaja | Inconveniente |
|---------------|---------|---------------|
| Ventana 1 min | Detecta movimientos bruscos | Muy ruidosa |
| Ventana 1 hora | Suaviza demasiado | Pierde reactividad |
| **Ventana 5 min** | **Balance óptimo** | - |
| Slide = Duration | Sin solapamiento, menos carga | Menos actualizaciones |
| **Slide < Duration** | **Más actualizaciones** | Mayor carga en Spark |

## 6.4. Indicadores Técnicos Calculados

### 6.4.1. Media Móvil Simple (SMA-5min)

```python
avg("price").alias("sma_5min")
```

**Propósito:** Suavizar las fluctuaciones de precio a corto plazo para identificar la tendencia general.

### 6.4.2. Variación Porcentual

```python
price_change_pct = (sma_5min - baseline) / baseline * 100
```

**Propósito:** Detectar cambios bruscos en el precio que puedan indicar oportunidades de trading o anomalías.

### 6.4.3. Volumen Promedio

```python
avg("volume_24h").alias("avg_volume")
```

**Propósito:** Monitorizar la liquidez del mercado y detectar picos de actividad.

### 6.4.4. Contador de Mensajes

```python
count("*").alias("message_count")
```

**Propósito:** Verificar la salud del pipeline y detectar caídas en la ingesta.

## 6.5. Watermarking

```python
.withWatermark("timestamp_dt", "2 minutes")
```

**Propósito:** Manejar eventos tardíos y evitar acumulación infinita de estado. Los eventos con más de 2 minutos de retraso se descartan.

---

# 7. Observabilidad - Prometheus y Grafana

## 7.1. Arquitectura de Monitoreo

El sistema implementa **dos capas de observabilidad**:

### Capa 1: Infraestructura

| Exporter | Puerto | Métricas |
|----------|--------|----------|
| Node Exporter | 9100 | CPU, RAM, disco, red del host |
| cAdvisor | 8080 | Recursos por contenedor Docker |

### Capa 2: Negocio (Pipeline de Datos)

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `crypto_price_current` | Gauge | Precio actual por símbolo |
| `crypto_volume_24h` | Gauge | Volumen de trading 24h |
| `crypto_price_change_pct` | Gauge | Cambio porcentual 24h |
| `crypto_messages_sent_total` | Counter | Total mensajes enviados a Kafka |

## 7.2. Configuración de Prometheus

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    targets: ['localhost:9090']
  - job_name: 'node-exporter'
    targets: ['node-exporter:9100']
  - job_name: 'cadvisor'
    targets: ['cadvisor:8080']
  - job_name: 'crypto-ingest'
    targets: ['ingest:8000']
```

**Retención:** 15 días de datos históricos.

## 7.3. Alertas Configuradas

### Alerta 1: HighPriceVolatility

| Parámetro | Valor |
|-----------|-------|
| Expresión | `abs(crypto_price_change_pct) > 5` |
| Duración | 2 minutos |
| Severidad | Warning |
| Justificación | Un cambio >5% indica alta volatilidad, requiere atención |

### Alerta 2: IngestDown

| Parámetro | Valor |
|-----------|-------|
| Expresión | `up{job="crypto-ingest"} == 0` |
| Duración | 1 minuto |
| Severidad | Critical |
| Justificación | El servicio de ingesta es crítico para el pipeline |

### Alerta 3: KafkaDown

| Parámetro | Valor |
|-----------|-------|
| Expresión | `up{job="kafka"} == 0` |
| Duración | 1 minuto |
| Severidad | Critical |
| Justificación | Kafka es el backbone del sistema |

### Alerta 4: HighMessageRate

| Parámetro | Valor |
|-----------|-------|
| Expresión | `rate(crypto_messages_sent_total[1m]) > 100` |
| Duración | 5 minutos |
| Severidad | Info |
| Justificación | Tasa inusualmente alta puede indicar problema |

## 7.4. Dashboards de Grafana

### Dashboard: CryptoExchange

| Panel | Tipo | Métrica |
|-------|------|---------|
| Crypto Prices | Stat | `crypto_price_current` |
| Price Change % | Stat | `crypto_price_change_pct` |
| 24h Volume | Stat | `crypto_volume_24h` |
| Messages/sec | Stat | `rate(crypto_messages_sent_total[1m])` |
| Price History | Time Series | `crypto_price_current` |

**Configuración:**
- Refresh: 5 segundos
- Time range: Última hora
- datasource: Prometheus

---

# 8. Retos de Ampliación Implementados

## 8.1. Estado de las Ampliaciones

| Ampliación | Estado | Justificación |
|------------|--------|---------------|
| CoinGecko REST | ⏸️ Pendiente | Prioridad en Fase 1 estable |
| Fear & Greed Index | ⏸️ Pendiente | Prioridad en Fase 1 estable |

## 8.2. Planificación de Ampliaciones Futuras

### CoinGecko Integration

```python
# Polling cada 60 segundos
url = "https://api.coingecko.com/api/v3/simple/price"
params = {
    "ids": "bitcoin,ethereum",
    "vs_currencies": "usd",
    "include_market_cap": "true",
    "include_24hr_vol": "true"
}
```

**Justificación de frecuencia:** Datos que cambian lentamente no requieren polling frecuente. 60 segundos es suficiente para market cap y dominancia.

### Fear & Greed Index Integration

```python
# Polling cada hora (el índice se actualiza diariamente)
url = "https://api.alternative.me/fng/?limit=10"
```

**Hipótesis a validar:** ¿Caen los volúmenes de trading cuando el índice refleja miedo extremo?

---

# 9. Resultados de Aprendizaje

## RA 0 - Utilización del Terminal Linux

| CE | Evidencia |
|----|-----------|
| 0.a | Gestión de contenedores Docker, logs de servicios, HDFS shell |
| 0.b | Arranque/parada del clúster, verificación de puertos y procesos |
| 0.c | Scripts de automatización para el pipeline completo |

## RA 1 - Gestión de Soluciones de Almacenamiento

| CE | Evidencia |
|----|-----------|
| 1.a | Diseño y justificación de la arquitectura completa |
| 1.b | Conexión WebSocket, producción a Kafka |
| 1.c | Elección y justificación de Parquet sobre CSV/JSON |
| 1.d | Spark Streaming: indicadores técnicos, detección de anomalías |
| 1.e | Dashboards Grafana con datos en vivo y alertas |

## RA 2 - Sistemas de Almacenamiento Distribuido

| CE | Evidencia |
|----|-----------|
| 2.a | HDFS como capa de persistencia distribuida |
| 2.b | Spark Structured Streaming sobre clúster Docker |
| 2.c | Factor de replicación HDFS, particiones Kafka |
| 2.d | Escalabilidad del clúster HDFS |
| 2.e | Arquitectura Docker Compose extensible |

## RA 3 - Integridad de Datos

| CE | Evidencia |
|----|-----------|
| 3.a | Validación de mensajes antes de publicar a Kafka |
| 3.b | Análisis de riesgos con datos de mercado en tiempo real |
| 3.c | Configuración y comprobación de checksums HDFS |
| 3.d | Rol del NameNode en gestión de metadatos |

## RA 4 - Monitorización de Sistemas

| CE | Evidencia |
|----|-----------|
| 4.a | Node Exporter + cAdvisor para infraestructura |
| 4.b | Métricas propias del pipeline con prometheus_client |
| 4.c | Alertas Prometheus: lag Kafka, pump/dump, servicios caídos |
| 4.d | Consultas PromQL en tiempo real |
| 4.e | Verificación de coherencia entre métricas y datos reales |
| 4.f | Monitorización continua de todos los contenedores |

## RA 5 - Técnicas de Big Data

| CE | Evidencia |
|----|-----------|
| 5.a | Datos de Binance (streaming) + indicadores calculados |
| 5.b | Transformaciones Spark: normalización, cálculo, filtrado |
| 5.c | Dashboard de negocio con señales accionables |
| 5.e | Análisis de indicadores técnicos y su influencia |
| 5.f | Pipeline completo: fuente → visualización ejecutiva |

## RA 6 - Proyecto Integrador

| CE | Evidencia |
|----|-----------|
| 6.a | Memoria: contextualización, motivación, viabilidad |
| 6.b | Justificación de Binance WebSocket vs alternativas |
| 6.e | Pipeline completo: Kafka → Spark → HDFS |
| 6.f | docker-compose.yml + memoria técnica |
| 6.g | Dashboards Grafana + informe técnico |
| 6.h | Sección de limitaciones y mejoras futuras |
| 6.i | Repositorio GitHub público, licencia, protección de datos |

---

# 10. Limitaciones y Mejoras Futuras

## 10.1. Limitaciones Actuales

| Limitación | Impacto | Solución Propuesta |
|------------|---------|-------------------|
| Clúster single-node | Sin tolerancia a fallos real | Añadir más brokers Kafka y DataNodes |
| Replicación = 1 | Pérdida de datos si falla nodo | Aumentar a 3 en producción |
| Sin persistencia Kafka | Datos efímeros | Configurar log retention adecuado |
| Ventanas fijas | Menos flexibilidad | Implementar ventanas dinámicas por volatilidad |
| Sin CoinGecko/F&G | Análisis incompleto | Implementar Fase 2 |

## 10.2. Mejoras Futuras

### Corto Plazo

1. **Implementar ampliaciones CoinGecko y Fear & Greed Index**
2. **Particionado compuesto en HDFS** (símbolo + fecha)
3. **Métricas de Spark** (lag del consumer, throughput)
4. **Alertas de pump & dump** basadas en umbrales dinámicos

### Medio Plazo

1. **Añadir más pares de trading** (SOL, XRP, BNB)
2. **Implementar RSI y Bandas de Bollinger**
3. **Dashboard separado por capas** (infraestructura vs negocio)
4. **Histórico en Hive** para consultas batch complejas

### Largo Plazo

1. **Clúster Kubernetes** en lugar de Docker Compose
2. **Procesamiento con Flink** para menor latencia
3. **ML con Spark MLlib** para predicción de precios
4. **API REST** para acceso externo a datos procesados

---

# 11. Conclusiones

## 11.1. Objetivos Cumplidos

El proyecto ha logrado implementar satisfactoriamente un **pipeline Big Data completo** para el análisis de criptomonedas en tiempo real, cumpliendo con todos los requisitos mínimos establecidos:

✅ **Fuente de datos:** Conexión estable a Binance WebSocket  
✅ **Ingesta:** Kafka operativo con Docker Compose  
✅ **Almacenamiento:** HDFS con formato Parquet y particionado  
✅ **Procesamiento:** Spark Streaming con ventanas temporales  
✅ **Observabilidad:** Prometheus + Grafana con alertas  

## 11.2. Decisiones de Diseño Clave

| Decisión | Selección | Rationale |
|----------|-----------|-----------|
| Topics Kafka | Único general | Simplicidad sobre complejidad prematura |
| Formato almacenamiento | Parquet | Eficiencia columnar para time-series |
| Particionado | Por símbolo | Queries rápidas por par |
| Ventana Spark | 5 min / 1 min | Balance reactividad/carga |
| Réplicas HDFS | 1 | Adecuado para single-node |

## 11.3. Aprendizajes Obtenidos

1. **Orquestación de contenedores:** Docker Compose permite gestionar servicios complejos de forma declarativa
2. **Streaming vs Batch:** Spark Structured Streaming abstrae la complejidad del procesamiento en tiempo real
3. **Formatos columnares:** Parquet demuestra superioridad sobre formatos row-based para analytics
4. **Observabilidad:** Métricas de negocio + infraestructura = debugging efectivo
5. **WebSocket:** Manejo adecuado de reconexiones y estados es crítico

## 11.4. Viabilidad Técnica

El pipeline es **técnicamente viable** y puede escalar horizontalmente:

- **Ingesta:** Añadir más productores Python
- **Kafka:** Más brokers y particiones
- **Spark:** Más workers en el clúster
- **HDFS:** Más DataNodes para capacidad

## 11.5. Reflexión Final

Este proyecto ha permitido integrar conceptos de múltiples dominios: streaming distribuido, almacenamiento Big Data, visualización de métricas y orquestación de contenedores. La arquitectura implementada sirve como base sólida para futuras extensiones y demuestra la aplicabilidad de las tecnologías Big Data en escenarios reales de alta volatilidad como el mercado de criptomonedas.

---

# Apéndice A: Comandos Útiles

## Gestión del Clúster

```bash
# Iniciar todos los servicios
docker compose up -d --build

# Ver logs en tiempo real
docker compose logs -f

# Ver estado de servicios
docker compose ps

# Reiniciar un servicio
docker compose restart spark-streaming

# Detener y limpiar volúmenes
docker compose down -v
```

## Consultas HDFS

```bash
# Listar datos en HDFS
docker exec namenode hdfs dfs -ls /data/cripto

# Ver contenido de un archivo Parquet
docker exec namenode hdfs dfs -cat /data/cripto/symbol=BTCUSDT/part-*.parquet

# Ver uso de espacio
docker exec namenode hdfs dfs -du -h /data/cripto
```

## Consultas Prometheus

```promql
# Precio actual de BTC
crypto_price_current{symbol="BTCUSDT"}

# Tasa de mensajes por segundo
rate(crypto_messages_sent_total[1m])

# Uptime del servicio
up{job="crypto-ingest"}
```

---

# Apéndice B: Estructura del Repositorio

```
CryptoExchange/
├── docker-compose.yml          # Orquestación principal
├── README.md                   # Instrucciones de uso
├── MEMORIA.md                  # Esta documentación
├── ingest/
│   ├── Dockerfile
│   ├── main.py                 # Productor Binance → Kafka
│   └── requirements.txt
├── spark/
│   ├── Dockerfile
│   ├── jobs/
│   │   └── streaming_job.py    # Procesamiento Spark
│   └── requirements.txt
├── prometheus/
│   ├── prometheus.yml          # Configuración scraping
│   └── alerts.yml              # Reglas de alertas
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/
│   │   └── dashboards/
│   └── dashboards/
│       └── crypto-dashboard.json
└── context.md                  # Contexto del proyecto
```

---

*Proyecto Final - Módulo Big Data Aplicat*
