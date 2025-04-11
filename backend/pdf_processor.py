import fitz  # PyMuPDF
from lxml import etree

class PDFProcessor:
    def __init__(self):
        self.title_threshold = 20  # 字体大小阈值，用于判断标题

    def process_pdf(self, pdf_path):
        """处理PDF文件，提取文本和结构"""
        doc = fitz.open(pdf_path)
        root = etree.Element("document")
        current_section = root

        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if not text:
                                continue

                            # 根据字体大小判断是否为标题
                            if span["size"] > self.title_threshold:
                                current_section = etree.SubElement(
                                    root, 
                                    "section",
                                    title=text,
                                    level="1"
                                )
                            else:
                                if current_section is root:
                                    # 如果没有标题，创建默认section
                                    current_section = etree.SubElement(
                                        root,
                                        "section",
                                        title="Untitled",
                                        level="0"
                                    )
                                etree.SubElement(current_section, "content").text = text

        return etree.tostring(root, pretty_print=True, encoding="unicode")

    def save_xml(self, xml_content, output_path):
        """保存XML内容到文件"""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_content) 