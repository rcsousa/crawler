import requests, re, redis, os, pika, traceback


RABBIT = str(os.getenv('RABBIT'))
REDIS_HOST = str(os.getenv('REDIS_HOST', 'localhost'))
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = str(os.getenv('REDIS_PASSWORD'))

try:
        rd = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
except:
        print "Falha ao conectar com o Redis"

try:
	#urls = rd.lrange("jusbrasil", 0, -1)
	#urlset = set(urls)
	params = pika.URLParameters(RABBIT)
        #params.socket_timeout = 5
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.exchange_declare(exchange="jus_exchange_adv_phase3", exchange_type='fanout', durable=True,auto_delete=False)
        channel.queue_declare(queue="jusbrasil_adv_phase3", durable=True, auto_delete=False)
        channel.queue_bind(queue="jusbrasil_adv_phase3",exchange="jus_exchange_adv_phase3",routing_key='')
	for x in range(1,51):
        	channel.basic_publish(exchange="jus_exchange_adv_phase3", routing_key='' ,  body="https://www.jusbrasil.com.br/advogados/rj/?rand=41481&p="+str(x), properties=pika.BasicProperties(delivery_mode = 2,))
        channel.close()
        connection.close()
except:
	print traceback.format_exc()
