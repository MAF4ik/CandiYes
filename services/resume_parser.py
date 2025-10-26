import PyPDF2
from docx import Document
from typing import Optional

class ResumeParser:
    """Парсер резюме из различных форматов"""
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Извлечение текста из PDF файла"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return "Не удалось прочитать PDF файл"
    
    def extract_text_from_docx(self, docx_file) -> str:
        """Извлечение текста из DOCX файла"""
        try:
            doc = Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error reading DOCX: {e}")
            return "Не удалось прочитать DOCX файл"