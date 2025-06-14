import json
import time
from typing import Dict, Any
from src.utils.kafka_client import KafkaClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleProducer:
    def __init__(self, config_path: str = "config/kafka_config.yaml"):
        """
        Инициализация простого продюсера
        
        Args:
            config_path: путь к файлу конфигурации
        """
        self.kafka_client = KafkaClient(config_path)
        self.producer = self.kafka_client.create_producer()
        
    def send_message(self, topic: str, message: Dict[str, Any]) -> None:
        """
        Отправка сообщения в топик
        
        Args:
            topic: имя топика
            message: сообщение для отправки
        """
        try:
            # Сериализация сообщения в JSON
            message_bytes = json.dumps(message).encode('utf-8')
            
            # Отправка сообщения
            self.producer.send(topic, message_bytes)
            self.producer.flush()
            
            logger.info(f"Сообщение успешно отправлено в топик {topic}")
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            raise
            
    def close(self) -> None:
        """Закрытие соединений"""
        try:
            self.producer.close()
            self.kafka_client.close()
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединений: {e}")
            raise

if __name__ == "__main__":
    # Пример использования
    producer = SimpleProducer()
    
    try:
        # Отправка тестового сообщения
        message = {
            "id": 1,
            "timestamp": time.time(),
            "data": "Test message"
        }
        producer.send_message("topic-1", message)
    finally:
        producer.close() 