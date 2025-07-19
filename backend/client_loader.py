# In backend/client_loader.py
from pathlib import Path
import pandas as pd

def load_clients():
    # Path now points to backend/data/clients.xlsx
    excel_path = Path(__file__).parent / "data" / "clients.xlsx"
    df = pd.read_excel(excel_path, dtype=str)
    return df.to_dict("records")