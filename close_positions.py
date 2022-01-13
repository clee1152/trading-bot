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

bot = tb.PaperTradingBot(key, secret)
bot.close_positions()
