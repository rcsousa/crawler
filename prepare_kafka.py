from bs4 import BeautifulSoup
from kafka import KafkaProducer
import requests, re, redis, os

#Rotina para pegar a quantidade total de registros da busca
PageFile = requests.get("https://www.jusbrasil.com.br/busca?q=senten%C3%A7a+Ita%C3%BA+Unibanco+s%2Fa")
soup = BeautifulSoup(PageFile.content, "html.parser")
total = soup.find("span", { "class" : "total-results" })
records = int(total.contents[0].replace('.',''))

#Definicao da quantidade de paginas de resultado, dividido por 100000 para reduzir o resultset
pages = records/10

#Carregamento de todas as paginas HTML no array no Kafka
for i in range(1,pages):
    producer = KafkaProducer(bootstrap_servers='localhost:9092')
    producer.send('pages', b'https://www.jusbrasil.com.br/busca?q=senten%C3%A7a+Ita%C3%BA+Unibanco+s%2Fa&p='+str(i))
