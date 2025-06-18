import ssl
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['kafka1:9093'],
    security_protocol='SSL',
    ssl_cafile='infra/docker-compose/ssl/certificates/ca-cert.pem',
    ssl_certfile='infra/docker-compose/ssl/certificates/kafka1-cert.pem',
    ssl_keyfile='infra/docker-compose/ssl/certificates/kafka1-key.pem',
    ssl_check_hostname=False
)

for i in range(10):
    producer.send('topic-1', value=f'message {i}'.encode())
    print(f'Sent: message {i}')

producer.flush()
producer.close() 