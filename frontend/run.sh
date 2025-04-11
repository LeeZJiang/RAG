#!/bin/bash

# 确保日志目录存在
mkdir -p logs

# 停止已存在的进程
pkill -f "streamlit run app.py"

# 启动 Streamlit
export STREAMLIT_SERVER_ADDRESS="10.101.105.43"
export STREAMLIT_SERVER_PORT="8501"
export STREAMLIT_SERVER_HEADLESS="true"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS="false"

nohup streamlit run app.py \
    --server.address 10.101.105.43 \
    --server.port 8501 \
    --server.headless true \
    --browser.gatherUsageStats false \
    > logs/streamlit.log 2>&1 &

echo "Streamlit service starting... Check logs/streamlit.log for details"
sleep 5
echo "You can access the application at http://10.101.105.43:8501" 