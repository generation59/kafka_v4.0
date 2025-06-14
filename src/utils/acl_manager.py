import subprocess
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ACLManager:
    def __init__(self, bootstrap_servers: str = "localhost:9094"):
        """
        Инициализация менеджера ACL
        
        Args:
            bootstrap_servers: адреса брокеров Kafka
        """
        self.bootstrap_servers = bootstrap_servers
        
    def add_producer_acl(self, topic: str, principal: str, host: str = "*") -> None:
        """
        Добавление ACL для продюсера
        
        Args:
            topic: имя топика
            principal: имя пользователя/группы
            host: хост (по умолчанию "*" - любой)
        """
        try:
            subprocess.run([
                "kafka-acls",
                "--bootstrap-server", self.bootstrap_servers,
                "--add",
                "--allow-principal", principal,
                "--operation", "Write",
                "--topic", topic,
                "--host", host
            ], check=True)
            
            logger.info(f"ACL для продюсера {principal} добавлен для топика {topic}")
        except Exception as e:
            logger.error(f"Ошибка при добавлении ACL для продюсера: {e}")
            raise
            
    def add_consumer_acl(self, topic: str, principal: str, host: str = "*") -> None:
        """
        Добавление ACL для консьюмера
        
        Args:
            topic: имя топика
            principal: имя пользователя/группы
            host: хост (по умолчанию "*" - любой)
        """
        try:
            subprocess.run([
                "kafka-acls",
                "--bootstrap-server", self.bootstrap_servers,
                "--add",
                "--allow-principal", principal,
                "--operation", "Read",
                "--topic", topic,
                "--host", host
            ], check=True)
            
            logger.info(f"ACL для консьюмера {principal} добавлен для топика {topic}")
        except Exception as e:
            logger.error(f"Ошибка при добавлении ACL для консьюмера: {e}")
            raise
            
    def list_acls(self, topic: str) -> None:
        """
        Вывод списка ACL для топика
        
        Args:
            topic: имя топика
        """
        try:
            subprocess.run([
                "kafka-acls",
                "--bootstrap-server", self.bootstrap_servers,
                "--list",
                "--topic", topic
            ], check=True)
        except Exception as e:
            logger.error(f"Ошибка при получении списка ACL: {e}")
            raise
            
    def remove_acl(self, topic: str, principal: str, operation: str) -> None:
        """
        Удаление ACL
        
        Args:
            topic: имя топика
            principal: имя пользователя/группы
            operation: операция (Read/Write)
        """
        try:
            subprocess.run([
                "kafka-acls",
                "--bootstrap-server", self.bootstrap_servers,
                "--remove",
                "--allow-principal", principal,
                "--operation", operation,
                "--topic", topic
            ], check=True)
            
            logger.info(f"ACL для {principal} удален для топика {topic}")
        except Exception as e:
            logger.error(f"Ошибка при удалении ACL: {e}")
            raise

if __name__ == "__main__":
    # Пример использования
    acl_manager = ACLManager()
    
    try:
        # Настройка ACL для topic-1
        acl_manager.add_producer_acl("topic-1", "User:producer")
        acl_manager.add_consumer_acl("topic-1", "User:consumer")
        
        # Настройка ACL для topic-2
        acl_manager.add_producer_acl("topic-2", "User:producer")
        # Консьюмеры не имеют доступа к topic-2
        
        # Вывод списка ACL
        acl_manager.list_acls("topic-1")
        acl_manager.list_acls("topic-2")
    except Exception as e:
        logger.error(f"Ошибка при настройке ACL: {e}") 