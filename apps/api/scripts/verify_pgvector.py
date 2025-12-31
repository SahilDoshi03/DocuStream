import sys
import os

# Add parent dir to path to import app modules
# apps/api/scripts -> apps/api
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import engine, init_db
from sqlalchemy import text
from services.vector_store import vector_store

def verify():
    print("Initializing DB...")
    try:
        init_db()
    except Exception as e:
        print(f"init_db failed: {e}")
        print("Ensure Postgres is running: docker-compose up -d")
        return

    # 1. Check Extension
    print("Checking pgvector extension...")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM pg_extension WHERE extname = 'vector'"))
        if result.rowcount > 0:
            print("✅ pgvector extension is installed.")
        else:
            print("❌ pgvector extension MISSING!")
            return

    # 2. Add Document
    print("Adding test document...")
    doc = {"text": "This is a test document for pgvector.", "metadata": {"source": "test"}}
    try:
        vector_store.add_documents([doc])
        print("✅ Document added.")
    except Exception as e:
        print(f"❌ Failed to add document: {e}")
        return

    # 3. Search
    print("Searching...")
    query = "test document"
    results = vector_store.search(query, k=1)
    
    if results:
        print(f"Found {len(results)} results.")
        top_result = results[0]
        # Allow fuzzy match or exact match
        if "test document" in top_result['text']:
            print("✅ Search successful.")
            print(f"Result: {top_result}")
        else:
            print("⚠️ Search result content mismatch (might be expected for embeddings).")
            print(f"Result: {top_result}")
    else:
        print("❌ Search returned no results.")

if __name__ == "__main__":
    verify()
