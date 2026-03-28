import os
from pypdf import PdfReader
from docx import Document

class FileParser:
    @staticmethod
    def extract_text(file_path: str) -> str:
        _, extension = os.path.splitext(file_path)
        extension = extension.lower()

        if extension == ".pdf":
            return FileParser._extract_from_pdf(file_path)
        elif extension == ".docx":
            return FileParser._extract_from_docx(file_path)
        elif extension == ".txt":
            return FileParser._extract_from_txt(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text

    @staticmethod
    def _extract_from_docx(file_path: str) -> str:
        text = ""
        try:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX: {e}")
        return text

    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading TXT: {e}")
            return ""

    @staticmethod
    def clean_text(text: str) -> str:
        # Basic cleaning: remove extra whitespace
        return " ".join(text.split())
