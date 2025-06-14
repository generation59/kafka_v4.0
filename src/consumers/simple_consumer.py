import json
from typing import Dict, Any, Callable
from src.utils.kafka_client import KafkaClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleConsumer:
    def __init__(self, topic: str, group_id: str, config_path: str = "config/kafka_config.yaml"):
        """
        Инициализация простого консьюмера
        
        Args:
            topic: имя топика
            group_id: ID группы консьюмеров
            config_path: путь к файлу конфигурации
        """
        self.kafka_client = KafkaClient(config_path)
        self.consumer = self.kafka_client.create_consumer(topic, group_id)
        
    def consume_messages(self, message_handler: Callable[[Dict[str, Any]], None]) -> None:
        """
        Получение и обработка сообщений
        
        Args:
            message_handler: функция-обработчик сообщений
        """
        try:
            logger.info(f"Начало получения сообщений...")
            
            for message in self.consumer:
                try:
                    # Десериализация сообщения из JSON
                    message_data = json.loads(message.value.decode('utf-8'))
                    
                    # Обработка сообщения
                    message_handler(message_data)
                    
                    logger.info(f"Сообщение успешно обработано: {message_data}")
                except json.JSONDecodeError as e:
                    logger.error(f"Ошибка при десериализации сообщения: {e}")
                except Exception as e:
                    logger.error(f"Ошибка при обработке сообщения: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка при получении сообщений: {e}")
            raise
            
    def close(self) -> None:
        """Закрытие соединений"""
        try:
            self.consumer.close()
            self.kafka_client.close()
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединений: {e}")
            raise

if __name__ == "__main__":
    # Пример использования
    def handle_message(message: Dict[str, Any]) -> None:
        """Пример обработчика сообщений"""
        print(f"Получено сообщение: {message}")
    
    consumer = SimpleConsumer("topic-1", "test-group")
    
    try:
        consumer.consume_messages(handle_message)
    except KeyboardInterrupt:
        logger.info("Получение сообщений прервано пользователем")
    finally:
        consumer.close() 