import pandas as pd
import os

def load_data(file_path=None, text_data=None):
    """
    Carrega dados de uma lista de texto, arquivo CSV ou Excel.
    Retorna uma lista de números inteiros na ordem em que ocorreram.
    """
    numbers = []
    
    if text_data:
        for line in text_data.split('\n'):
            line = line.strip()
            if line.isdigit():
                numbers.append(int(line))
        return numbers
    
    if file_path and os.path.exists(file_path):
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path, header=None)
            for col in df.columns:
                if pd.to_numeric(df[col], errors='coerce').notnull().any():
                    numbers = pd.to_numeric(df[col], errors='coerce').dropna().astype(int).tolist()
                    break
        elif file_path.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path, header=None)
            for col in df.columns:
                if pd.to_numeric(df[col], errors='coerce').notnull().any():
                    numbers = pd.to_numeric(df[col], errors='coerce').dropna().astype(int).tolist()
                    break
                    
    return numbers
