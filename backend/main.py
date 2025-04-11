from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import fitz  # PyMuPDF
import pandas as pd
import docx
import markdown
import xml.etree.ElementTree as ET
from PIL import Image
import pytesseract
import io
import logging
import uvicorn
from vector_store import VectorStore
from pdf_processor import process_pdf
from xml_processor import process_xml

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="知识库 API")

# 配置CORS
origins = [
    "http://10.101.105.43:8501",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 定义请求模型
class SearchQuery(BaseModel):
    query: str

# 初始化向量存储
try:
    vector_store = VectorStore()
    logger.info("Vector store initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize vector store: {e}")
    vector_store = None

def process_excel(content: bytes) -> str:
    """处理Excel文件"""
    df = pd.read_excel(io.BytesIO(content))
    return df.to_string()

def process_word(content: bytes) -> str:
    """处理Word文档"""
    doc = docx.Document(io.BytesIO(content))
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def process_markdown(content: bytes) -> str:
    """处理Markdown文件"""
    return markdown.markdown(content.decode('utf-8'))

def process_image(content: bytes) -> str:
    """处理图片文件"""
    image = Image.open(io.BytesIO(content))
    return pytesseract.image_to_string(image)

def process_csv(content: bytes) -> str:
    """处理CSV文件"""
    df = pd.read_csv(io.BytesIO(content))
    return df.to_string()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@app.get("/")
async def root():
    return {"message": "Knowledge Base API is running"}

@app.get("/health")
async def health_check():
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    return {"status": "ok"}

@app.post("/upload/")
async def upload_files(files: list[UploadFile] = File(...)):
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        texts = []
        for file in files:
            content = await file.read()
            file_extension = file.filename.split('.')[-1].lower()
            
            # 根据文件类型选择处理方式
            if file_extension == 'pdf':
                text = process_pdf(content)
            elif file_extension in ['xlsx', 'xls']:
                text = process_excel(content)
            elif file_extension in ['docx', 'doc']:
                text = process_word(content)
            elif file_extension == 'md':
                text = process_markdown(content)
            elif file_extension in ['xml']:
                text = process_xml(content)
            elif file_extension in ['jpg', 'jpeg', 'png', 'bmp']:
                text = process_image(content)
            elif file_extension == 'csv':
                text = process_csv(content)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
            
            if text.strip():
                texts.append(text)
        
        if not texts:
            raise HTTPException(status_code=400, detail="No text content found in files")
        
        vector_store.add_documents(texts)
        return {"message": f"Successfully processed {len(texts)} text chunks"}
    
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/")
async def search(query: SearchQuery):
    if vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store not initialized")
    
    try:
        logger.info(f"Searching for query: {query.query}")
        results = vector_store.search(query.query)
        return {"results": results}
    except Exception as e:
        logger.error(f"Error searching: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    host = "10.101.105.43"
    port = 9081
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(
        "main:app", 
        host=host, 
        port=port, 
        reload=True,
        access_log=True
    ) 