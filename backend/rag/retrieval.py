import os, faiss, sqlite3, numpy as np
from sentence_transformers import SentenceTransformer
from backend.rag.ingest import INDEX_DIR, FAISS_PATH, SQLITE_PATH, MODEL_NAME, model  # reuse constants and model from ingest to avoid duplication


def retrieve(query, top_k):

    embeddings = model.encode([query])  # convert query string into a vector - must be a list

    if os.path.exists(FAISS_PATH):
        index = faiss.read_index(FAISS_PATH)  # load existing vector index from disk
    else:
        raise FileNotFoundError('No FAISS index found - ingest document first')  # no index means no documents have been ingested

    distances, indices = index.search(np.array(embeddings, dtype='float32'), top_k)  # find top_k most similar vectors - returns positions and distances

    con = sqlite3.connect(SQLITE_PATH)  # connect to metadata database to look up chunk text
    listOfRagSnippets = []  # will hold the final results

    for idx, i in enumerate(indices[0]):  # indices[0] because search returns 2D array - we only have one query
        row = con.execute('SELECT chunk_id, doc_id, text FROM chunks WHERE rowid = ?', (int(i) + 1,)).fetchone()  # look up chunk text by its position in the index
        listOfRagSnippets.append({
            'snippet_id': row[0],       # unique id of this chunk
            'source_doc_id': row[1],    # which document this chunk came from
            'text': row[2],             # the actual chunk text
            'score': float(distances[0][idx])  # similarity score - lower means more similar in L2 distance
        })

    con.close()  # close database connection

    return listOfRagSnippets  # return list of RagSnippet dicts