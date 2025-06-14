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

### 1. Подготовка окружения
```bash
# Клонирование репозитория
git clone <repository-url>
cd kafka-cluster-management

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows

# Установка зависимостей
pip install -r requirements.txt
```

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
- Конфигурационные файлы с чувствительными данными исключены из системы контроля версий

## Лицензия
MIT