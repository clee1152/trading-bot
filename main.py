import strategies as strats
import trading_bot as tb

# Prompt user for credentials and number of stocks from the S&P 500.
key = input("Enter Key: ")
secret = input("Enter Secret Key: ")
number = int(input("Enter Number of Stocks: "))
bp = int(input("Enter Buying Power: "))

strats.sma_crossover(key, secret, number, bp)