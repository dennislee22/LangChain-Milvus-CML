# Designing a Scalable Milvus RAG with Langchain on CML

## <a name="toc_0"></a>Table of Contents
[//]: # (TOC)
[1. Overview](#toc_0)<br>
[2. Deploy Milvus on K8s](#toc_1)<br>
[3. Run Langchain with Milvus on CML](#toc_2)<br>
&nbsp;&nbsp;&nbsp;&nbsp;[3.1. Build Custom Docker Image](#toc_3)<br>
&nbsp;&nbsp;&nbsp;&nbsp;[3.2. Create CML Session](#toc_4)<br>
&nbsp;&nbsp;&nbsp;&nbsp;[3.3. Create Tensorboard in CML Application](#toc_5)<br>
&nbsp;&nbsp;&nbsp;&nbsp;[3.4. Prepare Dataset & Model](#toc_6)<br>


### <a name="toc_0"></a>1. Overview

- When fine-tuning/training a LLM, insufficient VRAM is a major constraint. First, let's examine the actual GPU memory requirements for fine-tuning a model. 
- In general, the major components that will be loaded into the VRAM during LLM training process are as follows.

```
VRAM (training/fine-tuning) = Model Parameters + Optimizer + Gradient + Activation 
```



### <a name="toc_1"></a>2. Summary & Benchmark Score

- Tba
  
<img width="1418" alt="image" src="https://github.com/dennislee22/langchain-milvus/assets/35444414/0a13ff2b-fef0-4dc7-bc03-9a06757baf39">

<img width="1428" alt="image" src="https://github.com/dennislee22/langchain-milvus/assets/35444414/465eb6c6-b698-4fc3-b829-cf4cd2423911">

<img width="1418" alt="image" src="https://github.com/dennislee22/langchain-milvus/assets/35444414/5015305b-2d83-4288-9fd2-a87ffa1ddcc5">

<img width="1407" alt="image" src="https://github.com/dennislee22/langchain-milvus/assets/35444414/b19983dd-0a06-4338-818e-3adbdb493ec1">

<img width="1412" alt="image" src="https://github.com/dennislee22/langchain-milvus/assets/35444414/7a989057-3a00-435f-a000-c11518aec89d">
