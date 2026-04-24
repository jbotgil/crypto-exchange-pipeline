Claro, entiendo perfectamente lo que necesitas. He estructurado este `context.md` como una guía técnica de alta fidelidad, desglosando cada componente, requisito y decisión de diseño mencionada en el PDF para que puedas alimentar a Claude Code (o cualquier entorno de desarrollo) con instrucciones precisas.

---

# context.md: Proyecto Final CryptoExchange v1.0

## 1. Visión General del Proyecto
[cite_start]Construir un ecosistema **Big Data** completo para la ingesta, procesamiento y visualización de datos de criptomonedas en tiempo real, orquestado íntegramente mediante **Docker Compose**[cite: 16, 18, 22].

### Stack Tecnológico Obligatorio
* [cite_start]**Fuentes:** Binance WebSocket (RT) y opcionalmente CoinGecko (REST)[cite: 17, 49, 51].
* [cite_start]**Ingesta:** Apache Kafka (Bus de eventos)[cite: 18, 57].
* [cite_start]**Procesamiento:** Apache Spark Streaming (Structured Streaming)[cite: 18, 54, 151].
* [cite_start]**Almacenamiento:** HDFS (Formato Parquet)[cite: 18, 113].
* [cite_start]**Observabilidad:** Prometheus y Grafana[cite: 18, 198].

---

## 2. Arquitectura Detallada (Fase 1 - Obligatoria)

### 2.1. Fuentes de Datos (Binance)
* [cite_start]**Protocolo:** WebSocket (`wss://stream.binance.com:9443/ws/`)[cite: 82, 88].
* [cite_start]**Pares requeridos:** `BTC/USDT` (obligatorio) y un segundo par a elección (ej. `ETH/USDT`)[cite: 80, 81].
* **Streams a utilizar:**
    * [cite_start]`@miniTicker`: Precio actual, volumen 24h, % cambio (Frecuencia: ~1s)[cite: 83].
    * [cite_start]`@kline_1m`: Velas OHLCV de 1 minuto[cite: 83].
* [cite_start]**Restricción:** **NO** usar `@trade` ni `@depth` para evitar saturar el entorno local[cite: 85].

### 2.2. Ingesta (Apache Kafka)
* [cite_start]**Configuración:** Mínimo 1 broker en Docker[cite: 101].
* [cite_start]**Decisión de Diseño:** Debes definir si usas un topic general o uno por cada par/tipo de dato[cite: 98, 99].
* [cite_start]**Productor:** Script en Python que capture el WS de Binance y publique en Kafka[cite: 93, 97].

### 2.3. Procesamiento (Spark Streaming)
* [cite_start]**Lógica:** Suscripción al topic de Kafka mediante Structured Streaming[cite: 151].
* **Cálculos requeridos (mínimo 2):**
    * [cite_start]Media móvil (SMA/EMA)[cite: 157].
    * [cite_start]Variación porcentual[cite: 157].
    * [cite_start]*Opciones avanzadas:* RSI, Bandas de Bollinger o detección de Pump & Dump[cite: 157].
* [cite_start]**Ventanas Temporales:** Implementar ventanas con duración y deslizamiento (ej. últimos 5 min, actualizados cada 30s)[cite: 160, 161].

### 2.4. Almacenamiento (HDFS)
* [cite_start]**Formato:** Parquet (por eficiencia en compresión y lectura columnar)[cite: 113, 114].
* [cite_start]**Particionado:** Estructura recomendada por `par` y `fecha`[cite: 118, 123, 124].
    * [cite_start]`Ejemplo: /data/cripto/par=BTCUSDT/fecha=2026-04-15/`[cite: 119, 120, 123, 124].
* [cite_start]**Replicación:** Configurar factor de replicación 1 (dado que es un entorno Docker de un solo nodo)[cite: 140, 141].

### 2.5. Observabilidad (Prometheus & Grafana)
* **Infraestructura (Capa 1):**
    * [cite_start]`Node Exporter`: Métricas del host (CPU, RAM)[cite: 205].
    * [cite_start]`cAdvisor`: Recursos de los contenedores Docker[cite: 205].
* **Negocio (Capa 2):**
    * [cite_start]Mínimo 3 métricas propias (ej. `crypto_precio_actual`, `mensajes_procesados`, `kafka_lag`) usando `prometheus_client`[cite: 208, 209, 210, 222].
* [cite_start]**Dashboards:** Visualización en tiempo real en Grafana y al menos 1 alerta configurada en Prometheus[cite: 200, 230, 231].

---

## 3. Retos de Ampliación (Fase 2 - Opcional)

### 3.1. Enriquecimiento CoinGecko (REST)
* [cite_start]**Origen:** API REST pública (Polling cada 30-60s)[cite: 239, 240].
* [cite_start]**Datos:** Market cap, dominancia de BTC[cite: 239].
* [cite_start]**Objetivo:** Realizar un `join` (en Spark o Hive) para comparar precios locales vs. globales[cite: 248, 257].

### 3.2. Sentimiento (Fear & Greed Index)
* [cite_start]**Origen:** API de `alternative.me` (Polling cada hora/día)[cite: 262, 263].
* [cite_start]**Objetivo:** Cruzar el índice (0-100) con el volumen de trading en HDFS para validar si el miedo extremo afecta el volumen[cite: 262, 264].

---

## 4. Requisitos de Entrega y Calidad

### Estructura de Repositorio (GitHub)
* [cite_start]`docker-compose.yml` en la raíz[cite: 289].
* [cite_start]Carpetas: `/producer`, `/spark`, `/grafana`, etc.[cite: 289].
* [cite_start]`README.md` con instrucciones de levantamiento[cite: 289].
* [cite_start]`memoria.pdf` con justificación de cada decisión técnica[cite: 289].

### Factores Críticos de Evaluación
* [cite_start]**Estabilidad:** El pipeline debe funcionar en vivo sin caídas[cite: 271, 291].
* [cite_start]**Justificación:** No basta con "hacerlo", hay que explicar por qué se eligió cada parámetro (ventana de Spark, particionado de HDFS, topics de Kafka)[cite: 135, 177, 220].
* [cite_start]**Docker:** Absolutamente todo debe estar en contenedores; nada instalado directamente en el SO[cite: 23, 24].