from datetime import datetime
from elasticsearch import Elasticsearch
client = Elasticsearch('https://elasticsearch-master:9200', 
                 verify_certs=True, basic_auth=('elastic', '90x0AirLYncwXxW9'), 
                 ca_certs='es-ca.crt')
