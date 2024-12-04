import pandas as pd
from collections import deque
import math

def process_stocks(file_path, taxPeriodEnd):
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Ensure 'Date' column is in datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Sort the dataframe by Ticker and Date
    df_sorted = df.sort_values(by=['Ticker', 'Date'])

    # Filter the dataframe to only include rows before the date limit
    df_filtered = df_sorted[df_sorted['Date'] <= pd.to_datetime(taxPeriodEnd)]

    return df_filtered

def singleStockPrice(transaction):
    return abs(transaction["Spent"] / transaction["Amount"])

def calculateStats(q):
    spent = 0
    amount = 0
    for record in q:
        spent += record["Spent"]
        amount += record["Amount"]
    return (amount, (spent/amount) if amount > 0  else 0)
    # if len(q):
    #     print(f'Ticker {q[0]["Ticker"]} amount {amount} average stock price {(spent/amount):.2f}')

def calculate_tax_single_stock(stockData):
    totalTaxBase = 0
    q = deque()
    for i in range(len(stockData)):
        transaction = stockData.iloc[i].copy()
        if transaction["Transaction"] == "BUY":
            q.append(transaction)
        elif transaction["Transaction"] == "SELL":
            stocks2Sell = abs(transaction["Amount"])
            taxBase = 0
            while(stocks2Sell > 0):
                if q[0]["Amount"] > stocks2Sell:
                    taxBase += stocks2Sell*singleStockPrice(transaction) - stocks2Sell*singleStockPrice(q[0])
                    q[0]["Spent"] -= min(stocks2Sell*singleStockPrice(q[0]), stocks2Sell*singleStockPrice(transaction))
                    q[0]["Amount"] -= stocks2Sell
                    break
                else:
                    taxBase += singleStockPrice(transaction)*q[0]["Amount"] - q[0]["Spent"]
                    stocks2Sell -= q[0]["Amount"]
                    q.popleft()
            if transaction['Date'] >= pd.to_datetime(taxPeriodStart):
                # print(f"ticker {stockData.iloc[0]['Ticker']} taxBase {taxBase}")
                totalTaxBase += taxBase
        elif transaction["Transaction"] == "SPLIT":
            # print(f'Split {stockData.iloc[0]["Ticker"]} coefficient {transaction["Amount"]}')
            for record in q:
                record["Amount"] *= transaction["Amount"]
    # printBalance(q)    
    return calculateStats(q) + (totalTaxBase,)
        

# Example usage
file_path = 'stocks (2).xlsx'
taxYear = 2024
taxPeriodStart = f"{taxYear}-01-01"
taxPeriodEnd = f"{taxYear}-12-31"

if __name__ == "__main__":
    totalTaxBase = 0
    sorted_and_filtered_data = process_stocks(file_path, taxPeriodEnd)
    for ticker in sorted_and_filtered_data['Ticker'].unique():
        amount, avgPrice, taxBase = calculate_tax_single_stock(sorted_and_filtered_data[sorted_and_filtered_data['Ticker'] == ticker])
        if taxBase != 0:
            print(f"Ticker {ticker}, taxBase {taxBase}")
        # print(sorted_and_filtered_data[sorted_and_filtered_data['Ticker'] == ticker])
        # print(f"Ticker {ticker} left {amount} avgPrice {avgPrice:.2f} earned {taxBase}")

        totalTaxBase += taxBase
    print(f"Total tax base in {taxYear} is {totalTaxBase}")

