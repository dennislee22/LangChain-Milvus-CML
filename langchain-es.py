from datetime import datetime
from elasticsearch import Elasticsearch
client = Elasticsearch('https://elasticsearch-master:9200', 
                 verify_certs=True, basic_auth=('elastic', '90x0AirLYncwXxW9'), 
                 ca_certs='es-ca.crt')

from getpass import getpass
from langchain_elasticsearch import ElasticsearchStore
from urllib.request import urlopen
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

vector_store = ElasticsearchStore(
    es_connection = elastic_client,
    query_field="text_field",
    vector_query_field="vector_query_field.predicted_value",
    index_name="approx-search-demo",
    strategy=ElasticsearchStore.ApproxRetrievalStrategy(
        query_model_id="sentence-transformers__all-minilm-l6-v2"
    ),
)
