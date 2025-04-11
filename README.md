# RAG Knowledge Base System

基于 RAG (Retrieval-Augmented Generation) 的企业知识库系统，支持 PDF 文档的上传、解析和语义搜索。

## 系统架构

- 前端：Streamlit
- 后端：FastAPI
- 向量数据库：Milvus
- 向量模型：BGE-M3 (通过 Ollama 提供)

## 功能特点

1. PDF文档上传和解析
2. 文本向量化存储
3. 语义相似度搜索
4. 实时搜索结果展示

## 部署要求

### 系统要求
- Python 3.8+
- Docker
- Ollama

### 依赖安装
```bash
pip install -r requirements.txt
```

### 启动服务

1. 启动 Milvus:
```bash
docker-compose up -d
```

2. 启动后端服务:
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 9081 --reload
```

3. 启动前端服务:
```bash
cd frontend
streamlit run app.py
```

## 使用说明

1. 访问前端界面：http://localhost:8501
2. 上传 PDF 文件
3. 输入关键词进行搜索
4. 查看搜索结果

## API 文档

访问 http://localhost:9081/docs 查看完整的 API 文档。

## 目录结构

```
.
├── README.md
├── requirements.txt
├── docker-compose.yml
├── backend/
│   ├── main.py
│   └── vector_store.py
└── frontend/
    └── app.py
```

## 注意事项

1. 确保 Milvus 服务正常运行
2. 确保 Ollama 服务可用，并已下载 BGE-M3 模型
3. 检查防火墙设置，确保端口可访问 