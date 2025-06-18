# Kafka Cluster Management Project

## Описание проекта
Проект представляет собой набор инструментов и конфигураций для управления кластером Apache Kafka, включая балансировку партиций, диагностику кластера и настройку защищенного соединения.

## Структура проекта
```
.
├── infra/
│   └── docker-compose/
│       ├── docker-compose.yml
│       └── ssl/
│           ├── certificates/
│           └── config/
├── src/
│   ├── producers/
│   ├── consumers/
│   └── utils/
├── config/
│   └── kafka_config.yaml
└── README.md
```

## Требования
- Docker
- Docker Compose
- Python 3.8+
- OpenSSL (для генерации сертификатов)

## Установка и запуск

### 1. Генерация SSL сертификатов (обязательно до запуска кластера)

1. Убедитесь, что у вас установлен OpenSSL и keytool (обычно входит в JDK).
2. Проверьте наличие файла конфигурации для сертификатов: `infra/docker-compose/ssl/config/kafka_broker.cnf`.
   - Если файла нет, используйте пример из репозитория или создайте аналогичный.
3. Сгенерируйте сертификаты с помощью скрипта:

```bash
# Активируйте виртуальное окружение, если требуется
python src/utils/ssl_generator.py
```

В результате в папке `infra/docker-compose/ssl/certificates` появятся файлы:
- ca-cert.pem, ca-key.pem
- kafka-0.jks, kafka-1.jks, kafka-2.jks
- truststore.jks

**Важно:** Сертификаты должны быть сгенерированы до запуска docker-compose!

### 2. Запуск кластера Kafka
```bash
cd infra/docker-compose
docker-compose up -d
```

## Основные компоненты

### 1. Балансировка партиций
- Создание топика с 8 партициями и фактором репликации 3
- Перераспределение партиций с помощью Partition Reassignment Tools
- Диагностика и мониторинг состояния кластера

### 2. Защищенное соединение
- SSL/TLS настройка для всех брокеров
- Управление доступом (ACL) для топиков
- Безопасная передача сообщений

## Мониторинг
- Kafka UI доступен по адресу: http://localhost:8086
- Метрики и логи доступны через встроенные инструменты Kafka

## Безопасность
- Все сертификаты и ключи хранятся в директории `infra/docker-compose/ssl/certificates`
- Конфигурационный файл для генерации сертификатов: `infra/docker-compose/ssl/config/kafka_broker.cnf`
- Конфигурационные файлы с чувствительными данными исключены из системы контроля версий

## Лицензия
MIT

# Инструкция по запуску и диагностике Kafka-кластера

## Задание 1. Балансировка партиций и диагностика кластера

1. Запусти кластер KRaft (PLAINTEXT):
   ```bash
   docker-compose -f docker-compose.kraft.yml up --build
   ```
2. Создай топик:
   ```bash
   docker exec -it kafka-0 kafka-topics.sh --create --topic balanced_topic --partitions 8 --replication-factor 3 --bootstrap-server kafka-0:9092
   ```
3. Получи текущее распределение партиций:
   ```bash
   docker exec -it kafka-0 kafka-topics.sh --describe --topic balanced_topic --bootstrap-server kafka-0:9092
   ```
4. Сгенерируй reassignment.json (пример в проекте).
5. Применить reassignment:
   ```bash
   docker exec -it kafka-0 kafka-reassign-partitions.sh --bootstrap-server kafka-0:9092 --reassignment-json-file /path/to/reassignment.json --execute
   ```
6. Проверить статус:
   ```bash
   docker exec -it kafka-0 kafka-reassign-partitions.sh --bootstrap-server kafka-0:9092 --reassignment-json-file /path/to/reassignment.json --verify
   ```
7. Смоделировать сбой:
   - Остановить брокер: `docker stop kafka-1`
   - Проверить состояние: `docker exec -it kafka-0 kafka-topics.sh --describe --topic balanced_topic --bootstrap-server kafka-0:9092`
   - Запустить брокер: `docker start kafka-1`
   - Проверить восстановление: `docker exec -it kafka-0 kafka-topics.sh --describe --topic balanced_topic --bootstrap-server kafka-0:9092`

## Задание 2. SSL и ACL

1. Сгенерируй сертификаты:
   ```bash
   python3 src/utils/ssl_generator.py
   ```
   > Используется конфиг: `infra/docker-compose/ssl/config/kafka_broker.cnf`
2. Запусти кластер с SSL:
   ```bash
   docker-compose up --build
   ```
3. Создай топики:
   ```bash
   docker exec -it kafka1 kafka-topics.sh --create --topic topic-1 --partitions 3 --replication-factor 3 --bootstrap-server kafka1:9093 --command-config /bitnami/kafka/config/client-ssl.properties
   docker exec -it kafka1 kafka-topics.sh --create --topic topic-2 --partitions 3 --replication-factor 3 --bootstrap-server kafka1:9093 --command-config /bitnami/kafka/config/client-ssl.properties
   ```
4. Настрой ACL (см. пример скрипта или переменные окружения).
5. Проверь работу продюсера и консьюмера (см. примеры в src/producers/ и src/consumers/).

## Структура проекта
- `docker-compose.kraft.yml` — кластер для балансировки (KRaft, PLAINTEXT)
- `docker-compose.yml` — кластер с SSL и ACL (Zookeeper + 3 Kafka)
- `infra/docker-compose/ssl/certificates/` — все сертификаты и truststore
- `infra/docker-compose/ssl/config/kafka_broker.cnf` — конфиг для генерации сертификатов
- `src/utils/ssl_generator.py` — генератор сертификатов
- `src/producers/ssl_producer.py` — пример продюсера с SSL
- `src/consumers/ssl_consumer.py` — пример консьюмера с SSL
- `reassignment.json` — пример для перераспределения партиций
- `Отчет_по_генерации_сертификатов.md` — отчёт по сертификатам
- `Отчет_по_балансировке.md` — отчёт по балансировке
- `Отчет_по_SSL_ACL.md` — отчёт по SSL и ACL

## Важно
- Всегда сначала генерируй сертификаты, потом запускай docker-compose.
- Все команды выполняй из папки с docker-compose.yml.
- Для диагностики и ребалансировки используй kafka-topics.sh и kafka-reassign-partitions.sh внутри контейнера.