import yaml
from typing import Dict, List, Optional
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaClient:
    def __init__(self, config_path: str = "config/kafka_config.yaml"):
        """
        Инициализация клиента Kafka с конфигурацией из YAML файла
        
        Args:
            config_path: путь к файлу конфигурации
        """
        self.config = self._load_config(config_path)
        self.admin_client = self._create_admin_client()
        
    def _load_config(self, config_path: str) -> Dict:
        """Загрузка конфигурации из YAML файла"""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфигурации: {e}")
            raise
            
    def _create_admin_client(self) -> KafkaAdminClient:
        """Создание административного клиента Kafka"""
        try:
            return KafkaAdminClient(
                bootstrap_servers=self.config['kafka']['bootstrap_servers'],
                security_protocol="PLAINTEXT"  # Изменится на SSL при включении
            )
        except Exception as e:
            logger.error(f"Ошибка при создании admin client: {e}")
            raise
            
    def create_topic(self, topic_name: str, num_partitions: int, replication_factor: int) -> None:
        """
        Создание нового топика
        
        Args:
            topic_name: имя топика
            num_partitions: количество партиций
            replication_factor: фактор репликации
        """
        try:
            topic = NewTopic(
                name=topic_name,
                num_partitions=num_partitions,
                replication_factor=replication_factor
            )
            self.admin_client.create_topics([topic])
            logger.info(f"Топик {topic_name} успешно создан")
        except Exception as e:
            logger.error(f"Ошибка при создании топика {topic_name}: {e}")
            raise
            
    def get_topic_partitions(self, topic_name: str) -> Dict:
        """
        Получение информации о партициях топика
        
        Args:
            topic_name: имя топика
            
        Returns:
            Dict с информацией о партициях
        """
        try:
            return self.admin_client.describe_topics([topic_name])[0]
        except Exception as e:
            logger.error(f"Ошибка при получении информации о партициях топика {topic_name}: {e}")
            raise
            
    def create_producer(self) -> KafkaProducer:
        """Создание продюсера Kafka"""
        try:
            return KafkaProducer(
                bootstrap_servers=self.config['kafka']['bootstrap_servers'],
                security_protocol="PLAINTEXT"  # Изменится на SSL при включении
            )
        except Exception as e:
            logger.error(f"Ошибка при создании producer: {e}")
            raise
            
    def create_consumer(self, topic: str, group_id: str) -> KafkaConsumer:
        """
        Создание консьюмера Kafka
        
        Args:
            topic: имя топика
            group_id: ID группы консьюмеров
        """
        try:
            return KafkaConsumer(
                topic,
                bootstrap_servers=self.config['kafka']['bootstrap_servers'],
                group_id=group_id,
                security_protocol="PLAINTEXT",  # Изменится на SSL при включении
                auto_offset_reset='earliest'
            )
        except Exception as e:
            logger.error(f"Ошибка при создании consumer: {e}")
            raise
            
    def close(self) -> None:
        """Закрытие соединений"""
        try:
            self.admin_client.close()
        except Exception as e:
            logger.error(f"Ошибка при закрытии соединений: {e}")
            raise 