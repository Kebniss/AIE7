import glob
import time
from langchain_community.document_loaders import UnstructuredPDFLoader

# Get all PDF files in the data directory
pdf_files = glob.glob("./data/*.pdf")
print(f"Found {len(pdf_files)} PDF files:")
for file in pdf_files:
    print(f"  - {file}")

# Load all PDF files with timing
all_documents = []
for pdf_file in pdf_files:
    try:
        print(f"\n{'='*60}")
        print(f"Loading {pdf_file}...")
        start_time = time.time()
        
        loader = UnstructuredPDFLoader(
            pdf_file,
            mode="elements",  # Try 'fast' mode if this is too slow
            strategy="fast"   # Use fast strategy instead of default
        )
        documents = loader.load()
        
        elapsed = time.time() - start_time
        all_documents.extend(documents)
        print(f"✓ Successfully loaded {len(documents)} documents in {elapsed:.1f} seconds")
        
    except Exception as e:
        print(f"✗ Error loading {pdf_file}: {e}")

print(f"\n{'='*60}")
print(f"Total documents loaded: {len(all_documents)}")
if all_documents:
    print(f"First document preview: {all_documents[0].page_content[:200]}...")