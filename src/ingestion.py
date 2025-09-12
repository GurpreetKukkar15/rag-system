import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from dotenv import load_dotenv

def ingest_documents():
    """
    Ingests PDF documents, splits them into chunks, creates embeddings,
    and saves a FAISS vector store to disk.
    """
    print("Starting document ingestion process...")

    # Load environment variables from .env file
    load_dotenv()
    # Define a variable for the data directory
    DATA_DIR = os.getenv("DATA_DIR", "data")
    # Define a variable for the FAISS index path
    FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "data/faiss_index")

    # 1. Load documents from the specified directory
    documents = []
    for filename in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, filename)
        if filename.endswith(".pdf"):
            print(f"Loading PDF document: {file_path}")
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        elif filename.endswith(".txt"):
            print(f"Loading text document: {file_path}")
            loader = TextLoader(file_path, encoding='utf-8')
            documents.extend(loader.load())

    if not documents:
        print("No documents found in the data directory. Please add a PDF.")
        return

    # 2. Split the documents into smaller, manageable chunks
    print(f"Splitting {len(documents)} pages into text chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    docs = text_splitter.split_documents(documents)
    print(f"Created {len(docs)} text chunks.")

    # 3. Create a SentenceTransformer embedding model
    print("Initializing embedding model...")
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Create and save the FAISS vector store
    print("Creating FAISS vector store and saving...")
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(FAISS_INDEX_PATH)
    print(f"FAISS index saved successfully at: {FAISS_INDEX_PATH}")

if __name__ == "__main__":
    ingest_documents()
