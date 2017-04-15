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
        queue_state = channel.queue_declare("jusbrasil_adv_phase3", durable=True, passive=True)
        queue_size = queue_state.method.message_count
        payload = []
        for  method, properties, body in channel.consume("jusbrasil_adv_phase3"):
		print body
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    		PageFile = requests.get(body, headers=headers)
    		soup = BeautifulSoup(PageFile.content, "html.parser")
		adv = []
		oab = []
		for x in soup.findAll("ul", { "class" : "lawyers pro" }):   
	     		for y in x.findAll("li"):
	             		for z in y.findAll("div", { "class" : "title" }):
	                     		adv.append(z.text.split('  ')[1])
	                     		oab.append(z.text.split('  ')[2])
		for aa in range(0,len(adv)):
			data = { 
				'advogado': adv[aa],
				'oab' : oab[aa]
				}
			my_document = db.create_document(data)
		time.sleep(2)
		#else:
		#	 my_document = None
		#if my_document.exists():
                channel.basic_ack(method.delivery_tag)
except:
        print traceback.format_exc()
