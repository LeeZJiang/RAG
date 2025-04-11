from lxml import etree
from typing import List, Dict
import xml.etree.ElementTree as ET
import io

class XMLProcessor:
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size

    def process_xml(self, xml_content: str) -> List[Dict]:
        """处理XML内容，生成文本块"""
        chunks = []
        doc = etree.fromstring(xml_content)
        
        def traverse(node, current_path: List[str] = None):
            if current_path is None:
                current_path = []
            
            if node.tag == "section":
                new_path = current_path + [node.get("title", "Untitled")]
                for child in node:
                    traverse(child, new_path)
            elif node.tag == "content" and node.text:
                chunk = {
                    "text": node.text,
                    "metadata": {
                        "path": " > ".join(current_path),
                        "level": len(current_path)
                    }
                }
                chunks.append(chunk)
        
        traverse(doc)
        return chunks 

def process_xml(content: bytes) -> str:
    """处理XML文件并提取文本"""
    try:
        # 解析XML内容
        root = ET.fromstring(content)
        
        # 提取所有文本内容
        texts = []
        for elem in root.iter():
            if elem.text and elem.text.strip():
                texts.append(elem.text.strip())
            if elem.tail and elem.tail.strip():
                texts.append(elem.tail.strip())
        
        return "\n".join(texts)
    except Exception as e:
        raise Exception(f"Error processing XML: {str(e)}") 