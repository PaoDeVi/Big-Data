#!/usr/bin/python3

from kafka import KafkaProducer
from datetime import datetime
import sys

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'ferreteria'

class FileReader:
    def __init__(self, file_path):
        self.file_path = file_path
    
    def read_file(self):
        with open(self.file_path, 'r') as file:
            for line in file:
                yield line.strip()

def send_to_kafka(producer, topic, message):
    producer.send(topic, bytes(message, encoding='utf-8'))

def main(file_path):
    try:
        producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER)
    except Exception as e:
        print(f'Error Connecting to Kafka --> {e}')
        sys.exit(1)

    file_reader = FileReader(file_path)

    for line in file_reader.read_file():
        if '|' in line:
            parts = line.split('|')
            item = parts[0]
            quantity = parts[1]
            category = parts[2]
            price = parts[3]
            date_sold = parts[4]
            item_id = parts[5]
            
            message = f'{item}|{quantity}|{category}|{price}|{date_sold}|{item_id}'
            
            # Imprimir el mensaje antes de enviarlo a Kafka
            print(f'Preparando para enviar mensaje a Kafka: {message}')
            
            send_to_kafka(producer, KAFKA_TOPIC, message)
            
            d = datetime.now()
            print(f'[{d.hour}:{d.minute}.{d.second}] Enviando item: {item}, cantidad: {quantity}')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 productor.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    main(file_path)
