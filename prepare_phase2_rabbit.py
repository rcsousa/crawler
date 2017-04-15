from bs4 import BeautifulSoup
from kafka import KafkaConsumer
import requests, re, redis, os, pika, traceback

RABBIT = str(os.getenv('RABBIT'))

#Conecta com Redis fazendo parsing de variavel de ambiente

REDIS_HOST = str(os.getenv('REDIS_HOST', 'localhost'))
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = str(os.getenv('REDIS_PASSWORD'))

try:
        rd = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
except:
        print "Falha ao conectar com o Redis"

try:
	r = re.compile("/diarios/[0-9]")
        params = pika.URLParameters(RABBIT)
        #params.socket_timeout = 5
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
	channel.basic_qos(prefetch_count=1)
        queue_state = channel.queue_declare("jusbrasil_phase1", durable=True, passive=True)
        queue_size = queue_state.method.message_count
        payload = []
        for  method, properties, body in channel.consume("jusbrasil_phase1"):
                #payload.append(result)
		print body
    		PageFile = requests.get(body)
    		soup = BeautifulSoup(PageFile.content, "html.parser")
    		for links in soup.find_all('a'):
            		if links.get('href') is not None:
                		if r.match(links.get('href')):
                        		rd.lpush("jusbrasil",links.get('href'))
                        		print links.get('href')
                channel.basic_ack(method.delivery_tag)
                #if method.delivery_tag == queue_size:
                #        break
                #requeued_messages = channel.cancel()
                #channel.close()
except:
        print traceback.format_exc()
