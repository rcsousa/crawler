from bs4 import BeautifulSoup
from kafka import KafkaProducer
import requests, re, redis, os, pika

RABBIT = str(os.getenv('RABBIT'))

#Rotina para pegar a quantidade total de registros da busca
PageFile = requests.get("https://www.jusbrasil.com.br/busca?q=senten%C3%A7a+Ita%C3%BA+Unibanco+s%2Fa")
soup = BeautifulSoup(PageFile.content, "html.parser")
total = soup.find("span", { "class" : "total-results" })
records = int(total.contents[0].replace('.',''))

#Definicao da quantidade de paginas de resultado, dividido por 100000 para reduzir o resultset
pages = records/10

#Carregamento de todas as paginas HTML no array no Kafka
for i in range(1,pages):
        params = pika.URLParameters(RABBIT)
        #params.socket_timeout = 5
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
	payload = "https://www.jusbrasil.com.br/busca?q=senten%C3%A7a+Ita%C3%BA+Unibanco+s%2Fa&p="+str(i)
	channel.exchange_declare(exchange="jus_exchange_phase1", exchange_type='fanout', durable=True,auto_delete=False)
        channel.queue_declare(queue="jusbrasil_phase1", durable=True, auto_delete=False)
        channel.queue_bind(queue="jusbrasil_phase1",exchange="jus_exchange_phase1",routing_key='')
        channel.basic_publish(exchange="jus_exchange_phase1", routing_key='' ,  body=payload, properties=pika.BasicProperties(delivery_mode = 2,))
        channel.close()
        connection.close()
