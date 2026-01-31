"""
Script to clear all memories from the memory system.
Deletes all embeddings and metadata, resetting the memory system to empty state.
"""

import os
from pathlib import Path

def clear_memory_system():
    """Clear all memory data files."""
    # Get memory data directory path
    memory_data_path = Path("./memory_data")
    
    # Files to delete
    files_to_delete = [
        memory_data_path / "embeddings.npy",
        memory_data_path / "metadata.json",
        memory_data_path / "config.json"
    ]
    
    # Delete each file if it exists
    deleted_count = 0
    for file_path in files_to_delete:
        if file_path.exists():
            try:
                file_path.unlink()  # Delete the file
                print(f"Deleted: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nCleared {deleted_count} file(s). Memory system is now empty.")
    print("Note: config.json will be regenerated automatically when the memory system is next used.")

if __name__ == "__main__":
    clear_memory_system()


