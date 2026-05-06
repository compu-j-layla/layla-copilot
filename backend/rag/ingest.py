from pypdf import PdfReader  # PDF parsing library
from sentence_transformers import SentenceTransformer  # loads the embedding model
import faiss, sqlite3, os, uuid  # vector store, metadata db, file paths, unique IDs
import numpy as np  # FAISS requires numpy arrays

CHUNK_SIZE = 600  # max characters per chunk
CHUNK_OVERLAP = 120  # characters shared between adjacent chunks to avoid cutting sentences
MODEL_NAME = 'BAAI/bge-small-en-v1.5'  # embedding model - small, fast, no cloud needed
INDEX_DIR = os.path.join(os.path.dirname(__file__), 'index')  # path to index folder relative to this file
FAISS_PATH = os.path.join(INDEX_DIR, 'faiss.index')  # where FAISS vector index is saved on disk
SQLITE_PATH = os.path.join(INDEX_DIR, 'metadata.db')  # where chunk metadata is saved on disk

model = SentenceTransformer(MODEL_NAME)  # load embedding model once at startup, not on every call

def load_text(source_type, source_path):

    if source_type == 'pdf':
        pages = []
        reader = PdfReader(source_path)  # open the PDF

        for page in reader.pages:
            pages.append(page.extract_text() or '')  # extract text from each page, default to empty string if None
        text = '\n'.join(pages)  # combine all pages into one string


    elif source_type == 'text':
        with open(source_path, 'r') as f:
            text = f.read()  # read plain text file directly


    else:
        raise ValueError('Filetype not pdf/text')  # reject unsupported file types
    
    return text

def chunk_text(text):

    chunks = []
    start = 0

    while start < len(text):
        chunks.append(text[start : start + CHUNK_SIZE])  # slice a chunk of CHUNK_SIZE characters
        start += CHUNK_SIZE - CHUNK_OVERLAP  # advance by 480 chars, keeping 120 char overlap with next chunk
    
    return chunks

def ingest_document(doc_id, source_type, source_path, tags):

    os.makedirs(INDEX_DIR, exist_ok=True)  # create index directory if it doesn't exist

    text = load_text(source_type, source_path)  # parse document into raw text
    chunks = chunk_text(text)  # split text into overlapping chunks
    embeddings = model.encode(chunks)  # convert chunks into semantic vectors

    # load existing FAISS index or create a new one
    if os.path.exists(FAISS_PATH):
        index = faiss.read_index(FAISS_PATH)
        
    else:
        index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 = straight line distance between vectors

    index.add(np.array(embeddings, dtype='float32'))  # add new vectors to the index
    faiss.write_index(index, FAISS_PATH)  # save index to disk

    con = sqlite3.connect(SQLITE_PATH)  # connect to metadata database
    con.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT NOT NULL PRIMARY KEY,
            doc_id TEXT NOT NULL,
            text TEXT,
            position INT NOT NULL  
        )                
    ''')  # create chunks table if it doesn't already exist

    for position, chunk in enumerate(chunks):  # loop through chunks with their position index
        chunk_id = str(uuid.uuid4())  # generate unique ID for this chunk
        con.execute('INSERT INTO chunks VALUES (?, ?, ?, ?)', (chunk_id, doc_id, chunk, position))  # store metadata

    con.commit()  # save all inserts to disk
    con.close()  # close database connection

    return {'doc_id': doc_id, 'chunks_indexed': len(chunks), 'index_version': '1.0'}  # confirm ingestion result