# RAG: LangChain with Milvus on CML

![image](https://github.com/dennislee22/langchain-milvus/assets/35444414/f1797486-12a7-4580-abd2-fa4f65dcfc7b)

- RAG (Retrieval Augmented Generation) is a great mechanism to build a chatbot with the latest/custom data, mainly for producing an answer with a high degree of accuracy. Building a scalable and secured vector DB system is equally indispensable as its counterpart LLM platform - both need to be in always ready and highly performant mode.
- This article focuses on the design aspects of architecting Milvus vector store on-premise solution on a microservices platform and also demonstrates how LangChain running on CML (Cloudera Machine Learning) can be integrated with vector DB and local LLM (no OpenAI 🤗) to answer user’s questions based on the context of the infused document. All the solution components are running inside the air-gapped environment.

### Deploy a scalable vector DB platform
Milvus is one of the handful cloud-native vector DB solutions in the AI realm today. It is composed of different stateful and stateless pods running different functionalities, leveraging suitable deployment technologies (statefulset, replicaset) to ensure the solution is resilient, persistent, and scalable. Here's the summary of the design aspects when hosting Milvus solution on the K8s platform.
- Host Milvus cluster in a dedicated namespace.
- As Milvus is a persistent DB solution, stateful pods such as etcd, pulsar, zookeeper and minio can leverage the storageClass with RWO storage backend. etcd stateful pod is best running with SSD/NVMe device.
- AI framework such as LangChain on CML is hosted on a separate namespace, communicating with the vector DB via the internal VXLAN/GRE network segment. This aids in ensuring low latency as well as minimizing attack surface.
- Attu can be deployed as the Milvus GUI tool and expose it as a dedicated route/ingress object. 

As a result, here are the snapshots of the running Milvus pods (minimum setup) and its associated pvc in its namespace. They are deployed and managed by the helm operator with the associated CRD.

```
# helm repo list
NAME    URL                                      
milvus  https://zilliztech.github.io/milvus-helm/
```
```
# oc -n milvus get pods
NAME                                            READY   STATUS      RESTARTS   AGE
my-attu-7bfd998dd6-8lkg6                        1/1     Running     0          30h
my-release-etcd-0                               1/1     Running     0          30h
my-release-milvus-datacoord-78f57b8cc7-m2k9l    1/1     Running     0          30h
my-release-milvus-datanode-69db8bdf66-vj2c8     1/1     Running     0          30h
my-release-milvus-indexcoord-6fd9955db7-4458s   1/1     Running     0          30h
my-release-milvus-indexnode-578f486fbb-v27d4    1/1     Running     0          30h
my-release-milvus-proxy-74f8758f66-vwdpw        1/1     Running     0          30h
my-release-milvus-querycoord-789cff8fbc-xdbqm   1/1     Running     0          30h
my-release-milvus-querynode-0-8955c9899-8dvws   1/1     Running     0          30h
my-release-milvus-rootcoord-75f74ddc6f-tkltj    1/1     Running     0          30h
my-release-minio-77c48997d8-q295c               1/1     Running     0          30h
my-release-pulsar-bookie-0                      1/1     Running     0          30h
my-release-pulsar-bookie-1                      1/1     Running     0          30h
my-release-pulsar-bookie-init-xj6zz             0/1     Completed   0          30h
my-release-pulsar-broker-0                      1/1     Running     0          30h
my-release-pulsar-proxy-0                       1/1     Running     0          30h
my-release-pulsar-pulsar-init-jm9gp             0/1     Completed   0          30h
my-release-pulsar-zookeeper-0                   1/1     Running     0          30h
```
```
# oc -n milvus get pvc | awk '{ printf("%-10s%-10s%-10s%-10s\n",$4, $5, $2, $1) }'
CAPACITY  ACCESS    STATUS    NAME      
10Gi      RWO       Bound     data-my-release-etcd-0
500Gi     RWO       Bound     my-release-minio
100Gi     RWO       Bound     my-release-pulsar-bookie-journal-my-release-pulsar-bookie-0
100Gi     RWO       Bound     my-release-pulsar-bookie-journal-my-release-pulsar-bookie-1
200Gi     RWO       Bound     my-release-pulsar-bookie-ledgers-my-release-pulsar-bookie-0
200Gi     RWO       Bound     my-release-pulsar-bookie-ledgers-my-release-pulsar-bookie-1
20Gi      RWO       Bound     my-release-pulsar-zookeeper-data-my-release-pulsar-zookeeper-0
```

- Attu dashboard shows the status of the vector DB platform visually.
![image](https://github.com/dennislee22/langchain-milvus/assets/35444414/2f33ca95-2985-4629-bd94-6530227f7f8e)

###  Run LangChain in the CML platform
- CML is yet another cloud-native AI platform, leveraging K8s technologies such as Openshift and RKE2. It can handle multiple data scientists' requests by spinning up dedicated user namespaces, preventing noisy neighbour problems. In this case, I spin up a Jupyter Notebook session without GPU to run the LangChain framework with Python3.10 on the Ubuntu20.04 OS image. Because CML is a multi-user AI platform, it is supported by the RWX storage for allowing different users to share the same project files for collaboration purposes.

### RetrievalQA Chain
- Now that I have both vector DB and LangChain framework running, let's build a RetrievalQA chain use case - user as the financial analyst wants to inquire about the financial status of a company using natural language. The full iPython code running on CML is illustrated here.

### Prerequisites
a. Install the necessary python modules.
b. Download a PDF document.
```
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import Milvus
from langchain.embeddings import HuggingFaceEmbeddings, SentenceTransformerEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter

loader = PyPDFLoader("samsungreport.pdf") #wget https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2023_con_quarter04_all.pdf
pages = loader.load_and_split()
```

c. Download sentence-transformers embedding model from 🤗 site.
```
git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
```

d. As my platform doesn't have GPU, I download the Falcon GGUF model which works seamlessly on the CPU-only platform, leveraging Llama-Cpp module.

### Step 1: Chunking
Because a document is huge, it is normally split up into smaller chunks before it is stored in the vector DB. Rather than "looking for a needle in a haystack", chunking aids in producing quicker results especially when using the refine chain method.
```
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(pages)
```

### Step 2: Embeddings
Next, transform those chunks into the form of embeddings.
```
local_embedding_model="all-MiniLM-L6-v2" #git clone https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
embeddings = HuggingFaceEmbeddings(model_name=local_embedding_model)
```

### Step 3: Store
Subsequently, store those chunks in the form of embeddings in the vector DB so that LangChain can call and query the context.
```
vector_db = Milvus.from_documents(
    docs,
    embeddings,
    collection_name="samsungreport2023",
    connection_args={"host": "my-release-milvus.milvus.svc.cluster.local", "port": "19530"},
)
```

A quick check at the Attu dashboard shows the details of the stored database.
![image](https://github.com/dennislee22/langchain-milvus/assets/35444414/23da624d-db15-4473-b814-49403fb7e542)
![image](https://github.com/dennislee22/langchain-milvus/assets/35444414/b32926eb-e9f7-4b95-952e-ed8bfee0146c)

Also, load the downloaded Falcon GGUF model with specific temperature and top values into the platform memory.
```
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

template = """Question: {question}
Answer: Let's work this out in a step by step way to be sure we have the right answer"""
prompt = PromptTemplate.from_template(template)
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

local_path = (
    "gpt4all-falcon-newbpe-q4_0.gguf"  #wget https://gpt4all.io/models/gguf/gpt4all-falcon-newbpe-q4_0.gguf
)
llm = LlamaCpp(
    model_path=local_path,
    temperature=0.75,
    max_tokens=2000,
    top_p=1,
    n_ctx=4096,
    callback_manager=callback_manager,
    verbose=True,
)
```

### Step 4: Show time! User query
Let's try asking questions directly to the Falcon model without going through the LangChain. As expected, the generated result is rather disappointing because the model was trained without the latest dataset.
Now let's try asking the same question by involving LangChain wrapper to call upon the vector DB.
```
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

prompt_template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:"""
QA_CHAIN_PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

chain_type_kwargs={
        "refine_prompt": QA_CHAIN_PROMPT
        }

qa_chain = RetrievalQA.from_chain_type(
    llm,
    chain_type="refine",
    retriever=vector_db.as_retriever(search_type="mmr", search_kwargs={"k": 1}),
    return_source_documents=False,
    callbacks=None,
    chain_type_kwargs={"refine_prompt": QA_CHAIN_PROMPT,"verbose":True},
    verbose=True
)

question = "What is Samsung's revenue in 2023 in KRW?"
result = qa_chain({"query": question}) # must be query
result["result"]
```

### Step 5: vector_db.as_retriever
Upon calling LangChain `RetrievalQA` method with `vector_db.as_retriever` module, the context is retrieved quickly with the help of using chain_type="refine" and search_type="mmr". The retrieval outcome is then passed to LangChain for further processing. 

### Step 6: Context + Prompt + Question
The chain is now filled with the context (as a result of previous step), prompt template, and question asked by the user. LangChain calls LLM (Falcon model) again to produce the final answer in natural language.

### Step 7: Answer!
Here's the generated answer with `verbose=true`.
![image](https://github.com/dennislee22/langchain-milvus/assets/35444414/02d6f4c3-243e-4c99-9754-761c09f96ba7)


A quick check with the PDF document reveals the same answer!
![image](https://github.com/dennislee22/langchain-milvus/assets/35444414/9421b130-9030-48e0-af45-59cbbadff968)
source: https://images.samsung.com/is/content/samsung/assets/global/ir/docs/2023_con_quarter04_all.pdf

# Acknowledgement:
Thanks to the contributions from the individuals/organizations for democratizing AI/ML!
