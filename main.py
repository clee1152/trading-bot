import strategies as strats
import trading_bot as tb

# Prompt user for credentials and number of stocks from the S&P 500.
credentials = open("alpacainfo.txt", "r")
line1 = credentials.readline()
line2 = credentials.readline() 
credentials.close()

if line1 == line2:
    key = input("Enter Key: ")
    secret = input("Enter Secret Key: ")
else:
    key = line1.rstrip("\n")
    secret = line2.rstrip("\n")

option = input("Enter 'CUSTOM' for Custom List of Stocks: ")

if "CUSTOM" not in option:
    number = int(input("Enter Number of S&P 500 Stocks: "))
    stocks = []
else:
    stocks = input("Enter Custom List of Stocks: ").split()
    number = len(stocks)

bp = int(input("Enter Buying Power: "))

strats.sma_crossover(key, secret, number, bp, stocks)
