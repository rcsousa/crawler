from bs4 import BeautifulSoup
from kafka import KafkaProducer
import requests, re, redis, os

#Conecta com Redis fazendo parsing de variavel de ambiente

REDIS_HOST = str(os.getenv('REDIS_HOST', 'localhost'))
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_PASSWORD = str(os.getenv('REDIS_PASSWORD'))

try:
        rd = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD)
except:
        print "Falha ao conectar com o Redis"

#Inicializacao dos arrays
url = []
list = []

#Rotina para pegar a quantidade total de registros da busca
PageFile = requests.get("https://www.jusbrasil.com.br/busca?q=senten%C3%A7a+Ita%C3%BA+Unibanco+s%2Fa")
soup = BeautifulSoup(PageFile.content, "html.parser")
total = soup.find("span", { "class" : "total-results" })
records = int(total.contents[0].replace('.',''))

#Definicao da quantidade de paginas de resultado, dividido por 100000 para reduzir o resultset
pages = records/10000

#Carregamento de todas as paginas HTML no array "URL"
for i in range(1,pages):
    PageFile = requests.get("https://www.jusbrasil.com.br/busca?q=senten%C3%A7a+Ita%C3%BA+Unibanco+s%2Fa&p="+str(i))
    url.append(PageFile)

#Parsing de todos os HTMLs para identificacao dos links ('href')
for x in range(len(url)):
    soup = BeautifulSoup(url[x].content, "html.parser")
    for links in soup.find_all('a'):
            list.append(links.get('href'))

#Eliminacao de todos os indices nulos do array
newurls = [x for x in list if x is not None]

#Filtro para listar apenas os resultados importantes
r = re.compile("/diarios/[0-9]")
newlist = filter(r.match, newurls)

#Remove key anterior
rd.delete("jusbrasil")

#Print de todos resultados
for x in range(len(newlist)):
     rd.lpush("jusbrasil",newlist[x])
