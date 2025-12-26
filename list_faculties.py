"""
Script to list all unique faculty entities found in the database.
"""

import lancedb
import json

def list_faculties():
    try:
        # Connect to database
        db = lancedb.connect("lancedb_data")
        table = db.open_table("vectors")
        
        # Get all data
        df = table.to_pandas()
        
        all_faculties = set()
        
        print(f"Scanning {len(df)} chunks for faculty entities...\n")
        
        for _, row in df.iterrows():
            metadata_str = row.get('metadata', '{}')
            if not metadata_str:
                continue
                
            try:
                metadata = json.loads(metadata_str)
                # Check for 'faculties' key
                if 'faculties' in metadata and metadata['faculties']:
                    for faculty in metadata['faculties']:
                        all_faculties.add(faculty)
            except json.JSONDecodeError:
                continue
        
        if not all_faculties:
            print("No faculty entities found in the database.")
        else:
            print(f"Found {len(all_faculties)} unique faculties:\n")
            for i, faculty in enumerate(sorted(all_faculties), 1):
                print(f"{i}. {faculty}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_faculties()
