import os
from typing import List
import nltk
from nltk.corpus import stopwords
import pdfplumber
import docx2txt
import html2text
import re

class TextFileLoader:
    def __init__(self, path: str, encoding: str = "utf-8"):
        self.documents = []
        self.path = path
        self.encoding = encoding

    def load(self):
        if os.path.isdir(self.path):
            self.load_directory()
        elif os.path.isfile(self.path) and self.path.endswith(".txt"):
            self.load_txt_file()
        elif os.path.isfile(self.path) and self.path.endswith(".pdf"):
            self.load_pdf_file()
        elif os.path.isfile(self.path) and self.path.endswith(".docx"):
            self.load_docx_file()
        elif os.path.isfile(self.path) and self.path.endswith(".html"):
            self.load_html_file()
        else:
            raise ValueError(
                "Provided path is neither a valid directory nor a .txt file."
            )

    def load_txt_file(self):
        with open(self.path, "r", encoding=self.encoding) as f:
            self.documents.append(f.read())

    def load_pdf_file(self):
        with pdfplumber.open(self.path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
            self.documents.append(text)

    def load_docx_file(self):
        text = docx2txt.process(self.path)
        self.documents.append(text)

    def load_html_file(self):
        with open(self.path, "r", encoding=self.encoding) as f:
            html_content = f.read()
        text = html2text.html2text(html_content)
        self.documents.append(text)

    def load_directory(self):
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".txt"):
                    with open(
                        os.path.join(root, file), "r", encoding=self.encoding
                    ) as f:
                        self.documents.append(f.read())

    def load_documents(self):
        self.load()
        return self.documents


class CharacterTextSplitter:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        assert (
            chunk_size > chunk_overlap
        ), "Chunk size must be greater than chunk overlap"

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[str]:
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunks.append(text[i : i + self.chunk_size])
        return chunks

    def split_texts(self, texts: List[str]) -> List[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks

class ParagraphTextSplitter:
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size

    def split(self, text: str) -> List[str]:
        # Split text into paragraphs at each single newline
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            # If adding this paragraph would exceed the chunk size, start a new chunk
            if current_chunk and len(current_chunk) + len(para) + 2 > self.chunk_size:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n" + para
                else:
                    current_chunk = para

        # Add any remaining text as the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def split_texts(self, texts: List[str]) -> List[str]:
        chunks = []
        for text in texts:
            chunks.extend(self.split(text))
        return chunks

class TextPreprocessor:
    def __init__(self, text: str):
        self.text = text
        self.ensure_nltk_stopwords()
        self.stopwords = set(stopwords.words('english'))

    def ensure_nltk_stopwords(self):
        try:
            # Try to access the stopwords corpus
            nltk.data.find('corpora/stopwords')
        except LookupError:
            # If not found, download it
            nltk.download('stopwords', quiet=True)
    
    def remove_stopwords(self):
        words = self.text.split()
        filtered_words = [word for word in words if word.lower() not in self.stopwords]
        return " ".join(filtered_words)


if __name__ == "__main__":
    import os
    king_lear_path = "data/KingLear.txt"
    if os.path.isfile(king_lear_path):
        loader = TextFileLoader(king_lear_path)
        loader.load()
        splitter = CharacterTextSplitter()
        chunks = splitter.split_texts(loader.documents)
        print(len(chunks))
        print(chunks[0])
        print("--------")
        print(chunks[1])
        print("--------")
        print(chunks[-2])
        print("--------")
        print(chunks[-1])

        print("\nParagraphTextSplitter test:")
        # New test: use a hardcoded multiline string with single newlines
        test_text = """This is the first line.\nThis is the second line.\n\nThis is the fourth line after an empty line.\nFifth line."""
        para_splitter = ParagraphTextSplitter(chunk_size=1000)
        para_chunks = para_splitter.split_texts([test_text])
        print(f"Input text:\n{test_text}\n")
        print(f"Number of chunks: {len(para_chunks)}")
        for i, chunk in enumerate(para_chunks):
            print(f"Chunk {i+1}: {repr(chunk)}")
            print("--------")
    else:
        print(f"File {king_lear_path} not found. Skipping splitter tests.")

    print("\nTextPreprocessor test:")
    sample_text = "This is a simple test sentence to demonstrate stopword removal."
    preprocessor = TextPreprocessor(sample_text)
    cleaned_text = preprocessor.remove_stopwords()
    print(f"Original: {sample_text}")
    print(f"After stopword removal: {cleaned_text}")
