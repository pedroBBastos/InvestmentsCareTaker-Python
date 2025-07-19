import argparse
import sqlite3
import matplotlib.pyplot as plt

def parse_last_prices(filepath):
    prices = {}
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith('01'):  # content line
                ticker = line[12:24].strip()
                price_str = line[108:121]
                price = int(price_str) / 100.0
                prices[ticker] = price
    return prices

def get_wallet_quantities(db_path):
    query = """
        WITH contagem AS (
            SELECT n.ticker AS ticker,
                   SUM(CASE WHEN n.operacao = 'C' THEN n.quantidade ELSE -1 * n.quantidade END) AS quantidade
            FROM negociacao n
            GROUP BY n.ticker
        )
        SELECT contagem.ticker,
               contagem.quantidade,
               s.setor,
               s.subsetor,
               s.segmento
        FROM contagem
        INNER JOIN stocks s ON s.ticker = contagem.ticker
        WHERE contagem.quantidade > 0;
    """

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    # ticker -> (quantity, setor, subsetor, segmento)
    return {
        row[0]: (row[1], row[2] or "N/D", row[3] or "N/D", row[4] or "N/D")
        for row in results
    }

def calculate_wallet_value(prices, ticker_data):
    total_value = 0.0
    values_by_ticker = {}
    values_by_structure = {}

    print(f"{'Ticker':<10} {'Quantity':<10} {'Price':<10} {'Total Value':<12} {'Structure'}")
    print("-" * 85)

    for ticker, (quantity, setor, subsetor, segmento) in ticker_data.items():
        price = prices.get(ticker)
        structure = f"{setor}/{subsetor}/{segmento}"
        if price is not None:
            value = price * quantity
            total_value += value
            values_by_ticker[ticker] = value
            values_by_structure[structure] = values_by_structure.get(structure, 0) + value
            print(f"{ticker:<10} {quantity:<10} {price:<10.2f} {value:<12.2f} {structure}")
        else:
            print(f"{ticker:<10} {quantity:<10} {'N/A':<10} {'Price not found':<12} {structure}")

    print("-" * 85)
    print(f"{'TOTAL':<50} {total_value:.2f}")

    if values_by_ticker:
        show_pie_chart(values_by_ticker, title="Wallet Distribution by Stock", filename="wallet_by_ticker.png")
    if values_by_structure:
        show_pie_chart(values_by_structure, title="Wallet Distribution by Segment", filename="wallet_by_segment.png")

def show_pie_chart(values, title, filename):
    import pandas as pd

    labels = list(values.keys())
    sizes = list(values.values())
    total = sum(sizes)
    percentages = [(v / total) * 100 for v in sizes]

    fig, ax = plt.subplots(figsize=(12, 8))

    # Draw pie chart without labels but keep wedge references
    wedges, _ = ax.pie(
        sizes,
        startangle=140,
        wedgeprops={'edgecolor': 'black'}
    )
    ax.set_title(title)
    ax.axis('equal')

    # Add legend mapping wedge color to segment name
    ax.legend(
        wedges,
        labels,
        title="Segments",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        fontsize=8
    )

    # Build table for value and percentage
    df = pd.DataFrame({
        'Segment': labels,
        'Value (R$)': [f"{v:,.2f}" for v in sizes],
        'Percentage (%)': [f"{p:.2f}%" for p in percentages]
    })

    # Create a table below the chart
    table_ax = fig.add_subplot(111, frame_on=False)
    table_ax.axis('off')

    table = plt.table(
        cellText=df.values,
        colLabels=df.columns,
        loc='bottom',
        cellLoc='center'
    )

    table.scale(1, 1.5)
    table.auto_set_font_size(False)
    table.set_fontsize(8)

    plt.subplots_adjust(left=0.05, bottom=0.3, right=0.8, top=0.9)

    plt.savefig(filename, bbox_inches='tight')
    print(f"✅ Pie chart saved to: {filename}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate wallet value from cotahist file and SQLite DB.')
    parser.add_argument('cotahist_file', help='Path to the cotahist .txt file')
    parser.add_argument('db_file', help='Path to the SQLite database file')
    args = parser.parse_args()

    prices = parse_last_prices(args.cotahist_file)
    quantities = get_wallet_quantities(args.db_file)
    calculate_wallet_value(prices, quantities)

