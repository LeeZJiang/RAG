#!/bin/bash

# 启动 Milvus
docker-compose up -d

# 等待 Milvus 启动
echo "Waiting for Milvus to start..."
sleep 30

# 安装 Python 依赖
pip install -r requirements.txt

# 启动 FastAPI 服务
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload 