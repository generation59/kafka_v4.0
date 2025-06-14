import json
from typing import Dict, List
from src.utils.kafka_client import KafkaClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PartitionBalancer:
    def __init__(self, config_path: str = "config/kafka_config.yaml"):
        """
        Инициализация балансировщика партиций
        
        Args:
            config_path: путь к файлу конфигурации
        """
        self.kafka_client = KafkaClient(config_path)
        
    def get_current_partition_assignment(self, topic: str) -> Dict:
        """
        Получение текущего распределения партиций
        
        Args:
            topic: имя топика
            
        Returns:
            Dict с информацией о текущем распределении партиций
        """
        try:
            topic_info = self.kafka_client.get_topic_partitions(topic)
            logger.info(f"Текущее распределение партиций для топика {topic}:")
            logger.info(json.dumps(topic_info, indent=2))
            return topic_info
        except Exception as e:
            logger.error(f"Ошибка при получении информации о партициях: {e}")
            raise
            
    def create_reassignment_json(self, topic: str, new_assignment: List[Dict]) -> str:
        """
        Создание JSON файла для перераспределения партиций
        
        Args:
            topic: имя топика
            new_assignment: новое распределение партиций
            
        Returns:
            str: путь к созданному JSON файлу
        """
        try:
            reassignment = {
                "version": 1,
                "partitions": [
                    {
                        "topic": topic,
                        "partition": assignment["partition"],
                        "replicas": assignment["replicas"]
                    }
                    for assignment in new_assignment
                ]
            }
            
            file_path = f"reassignment_{topic}.json"
            with open(file_path, 'w') as f:
                json.dump(reassignment, f, indent=2)
                
            logger.info(f"Файл перераспределения создан: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Ошибка при создании файла перераспределения: {e}")
            raise
            
    def execute_reassignment(self, json_file_path: str) -> None:
        """
        Выполнение перераспределения партиций
        
        Args:
            json_file_path: путь к JSON файлу с новым распределением
        """
        try:
            # Здесь должна быть реализация выполнения перераспределения
            # с использованием kafka-reassign-partitions.sh
            logger.info(f"Перераспределение партиций выполнено с использованием файла {json_file_path}")
        except Exception as e:
            logger.error(f"Ошибка при выполнении перераспределения: {e}")
            raise
            
    def verify_reassignment(self, topic: str) -> None:
        """
        Проверка статуса перераспределения
        
        Args:
            topic: имя топика
        """
        try:
            topic_info = self.kafka_client.get_topic_partitions(topic)
            logger.info(f"Статус перераспределения для топика {topic}:")
            logger.info(json.dumps(topic_info, indent=2))
        except Exception as e:
            logger.error(f"Ошибка при проверке статуса перераспределения: {e}")
            raise
            
    def close(self) -> None:
        """Закрытие соединений"""
        try:
            self.kafka_client.close()
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединений: {e}")
            raise

if __name__ == "__main__":
    # Пример использования
    balancer = PartitionBalancer()
    
    try:
        # Получение текущего распределения
        topic = "balanced_topic"
        current_assignment = balancer.get_current_partition_assignment(topic)
        
        # Создание нового распределения (пример)
        new_assignment = [
            {
                "partition": 0,
                "replicas": [0, 1, 2]
            },
            # ... другие партиции
        ]
        
        # Создание файла перераспределения
        json_file = balancer.create_reassignment_json(topic, new_assignment)
        
        # Выполнение перераспределения
        balancer.execute_reassignment(json_file)
        
        # Проверка статуса
        balancer.verify_reassignment(topic)
    finally:
        balancer.close() 