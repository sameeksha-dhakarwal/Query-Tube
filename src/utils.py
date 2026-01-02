import os
import pandas as pd

def ensure_dir(path):
    """Create folder if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)

def load_csv(path):
    """Load CSV safely"""
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

def save_csv(data, path):
    """Save Python list/dict to CSV"""
    df = pd.DataFrame(data)
    df.to_csv(path, index=False)
    print(f"[✓] Saved: {path}")
