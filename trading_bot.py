import alpaca_trade_api as tradeapi
import os
import bs4 as bs
import requests

class PaperTradingBot(object):

    '''
    This method initializes the TradingBot object.
    '''
    def __init__(self, key="", secret="", numTickers=1, stocks=[]):
        self.key = key
        self.secret = secret
        self.endpoint = 'https://paper-api.alpaca.markets'
        self.api = tradeapi.REST(self.key, self.secret, self.endpoint)
        self.symbols = self.get_tickers(numTickers, stocks)
        self.current_orders = [None] * len(self.symbols)
        self.last_deltas = [0] * len(self.symbols)
        self.last_prices = [0] * len(self.symbols)
        self.positions = [0] * len(self.symbols)

        # Fill in the last prices for each symbol.
        for i in range(len(self.symbols)):
            last_quote = self.api.get_last_quote(self.symbols[i])
            if last_quote.bidprice == 0:
                last_quote = self.api.get_barset(self.symbols[i], limit=1, timeframe='minute')
                last_quote.bidprice = last_quote[self.symbols[i]][0].h

            self.last_prices[i] = float(last_quote.bidprice)

        # Fill in the current position for each symbol.
        for i in range(len(self.symbols)):
            try:
                self.positions[i] = int(self.api.get_position(self.symbols[i]).qty)
            except:
                self.position = 0

        # Fill in the current order for each symbol.
        existing_orders = self.api.list_orders(limit=1)
        for order in existing_orders:
            symbol = order.symbol
            id = order.id

            if symbol in self.symbols:
                index = self.symbols.index(symbol)
                self.current_orders[index] = self.api.get_order(id)

        # Set the trading environment to paper trading
        os.environ['APCA_API_BASE_URL'] = 'https://paper-api.alpaca.markets'

    '''
    This method submits an order to buy or sell according to the target
    number of shares. Takes in the index of the symbol in self.symbols.
    Returns the number of shares bought or sold.
    '''
    def submit_order(self, index, target):

        # If there is an existing order, we cancel our order.
        if self.current_orders[index] is not None: 
            print(f"CLOSED: [{self.last_deltas[index]:4d}] OF [{self.symbols[index]:>4s}] AT $[{self.last_prices[index]:8.2f}] EACH")
            self.last_deltas[index] = 0
            self.api.cancel_order(self.current_orders[index].id)

        # Delta is the difference in the number of shares.
        delta = target - self.positions[index]

        # If delta is 0, then we take no action.
        if delta == 0:
            print(f"BOUGHT: [{delta:4d}] OF [{self.symbols[index]:>4s}] AT $[{self.last_prices[index]:8.2f}] EACH")
            return delta

        # If delta is positive, we buy delta shares of the stock.
        if delta > 0:
            buy_quantity = delta
            if self.positions[index] < 0:
                buy_quantity = min(abs(self.position), buy_quantity)
            print(f"BOUGHT: [{buy_quantity:4d}] OF [{self.symbols[index]:>4s}] AT $[{self.last_prices[index]:8.2f}] EACH")
            self.last_deltas[index] = buy_quantity
            self.current_orders[index] = self.api.submit_order(self.symbols[index],
            buy_quantity, 'buy', 'limit', 'day', self.last_prices[index])
            return delta

        # If delta is negative, we sell delta shares of the stock.
        if delta < 0:
            sell_quantity = abs(delta)
            if self.positions[index] > 0:
                sell_quantity = min(abs(self.positions[index]), sell_quantity)
            self.last_deltas[index] = -1 * sell_quantity
            print(f"SOLD:   [{sell_quantity:4d}] OF [{self.symbols[index]:>4s}] AT $[{self.last_prices[index]:8.2f}] EACH")
            self.current_orders[index] = self.api.submit_order(self.symbols[index],
            sell_quantity, 'sell', 'limit', 'day', self.last_prices[index])
            return delta

    '''
    This method returns a list of the S&P 500 companies and their tickers
    and saves them into symbols.
    '''
    def get_tickers(self, numTickers, stocks):  

        if not stocks:
            # Get the S&P 500 data from Wikipedia.
            resp = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
            soup = bs.BeautifulSoup(resp.text, 'lxml')
            table = soup.find('table', {'class': 'wikitable sortable'})

            # Put the ticker symbols into tickers.
            tickers = []
            for row in table.findAll('tr')[1:]:
                ticker = row.findAll('td')[0].text
                if '.' not in ticker:
                    tickers.append(ticker[:-1])

            tickers = tickers[0:min(numTickers,500)]
        else:
            tickers = stocks

        return tickers

    '''
    This method closes all current positions.
    '''
    def close_positions(self):
        existing_orders = self.api.list_orders(limit=500)
        for order in existing_orders:
            print(f"CLOSED: [{int(order.qty):4d}] OF [{order.symbol:>4s}] AT $[{float(order.limit_price):8.2f}] EACH")
            self.api.cancel_order(order.id)
