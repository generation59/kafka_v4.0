import ssl
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'topic-1',
    bootstrap_servers=['kafka1:9093'],
    security_protocol='SSL',
    ssl_cafile='infra/docker-compose/ssl/certificates/ca-cert.pem',
    ssl_certfile='infra/docker-compose/ssl/certificates/kafka1-cert.pem',
    ssl_keyfile='infra/docker-compose/ssl/certificates/kafka1-key.pem',
    ssl_check_hostname=False,
    group_id='test-group',
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

for message in consumer:
    print(f'Received: {message.value.decode()}') 