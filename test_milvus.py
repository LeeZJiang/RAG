from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

# 连接到 Milvus
connections.connect(host='localhost', port='19530')

# 检查连接是否成功
print("Connected to Milvus successfully!")

# 检查 Milvus 版本
print(f"Milvus version: {utility.get_server_version()}")

# 检查是否有现有的集合
collections = utility.list_collections()
print(f"Existing collections: {collections}")

# 创建一个测试集合
collection_name = "test_collection"
if collection_name in collections:
    utility.drop_collection(collection_name)

# 定义集合的字段
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128)
]

# 创建集合
schema = CollectionSchema(fields=fields, description="test collection")
collection = Collection(name=collection_name, schema=schema)

print(f"Collection '{collection_name}' created successfully!")

# 插入一些测试数据
import numpy as np
vectors = np.random.random((10, 128)).tolist()
collection.insert([vectors])

print("Data inserted successfully!")

# 创建索引
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 1024}
}
collection.create_index(field_name="embedding", index_params=index_params)

print("Index created successfully!")

# 加载集合到内存
collection.load()

# 执行搜索
search_params = {
    "metric_type": "L2",
    "params": {"nprobe": 10}
}
results = collection.search(
    data=[vectors[0]],  # 使用第一个向量作为查询向量
    anns_field="embedding",
    param=search_params,
    limit=5
)

print("Search results:")
for hits in results:
    for hit in hits:
        print(f"Hit: {hit}")

# 清理
collection.drop()
print("Test completed successfully!") 