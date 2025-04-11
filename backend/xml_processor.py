from lxml import etree
from typing import List, Dict

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