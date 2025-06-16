import os
import subprocess
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SSLGenerator:
    def __init__(self, output_dir: str = "infra/docker-compose/ssl/certificates"):
        """
        Инициализация генератора SSL сертификатов
        
        Args:
            output_dir: директория для сохранения сертификатов
        """
        self.output_dir = output_dir
        self._create_output_dir()
        
    def _create_output_dir(self) -> None:
        """Создание директории для сертификатов"""
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            logger.info(f"Директория для сертификатов создана: {self.output_dir}")
        except Exception as e:
            logger.error(f"Ошибка при создании директории: {e}")
            raise
            
    def generate_ca(self) -> None:
        """Генерация корневого сертификата (CA)"""
        try:
            # Генерация приватного ключа CA
            subprocess.run([
                "openssl", "genrsa",
                "-out", f"{self.output_dir}/ca-key.pem",
                "2048"
            ], check=True)
            
            # Генерация самоподписанного сертификата CA
            subprocess.run([
                "openssl", "req",
                "-new", "-x509",
                "-key", f"{self.output_dir}/ca-key.pem",
                "-out", f"{self.output_dir}/ca-cert.pem",
                "-days", "365",
                "-subj", "/CN=kafka-ca"
            ], check=True)
            
            logger.info("Корневой сертификат (CA) успешно создан")
        except Exception as e:
            logger.error(f"Ошибка при генерации CA: {e}")
            raise
            
    def generate_broker_certificates(self, broker_names: List[str], cnf_path: str = None) -> None:
        """
        Генерация сертификатов для брокеров
        
        Args:
            broker_names: список имен брокеров
            cnf_path: путь к .cnf файлу для openssl (с расширениями SAN)
        """
        try:
            for broker in broker_names:
                # Генерация приватного ключа брокера
                subprocess.run([
                    "openssl", "genrsa",
                    "-out", f"{self.output_dir}/{broker}-key.pem",
                    "2048"
                ], check=True)
                
                # Создание CSR для брокера с использованием .cnf файла
                csr_cmd = [
                    "openssl", "req",
                    "-new",
                    "-key", f"{self.output_dir}/{broker}-key.pem",
                    "-out", f"{self.output_dir}/{broker}-csr.pem",
                    "-subj", f"/CN={broker}"
                ]
                if cnf_path:
                    csr_cmd += ["-config", cnf_path, "-extensions", "req_ext"]
                subprocess.run(csr_cmd, check=True)
                
                # Подписание сертификата брокера CA
                subprocess.run([
                    "openssl", "x509",
                    "-req",
                    "-in", f"{self.output_dir}/{broker}-csr.pem",
                    "-CA", f"{self.output_dir}/ca-cert.pem",
                    "-CAkey", f"{self.output_dir}/ca-key.pem",
                    "-CAcreateserial",
                    "-out", f"{self.output_dir}/{broker}-cert.pem",
                    "-days", "365"
                ], check=True)
                
                logger.info(f"Сертификат для брокера {broker} успешно создан")
        except Exception as e:
            logger.error(f"Ошибка при генерации сертификатов брокеров: {e}")
            raise
            
    def create_keystore(self, broker_name: str, password: str) -> None:
        """
        Создание keystore для брокера
        
        Args:
            broker_name: имя брокера
            password: пароль для keystore
        """
        try:
            # Создание PKCS12 хранилища
            subprocess.run([
                "openssl", "pkcs12",
                "-export",
                "-in", f"{self.output_dir}/{broker_name}-cert.pem",
                "-inkey", f"{self.output_dir}/{broker_name}-key.pem",
                "-out", f"{self.output_dir}/{broker_name}.p12",
                "-name", broker_name,
                "-password", f"pass:{password}"
            ], check=True)
            
            # Конвертация в JKS формат
            subprocess.run([
                "keytool",
                "-importkeystore",
                "-srckeystore", f"{self.output_dir}/{broker_name}.p12",
                "-srcstoretype", "PKCS12",
                "-srcstorepass", password,
                "-destkeystore", f"{self.output_dir}/{broker_name}.jks",
                "-deststorepass", password,
                "-destkeypass", password
            ], check=True)
            
            logger.info(f"Keystore для брокера {broker_name} успешно создан")
        except Exception as e:
            logger.error(f"Ошибка при создании keystore: {e}")
            raise
            
    def create_truststore(self, password: str) -> None:
        """
        Создание truststore с корневым сертификатом
        
        Args:
            password: пароль для truststore
        """
        try:
            subprocess.run([
                "keytool",
                "-import",
                "-alias", "ca",
                "-file", f"{self.output_dir}/ca-cert.pem",
                "-keystore", f"{self.output_dir}/truststore.jks",
                "-storepass", password,
                "-noprompt"
            ], check=True)
            
            logger.info("Truststore успешно создан")
        except Exception as e:
            logger.error(f"Ошибка при создании truststore: {e}")
            raise

if __name__ == "__main__":
    # Пример использования
    ssl_generator = SSLGenerator()
    
    try:
        # Генерация CA
        ssl_generator.generate_ca()
        
        # Путь к .cnf файлу
        cnf_path = os.path.abspath("infra/docker-compose/ssl/config/kafka_broker.cnf")
        if not os.path.exists(cnf_path):
            logger.warning(f"Файл конфигурации {cnf_path} не найден! Сертификаты будут сгенерированы без расширений SAN. Это может привести к ошибкам SSL.")
            cnf_path = None
        
        # Генерация сертификатов для брокеров
        broker_names = ["kafka-0", "kafka-1", "kafka-2"]
        ssl_generator.generate_broker_certificates(broker_names, cnf_path=cnf_path)
        
        # Создание keystore для каждого брокера
        password = "changeit"  # В реальном проекте использовать безопасный пароль
        for broker in broker_names:
            ssl_generator.create_keystore(broker, password)
            
        # Создание truststore
        ssl_generator.create_truststore(password)
    except Exception as e:
        logger.error(f"Ошибка при генерации SSL сертификатов: {e}") 