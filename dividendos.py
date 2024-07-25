import pandas as pd
import numpy as np
import sqlite3

def convert_to_float(value):
    return float(value.replace('.', '').replace(',', '.'))

df = pd.read_csv('movimentacao-07-23-a-06-24.csv')
df.info()

print(df['Movimentação'].unique())

df = df.iloc[::-1].reset_index(drop=True)

#'Juros Sobre Capital Próprio' 'Rendimento' 'Dividendo'
df_only_dividends = df[df['Movimentação'].isin(['Juros Sobre Capital Próprio', 'Rendimento', 'Dividendo'])]
# print(df_only_dividends[['Entrada/Saída', 'Produto', 'Quantidade', 'Data', 'Preço unitário', 'Valor da Operação']])

df_only_dividends['Data'] = pd.to_datetime(df_only_dividends['Data'], format='%d/%m/%Y').dt.date
start_date = pd.to_datetime('2023-12-28').date()
print("start -> ", start_date)
end_date = pd.to_datetime('2024-06-30').date()
print("end -> ", end_date)

df_only_dividends = df_only_dividends[(df_only_dividends['Data'] > start_date) & (df_only_dividends['Data'] <= end_date)]


pattern = r'([A-Z]{4}[0-9]{1,2})'
df_only_dividends['Produto'] = df_only_dividends['Produto'].str.extract(pattern, expand=False)

pattern = r'(([0-9]+\.+)*[0-9]+\,[0-9]{2})'
df_only_dividends['Preço unitário'] = df_only_dividends['Preço unitário'].str.extract(pattern, expand=False)[0]
df_only_dividends['Valor da Operação'] = df_only_dividends['Valor da Operação'].str.extract(pattern, expand=False)[0]

df_only_dividends['Preço unitário'] = df_only_dividends['Preço unitário'].apply(convert_to_float)
df_only_dividends['Valor da Operação'] = df_only_dividends['Valor da Operação'].apply(convert_to_float)

df_only_dividends['Preço unitário'] = pd.to_numeric(df_only_dividends['Preço unitário'], errors='coerce')
df_only_dividends['Valor da Operação'] = pd.to_numeric(df_only_dividends['Valor da Operação'], errors='coerce')

print(df_only_dividends[['Entrada/Saída', 'Produto', 'Quantidade', 'Data', 'Preço unitário', 'Valor da Operação']])

try:
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('myInvestments.db')
    cursor = conn.cursor()

    # Convert DataFrame to list of tuples
    rows_to_insert = [tuple(x) for x in df_only_dividends[['Data', 'Data', 'Valor da Operação', 'Produto']].values]

    # Insert rows into the table
    cursor.executemany('''
        INSERT INTO dividendo (data_liquidacao, data_movimentacao, lancamento, ticker)
        VALUES (?, ?, ?, ?)
    ''', rows_to_insert)

    # Commit the transaction
    conn.commit()

except sqlite3.Error as e:
    print(f"An error occurred: {e}")
finally:
    if conn:
        # Close the connection
        conn.close()