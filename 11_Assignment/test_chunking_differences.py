import glob
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Test with the smallest PDF
test_file = "./data/foonf_2024_manual_US_EN_02_27_2024_WEB_Final.pdf"

print("=== UnstructuredPDFLoader (Elements Mode) ===")
try:
    unstructured_loader = UnstructuredPDFLoader(
        test_file,
        mode="elements",  # Default mode
        strategy="fast"
    )
    # Note: This would be very slow, so we'll just show the concept
    print("Would extract semantic elements like:")
    print("- Document(page_content='Safety Warning', metadata={'category': 'Title'})")
    print("- Document(page_content='Always secure...', metadata={'category': 'NarrativeText'})")
    print("- Document(page_content='Table: Weight Limits', metadata={'category': 'Table'})")
except:
    pass

print("\n=== PyPDFLoader (Raw Pages) ===")
pypdf_loader = PyPDFLoader(test_file)
pages = pypdf_loader.load()
print(f"Loaded {len(pages)} pages")
print(f"Page 1 preview: {pages[0].page_content[:200]}...")
print(f"Page 1 length: {len(pages[0].page_content)} characters")

print("\n=== After Text Splitting ===")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", "!", "?", " ", ""]
)
chunks = text_splitter.split_documents(pages[:5])  # Just first 5 pages
print(f"5 pages → {len(chunks)} chunks")
print(f"Chunk 1: {chunks[0].page_content[:100]}...")
print(f"Chunk 2: {chunks[1].page_content[:100]}...")

# Show metadata differences
print("\n=== Metadata Comparison ===")
print("PyPDFLoader metadata:", pages[0].metadata)
print("After splitting metadata:", chunks[0].metadata)