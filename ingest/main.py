import json
import time
import logging
from datetime import datetime
from kafka import KafkaProducer
from prometheus_client import start_http_server, Counter, Gauge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MESSAGES_SENT = Counter('crypto_messages_sent_total', 'Total messages sent to Kafka', ['symbol'])
CURRENT_PRICE = Gauge('crypto_price_current', 'Current cryptocurrency price', ['symbol'])
VOLUME_24H = Gauge('crypto_volume_24h', '24h trading volume', ['symbol'])
PRICE_CHANGE_PCT = Gauge('crypto_price_change_pct', 'Price change percentage 24h', ['symbol'])

class BinanceKafkaProducer:
    def __init__(self, kafka_servers, symbols, topic):
        self.symbols = symbols
        self.topic = topic
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3
        )
        logger.info(f"Producer connected to Kafka: {kafka_servers}")

    def build_ws_url(self):
        # Usar ticker (no miniTicker) para obtener price_change_percent
        streams = []
        for symbol in self.symbols:
            symbol_lower = symbol.lower()
            streams.append(f"{symbol_lower}@ticker")
        return f"wss://stream.binance.com:9443/ws/{'/'.join(streams)}"

    def send_to_kafka(self, message):
        try:
            future = self.producer.send(self.topic, value=message)
            record_metadata = future.get(timeout=10)
            MESSAGES_SENT.labels(symbol=message.get('s', 'UNKNOWN')).inc()
            logger.debug(f"Message sent to {record_metadata.topic} partition {record_metadata.partition}")
        except Exception as e:
            logger.error(f"Error sending message to Kafka: {e}")

    def process_message(self, data):
        if 'e' not in data:
            return
        
        event_type = data['e']
        
        if event_type == '24hrTicker':
            symbol = data.get('s', 'UNKNOWN')
            price = float(data.get('c', 0))
            volume = float(data.get('v', 0))
            change_pct = float(data.get('P', 0))

            CURRENT_PRICE.labels(symbol=symbol).set(price)
            VOLUME_24H.labels(symbol=symbol).set(volume)
            PRICE_CHANGE_PCT.labels(symbol=symbol).set(change_pct)

            message = {
                'type': 'ticker',
                'symbol': symbol,
                'price': price,
                'volume_24h': volume,
                'change_pct_24h': change_pct,
                'timestamp': data.get('E', 0)
            }
            self.send_to_kafka(message)
            
        elif event_type == 'kline':
            kline = data['k']
            symbol = data['s']
            message = {
                'type': 'kline',
                'symbol': symbol,
                'open_time': kline['t'],
                'open': float(kline['o']),
                'high': float(kline['h']),
                'low': float(kline['l']),
                'close': float(kline['c']),
                'volume': float(kline['v']),
                'close_time': kline['T'],
                'interval': kline['i']
            }
            self.send_to_kafka(message)

    def run(self):
        import websocket
        
        start_http_server(8000)
        logger.info("Prometheus metrics server started on port 8000")
        
        ws_url = self.build_ws_url()
        logger.info(f"Connecting to Binance WebSocket: {ws_url}")
        
        def on_message(ws, message):
            try:
                data = json.loads(message)
                if isinstance(data, dict):
                    self.process_message(data)
                elif isinstance(data, list):
                    for item in data:
                        self.process_message(item)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            logger.warning(f"WebSocket closed: {close_status_code} - {close_msg}")

        def on_open(ws):
            logger.info("WebSocket connection opened")

        while True:
            try:
                ws = websocket.WebSocketApp(
                    ws_url,
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close
                )
                ws.run_forever(ping_interval=30, ping_timeout=10)
            except Exception as e:
                logger.error(f"Connection error: {e}")
                logger.info("Reconnecting in 5 seconds...")
                time.sleep(5)

if __name__ == "__main__":
    import os
    
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092').split(',')
    symbols = os.getenv('SYMBOLS', 'BTCUSDT,ETHUSDT').split(',')
    topic = os.getenv('KAFKA_TOPIC', 'crypto-prices')
    
    producer = BinanceKafkaProducer(kafka_servers, symbols, topic)
    producer.run()
