import streamlit as st
import requests
import json
import time
import logging
from urllib.parse import urljoin
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('frontend.log')
    ]
)
logger = logging.getLogger(__name__)

# 设置页面配置
try:
    st.set_page_config(
        page_title="企业知识库",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception as e:
    logger.error(f"Failed to set page config: {e}")

# 设置后端API地址
BACKEND_URL = "http://10.101.105.43:9081"

def check_backend_health():
    """检查后端服务健康状态"""
    try:
        response = requests.get(urljoin(BACKEND_URL, "health"), timeout=5)
        if response.status_code == 200:
            logger.info("Backend service is healthy")
            return True
        else:
            logger.error(f"Backend health check failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Backend health check failed: {e}")
        return False

# 添加标题
st.title("企业知识库系统")

# 检查后端服务状态
backend_status = check_backend_health()
if backend_status:
    st.success("系统状态: 正常运行")
else:
    st.error("系统状态: 后端服务异常")
    st.stop()

# 文件上传部分
st.header("上传PDF文件")
uploaded_files = st.file_uploader("选择PDF文件", type="pdf", accept_multiple_files=True)

if uploaded_files:
    if st.button("上传"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            files = []
            for file in uploaded_files:
                logger.info(f"Processing file: {file.name}")
                files.append(("files", (file.name, file, "application/pdf")))
            
            status_text.text("正在上传文件...")
            progress_bar.progress(30)
            
            logger.info("Sending files to backend")
            response = requests.post(
                urljoin(BACKEND_URL, "upload/"),
                files=files,
                timeout=30
            )
            progress_bar.progress(70)
            
            if response.status_code == 200:
                logger.info("Files uploaded successfully")
                progress_bar.progress(100)
                st.success("文件上传成功！")
                status_text.text("处理完成！")
            else:
                logger.error(f"Upload failed with status code {response.status_code}: {response.text}")
                st.error(f"上传失败: {response.text}")
                status_text.text("上传失败")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            st.error("无法连接到后端服务，请确保后端服务正在运行")
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            st.error("请求超时，请稍后重试")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            st.error(f"发生错误: {str(e)}")
        finally:
            progress_bar.empty()

# 搜索部分
st.header("搜索知识库")
query = st.text_input("输入搜索关键词")

if st.button("搜索"):
    if not query:
        st.warning("请输入搜索关键词")
    else:
        try:
            with st.spinner("正在搜索..."):
                logger.info(f"Searching for query: {query}")
                response = requests.post(
                    urljoin(BACKEND_URL, "search/"),
                    json={"query": query},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    results = response.json()["results"]
                    logger.info(f"Found {len(results)} results")
                    if results:
                        for i, result in enumerate(results):
                            score = 1 - result['score']  # 转换为相似度分数
                            with st.expander(f"结果 {i+1} (相似度: {score:.2%})"):
                                st.write(result["text"])
                    else:
                        st.info("没有找到相关结果")
                else:
                    logger.error(f"Search failed with status code {response.status_code}: {response.text}")
                    st.error(f"搜索失败: {response.text}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            st.error("无法连接到后端服务，请确保后端服务正在运行")
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            st.error("请求超时，请稍后重试")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            st.error(f"发生错误: {str(e)}")

# 添加页脚
st.markdown("---")
st.markdown("### 使用说明")
st.markdown("""
1. 上传PDF文件：支持单个或多个PDF文件上传
2. 搜索知识库：输入关键词，系统会返回最相关的内容
3. 相似度分数：越高表示越相关
""") 