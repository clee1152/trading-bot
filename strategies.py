import trading_bot as tb
import numpy as np
import datetime as dt

'''
This method will algorithmically trade according to
the SMA Crossover strategy. We will use the 10-day 
SMA as the short moving average and the 20-day SMA 
as the long moving average.
'''
def sma_crossover(key, secret, number, bp=0, stocks=[]):

    # Get the percent of the portfolio each stock takes up.
    if not stocks:
        percent = float(1 / number)
    else:
        percent = float(1 / len(stocks))
    pc_bp = percent * bp

    # Initialize the trading bot.
    bot = tb.PaperTradingBot(key, secret, number, stocks)
    bot.close_positions()
    tickers = bot.symbols

    # Gather the quotes from the last 20 dates and
    # calculate 10-day and 20-day SMA.
    for i in range(len(tickers)):
        data = bot.api.get_barset(tickers[i], 'day', limit=20).df

        data['10_sma'] = data.iloc[:,3].rolling(window=10, min_periods=1).mean()
        data['20_sma'] = data.iloc[:,3].rolling(window=20, min_periods=1).mean()

        data['cross'] = 0.0
        data['cross'] = np.where(data['10_sma'] > data['20_sma'], 1.0, 0.0)

        # If 10-day SMA > 20-day SMA, we buy shares. Otherwise, we sell shares.
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
    textfile.write(str(dt.datetime.today().date()) + " | New Buying Power: " + str(bp) + "\n")
    textfile.close()
            