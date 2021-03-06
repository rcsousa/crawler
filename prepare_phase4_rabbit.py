from bs4 import BeautifulSoup
from cloudant.client import Cloudant
import requests, re, redis, os, pika, traceback, time

RABBIT = str(os.getenv('RABBIT'))


CLOUDANT_USERNAME = str(os.getenv('CLOUDANT_USERNAME'))
CLOUDANT_PASSWORD = str(os.getenv('CLOUDANT_PASSWORD'))
CLOUDANT_ACCCOUNT = str(os.getenv('CLOUDANT_ACCCOUNT'))
CLOUDANT_DB = str(os.getenv('CLOUDANT_DB'))

client = Cloudant(CLOUDANT_USERNAME, CLOUDANT_PASSWORD, account=CLOUDANT_ACCCOUNT, connect=True)


try:
        params = pika.URLParameters(RABBIT)
	db = client[CLOUDANT_DB]
        #params.socket_timeout = 5
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
	channel.basic_qos(prefetch_count=1)
        queue_state = channel.queue_declare("jusbrasil_phase3", durable=True, passive=True)
        queue_size = queue_state.method.message_count
        payload = []
        for  method, properties, body in channel.consume("jusbrasil_phase3"):
		print body
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    		PageFile = requests.get("http://www.jusbrasil.com.br"+body, headers=headers)
    		soup = BeautifulSoup(PageFile.content, "html.parser")
		payload = []
    		for links in soup.find("article", { "class" : "text" }).findAll("p"):
			rules = [ "PROCESSO" in links.text, "Reclamante" in links.text, "Reclamado" in links.text]
			if any(rules):
                		payload.append(links.text)
		if len(payload) > 0:
			PROCESSO_idx = [i for i, s in enumerate(payload) if 'PROCESSO' in s]
			Reclamante_idx = [i for i, s in enumerate(payload) if 'Reclamante' in s]
			Reclamado_idx = [i for i, s in enumerate(payload) if 'Reclamado' in s]
			if PROCESSO_idx:
				PROCESSO = payload[PROCESSO_idx[0]]
			else:
				PROCESSO = "Not Found"
                        if Reclamante_idx:
                                RECLAMANTE = payload[Reclamante_idx[0]]
                        else:
                                RECLAMANTE = "Not Found"
                        if Reclamado_idx:
                                RECLAMADO = payload[Reclamado_idx[0]]
                        else:
                                RECLAMADO = "Not Found"
			data = { 
				'_id' : body,
				'processo': PROCESSO,
				'reclamante': RECLAMANTE,
				'reclamado': RECLAMADO 
				}
			my_document = db.create_document(data)
		time.sleep(2)
		#else:
		#	 my_document = None
		#if my_document.exists():
                channel.basic_ack(method.delivery_tag)
except:
        print traceback.format_exc()
