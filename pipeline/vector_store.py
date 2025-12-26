import lancedb
import pyarrow as pa
from config import LANCEDB_URI

def get_db_connection():
    return lancedb.connect(LANCEDB_URI)

def create_table_if_not_exists(table_name="vectors"):
    db = get_db_connection()
    
    # Define Schema
    # id: string, text: string, embedding: vector, source: string, metadata: string (json string)
    # LanceDB infers vector size from data, but we can be explicit if needed.
    # For simplicity, we'll let it auto-create on first add OR define minimal schema.
    # But usually, it's better to pass a list of dicts and let LanceDB infer.
    
    # We will just verify connection here. Table creation happens on 'add'.
    return db

def add_documents(documents, table_name="vectors", vector_dim=1024):
    """
    documents: list of dicts 
    [
        {"id": "...", "text": "...", "embedding": [...], "source": "...", "metadata": {...}}
    ]
    """
    if not documents:
        return

    db = get_db_connection()
    if table_name in db.table_names():
        table = db.open_table(table_name)
        table.add(documents)
    else:
        # Table doesn't exist, create it
        db.create_table(table_name, data=documents)

def search_vectors(query_embedding, table_name="vectors", limit=5):
    """
    Search for similar vectors using cosine distance.
    Cosine distance range: 0-2 (0 = identical, 2 = opposite)
    """
    db = get_db_connection()
    try:
        table = db.open_table(table_name)
        # CRITICAL FIX: Use cosine metric for normalized distances
        # L2 distance can be very large for non-normalized vectors
        results = table.search(query_embedding).metric("cosine").limit(limit).to_list()
        return results
    except Exception as e:
        print(f"Error searching vectors: {e}")
        return []

def is_file_indexed(filename, table_name="vectors"):
    db = get_db_connection()
    if table_name not in db.table_names():
        return False
    
    try:
        table = db.open_table(table_name)
        # Assuming we can filter or search.
        # LanceDB SQL-like filter: "source = 'filename'"
        results = table.search().where(f"source = '{filename}'").limit(1).to_list()
        return len(results) > 0
    except Exception as e:
        print(f"Error checking index for {filename}: {e}")
        return False

def delete_document_by_source(filename, table_name="vectors"):
    db = get_db_connection()
    if table_name not in db.table_names():
        return False
    
    try:
        table = db.open_table(table_name)
        table.delete(f"source = '{filename}'")
        return True
    except Exception as e:
        print(f"Error deleting document {filename}: {e}")
        return False
