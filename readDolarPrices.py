import pandas as pd
import sqlite3

df = pd.read_json('dolar-07-23-a-06-24.json')

df.info()
# print(df.head())
# print(df[['bid', 'timestamp']])

df['timestamp'] = df['timestamp'].dt.date
# print(df[['bid', 'timestamp']])


# Reverse the rows of the DataFrame
df_reversed = df[['bid', 'timestamp']].iloc[::-1].reset_index(drop=True)

# Display the reversed DataFrame
# print("\nReversed DataFrame:")
# print(df_reversed)

# Iterate over rows and print each one
# for index, row in df_reversed.iterrows():
#     print(row)

start_date = pd.to_datetime('2023-12-28').date()
print("start -> ", start_date)
end_date = pd.to_datetime('2024-06-30').date()
print("end -> ", end_date)

df_date_filtered = df_reversed[(df_reversed['timestamp'] > start_date) & (df_reversed['timestamp'] <= end_date)]
# print("\nDate filtered DataFrame:")
# print(df_date_filtered)

# for index, row in df_date_filtered.iterrows():
#     print(row)

# Remove rows with duplicated 'timestamp' values
df_no_duplicates = df_date_filtered.drop_duplicates(subset=['timestamp'])

print("DataFrame with duplicates removed:")
print(df_no_duplicates)

for index, row in df_no_duplicates.iterrows():
    print(row)

# try:
#     # Connect to the SQLite database (or create it if it doesn't exist)
#     conn = sqlite3.connect('myInvestments.db')
#     cursor = conn.cursor()

#     # Convert DataFrame to list of tuples
#     rows_to_insert = [tuple(x) for x in df_no_duplicates[['timestamp', 'bid']].values]

#     # Insert rows into the table
#     cursor.executemany('''
#         INSERT INTO cotacao_dolar (data, valor)
#         VALUES (?, ?)
#     ''', rows_to_insert)

#     # Commit the transaction
#     conn.commit()

# except sqlite3.Error as e:
#     print(f"An error occurred: {e}")
# finally:
#     if conn:
#         # Close the connection
#         conn.close()