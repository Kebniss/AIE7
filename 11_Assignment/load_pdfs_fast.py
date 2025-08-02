import glob
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Get all PDF files in the data directory
pdf_files = glob.glob("./data/*.pdf")
print(f"Found {len(pdf_files)} PDF files:")
for file in pdf_files:
    print(f"  - {file}")

# Load all PDF files with PyPDF (much faster!)
all_documents = []
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

for pdf_file in pdf_files:
    try:
        print(f"\n{'='*60}")
        print(f"Loading {pdf_file}...")
        start_time = time.time()
        
        # PyPDFLoader is MUCH faster than UnstructuredPDFLoader
        loader = PyPDFLoader(pdf_file)
        pages = loader.load()
        
        # Split into smaller chunks
        documents = text_splitter.split_documents(pages)
        
        elapsed = time.time() - start_time
        all_documents.extend(documents)
        print(f"✓ Successfully loaded {len(pages)} pages → {len(documents)} chunks in {elapsed:.1f} seconds")
        
    except Exception as e:
        print(f"✗ Error loading {pdf_file}: {e}")

print(f"\n{'='*60}")
print(f"Total documents loaded: {len(all_documents)}")
if all_documents:
    print(f"First document preview: {all_documents[0].page_content[:200]}...")