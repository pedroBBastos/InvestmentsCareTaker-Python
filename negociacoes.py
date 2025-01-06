import pandas as pd
import numpy as np
import sqlite3

def convert_to_float(value):
    return float(value.replace('.', '').replace(',', '.'))

df = pd.read_csv('./data/movimentacao-07-24-a-12-24.csv')
df.info()

print(df['Movimentação'].unique())

# df_only_compras = df[(df['Movimentação'] == 'Transferência - Liquidação') & (df['Entrada/Saída'] == 'Credito')]
df_only_compras = df[df['Movimentação'] == 'Transferência - Liquidação']
# print(df_only_compras[['Entrada/Saída', 'Produto', 'Quantidade']])

df_only_compras['Entrada/Saída'] = np.where(df_only_compras['Entrada/Saída'] == 'Credito', 'C', 'V')

pattern = r'([A-Z]{4}[0-9]{1,2})'
# Extract all matches and convert to a list
# matches = df_only_compras['Produto'].str.extractall(pattern)
# matches_list = matches[0].tolist()
# print(matches)

df_only_compras['Produto'] = df_only_compras['Produto'].str.extract(pattern, expand=False)
# print(df_only_compras[['Entrada/Saída', 'Produto', 'Quantidade', 'Data']])

df_only_compras['Data'] = pd.to_datetime(df_only_compras['Data'], format='%d/%m/%Y').dt.date
# print(df_only_compras[['Entrada/Saída', 'Produto', 'Quantidade', 'Data', 'Preço unitário', 'Valor da Operação']])

# Tratar os campos de preço unitario e valor da operação para serem floats
pattern = r'(([0-9]+\.+)*[0-9]+\,[0-9]{2})'
# extracted = df_only_compras['Preço unitário'].str.extract(pattern, expand=False)
# extracted2 = df_only_compras['Valor da Operação'].str.extract(pattern, expand=False)
# print(extracted[0])
# print(extracted2[0])
df_only_compras['Preço unitário'] = df_only_compras['Preço unitário'].str.extract(pattern, expand=False)[0]
df_only_compras['Valor da Operação'] = df_only_compras['Valor da Operação'].str.extract(pattern, expand=False)[0]

df_only_compras['Preço unitário'] = df_only_compras['Preço unitário'].apply(convert_to_float)
df_only_compras['Valor da Operação'] = df_only_compras['Valor da Operação'].apply(convert_to_float)

df_only_compras['Preço unitário'] = pd.to_numeric(df_only_compras['Preço unitário'], errors='coerce')
df_only_compras['Valor da Operação'] = pd.to_numeric(df_only_compras['Valor da Operação'], errors='coerce')

print(df_only_compras[['Entrada/Saída', 'Produto', 'Quantidade', 'Data', 'Preço unitário', 'Valor da Operação']])

try:
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('myInvestments.db')
    cursor = conn.cursor()

    # Convert DataFrame to list of tuples
    rows_to_insert = [tuple(x) for x in df_only_compras[['Data', 'Entrada/Saída', 'Preço unitário', 'Quantidade', 'Produto', 'Valor da Operação']].values]

    # Insert rows into the table
    cursor.executemany('''
        INSERT INTO negociacao (date, operacao, preco_unitario, quantidade, ticker, valor_total)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', rows_to_insert)

    # Commit the transaction
    conn.commit()

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        # Close the connection
        conn.close()