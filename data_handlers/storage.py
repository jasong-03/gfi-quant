import json
import os
from datetime import datetime
from pathlib import Path
from config import DATA_DIR

def ensure_directory(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def save_json(data, source, chain, address, endpoint_name):
    """
    Save raw API response to JSON file
    Format: data/{source}/{chain}/{contract_address}/{endpoint_name}_{timestamp}.json
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    directory = Path(DATA_DIR) / source / chain / address
    ensure_directory(directory)
    
    filename = f"{endpoint_name}_{timestamp}.json"
    filepath = directory / filename
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)
        
    return str(filepath)

def load_latest_json(source, chain, address, endpoint_name):
    """
    Load the most recent JSON file for a given endpoint
    """
    directory = Path(DATA_DIR) / source / chain / address
    if not directory.exists():
        return None
        
    # Find all files matching the pattern
    files = list(directory.glob(f"{endpoint_name}_*.json"))
    if not files:
        return None
        
    # Sort by name (which includes timestamp) and get last
    latest_file = sorted(files)[-1]
    
    with open(latest_file, 'r') as f:
        return json.load(f)
