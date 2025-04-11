from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import fitz  # PyMuPDF
import io
from vector_store import VectorStore
import logging
import uvicorn

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="知识库 API")

# 配置CORS - 明确指定允许的源
origins = [
    "http://10.101.105.43:8501",  # Streamlit 前端
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
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            
            content = await file.read()
            doc = fitz.open(stream=content, filetype="pdf")
            
            for page in doc:
                text = page.get_text()
                if text.strip():
                    texts.append(text)
            doc.close()
        
        if not texts:
            raise HTTPException(status_code=400, detail="No text content found in PDFs")
        
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
    # 明确指定主机地址
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