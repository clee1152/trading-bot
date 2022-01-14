import trading_bot as tb
import numpy as np
import datetime as dt
import pandas as pd
import talib as ta

'''
This method algorithmically trades according to
the SMA Crossover strategy. 

Parameters:
key     --> Alpaca API Key
secret  --> Alpaca Secret Key
number  --> Number of Stocks
bp      --> Buying Power
stocks  --> List of Stocks
ssma    --> Short SMA
lsma    --> Long SMA
'''
def sma_crossover(key, secret, number, bp=0, stocks=[], ssma=10, lsma=20):

    # Get the percent of the portfolio each stock takes up.
    if not stocks:
        percent = float(1 / number)
    else:
        percent = float(1 / len(stocks))
    pc_bp = percent * bp

    # Initialize the trading bot.
    bot = tb.PaperTradingBot(key, secret, number, stocks)
    bot.cancel_orders()
    tickers = bot.symbols

    # Gather the quotes from the last 20 dates and
    # calculate 10-day and 20-day SMA.
    for i in range(len(tickers)):
        data = bot.api.get_barset(tickers[i], 'day', limit=lsma).df

        data['sma'] = data.iloc[:,3].rolling(window=ssma, min_periods=1).mean()
        data['lma'] = data.iloc[:,3].rolling(window=lsma, min_periods=1).mean()

        data['cross'] = 0.0
        data['cross'] = np.where(data['sma'] > data['lma'], 1.0, 0.0)

        # If SMA > LMA, we buy shares. Otherwise, we sell shares.
        if data[('cross','')][len(data.index) - 1] == 1:
            num_bought = int(pc_bp / bot.last_prices[i])
            bp -= num_bought * bot.last_prices[i]
            bot.submit_order(i, num_bought)
        else:
            bp += bot.positions[i] * bot.last_prices[i]
            bot.submit_order(i, bot.positions[i])

    # Print out the new buying power and append it to a text file.
    print(f"New Buying Power: ${bp:.2f}")
    textfile = open("buying_power.txt", "a")
    textfile.write(str(dt.datetime.today().date()) + " | New Buying Power: " + str(round(bp, 2)) + "\n")
    textfile.close()

'''
This method algorithmically trades according to
the Capital Asset Pricing Model.

Parameters:
key     --> Alpaca API Key
secret  --> Alpaca Secret Key
number  --> Number of Stocks
bp      --> Buying Power
stocks  --> List of Stocks
rfrate  --> Risk-Free Rate
erm     --> Expected Return of Market
'''
def capm(key, secret, number, bp=0, stocks=[], rfrate=0.0012, erm=0.10):

    # Get the percent of the portfolio each stock takes up.
    if not stocks:
        percent = float(1 / number)
    else:
        percent = float(1 / len(stocks))
    pc_bp = percent * bp

    # Initialize the trading bot.
    bot = tb.PaperTradingBot(key, secret, number, stocks)
    bot.cancel_orders()
    tickers = bot.symbols

    # Get the prices for VOO.
    voo_barset = bot.api.get_barset("VOO", 'day', limit=1000).df
    voo_prices = voo_barset.iloc[:,3]

    # Get the prices for each ticker.
    for i in range(len(tickers)):

        # Find beta for the stock.
        indiv_barset = bot.api.get_barset(tickers[i], 'day', limit=1000).df
        indiv_prices = indiv_barset.iloc[:,3]
        prices = pd.concat([voo_prices, indiv_prices], axis=1)
        prices = (prices/prices.shift(1) - 1.0)[1:]
        cum_prices = (prices + 1.0).cumprod()
        cov = cum_prices.cov()
        beta = abs(cov.iloc[0][1] / cov.iloc[0][0])

        # Calculate capital asset expected return.
        eri = rfrate + beta * (erm - rfrate)

        # If eri is negative we buy. Otherwise, we sell.
        if eri > 0:
            num_bought = int(pc_bp / bot.last_prices[i])
            bp -= num_bought * bot.last_prices[i]
            bot.submit_order(i, num_bought)
        else:
            bp += bot.positions[i] * bot.last_prices[i]
            bot.submit_order(i, bot.positions[i])

    # Print out the new buying power and append it to a text file.
    print(f"New Buying Power: ${bp:.2f}")
    textfile = open("buying_power.txt", "a")
    textfile.write(str(dt.datetime.today().date()) + " | New Buying Power: " + str(round(bp, 2)) + "\n")
    textfile.close()

'''
This method algorithmically trades according to
the RSI strategy. 

Parameters:
key       --> Alpaca API Key
secret    --> Alpaca Secret Key
number    --> Number of Stocks
bp        --> Buying Power
stocks    --> List of Stocks
threshold --> Threshold for over-bought/sold stocks
ema       --> Exponential Moving Average
'''
def rsi(key, secret, number, bp=0, stocks=[], threshold=30, ema=20):

    # Get the percent of the portfolio each stock takes up.
    if not stocks:
        percent = float(1 / number)
    else:
        percent = float(1 / len(stocks))
    pc_bp = percent * bp

    # Initialize the trading bot.
    bot = tb.PaperTradingBot(key, secret, number, stocks)
    bot.cancel_orders()
    tickers = bot.symbols

    for i in range(len(tickers)):
        data = bot.api.get_barset(tickers[i], 'day', limit=ema+2).df

        rsi = ta.RSI(data.iloc[:,3], timeperiod=2)

        # If RSI fulfills the conditions, we buy or sell accordingly.
        if rsi[len(rsi) - 2] > threshold and rsi[len(rsi) - 1] < threshold:
            num_bought = int(pc_bp / bot.last_prices[i])
            bp -= num_bought * bot.last_prices[i]
            bot.submit_order(i, num_bought)
        if rsi[len(rsi) - 2] < 100 - threshold and rsi[len(rsi) - 1] > 100 - threshold:
            bp += bot.positions[i] * bot.last_prices[i]
            bot.submit_order(i, bot.positions[i])
            

    # Print out the new buying power and append it to a text file.
    print(f"New Buying Power: ${bp:.2f}")
    textfile = open("buying_power.txt", "a")
    textfile.write(str(dt.datetime.today().date()) + " | New Buying Power: " + str(round(bp, 2)) + "\n")
    textfile.close()
