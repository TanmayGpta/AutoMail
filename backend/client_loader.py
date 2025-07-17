import pandas as pd

def load_clients():
    df = pd.read_excel("data/clients.xlsx", dtype=str)
    df.fillna("", inplace=True)
    return df.to_dict(orient="records")
