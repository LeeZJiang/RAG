import os
import requests
import json
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
import numpy as np
import time

# 设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'

class VectorStore:
    def __init__(self, max_retries=3):
        # 尝试连接 Milvus
        retry_count = 0
        while retry_count < max_retries:
            try:
                # 连接到 Milvus
                connections.connect(host='localhost', port='19530')
                print("Successfully connected to Milvus")
                break
            except Exception as e:
                retry_count += 1
                if retry_count == max_retries:
                    raise Exception(f"Failed to connect to Milvus after {max_retries} attempts: {str(e)}")
                print(f"Failed to connect to Milvus (attempt {retry_count}/{max_retries}). Retrying in 5 seconds...")
                time.sleep(5)
        
        # 设置 Ollama API 地址
        self.ollama_url = "http://localhost:11434/api/embeddings"
        self.model_name = "bge-m3"  # 使用 bge-m3 模型
        
        # 删除现有集合（如果存在）
        self.collection_name = "documents"
        if utility.has_collection(self.collection_name):
            utility.drop_collection(self.collection_name)
            print(f"Dropped existing collection: {self.collection_name}")
        
        # 创建新集合
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),  # bge-m3 的维度是768
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        schema = CollectionSchema(fields=fields, description="document collection")
        self.collection = Collection(name=self.collection_name, schema=schema)
        
        # 创建索引
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)
        self.collection.load()
        print(f"Created new collection: {self.collection_name}")

    def _get_embeddings(self, texts):
        """使用 Ollama API 获取文本的嵌入向量"""
        embeddings = []
        for text in texts:
            try:
                response = requests.post(
                    self.ollama_url,
                    json={
                        "model": self.model_name,
                        "prompt": text
                    }
                )
                response.raise_for_status()
                embedding = response.json()["embedding"]
                # 确保向量维度正确
                if len(embedding) != 768:
                    print(f"Warning: Expected embedding dimension 768, but got {len(embedding)}")
                    # 如果维度不正确，可以选择填充或截断
                    if len(embedding) > 768:
                        embedding = embedding[:768]
                    else:
                        embedding = embedding + [0] * (768 - len(embedding))
                embeddings.append(embedding)
            except Exception as e:
                print(f"获取嵌入向量失败: {e}")
                raise
        return np.array(embeddings)

    def add_documents(self, texts, metadatas=None):
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        # 生成嵌入
        embeddings = self._get_embeddings(texts)
        
        # 准备数据
        entities = [
            texts,
            embeddings.tolist(),
            metadatas
        ]
        
        # 插入数据
        self.collection.insert(entities)
        self.collection.flush()

    def search(self, query, k=5):
        # 生成查询嵌入
        query_embedding = self._get_embeddings([query])[0]
        
        # 搜索参数
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10}
        }
        
        # 执行搜索
        results = self.collection.search(
            data=[query_embedding.tolist()],
            anns_field="embedding",
            param=search_params,
            limit=k,
            output_fields=["text", "metadata"]
        )
        
        # 处理结果
        search_results = []
        for hits in results:
            for hit in hits:
                search_results.append({
                    "text": hit.entity.get('text'),
                    "metadata": hit.entity.get('metadata'),
                    "score": hit.distance
                })
        
        return search_results 