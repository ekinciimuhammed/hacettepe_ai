import sys
import os
import argparse
from pipeline.vector_store import get_db_connection, delete_document_by_source, is_file_indexed
from main import process_file

def list_documents():
    db = get_db_connection()
    if "vectors" not in db.table_names():
        print("No 'vectors' table found.")
        return

    table = db.open_table("vectors")
    # LanceDB doesn't have a distinct query easily yet in all versions
    # But we can iterate. Ideally we query distinct sources.
    # For now, let's fetch unique sources via pyarrow/pandas if dataset is small
    # or just show count.
    
    # Efficient way:
    try:
        df = table.to_pandas()
        if df.empty:
            print("Database is empty.")
            return
            
        sources = df['source'].unique()
        print(f"Indexed Documents ({len(sources)}):")
        for s in sources:
            count = len(df[df['source'] == s])
            print(f"- {s} ({count} chunks)")
    except Exception as e:
        print(f"Error listing documents: {e}")

def add_document(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
        
    filename = os.path.basename(file_path)
    if is_file_indexed(filename):
        print(f"Warning: {filename} is already indexed.")
        choice = input("Do you want to delete and re-index it? (y/n): ")
        if choice.lower() == 'y':
            delete_document_by_source(filename)
            print(f"Deleted old entries for {filename}")
        else:
            print("Skipping.")
            return

    print(f"Processing {file_path}...")
    process_file(file_path)
    print("Done.")

def delete_document(filename):
    if not is_file_indexed(filename):
        print(f"File {filename} is NOT in the index.")
        return

    check = input(f"Are you sure you want to delete all vectors for '{filename}'? (y/n): ")
    if check.lower() == 'y':
        success = delete_document_by_source(filename)
        if success:
            print(f"Successfully deleted {filename}.")
        else:
            print("Failed to delete.")
    else:
        print("Cancelled.")

def main():
    parser = argparse.ArgumentParser(description="Manage LanceDB Vector Database")
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # List
    parser_list = subparsers.add_parser("list", help="List all indexed documents")
    
    # Add
    parser_add = subparsers.add_parser("add", help="Add a specific PDF file")
    parser_add.add_argument("path", help="Path to the PDF file")
    
    # Delete
    parser_delete = subparsers.add_parser("delete", help="Delete a document by filename")
    parser_delete.add_argument("filename", help="Filename (e.g., document.pdf)")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_documents()
    elif args.command == "add":
        add_document(args.path)
    elif args.command == "delete":
        delete_document(args.filename)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
