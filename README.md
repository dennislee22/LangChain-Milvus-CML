# On-Premise RAG (Langchain+Milvus+) system with CML

## <a name="toc_0"></a>Table of Contents
[//]: # (TOC)
[1. Overview](#toc_0)<br>
[2. Deploy Scalable Milvus on K8s](#toc_1)<br>
[3. Run Langchain with Milvus on CML](#toc_2)<br>
&nbsp;&nbsp;&nbsp;&nbsp;[3.1. Installation](#toc_3)<br>


### <a name="toc_0"></a>1. Overview

- tba


### <a name="toc_1"></a>2. Deploy Scalable Milvus on K8s

```
# helm repo list
NAME   	URL                                      
milvus 	https://zilliztech.github.io/milvus-helm/
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

  
<img width="1418" alt="image" src="https://github.com/dennislee22/langchain-milvus/assets/35444414/0a13ff2b-fef0-4dc7-bc03-9a06757baf39">

<img width="1428" alt="image" src="https://github.com/dennislee22/langchain-milvus/assets/35444414/465eb6c6-b698-4fc3-b829-cf4cd2423911">

<img width="1418" alt="image" src="https://github.com/dennislee22/langchain-milvus/assets/35444414/5015305b-2d83-4288-9fd2-a87ffa1ddcc5">

<img width="1407" alt="image" src="https://github.com/dennislee22/langchain-milvus/assets/35444414/b19983dd-0a06-4338-818e-3adbdb493ec1">

<img width="1412" alt="image" src="https://github.com/dennislee22/langchain-milvus/assets/35444414/7a989057-3a00-435f-a000-c11518aec89d">
